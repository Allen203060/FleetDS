import os
import shutil
import pandas as pd
from core.config import AppConfig
from core.profiler import DataProfiler
from agents.cleaning_squad import CLEANING_CHECKLIST, build_cleaning_squad_graph


def create_messy_dataset(path: str):
    """Creates a synthetic dirty CSV exercising every item in the cleaning checklist."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df = pd.DataFrame({
        "Unnamed: 0": [0, 1, 2, 3, 4, 5, 6, 6, 7],
        " Customer Age ": [28, 35, -5, 42, "N/A", 29, 31, 31, 220],
        "Total Price($)": ["$1,200.50", "$850.00", "$450.25", "?", "$2,100.00", "$600.00", "$999,999.00", "$999,999.00", "$710.00"],
        "Category": ["Electronics ", "electronics", "HOME", "Home ", "ELECTRONICS", "home", "Clothing", "Clothing", None],
        "Constant_Flag": ["ACTIVE"] * 9,
        "Churned": [0, 1, 0, 1, 0, None, 1, 1, 0],
    })
    df.to_csv(path, index=False)


def main():
    raw_path = os.path.join(AppConfig.DATA_DIR, "messy_sales.csv")
    working_dir = os.path.join(AppConfig.DATA_DIR, "cleaning_workspace")
    os.makedirs(working_dir, exist_ok=True)

    last_approved = os.path.join(working_dir, "approved_snapshot.csv")
    candidate = os.path.join(working_dir, "candidate_snapshot.csv")

    create_messy_dataset(raw_path)
    shutil.copyfile(raw_path, last_approved)

    print("\n=== INITIAL RAW DATASET X-RAY ===")
    print(DataProfiler.profile(raw_path).to_markdown())

    graph = build_cleaning_squad_graph()
    initial_state = {
        "messages": [],
        "raw_data_path": raw_path,
        "last_approved_path": last_approved,
        "candidate_path": candidate,
        "target_column": "churned",
        "checklist": {item["id"]: "pending" for item in CLEANING_CHECKLIST},
        "current_step": "",
        "step_attempts": {},
        "max_retries": 3,
        "directive": "",
        "generated_code": "",
        "execution_stdout": "",
        "execution_error": None,
        "before_profile": "",
        "after_profile": "",
        "reviewer_feedback": "",
        "approved_scripts": [],
    }

    print("\n=== RUNNING AUTONOMOUS CLEANING SQUAD ===")
    final_state = graph.invoke(initial_state, config={"recursion_limit": 60})

    for msg in final_state["messages"]:
        print(msg.content)

    print("\n=== FINAL CHECKLIST STATUS ===")
    for step_id, status in final_state["checklist"].items():
        print(f"  {step_id}: {status} (retries: {final_state['step_attempts'].get(step_id, 0)})")

    print("\n=== FINAL CLEANED DATASET X-RAY ===")
    print(DataProfiler.profile(last_approved).to_markdown())


if __name__ == "__main__":
    main()
