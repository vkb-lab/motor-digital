from pathlib import Path
from k_atlas.command_autopilot import run_autopilot_demo

def test_artifacts_indexed():
    result = run_autopilot_demo()
    items = result["artifacts"]["items"]
    for key in ["campaign", "landing_page", "qr_code", "instagram_post", "creative", "publication_queue"]:
        assert items[key]["status"] == "PENDING_APPROVAL"
    assert Path(result["artifacts"]["path"]).exists()
