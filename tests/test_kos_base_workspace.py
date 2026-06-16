from __future__ import annotations

from k_atlas.kos_base import workspace
from k_atlas.whiteboard import board_store


def test_base_workspace_snapshot_is_safe(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(board_store, "WHITEBOARD_PATH", tmp_path / "whiteboard_state.json")
    snapshot = workspace.build_workspace_snapshot()

    assert snapshot["meta_level4_side_effects"] == "none"
    assert snapshot["board"]["status"] != "EMPTY"
    assert "branch" in snapshot
    assert snapshot["runtime_presence"]["secret_values_exposed"] is False
    assert "clients" in snapshot
    assert "connectors" in snapshot


def test_base_workspace_marks_production_client_blocked(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(board_store, "WHITEBOARD_PATH", tmp_path / "whiteboard_state.json")
    snapshot = workspace.build_workspace_snapshot()

    clients = {row["client_id"]: row for row in snapshot["clients"]}
    assert clients["parada_atlantida"]["role"] == "protected_production"
    assert clients["parada_atlantida"]["real_publish_allowed_now"] is False
    assert clients["vikhing"]["publish_gate"] == "test_page_ready_meta_l4_preview"


def test_runtime_presence_redacts_values(tmp_path) -> None:
    runtime_path = tmp_path / "ig_runtime.env"
    runtime_path.write_text(
        "IG_BUSINESS_ACCOUNT_ID=123\nMETA_ACCESS_KEY=secret\nKOS_REAL_IG_PUBLISH_ENABLED=false\n",
        encoding="utf-8",
    )

    result = workspace.read_runtime_presence(runtime_path)

    assert result["exists"] is True
    assert result["secret_values_exposed"] is False
    assert result["keys"]["META_ACCESS_KEY"] == "present"
    assert "META_ACCESS_KEY=secret" not in str(result)


def test_base_workspace_board_card_flow(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(board_store, "WHITEBOARD_PATH", tmp_path / "whiteboard_state.json")
    board = workspace.ensure_base_board()
    assert "cards" in board

    card = workspace.add_board_card("Teste BASE", "plan", "Validar fluxo de lousa.", agent="pytest")
    assert card["lane"] == "plan"

    updated = workspace.move_card(card["id"], "review")
    moved = [item for item in updated["cards"] if item.get("id") == card["id"]][0]
    assert moved["lane"] == "review"
