import sys
import subprocess
import tempfile
import os
from typing import NamedTuple
from langsmith import traceable

class ExecutionResult(NamedTuple):
    """Encapsulates the outcome of an isolated Python code execution."""
    success: bool
    stdout: str
    stderr: str
    return_code: int

class CodeExecutor:
    """
    Executes dynamically generated Python code inside an isolated subprocess.
    Protects the master orchestrator from crashes, hangs, and memory corruption.
    """

    @staticmethod
    @traceable(run_type="tool", name="SubprocessCodeExecutor")
    def execute(code: str, timeout_seconds: int = 60) -> ExecutionResult:
        """
        Writes code to a temporary file and runs it with the current Python environment.
        """
        # Inject headless matplotlib configuration to prevent GUI popups
        headless_preamble = (
            "try:\n"
            "    import matplotlib\n"
            "    matplotlib.use('Agg')\n"
            "except ImportError:\n"
            "    pass\n"
        )
        complete_code = headless_preamble + code

        temp_file_path = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as temp_file:
                temp_file.write(complete_code)
                temp_file_path = temp_file.name

            # Run in a dedicated subprocess using the active Python interpreter
            process = subprocess.run(
                [sys.executable, temp_file_path],
                capture_output=True,
                text=True,
                timeout=timeout_seconds
            )

            return ExecutionResult(
                success=(process.returncode == 0),
                stdout=process.stdout,
                stderr=process.stderr,
                return_code=process.returncode
            )

        except subprocess.TimeoutExpired:
            return ExecutionResult(
                success=False,
                stdout="",
                stderr=f"Execution timed out after {timeout_seconds} seconds.",
                return_code=-1
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                stdout="",
                stderr=f"System executor error: {str(e)}",
                return_code=-2
            )
        finally:
            # Always clean up the temporary script
            if temp_file_path and os.path.exists(temp_file_path):
                os.remove(temp_file_path)
