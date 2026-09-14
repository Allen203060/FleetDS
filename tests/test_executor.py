import pytest
from core.executor import CodeExecutor

def test_successful_execution():
    """Verify that valid Python code executes and returns stdout."""
    code = "print('Hello from Agent Sandbox!')"
    result = CodeExecutor.execute(code)
    
    assert result.success is True
    assert "Hello from Agent Sandbox!" in result.stdout
    assert result.return_code == 0

def test_syntax_error_handling():
    """Verify that code errors are caught cleanly without crashing the test."""
    bad_code = "print('Missing closing parenthesis"
    result = CodeExecutor.execute(bad_code)
    
    assert result.success is False
    assert result.return_code != 0
    assert "SyntaxError" in result.stderr

def test_timeout_protection():
    """Verify that infinite loops or long scripts are safely terminated."""
    slow_code = "import time\ntime.sleep(5)"
    result = CodeExecutor.execute(slow_code, timeout_seconds=1)
    
    assert result.success is False
    assert "timed out" in result.stderr.lower()

def test_headless_matplotlib():
    """Verify that matplotlib code can run without GUI display errors."""
    plot_code = (
        "import matplotlib.pyplot as plt\n"
        "fig, ax = plt.subplots()\n"
        "ax.plot([1, 2], [3, 4])\n"
        "print('Plot created successfully!')\n"
    )
    result = CodeExecutor.execute(plot_code)
    assert result.success is True
    assert "Plot created successfully!" in result.stdout
