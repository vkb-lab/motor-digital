from pathlib import Path
import json
from datetime import datetime, timezone
from k_atlas.artifact_index import save_artifact_index

ROOT = Path(__file__).resolve().parents[1]

def build_artifacts(client_id: str, job_id: str):
    artifacts = {
        "status": "PENDING_APPROVAL",
        "client_id": client_id,
        "job_id": job_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "external_call_executed": False,
        "items": {
            "campaign": {"status": "PENDING_APPROVAL"},
            "landing_page": {"status": "PENDING_APPROVAL"},
            "qr_code": {"status": "PENDING_APPROVAL"},
            "instagram_post": {"status": "PENDING_APPROVAL"},
            "creative": {"status": "PENDING_APPROVAL"},
            "publication_queue": {"status": "PENDING_APPROVAL"},
        },
    }
    path = ROOT / "reports" / "artifacts" / f"{job_id}_artifacts.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(artifacts, ensure_ascii=False, indent=2), encoding="utf-8")
    artifacts["path"] = str(path)
    save_artifact_index({"job_id": job_id, "client_id": client_id, "artifacts": artifacts["items"]})
    return artifacts
