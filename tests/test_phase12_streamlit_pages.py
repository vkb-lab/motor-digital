from pathlib import Path
import py_compile

def test_phase12_pages_compile():
    for path in [
        "pages/KOS_Instagram_First_Post_Test.py",
        "pages/KOS_Instagram_Final_Arming_Check.py",
    ]:
        assert Path(path).exists()
        py_compile.compile(path, doraise=True)
