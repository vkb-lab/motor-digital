from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MARKET_REFERENCES = [
    {"name": "OpenAI ChatGPT Agent", "patterns": ["tool_use", "connectors", "files", "human_control", "multi_step_tasks"]},
    {"name": "OpenAI Agents SDK / Codex", "patterns": ["agents", "tools", "handoffs", "guardrails", "software_engineering"]},
    {"name": "Anthropic Claude Code", "patterns": ["read_codebase", "edit_files", "run_commands", "terminal_ide_workflow"]},
    {"name": "Cursor Agents / CLI", "patterns": ["ide_agent", "cli_agent", "automation", "mcp", "cloud_agents"]},
    {"name": "Replit Agent", "patterns": ["natural_language_to_apps", "build_apps", "websites", "publish_flow"]},
]

DIMENSIONS = [
    {"dimension": "intent_to_action", "score": 0.82, "kos_status": "implemented", "next": "launcher_with_buttons"},
    {"dimension": "multi_step_missions", "score": 0.78, "kos_status": "implemented", "next": "automatic_goal_decomposition"},
    {"dimension": "safety_governance", "score": 0.92, "kos_status": "strong", "next": "per_agent_permission_registry"},
    {"dimension": "observability_dashboard", "score": 0.74, "kos_status": "implemented", "next": "operator_dashboard_polish"},
    {"dimension": "codebase_editing_agent", "score": 0.32, "kos_status": "planned", "next": "safe_patch_proposer"},
    {"dimension": "idea_to_app_factory", "score": 0.42, "kos_status": "foundation", "next": "guided_app_builder"},
    {"dimension": "skills_registry", "score": 0.38, "kos_status": "foundation", "next": "kos_skills_registry"},
    {"dimension": "cloud_team_agents", "score": 0.24, "kos_status": "planned", "next": "cloud_worker_team_mode"},
]

NEXT_MOVES = [
    {"phase": "69B", "name": "User-Friendly Local Launcher", "why": "usar K-OS em 5 minutos sem PowerShell"},
    {"phase": "70A", "name": "Safe Patch Proposer", "why": "aproximar K-OS de Claude Code, Codex e Cursor sem editar sem aprovação"},
    {"phase": "71A", "name": "Idea-to-App Builder", "why": "aproximar K-OS do fluxo Replit Agent"},
    {"phase": "72A", "name": "K-OS Skills Registry", "why": "criar playbooks reutilizáveis por agentes"},
]

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def main() -> int:
    overall = round(sum(x["score"] for x in DIMENSIONS) / len(DIMENSIONS), 3)
    snapshot = {
        "status": "KOS_AGENT_OS_MARKET_RADAR_READY",
        "phase": "69A",
        "purpose": "Comparar K-OS com padroes atuais de Agent Operating Systems.",
        "market_references": MARKET_REFERENCES,
        "dimensions": DIMENSIONS,
        "overall_score": overall,
        "strong_dimensions": [x["dimension"] for x in DIMENSIONS if x["score"] >= 0.70],
        "gap_dimensions": [x["dimension"] for x in DIMENSIONS if x["score"] < 0.50],
        "priority_next_moves": NEXT_MOVES,
        "market_position": "K-OS esta forte em autonomia local governada, missoes, fila, loop, auditoria e kill switch. O proximo salto e UX simples, safe patch proposer e app builder.",
        "production_publish_locked": True,
        "paid_ai_locked": True,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "browser_logged_account_automation_used": False,
        "created_at": now_iso(),
    }
    out = ROOT / "local_runtime" / "kos_agent_os_market" / "latest_market_radar_snapshot.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(snapshot, indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
