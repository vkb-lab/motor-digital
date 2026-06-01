from pathlib import Path
import py_compile

def test_phase15_pages_compile():
    for path in [
        "pages/KOS_Creative_Asset_Factory.py",
        "pages/KOS_Public_Asset_URL_Check.py",
        "pages/KOS_Instagram_Asset_Handoff.py",
    ]:
        assert Path(path).exists()
        py_compile.compile(path, doraise=True)
