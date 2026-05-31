# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path.cwd()

POLICY_PATH = ROOT / "config" / "command_center" / "k_os_command_center_action_router_policy.json"
STATE_DIR = ROOT / "local_secrets" / "k_os_command_center"
STATE_PATH = STATE_DIR / "action_router_state.json"

REPORT_DIR = ROOT / "reports" / "command_center"
MEMORY_DIR = ROOT / "memory" / "command_center"

LATEST_JSON = REPORT_DIR / "latest_command_center_action_router_report.json"
LATEST_MD = REPORT_DIR / "latest_command_center_action_router_report.md"
EXECUTION_JSON = REPORT_DIR / "latest_action_execution_report.json"
EXECUTION_MD = REPORT_DIR / "latest_action_execution_report.md"
CATALOG_JSON = REPORT_DIR / "latest_action_catalog.json"
CATALOG_MD = REPORT_DIR / "latest_action_catalog.md"
EVENTS_JSONL = MEMORY_DIR / "events.jsonl"


ACTION_CATALOG: dict[str, dict[str, Any]] = {
    "analytics_audit": {
        "domain": "analytics",
        "label": "Atualizar Analytics Executive Metrics",
        "risk": "low",
        "requires_approval": False,
        "command": ["__python__", "ops/k_os_analytics_executive_metrics_core.py", "--mode", "audit"]
    },
    "analytics_dashboard": {
        "domain": "analytics",
        "label": "Atualizar Dashboard Executivo",
        "risk": "low",
        "requires_approval": False,
        "command": ["__python__", "ops/k_os_analytics_executive_metrics_core.py", "--mode", "dashboard"]
    },
    "cockpit_audit": {
        "domain": "cockpit",
        "label": "Atualizar Executive Cockpit",
        "risk": "low",
        "requires_approval": False,
        "command": ["__python__", "ops/k_os_executive_cockpit_consolidation_layer.py", "--mode", "audit"]
    },
    "cockpit_navigation": {
        "domain": "cockpit",
        "label": "Atualizar Mapa de Navegação",
        "risk": "low",
        "requires_approval": False,
        "command": ["__python__", "ops/k_os_executive_cockpit_consolidation_layer.py", "--mode", "navigation"]
    },
    "cockpit_health": {
        "domain": "cockpit",
        "label": "Atualizar Health do Cockpit",
        "risk": "low",
        "requires_approval": False,
        "command": ["__python__", "ops/k_os_executive_cockpit_consolidation_layer.py", "--mode", "health"]
    },
    "security_scan_staged": {
        "domain": "security",
        "label": "Rodar Security Firewall no staged",
        "risk": "medium",
        "requires_approval": True,
        "command": ["__python__", "ops/k_os_security_firewall.py", "--mode", "scan-staged"]
    },
    "schema_audit": {
        "domain": "security",
        "label": "Auditar Schema Guard",
        "risk": "low",
        "requires_approval": False,
        "command": ["__python__", "ops/k_os_schema_guard.py", "--mode", "audit"]
    },
    "support_audit": {
        "domain": "support",
        "label": "Auditar Support Desk",
        "risk": "low",
        "requires_approval": False,
        "command": ["__python__", "ops/k_os_support_desk_ticketing_core.py", "--mode", "audit"]
    },
    "customer_success_audit": {
        "domain": "customer_ops",
        "label": "Auditar Customer Success",
        "risk": "low",
        "requires_approval": False,
        "command": ["__python__", "ops/k_os_customer_success_delivery_tracker.py", "--mode", "audit"]
    },
    "product_feedback_audit": {
        "domain": "product",
        "label": "Auditar Product Feedback",
        "risk": "low",
        "requires_approval": False,
        "command": ["__python__", "ops/k_os_product_feedback_feature_request_core.py", "--mode", "audit"]
    },
    "roadmap_audit": {
        "domain": "roadmap",
        "label": "Auditar Roadmap Planner",
        "risk": "low",
        "requires_approval": False,
        "command": ["__python__", "ops/k_os_roadmap_planner_release_notes_core.py", "--mode", "audit"]
    },
    "git_status": {
        "domain": "git_local",
        "label": "Ver Git Status local",
        "risk": "low",
        "requires_approval": False,
        "command": ["git", "status", "--short"]
    },
    "git_diff_cached_stat": {
        "domain": "git_local",
        "label": "Ver diff staged resumido",
        "risk": "low",
        "requires_approval": False,
        "command": ["git", "diff", "--cached", "--stat"]
    }
}


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        return {"_read_error": str(exc), "_path": str(path)}


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def event(name: str, data: dict[str, Any]) -> None:
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    with EVENTS_JSONL.open("a", encoding="utf-8") as file:
        file.write(json.dumps({
            "event": name,
            "created_at": now(),
            "data": data
        }, ensure_ascii=False) + "\n")


def load_policy() -> dict[str, Any]:
    data = read_json(POLICY_PATH)
    if not data:
        raise RuntimeError("Command Center policy not found.")
    return data


def ensure_state() -> dict[str, Any]:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)

    if not STATE_PATH.exists():
        data = {
            "version": "1.0.0",
            "created_at": now(),
            "updated_at": now(),
            "local_only": True,
            "external_publish_enabled": False,
            "arbitrary_shell_command_allowed": False,
            "executions": []
        }
        write_json(STATE_PATH, data)

    state = read_json(STATE_PATH)
    if not state:
        raise RuntimeError("Could not load Command Center state.")
    return state


def save_state(data: dict[str, Any]) -> None:
    data["updated_at"] = now()
    write_json(STATE_PATH, data)


def resolve_command(command: list[str]) -> list[str]:
    if not command:
        return command

    if command[0] == "__python__":
        return [sys.executable, *command[1:]]

    return command


def safe_catalog() -> list[dict[str, Any]]:
    items = []

    for action_id, item in ACTION_CATALOG.items():
        command = resolve_command(item.get("command", []))
        script_path = ""
        exists = True

        if len(command) >= 2 and command[0] == sys.executable:
            script_path = command[1]
            exists = (ROOT / script_path).exists()

        items.append({
            "action_id": action_id,
            "domain": item.get("domain"),
            "label": item.get("label"),
            "risk": item.get("risk"),
            "requires_approval": item.get("requires_approval", False),
            "command_preview": " ".join(command),
            "script_path": script_path,
            "script_exists": exists
        })

    return sorted(items, key=lambda x: (x["domain"], x["action_id"]))


def write_catalog() -> dict[str, Any]:
    catalog = {
        "ok": True,
        "checkpoint": "038",
        "module": "k_os_command_center_action_router",
        "status": "action_catalog_generated",
        "generated_at": now(),
        "allowlist_only_execution": True,
        "arbitrary_shell_command_allowed": False,
        "actions": safe_catalog()
    }

    CATALOG_JSON.write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Command Center Action Catalog",
        "",
        f"- Generated at: {catalog.get('generated_at')}",
        f"- Allowlist only: {catalog.get('allowlist_only_execution')}",
        f"- Arbitrary shell allowed: {catalog.get('arbitrary_shell_command_allowed')}",
        "",
        "## Actions",
        ""
    ]

    for item in catalog["actions"]:
        lines.append(
            f"- {item.get('action_id')} | {item.get('domain')} | risk={item.get('risk')} | "
            f"approval={item.get('requires_approval')} | script_exists={item.get('script_exists')}"
        )

    CATALOG_MD.write_text("\n".join(lines), encoding="utf-8")
    return catalog


def action_requires_approval(action: dict[str, Any]) -> bool:
    risk = action.get("risk", "low")
    return bool(action.get("requires_approval")) or risk in {"medium", "high", "critical"}


def route_action(action_id: str, approved: bool, reason: str, dry_run: bool) -> dict[str, Any]:
    ensure_state()
    policy = load_policy()

    execution_id = "exec_" + uuid.uuid4().hex[:12]
    action = ACTION_CATALOG.get(action_id)

    blockers = []
    warnings = []

    if not action:
        blockers.append("action_not_in_allowlist")
        result = {
            "ok": False,
            "checkpoint": "038",
            "module": "k_os_command_center_action_router",
            "status": "blocked",
            "execution_id": execution_id,
            "generated_at": now(),
            "action_id": action_id,
            "decision": "blocked",
            "blockers": blockers,
            "warnings": warnings,
            "external_send_performed": False,
            "external_publish_performed": False,
            "command_executed": False
        }
        write_execution(result)
        record_execution(result)
        return result

    command = resolve_command(action.get("command", []))
    command_preview = " ".join(command)
    requires_approval = action_requires_approval(action)

    if requires_approval and not approved:
        blockers.append("approval_required")

    if requires_approval and not reason:
        blockers.append("operator_reason_required")

    if action.get("risk") == "critical":
        blockers.append("critical_actions_not_enabled")

    if blockers:
        result = {
            "ok": False,
            "checkpoint": "038",
            "module": "k_os_command_center_action_router",
            "status": "blocked",
            "execution_id": execution_id,
            "generated_at": now(),
            "action_id": action_id,
            "action_label": action.get("label"),
            "domain": action.get("domain"),
            "risk": action.get("risk"),
            "requires_approval": requires_approval,
            "approved": approved,
            "reason": reason,
            "dry_run": dry_run,
            "decision": "blocked_until_requirements_met",
            "blockers": blockers,
            "warnings": warnings,
            "command_preview": command_preview,
            "external_send_performed": False,
            "external_publish_performed": False,
            "command_executed": False,
            "required_gates_before_action_execution": policy.get("required_gates_before_action_execution", [])
        }
        write_execution(result)
        record_execution(result)
        event("command_center.action_blocked", {"action_id": action_id, "blockers": blockers})
        return result

    if dry_run:
        result = {
            "ok": True,
            "checkpoint": "038",
            "module": "k_os_command_center_action_router",
            "status": "dry_run_completed",
            "execution_id": execution_id,
            "generated_at": now(),
            "action_id": action_id,
            "action_label": action.get("label"),
            "domain": action.get("domain"),
            "risk": action.get("risk"),
            "requires_approval": requires_approval,
            "approved": approved,
            "reason": reason,
            "dry_run": True,
            "decision": "ready_for_execution",
            "blockers": [],
            "warnings": warnings,
            "command_preview": command_preview,
            "external_send_performed": False,
            "external_publish_performed": False,
            "command_executed": False
        }
        write_execution(result)
        record_execution(result)
        event("command_center.action_dry_run", {"action_id": action_id})
        return result

    completed = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    result = {
        "ok": completed.returncode == 0,
        "checkpoint": "038",
        "module": "k_os_command_center_action_router",
        "status": "executed" if completed.returncode == 0 else "execution_failed",
        "execution_id": execution_id,
        "generated_at": now(),
        "action_id": action_id,
        "action_label": action.get("label"),
        "domain": action.get("domain"),
        "risk": action.get("risk"),
        "requires_approval": requires_approval,
        "approved": approved,
        "reason": reason,
        "dry_run": False,
        "decision": "executed" if completed.returncode == 0 else "failed",
        "returncode": completed.returncode,
        "stdout_tail": completed.stdout[-4000:],
        "stderr_tail": completed.stderr[-4000:],
        "blockers": [],
        "warnings": warnings,
        "command_preview": command_preview,
        "external_send_performed": False,
        "external_publish_performed": False,
        "command_executed": True
    }

    write_execution(result)
    record_execution(result)
    event("command_center.action_executed", {"action_id": action_id, "returncode": completed.returncode})
    return result


def record_execution(result: dict[str, Any]) -> None:
    state = ensure_state()
    state.setdefault("executions", []).append({
        "execution_id": result.get("execution_id"),
        "created_at": result.get("generated_at"),
        "action_id": result.get("action_id"),
        "status": result.get("status"),
        "decision": result.get("decision"),
        "risk": result.get("risk"),
        "dry_run": result.get("dry_run"),
        "command_executed": result.get("command_executed"),
        "ok": result.get("ok")
    })
    state["executions"] = state["executions"][-200:]
    save_state(state)


def write_execution(result: dict[str, Any]) -> None:
    EXECUTION_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Command Center Action Execution",
        "",
        f"- Execution ID: {result.get('execution_id')}",
        f"- Action: {result.get('action_id')}",
        f"- Status: {result.get('status')}",
        f"- Decision: {result.get('decision')}",
        f"- Risk: {result.get('risk')}",
        f"- Dry run: {result.get('dry_run')}",
        f"- Command executed: {result.get('command_executed')}",
        f"- External send performed: {result.get('external_send_performed')}",
        f"- External publish performed: {result.get('external_publish_performed')}",
        "",
        "## Command preview",
        "",
        f"`{result.get('command_preview', '')}`",
        "",
        "## Blockers",
        ""
    ]

    if result.get("blockers"):
        for item in result.get("blockers", []):
            lines.append(f"- {item}")
    else:
        lines.append("- Nenhum blocker.")

    if result.get("stdout_tail"):
        lines.extend(["", "## stdout tail", "", "```text", str(result.get("stdout_tail")), "```"])

    if result.get("stderr_tail"):
        lines.extend(["", "## stderr tail", "", "```text", str(result.get("stderr_tail")), "```"])

    EXECUTION_MD.write_text("\n".join(lines), encoding="utf-8")


def audit_report() -> dict[str, Any]:
    state = ensure_state()
    policy = load_policy()
    catalog = safe_catalog()

    risk_counts: dict[str, int] = {}
    domain_counts: dict[str, int] = {}

    for item in catalog:
        risk = item.get("risk", "unknown")
        domain = item.get("domain", "unknown")
        risk_counts[risk] = risk_counts.get(risk, 0) + 1
        domain_counts[domain] = domain_counts.get(domain, 0) + 1

    script_missing = [item for item in catalog if not item.get("script_exists")]

    report = {
        "ok": True,
        "checkpoint": "038",
        "module": "k_os_command_center_action_router",
        "status": "audit_generated",
        "generated_at": now(),
        "command_center_state_path": "local_secrets/k_os_command_center/action_router_state.json",
        "command_center_state_committed": False,
        "sanitized_reports_only": True,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "automatic_message_enabled": False,
        "arbitrary_shell_command_allowed": False,
        "allowlist_only_execution": True,
        "dry_run_default": True,
        "action_count": len(catalog),
        "script_missing_count": len(script_missing),
        "risk_counts": risk_counts,
        "domain_counts": domain_counts,
        "actions": catalog,
        "recent_executions": state.get("executions", [])[-30:],
        "required_gates_before_action_execution": policy.get("required_gates_before_action_execution", []),
        "blocked_actions": policy.get("blocked_actions", []),
        "next_checkpoint": policy.get("next_checkpoint", "039 - K-Agent Orchestration Queue Core")
    }

    write_report(report)
    write_catalog()
    event("command_center.audit_generated", {"action_count": len(catalog)})
    return report


def write_report(report: dict[str, Any]) -> None:
    LATEST_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Command Center Action Router",
        "",
        f"- Status: {report.get('status')}",
        f"- OK: {report.get('ok')}",
        f"- Generated at: {report.get('generated_at')}",
        f"- Action count: {report.get('action_count')}",
        f"- Script missing count: {report.get('script_missing_count')}",
        f"- Allowlist only: {report.get('allowlist_only_execution')}",
        f"- Dry-run default: {report.get('dry_run_default')}",
        f"- Arbitrary shell allowed: {report.get('arbitrary_shell_command_allowed')}",
        f"- External publish enabled: {report.get('external_publish_enabled')}",
        "",
        "## Actions",
        ""
    ]

    for item in report.get("actions", []):
        lines.append(
            f"- {item.get('action_id')} | {item.get('domain')} | {item.get('label')} | "
            f"risk={item.get('risk')} | approval={item.get('requires_approval')}"
        )

    lines.extend(["", "## Recent executions", ""])

    if report.get("recent_executions"):
        for item in report.get("recent_executions", []):
            lines.append(
                f"- {item.get('execution_id')} | {item.get('action_id')} | {item.get('status')} | "
                f"dry_run={item.get('dry_run')} | executed={item.get('command_executed')}"
            )
    else:
        lines.append("- Nenhuma execução registrada.")

    lines.extend(["", "## Required gates before action execution", ""])

    for gate in report.get("required_gates_before_action_execution", []):
        lines.append(f"- {gate}")

    lines.extend(["", "## Blocked actions", ""])

    for item in report.get("blocked_actions", []):
        lines.append(f"- {item}")

    lines.extend(["", "## Next checkpoint", "", f"- {report.get('next_checkpoint')}"])

    LATEST_MD.write_text("\n".join(lines), encoding="utf-8")


def show_latest() -> int:
    if LATEST_JSON.exists():
        print(LATEST_JSON.read_text(encoding="utf-8-sig"))
    else:
        print("{}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["init", "audit", "catalog", "route", "show"], required=True)
    parser.add_argument("--action-id", default="")
    parser.add_argument("--approved", action="store_true")
    parser.add_argument("--reason", default="")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()

    if args.mode == "init":
        ensure_state()
        result = audit_report()

    elif args.mode == "audit":
        result = audit_report()

    elif args.mode == "catalog":
        result = write_catalog()

    elif args.mode == "route":
        if not args.action_id:
            raise SystemExit("Informe --action-id")
        dry_run = not args.execute
        result = route_action(args.action_id, args.approved, args.reason, dry_run)

    elif args.mode == "show":
        return show_latest()

    else:
        raise SystemExit(1)

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())