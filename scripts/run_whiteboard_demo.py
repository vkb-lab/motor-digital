from k_atlas.command_autopilot import run_autopilot_demo
from k_atlas.whiteboard.board_store import load_board

run_autopilot_demo()
board = load_board()
print(board["status"])
