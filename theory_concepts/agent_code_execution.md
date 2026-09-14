# Theory Note: Dynamic Code Execution in Autonomous Agents

## 1. Subprocess Isolation vs In-Process Execution
- **Dangerous (In-Process `exec()`):** Running arbitrary LLM code inside the main application process using `eval()` or `exec()` can mutate global application memory, crash the server, or trigger memory leaks.
- **Safe (Subprocess Execution):** Spawning a fresh Python interpreter via `subprocess.run([sys.executable, ...])` isolates the execution. If the code segfaults, runs out of memory, or crashes, the parent orchestrator remains unharmed.

## 2. Execution Safeguards
- **Timeouts:** Long-running loops or infinite recursion are terminated via `timeout` parameters to prevent hanging the fleet.
- **Headless Matplotlib (`Agg`):** Plotting code must use the non-interactive `'Agg'` backend so it saves images to disk without trying to open a desktop GUI window.
- **Exit Code Inspection:** A zero exit code (`returncode == 0`) signifies successful execution; a non-zero code captures the stderr traceback for agent self-healing.
