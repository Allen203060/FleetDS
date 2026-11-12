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
* **Phase 2 (Hierarchical Squad Architecture):**
  - **Orchestrator (Top-Level):** Macro-level workflow director coordinating specialized agent squads.
  - **Squad Pattern (Triad Loop):** Each squad operates in a self-healing cyclic LangGraph subgraph (Lead Reviewer/Checklist Owner ↔ Coder ↔ Deterministic Sandbox/Profiler) with per-task iteration caps and snapshot rollback.
  - **Squad 1 (Initial Data Cleaning & Profiling):** Deterministic X-Ray Profiler + 7-Step Cleaning Checklist (`core/profiler.py`, `agents/cleaning_squad.py`).
  - **Squad 2+ (EDA, Feature Engineering, Modeling, Storytelling):** Subsequent specialized squads built on the same verified subgraph pattern.

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

### Phase 2: Hierarchical Squad Development (In Progress)
- [x] Locked in Hierarchical Squad Triad Architecture (Lead Reviewer ↔ Coder ↔ Deterministic Profiler/Sandbox).
- [ ] Build Deterministic X-Ray Profiler (`core/profiler.py` + `tests/test_profiler.py`).
- [ ] Finalize Lead Data Scientist Checklist & Evaluation Gates.
- [ ] Build **Squad 1: Data Cleaning Subgraph** (`agents/cleaning_squad.py` + `tests/test_cleaning_squad.py`).
- [ ] Build **Squad 2: EDA & Problem Framing Subgraph**.
- [ ] Build **Squad 3: Model Training & Optimization Subgraph**.
- [ ] Build **Squad 4: Storytelling & UI Layer (`app.py`)**.

---

## 🎯 Next Steps
1. Lock down the exact Data Cleaning Checklist & Reviewer Evaluation Gates.
2. Save theory note on **Automated Tabular Data Cleaning & Validation Gates** (`theory_concepts/data_cleaning_checklist.md`).
3. Implement `core/profiler.py` (Deterministic Data X-Ray) with companion unit tests (`tests/test_profiler.py`).
