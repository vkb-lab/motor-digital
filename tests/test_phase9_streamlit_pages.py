from pathlib import Path
import py_compile

def test_phase9_pages_compile():
    for path in [
        "pages/KOS_Approved_Safe_Execution.py",
        "pages/KOS_Safe_Execution_Queue.py",
        "pages/KOS_Safe_Execution_Review.py",
    ]:
        assert Path(path).exists()
        py_compile.compile(path, doraise=True)
