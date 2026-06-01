from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
WHITEBOARD_PATH = ROOT / "live" / "whiteboard_state.json"

def save_board(board: dict):
    WHITEBOARD_PATH.parent.mkdir(parents=True, exist_ok=True)
    WHITEBOARD_PATH.write_text(json.dumps(board, ensure_ascii=False, indent=2), encoding="utf-8")
    return board

def load_board():
    if not WHITEBOARD_PATH.exists():
        return {"status": "EMPTY"}
    return json.loads(WHITEBOARD_PATH.read_text(encoding="utf-8-sig"))
