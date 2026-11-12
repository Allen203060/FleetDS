import os
import shutil
import operator
from typing import Annotated, Dict, List, Optional, TypedDict
from pydantic import BaseModel, Field

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langsmith import traceable

from core.config import AppConfig
from core.executor import CodeExecutor
from core.profiler import DataProfiler


# ---------------------------------------------------------------------------
# 1. The Lead Data Scientist's 6-Step Sequential Checklist & Eval Gates
# ---------------------------------------------------------------------------
CLEANING_CHECKLIST: List[Dict[str, str]] = [
    {
        "id": "1_structural_hygiene",
        "title": "Structural Hygiene & Sentinel Standardization",
        "rules": (
            "1. Strip whitespace and convert column names to unique snake_case.\n"
            "2. Drop useless auto-index columns (e.g. 'unnamed:_0') and 100%-empty rows/columns.\n"
            "3. Convert disguised sentinel values ('?', 'N/A', 'NA', 'null', 'None', '', '-', -999, 999999) into true NaN."
        ),
        "eval_gate": (
            "Zero UNNAMED columns remain; all headers are clean snake_case; "
            "sentinel_hits == 0 across columns; zero 100%-empty columns."
        ),
    },
    {
        "id": "2_type_recovery",
        "title": "Data Type Recovery & Parsing",
        "rules": (
            "1. Parse numeric strings containing currency symbols ($, €, ₹), commas, or % into float64/int64.\n"
            "2. Standardize boolean-like columns ('Yes'/'No', 'True'/'False') consistently.\n"
            "3. Parse date/time string columns with pd.to_datetime where appropriate."
        ),
        "eval_gate": (
            "Num-Str (numeric_string_suspects) == 0 on numeric columns; "
            "no silent wipeout where >10% of valid values become NaN from blind coercion."
        ),
    },
    {
        "id": "3_string_normalization",
        "title": "String & Categorical Normalization",
        "rules": (
            "1. Strip leading/trailing whitespace and collapse multiple internal spaces in text/categorical columns.\n"
            "2. Normalize casing (e.g. lowercase) on low/medium-cardinality categorical columns so 'Male'/'male '/'MALE' unify."
        ),
        "eval_gate": "Whitespace hits == 0 across all string columns; redundant casing duplicates unified.",
    },
    {
        "id": "4_deduplication",
        "title": "Deduplication & Key Integrity",
        "rules": (
            "1. Drop exact duplicate rows via df.drop_duplicates().\n"
            "2. If a clear unique ID column exists with duplicate IDs, keep the most complete/recent row."
        ),
        "eval_gate": "Exact Duplicate Rows == 0; row loss matches duplicate count cleanly.",
    },
    {
        "id": "5_missing_values",
        "title": "Missing Value Triage & Zero-Variance Pruning",
        "rules": (
            "1. If target_column is specified and has NaNs, DROP those rows (never impute target labels).\n"
            "2. Drop constant (zero-variance) columns and columns with >60% missing values.\n"
            "3. For remaining features: add a binary '{col}_is_missing' indicator if 5%-60% null.\n"
            "4. Impute numeric with median (if |skew| > 1.0) else mean; impute categorical with 'unknown' or mode."
        ),
        "eval_gate": "Total Missing Cells == 0; zero CONSTANT columns remain; target column has 0 nulls.",
    },
    {
        "id": "6_outlier_sanity",
        "title": "Domain Sanity & Statistical Outlier Handling",
        "rules": (
            "1. Fix physically/domain-impossible values (e.g. negative age, negative price/count) by converting to NaN & imputing or clipping.\n"
            "2. Handle extreme statistical outliers (IQR or 1st/99th percentile) via Winsorization/capping (not mass row deletion!)."
        ),
        "eval_gate": "Row retention >= 85% compared to pre-step count; zero domain-impossible values; zero NaNs.",
    },
]

CHECKLIST_BY_ID = {item["id"]: item for item in CLEANING_CHECKLIST}


# ---------------------------------------------------------------------------
# 2. LangGraph State Schema (Isolated Local State for Squad 1)
# ---------------------------------------------------------------------------
class CleaningSquadState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    raw_data_path: str
    last_approved_path: str
    candidate_path: str
    target_column: Optional[str]

    # Checklist & Loop Guards
    checklist: Dict[str, str]       # step_id -> 'pending' | 'passed' | 'skipped_max_retries'
    current_step: str               # active step_id or 'done'
    step_attempts: Dict[str, int]   # per-task retry counter
    max_retries: int

    # Artifacts & Feedback
    directive: str
    generated_code: str
    execution_stdout: str
    execution_error: Optional[str]
    before_profile: str
    after_profile: str
    reviewer_feedback: str
    approved_scripts: Annotated[List[str], operator.add]


# ---------------------------------------------------------------------------
# 3. Pydantic Structured Outputs for Deterministic Control Flow
# ---------------------------------------------------------------------------
class ReviewerDirective(BaseModel):
    already_clean: bool = Field(
        description="True ONLY if the current Dataset X-Ray proves this checklist step already satisfies its eval gate and needs zero code changes."
    )
    directive: str = Field(
        description="Concrete, actionable Pandas data-cleaning instructions for the Coder Agent to execute this step."
    )


class CoderOutput(BaseModel):
    explanation: str = Field(description="Brief explanation of what the script does.")
    code: str = Field(description="Complete, standalone executable Python code without markdown fences.")


class ReviewerVerdict(BaseModel):
    passed: bool = Field(description="True if After-Profile strictly satisfies the step's eval gate without breaking data integrity.")
    feedback: str = Field(description="Concise justification if passed, or exact fix instructions if rejected.")


# ---------------------------------------------------------------------------
# 4. Helper: Initialize Gemini LLM via Central AppConfig
# ---------------------------------------------------------------------------
def _get_llm(temperature: float = 0.0) -> ChatGoogleGenerativeAI:
    AppConfig.validate()
    os.environ["GOOGLE_API_KEY"] = AppConfig.GOOGLE_API_KEY
    return ChatGoogleGenerativeAI(model=AppConfig.DEFAULT_MODEL, temperature=temperature)


# ---------------------------------------------------------------------------
# 5. Graph Nodes
# ---------------------------------------------------------------------------
@traceable(name="ReviewerPlanNode")
def reviewer_plan_node(state: CleaningSquadState) -> dict:
    """Selects the next pending checklist step, enforces retry caps, and issues a directive."""
    checklist = dict(state["checklist"])
    step_attempts = dict(state["step_attempts"])
    max_retries = state["max_retries"]

    # Refresh the current dataset profile if not yet loaded
    before_profile = state.get("before_profile") or DataProfiler.profile(state["last_approved_path"]).to_markdown()

    # Find the next pending step in strict sequential order
    next_step_id = None
    for item in CLEANING_CHECKLIST:
        sid = item["id"]
        if checklist.get(sid, "pending") == "pending":
            if step_attempts.get(sid, 0) >= max_retries:
                checklist[sid] = "skipped_max_retries"
                continue
            next_step_id = sid
            break

    if next_step_id is None:
        return {
            "checklist": checklist,
            "current_step": "done",
            "before_profile": before_profile,
            "messages": [AIMessage(content="[Lead Reviewer] All checklist items completed.")],
        }

    step_spec = CHECKLIST_BY_ID[next_step_id]
    llm = _get_llm(temperature=0.0).with_structured_output(ReviewerDirective)

    prompt = (
        f"You are the Lead Data Scientist reviewing a dataset for Step '{step_spec['title']}'.\n"
        f"Target Column (do NOT impute or drop silently): {state.get('target_column') or 'Not specified'}\n\n"
        f"### Step Rules:\n{step_spec['rules']}\n\n"
        f"### Evaluation Gate:\n{step_spec['eval_gate']}\n\n"
        f"### Current Dataset X-Ray:\n{before_profile}\n\n"
        f"### Previous Rejection Feedback (if retrying):\n{state.get('reviewer_feedback') or 'None'}\n\n"
        "Decide if the dataset already passes this step's Evaluation Gate (already_clean=True), "
        "or issue crisp, specific column-level instructions for the Coder Agent."
    )
    decision: ReviewerDirective = llm.invoke([SystemMessage(content=prompt)])

    if decision.already_clean:
        checklist[next_step_id] = "passed"
        return {
            "checklist": checklist,
            "current_step": next_step_id,
            "before_profile": before_profile,
            "reviewer_feedback": "",
            "directive": "ALREADY_CLEAN",
            "messages": [AIMessage(content=f"[Lead Reviewer] Step '{next_step_id}' already clean -> PASSED.")],
        }

    return {
        "checklist": checklist,
        "current_step": next_step_id,
        "before_profile": before_profile,
        "directive": decision.directive,
        "messages": [AIMessage(content=f"[Lead Reviewer] Assigned '{next_step_id}': {decision.directive}")],
    }


@traceable(name="CoderNode")
def coder_node(state: CleaningSquadState) -> dict:
    """Writes or self-heals Pandas Python code to execute the Reviewer's directive."""
    llm = _get_llm(temperature=0.0).with_structured_output(CoderOutput)

    error_context = ""
    if state.get("execution_error"):
        error_context = (
            f"\n### PREVIOUS EXECUTION ERROR (FIX THIS):\n{state['execution_error']}\n"
            f"### PREVIOUS BROKEN CODE:\n{state.get('generated_code', '')}\n"
        )
    elif state.get("reviewer_feedback"):
        error_context = (
            f"\n### REVIEWER REJECTION FEEDBACK (FIX LOGIC):\n{state['reviewer_feedback']}\n"
            f"### PREVIOUS REJECTED CODE:\n{state.get('generated_code', '')}\n"
        )

    prompt = (
        "You are a Senior Data Engineer writing clean, defensive Pandas Python code.\n"
        f"Input CSV path: `{state['last_approved_path']}`\n"
        f"Output CSV path: `{state['candidate_path']}`\n\n"
        f"### Current Dataset X-Ray:\n{state['before_profile']}\n\n"
        f"### Lead Data Scientist Directive ({state['current_step']}):\n{state['directive']}\n"
        f"{error_context}\n"
        "Requirements:\n"
        "- Load the CSV safely using pandas (try utf-8, fallback latin1).\n"
        "- Apply ONLY the requested step transformations cleanly.\n"
        f"- MUST save the resulting DataFrame to `{state['candidate_path']}` with `index=False`.\n"
        "- Print a brief summary of rows/columns modified to stdout.\n"
        "- Return raw Python code only (no markdown ```python fences)."
    )

    result: CoderOutput = llm.invoke([HumanMessage(content=prompt)])
    return {
        "generated_code": result.code,
        "execution_error": None,
        "messages": [AIMessage(content=f"[Coder] Generated script for '{state['current_step']}': {result.explanation}")],
    }


@traceable(name="SandboxNode")
def sandbox_node(state: CleaningSquadState) -> dict:
    """Executes the Coder's script in an isolated subprocess and auto-profiles the candidate output."""
    candidate_path = state["candidate_path"]
    if os.path.exists(candidate_path):
        os.remove(candidate_path)

    exec_result = CodeExecutor.execute(state["generated_code"], timeout_seconds=60)
    step_id = state["current_step"]
    step_attempts = dict(state["step_attempts"])

    if not exec_result.success:
        step_attempts[step_id] = step_attempts.get(step_id, 0) + 1
        return {
            "step_attempts": step_attempts,
            "execution_stdout": exec_result.stdout,
            "execution_error": exec_result.stderr,
            "messages": [AIMessage(content=f"[Sandbox] Execution failed (attempt {step_attempts[step_id]}): {exec_result.stderr[:300]}")],
        }

    if not os.path.exists(candidate_path):
        step_attempts[step_id] = step_attempts.get(step_id, 0) + 1
        err = f"Script exited 0 but failed to write output file: {candidate_path}"
        return {
            "step_attempts": step_attempts,
            "execution_stdout": exec_result.stdout,
            "execution_error": err,
            "messages": [AIMessage(content=f"[Sandbox] {err}")],
        }

    after_profile = DataProfiler.profile(candidate_path).to_markdown()
    return {
        "execution_stdout": exec_result.stdout,
        "execution_error": None,
        "after_profile": after_profile,
        "messages": [AIMessage(content=f"[Sandbox] Executed cleanly. Generated post-step X-Ray.")],
    }


@traceable(name="ReviewerEvalNode")
def reviewer_eval_node(state: CleaningSquadState) -> dict:
    """Evaluates Before vs. After X-Rays against the active step's Evaluation Gate."""
    step_id = state["current_step"]
    step_spec = CHECKLIST_BY_ID[step_id]
    llm = _get_llm(temperature=0.0).with_structured_output(ReviewerVerdict)

    prompt = (
        f"You are the Lead Data Scientist auditing Step '{step_spec['title']}'.\n"
        f"### Evaluation Gate:\n{step_spec['eval_gate']}\n\n"
        f"### BEFORE X-Ray:\n{state['before_profile']}\n\n"
        f"### AFTER X-Ray:\n{state['after_profile']}\n\n"
        f"### Script Stdout:\n{state['execution_stdout']}\n\n"
        "Compare BEFORE vs AFTER carefully. Did the script satisfy the Evaluation Gate without accidental data destruction?"
    )
    verdict: ReviewerVerdict = llm.invoke([SystemMessage(content=prompt)])

    checklist = dict(state["checklist"])
    step_attempts = dict(state["step_attempts"])

    if verdict.passed:
        # Promote candidate snapshot -> last_approved_path
        shutil.copyfile(state["candidate_path"], state["last_approved_path"])
        checklist[step_id] = "passed"
        return {
            "checklist": checklist,
            "before_profile": state["after_profile"],
            "reviewer_feedback": "",
            "approved_scripts": [f"# --- {step_id} ---\n{state['generated_code']}\n"],
            "messages": [AIMessage(content=f"[Lead Reviewer] Step '{step_id}' PASSED: {verdict.feedback}")],
        }

    # Rejected: keep last_approved_path untouched and increment retry counter
    step_attempts[step_id] = step_attempts.get(step_id, 0) + 1
    return {
        "step_attempts": step_attempts,
        "reviewer_feedback": verdict.feedback,
        "messages": [AIMessage(content=f"[Lead Reviewer] Step '{step_id}' REJECTED (attempt {step_attempts[step_id]}): {verdict.feedback}")],
    }


# ---------------------------------------------------------------------------
# 6. Conditional Routing Functions
# ---------------------------------------------------------------------------
def route_after_plan(state: CleaningSquadState) -> str:
    if state["current_step"] == "done":
        return END
    if state.get("directive") == "ALREADY_CLEAN":
        return "reviewer_plan"
    return "coder"


def route_after_sandbox(state: CleaningSquadState) -> str:
    if state.get("execution_error"):
        step_id = state["current_step"]
        if state["step_attempts"].get(step_id, 0) >= state["max_retries"]:
            return "reviewer_plan"  # Escalate to mark skipped_max_retries
        return "coder"              # Self-heal syntax/runtime error
    return "reviewer_eval"


# ---------------------------------------------------------------------------
# 7. Subgraph Builder
# ---------------------------------------------------------------------------
def build_cleaning_squad_graph():
    """Compiles the cyclic Data Cleaning Squad LangGraph."""
    builder = StateGraph(CleaningSquadState)

    builder.add_node("reviewer_plan", reviewer_plan_node)
    builder.add_node("coder", coder_node)
    builder.add_node("sandbox", sandbox_node)
    builder.add_node("reviewer_eval", reviewer_eval_node)

    builder.add_edge(START, "reviewer_plan")
    builder.add_conditional_edges("reviewer_plan", route_after_plan, {"coder": "coder", "reviewer_plan": "reviewer_plan", END: END})
    builder.add_edge("coder", "sandbox")
    builder.add_conditional_edges("sandbox", route_after_sandbox, {"coder": "coder", "reviewer_plan": "reviewer_plan", "reviewer_eval": "reviewer_eval"})
    builder.add_edge("reviewer_eval", "reviewer_plan")

    return builder.compile()
