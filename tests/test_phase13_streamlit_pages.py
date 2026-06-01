from pathlib import Path
import py_compile

def test_phase13_pages_compile():
    for path in [
        "pages/KOS_Instagram_Live_Env_Setup.py",
        "pages/KOS_Instagram_Final_Live_Check.py",
    ]:
        assert Path(path).exists()
        py_compile.compile(path, doraise=True)
