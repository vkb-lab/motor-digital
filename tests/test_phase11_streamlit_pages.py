from pathlib import Path
import py_compile

def test_phase11_pages_compile():
    for path in [
        "pages/KOS_Instagram_Real_Publisher_Gate.py",
        "pages/KOS_Instagram_Real_Readiness.py",
    ]:
        assert Path(path).exists()
        py_compile.compile(path, doraise=True)
