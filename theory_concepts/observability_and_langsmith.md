# Theory Note: Observability & Testing in Multi-Agent Pipelines

## 1. Zero-Code LangSmith Tracing
LangGraph natively inherits LangChain's callback system. By defining standard environment variables, every `.invoke()` or `.stream()` automatically transmits spans to the LangSmith cloud without modifying node business logic:
- `LANGCHAIN_TRACING_V2=true`
- `LANGCHAIN_API_KEY=<your-key>`
- `LANGCHAIN_PROJECT=<project-name>`

## 2. Custom Tool Tracing with `@traceable`
For non-LangChain code (such as subprocess Python executors or custom database queries), the `@traceable` decorator from the `langsmith` library wraps the function in an OpenTelemetry-compatible span and embeds it into the active LangGraph trace tree.

## 3. Testing Pyramid for Agentic Systems
- **Unit Tests (Fast, Free, Local):** Tests state schema mutations, code execution sandboxes, and graph compilation without network or LLM dependencies.
- **Integration Tests (Mocked/Local Models):** Tests multi-step agent transitions using deterministic stubs.
- **Eval Sets (LangSmith Datasets):** Evaluates real LLM reasoning against benchmark data science problems in production.
