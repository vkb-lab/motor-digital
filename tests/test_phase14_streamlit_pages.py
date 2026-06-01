from pathlib import Path
import py_compile

def test_phase14_pages_compile():
    for path in [
        "pages/KOS_Instagram_Final_Run_Gate.py",
        "pages/KOS_Instagram_Real_Send_Control.py",
    ]:
        assert Path(path).exists()
        py_compile.compile(path, doraise=True)
