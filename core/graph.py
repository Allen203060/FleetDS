from langgraph.graph import StateGraph, START, END
from core.state import AgentState
from agents.stubs import explorer_agent_node, modeler_agent_node

def build_data_fleet_graph():
    """
    Assembles the multi-agent StateGraph.
    Connects nodes in the data science lifecycle: START -> Explorer -> Modeler -> END.
    """
    # 1. Initialize StateGraph with the shared blackboard schema
    workflow = StateGraph(AgentState)

    # 2. Register Agent Nodes
    workflow.add_node("explorer", explorer_agent_node)
    workflow.add_node("modeler", modeler_agent_node)

    # 3. Define Flow Edges
    workflow.add_edge(START, "explorer")
    workflow.add_edge("explorer", "modeler")
    workflow.add_edge("modeler", END)

    # 4. Compile the graph into an executable Runnable
    app = workflow.compile()
    return app
