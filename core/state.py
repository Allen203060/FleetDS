from typing import TypedDict, Annotated, List, Dict, Any, Optional
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """
    Central State Graph Schema for the Autonomous Data Science Pipeline.
    Acts as the shared blackboard across all orchestrator nodes and worker agents.
    """
    # Preserves conversational history across all agents (appends, does not overwrite)
    messages: Annotated[List[BaseMessage], add_messages]
    
    # Dataset tracking
    raw_data_path: str
    cleaned_data_path: Optional[str]
    target_column: Optional[str]
    task_type: Optional[str]  # e.g., 'regression', 'classification', 'unsupervised', 'eda'
    
    # Execution & Reasoning artifacts
    current_agent: Optional[str]
    generated_code: Optional[str]
    execution_output: Optional[str]
    execution_error: Optional[str]
    
    # Results & Deliverables
    metrics: Dict[str, Any]
    visualizations: List[str]  # File paths to generated PNG/HTML plots
    final_report: Optional[str]
                                        