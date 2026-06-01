from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]

def save_onboarding_state(client_id: str, data: dict):
    path = ROOT / "clients" / client_id / "connectors" / "live_onboarding.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return data

def load_onboarding_state(client_id: str):
    path = ROOT / "clients" / client_id / "connectors" / "live_onboarding.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8-sig"))
