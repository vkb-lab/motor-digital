def render_board_text(board: dict):
    lines = [f"Job: {board.get('job_id')}", f"Cliente: {board.get('client_id')}"]
    for card in board.get("cards", []):
        lines.append(f"- {card['task_id']}: {card['status']}")
    return "\n".join(lines)
