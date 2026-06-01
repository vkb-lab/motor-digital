from pathlib import Path
import py_compile

def test_phase8_pages_compile():
    for path in [
        "pages/KOS_Launch_Sandbox.py",
        "pages/KOS_Launch_Confirmation.py",
        "pages/KOS_Client_Launch_Board.py",
    ]:
        assert Path(path).exists()
        py_compile.compile(path, doraise=True)
