from pathlib import Path
from k_atlas.command_autopilot import run_autopilot_demo
from k_atlas.whiteboard.board_store import load_board

def test_whiteboard_created():
    run_autopilot_demo()
    assert Path("live/whiteboard_state.json").exists()
    board = load_board()
    assert board["status"] == "WHITEBOARD_READY"
    assert len(board["cards"]) >= 5
