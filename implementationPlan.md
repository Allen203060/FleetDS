# Implementation Plan: Autonomous AI Data Scientist Fleet

## 🎯 Project Goal
To build a sophisticated multi-agent system where specialized AI agents fully automate the Data Science lifecycle—from exploratory data analysis to model training and reporting.

---

## 🤝 Work Division (Concurrent Development)
To allow Allen and Divya to build this system simultaneously without blocking each other, we have divided the architecture into two distinct tracks.

### Track A: Infrastructure & The Orchestrator (Allen's Focus)
* **Focus:** The "Brain" and the execution environment. You are building the foundation that allows the agents to run code and share data.
* **Key Components to Build:**
  1. **Shared Memory State (The Brain):** A Python state manager that securely passes artifacts (like `processed_data.csv` or `model.pkl`) between agents.
  2. **Dynamic Code Execution Environment:** A secure Python sandbox (like an in-memory Jupyter kernel) where agents can write, test, and execute Python code dynamically.
  3. **The Orchestrator Agent:** The lead agent that takes the user's natural language request, plans the pipeline, and routes tasks to the specialized agents.
* **Output:** A robust backend system and the Lead Orchestrator ready to delegate tasks.

### Track B: Specialized Agents & User Interface (Divya's Focus)
* **Focus:** The specialized "Workers" and the Frontend experience. Divya will engineer the precise system prompts for each specialized agent and build the UI.
* **Key Components to Build:**
  1. **The Specialized Agents:** Creating the prompt templates, LLM chains, and logic for the Explorer, Engineer, Modeler, and Storyteller.
  2. **The User Interface:** Building a Streamlit or FastAPI dashboard where users can upload CSVs, chat with the Orchestrator, and view the generated plots.
  3. **Mock Executions:** While Allen builds the code execution sandbox, Divya can test her agents by having them output Python code as plain text (verifying the logic before it actually runs).
* **Output:** The specialized agent workforce and the beautiful user-facing dashboard.

---

## 🔗 The Integration Point (The Handshake)
Both tracks will converge in the `app.py` file. 
1. Divya's Streamlit UI will take the user's CSV and send it to Allen's Orchestrator.
2. Allen's Orchestrator will route the tasks to Divya's Specialized Agents.
3. The Specialized Agents will write Python code and send it to Allen's Execution Sandbox to run.
4. The results will be passed back to Divya's UI for rendering!

---

## 🚀 Next Steps
1. **Initialize Git & Folders:** Allen creates the base directory structure (`/core`, `/agents`, `/ui`).
2. **Define the Agent API:** Both of you agree on exactly what Python dictionary or schema an agent will output when it finishes a task.
3. **Begin Coding:** Divya starts building the Streamlit UI and prompt templates, while Allen begins building the Python Code Execution sandbox.
