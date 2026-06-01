from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
STATE_DIR = ROOT / "reports" / "phase6"

def save_job_state(job: dict):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    path = STATE_DIR / f"{job['job_id']}_state.json"
    path.write_text(json.dumps(job, ensure_ascii=False, indent=2), encoding="utf-8")
    job["state_path"] = str(path)
    return job

def load_job_state(job_id: str):
    path = STATE_DIR / f"{job_id}_state.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8-sig"))
