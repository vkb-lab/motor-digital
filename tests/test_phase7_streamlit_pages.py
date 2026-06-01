from pathlib import Path
import py_compile

def test_phase7_pages_compile():
    for path in ["pages/KOS_Live_Onboarding.py","pages/KOS_Connector_Readiness.py","pages/KOS_Approval_Gate.py"]:
        assert Path(path).exists()
        py_compile.compile(path, doraise=True)
