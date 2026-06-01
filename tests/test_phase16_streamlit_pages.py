from pathlib import Path
import py_compile

def test_phase16_pages_compile():
    for path in [
        "pages/KOS_Public_Image_URL_Bridge.py",
        "pages/KOS_Instagram_Image_URL_Ready.py",
    ]:
        assert Path(path).exists()
        py_compile.compile(path, doraise=True)
