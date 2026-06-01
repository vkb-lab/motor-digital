from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "reports" / "artifacts" / "artifact_index.json"

def save_artifact_index(data: dict):
    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    INDEX_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return data

def load_artifact_index():
    if not INDEX_PATH.exists():
        return {"artifacts": []}
    return json.loads(INDEX_PATH.read_text(encoding="utf-8-sig"))
