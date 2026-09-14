from core.state import AgentState
from langchain_core.messages import AIMessage

def explorer_agent_node(state: AgentState) -> dict:
    """
    Explorer / EDA Agent Stub.
    Implement the actual LLM prompt and schema inspection here.
    """
    # inspect state['raw_data_path']
    return {
        "current_agent": "Explorer",
        "task_type": "regression",  # Or determined by the LLM
        "messages": [AIMessage(content="[Explorer] Dataset analyzed. Identified target variable.")]
    }

def modeler_agent_node(state: AgentState) -> dict:
    """
    Modeler Agent Stub.
    Implement the model selection and training trigger here.
    """
    return {
        "current_agent": "Modeler",
        "metrics": {"r2_score": 0.85, "mae": 2.1},
        "messages": [AIMessage(content="[Modeler] Model trained successfully.")]
    }
