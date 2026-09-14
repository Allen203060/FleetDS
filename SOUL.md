# Project Soul: LangChain / LangGraph Multi-Agent RAG & Data Fleet

## 🏗️ Core Architecture & Agent Sync
This document serves as the central memory system for human-agent collaboration and synchronization across developer workstreams.

### Core Development Directive
* **Continuous Unit Testing & TDD:** Every newly introduced agent, tool, or graph edge must be accompanied by automated unit tests in `tests/`. No feature is considered complete until all unit tests pass with zero regressions.

### Work Division & Foundation Phase
* **Phase 1 (Foundational Backbone - COMPLETED ✅):** 
  - Standardized directory architecture (`/core`, `/agents`, `/data`, `/theory_concepts`, `/tests`).
  - Centralized LangGraph `AgentState` schema (`core/state.py`).
  - Environment and runtime configuration with LangSmith telemetry (`core/config.py`).
  - Base agent node stubs (`agents/stubs.py`).
  - Subprocess Code Execution Engine with `@traceable` telemetry and defensive headless plotting (`core/executor.py`).
  - Core LangGraph workflow compilation (`core/graph.py`).
  - Full unit test suite with `pytest` (`tests/test_executor.py`, `tests/test_graph.py`) — **6/6 tests passing**.
* **Phase 2 (Concurrent Agent Development):**
  - **Track A (Core Infrastructure & Execution Engine):** Data Ingestion, Semantic Chunking, Embeddings, Vector Store / Retriever, and self-healing execution loops.
  - **Track B (Specialized Agents & Presentation Layer):** Prompt engineering for specialized agents (Explorer, Modeler, Storyteller), LangGraph node logic, and Streamlit/FastAPI UI.

---

## 📜 Integration Contracts (Observability & Testing)
- **Test Discovery:** Configured via `pytest.ini` with `pythonpath = .`.
- **Sandbox Resilience:** `CodeExecutor.execute` safely handles missing GUI libraries via defensive try/except wrappers.
- **LangSmith Tracing:** Configured via `AppConfig` and native environment variables (`LANGCHAIN_TRACING_V2=true`).
- **Test Suite Status:** 6 passed in 2.47s.

---

## 📈 Current Progress

### Phase 1: Foundation (Completed ✅)
- [x] Initialized architecture plan and sync protocol in `SOUL.md`.
- [x] Formulated foundational `AgentState` design for LangGraph (`core/state.py`).
- [x] Created `core/config.py`.
- [x] Created `core/executor.py`.
- [x] Created `core/graph.py`.
- [x] Created `pytest.ini`.
- [x] Created unit test suite in `tests/`.
- [x] Fixed matplotlib dependency & verified 6/6 tests passing.

### Phase 2: Agent Development (Starting Now)
- [ ] Build the real **Explorer (Data Analyst / EDA) Agent** (`agents/explorer.py`).
  - [ ] Implement data profiling & schema extraction.
  - [ ] Implement LLM target/task inference via LangChain structured output.
  - [ ] Implement unit tests (`tests/test_explorer.py`).
- [ ] Build the real **Modeler (ML Engineer) Agent** (`agents/modeler.py`).
  - [ ] Implement dynamic scikit-learn training script generation.
  - [ ] Implement model evaluation & metrics capture.
  - [ ] Implement unit tests (`tests/test_modeler.py`).

---

## 🎯 Next Steps
1. Introduce concept and design for **The Explorer (Data Analyst) Agent**.
2. Save theory note on **Structured Outputs in LangChain** (`theory_concepts/structured_outputs.md`).
3. Implement `agents/explorer.py` and its companion unit tests in `tests/test_explorer.py`.
