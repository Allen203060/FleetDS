# Technical Interview Preparation: Challenges & Engineering Decisions Journal

This document records architectural challenges, significant bugs, root-cause analyses, and solutions encountered while building the Autonomous Multi-Agent Data Science Platform.

---

## Challenge 1: Python Module Resolution & Test Discovery Failure (`pytest`)

### The Bug / Challenge
When executing `pytest -v` from the project root (`/home/allen20306/allen/ADEP`), `pytest` terminated abruptly during the collection phase with:
```text
ModuleNotFoundError: No module named 'core'
```
The application executed without issue when run via `python main.py`, but automated unit tests inside `tests/` could not resolve internal application packages (`core.executor`, `core.graph`).

### The Root Cause / Trade-off
* **`sys.path` Entry Point Differences:** When running a script directly via `python path/to/script.py`, the Python interpreter automatically prepends the directory containing the script to `sys.path`.
* In contrast, when the `pytest` CLI runner executes as a standalone binary in `.venv/bin/pytest`, it does not automatically inject the current working directory into `sys.path` unless explicitly instructed.
* Because `tests/` is a separate subdirectory, Python attempted to resolve `core` relative to the Python standard library and `.venv/site-packages`, failing to recognize the project root as a root package directory.

### The Solution
* **Root Configuration (`pytest.ini`):** Configured standard test runner discovery settings by introducing a `pytest.ini` configuration file with:
  ```ini
  [pytest]
  pythonpath = .
  testpaths = tests
  ```
* **Why this approach?** Adding `pythonpath = .` explicitly instructs `pytest`'s import engine to prepend the workspace root directory to `sys.path` across all environments, IDE extensions, and CI/CD pipelines, avoiding brittle manual hacks like `sys.path.append(os.path.abspath(".."))` inside test files.

---

## Challenge 2: Unconditional Preamble Dependency & Sandbox Isolation Failure

### The Bug / Challenge
During unit testing of `CodeExecutor`, tests for basic standard output (`test_successful_execution`) and timeouts (`test_timeout_protection`) failed unexpectedly with:
```text
ModuleNotFoundError: No module named 'matplotlib'
```
Even simple commands like `print('Hello')` failed to run inside the execution sandbox.

### The Root Cause / Trade-off
* **Hardcoded Preamble Injection:** To prevent desktop GUI windows from freezing the application during agent plotting, `CodeExecutor` prepended an unconditional `import matplotlib; matplotlib.use('Agg')` to **every single script** before sending it to the Python subprocess.
* When `matplotlib` was missing from the virtual environment, this premature import crashed the entire execution sandbox before the agent's actual code could even start, violating the principle of least dependency.

### The Solution
1. **Defensive Preamble Wrapping:** Modified `CodeExecutor.execute()` to wrap the headless graphics configuration in a graceful `try...except ImportError` block. If `matplotlib` is installed, it safely sets `'Agg'`; if not, the sandbox continues running non-graphical code without crashing.
2. **Explicit Dependency Tracking:** Added `matplotlib` to `requirements.txt` to guarantee visualization support for the data science fleet.
