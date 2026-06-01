from pathlib import Path
import py_compile

def test_phase10_pages_compile():
    for path in [
        "pages/KOS_Production_Deploy_Bridge.py",
        "pages/KOS_Vercel_Readiness.py",
    ]:
        assert Path(path).exists()
        py_compile.compile(path, doraise=True)
