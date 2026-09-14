import pytest
from core.graph import build_data_fleet_graph
from core.state import AgentState

def test_graph_compilation():
    """Verify that the StateGraph compiles without disconnected nodes or topology errors."""
    fleet = build_data_fleet_graph()
    assert fleet is not None

def test_graph_execution_flow():
    """Verify that state passes through Explorer and Modeler nodes as expected."""
    fleet = build_data_fleet_graph()
    
    initial_state: AgentState = {
        "messages": [],
        "raw_data_path": "data/mock.csv",
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
    
    final_state = fleet.invoke(initial_state)
    
    # Verify state updates from nodes
    assert final_state["current_agent"] == "Modeler"
    assert "r2_score" in final_state["metrics"]
    assert len(final_state["messages"]) == 2
