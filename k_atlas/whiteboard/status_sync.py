from k_atlas.whiteboard.board_store import save_board

def sync_board_status(board: dict, status: str = "WHITEBOARD_READY"):
    board["status"] = status
    return save_board(board)
