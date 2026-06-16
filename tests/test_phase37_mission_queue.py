from pathlib import Path
import json

from k_atlas.kaizen.mission_queue import create_mission, plan_mission, approve_mission, summarize_queue

def test_create_mission_safe():
    mission = create_mission(
        title="Teste seguro",
        description="Planejar sem executar.",
        priority="high"
    )
    assert mission["execution_allowed"] is False
    assert mission["approval_status"] == "not_requested"

def test_plan_mission_does_not_execute():
    mission = create_mission(
        title="Teste plano",
        description="Gerar plano dry-run.",
        priority="medium"
    )
    result = plan_mission(mission["id"])
    assert result["ok"] is True
    assert result["execution_allowed"] is False
    assert result["mission"]["status"] == "planned"

def test_approval_is_dry_run_only():
    mission = create_mission(
        title="Teste aprovacao",
        description="Aprovar apenas dry-run.",
        priority="medium"
    )
    result = approve_mission(mission["id"], "YES_APPROVE_DRY_RUN_ONLY")
    assert result["ok"] is True
    assert result["status"] == "MISSION_APPROVED_DRY_RUN_ONLY"
    assert result["execution_allowed"] is False
