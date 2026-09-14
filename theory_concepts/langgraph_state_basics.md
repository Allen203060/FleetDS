# Theory Note: LangGraph State & The Blackboard Architecture

## 1. Core Concept
In multi-agent systems built with LangGraph, agents are modeled as a **StateGraph**.
- **Nodes** are Python functions or agents that perform actions (e.g., Engineer cleans data, Modeler trains model).
- **Edges** define the workflow and conditional routing between nodes.
- **State** is the centralized data structure passed from node to node across edges.

## 2. Reducers and Immutability
In standard Python dictionaries, writing a key overwrites its previous value. In LangGraph:
- Default behavior: Returning a dictionary like `{"task_type": "regression"}` overwrites that specific key in the state without touching other keys.
- Reducer behavior (`Annotated[list, add_messages]`): Tells LangGraph not to overwrite existing messages, but to **append** new messages to the existing list. This preserves the conversational and thinking history across all agents.
