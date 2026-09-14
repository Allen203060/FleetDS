from core.graph import build_data_fleet_graph
from core.state import AgentState

def run_dry_test():
    print("🚀 Initializing LangGraph Data Science Fleet...")
    fleet = build_data_fleet_graph()

    initial_state: AgentState = {
        "messages": [],
        "raw_data_path": "data/sample.csv",
        "cleaned_data_path": None,
        "target_column": None,
        "task_type": None,
        "current_agent": None,
        "generated_code": None,
        "execution_output": None,
        "execution_error": None,
        "metrics": {},
        "visualizations": [],
        "final_report": None,
    }

    print("⚡ Executing pipeline graph...")
    
    # Passing RunnableConfig to tag and organize runs in LangSmith
    config = {
        "run_name": "DryRunPipelineTest",
        "tags": ["phase1-foundation", "dry-run", "test"],
        "metadata": {"environment": "development"}
    }
    
    final_output = fleet.invoke(initial_state, config=config)

    print("\n✅ Execution Finished Successfully!")
    print(f"Active Agent at Finish: {final_output['current_agent']}")
    print(f"Metrics Recorded: {final_output['metrics']}")
    print(f"Message Log Count: {len(final_output['messages'])}")

if __name__ == "__main__":
    run_dry_test()
