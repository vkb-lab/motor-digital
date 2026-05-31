# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path.cwd()

CONFIG_PATH = ROOT / "config" / "mission_control" / "k_os_mission_control_2.json"
REPORT_DIR = ROOT / "reports" / "mission_control"
MEMORY_DIR = ROOT / "memory" / "mission_control"
LATEST_JSON = REPORT_DIR / "latest_mission_control_status.json"
LATEST_MD = REPORT_DIR / "latest_mission_control_status.md"
EVENTS_JSONL = MEMORY_DIR / "events.jsonl"


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def run_git(args: list[str]) -> tuple[int, str, str]:
    completed = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return completed.returncode, completed.stdout.strip(), completed.stderr.strip()


def read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None

    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return None


def file_info(path_text: str) -> dict[str, Any]:
    path = ROOT / path_text
    return {
        "path": path_text,
        "exists": path.exists(),
        "size_bytes": path.stat().st_size if path.exists() and path.is_file() else 0,
    }


def checkpoint_status(item: dict[str, Any]) -> dict[str, Any]:
    closure_path = ROOT / item["closure_report"]
    page_path = ROOT / item["page"]
    closure = read_json(closure_path)

    return {
        "id": item["id"],
        "name": item["name"],
        "closure_report": item["closure_report"],
        "closure_exists": closure_path.exists(),
        "closure_ok": bool(closure and closure.get("ok") is True),
        "closure_status": closure.get("status") if closure else "missing",
        "page": item["page"],
        "page_exists": page_path.exists(),
    }


def build_status() -> dict[str, Any]:
    config = read_json(CONFIG_PATH) or {}

    tracked = config.get("tracked_checkpoints", [])
    checkpoints = [checkpoint_status(item) for item in tracked]

    code_branch, branch, _ = run_git(["branch", "--show-current"])
    code_status, git_status, _ = run_git(["status", "--short"])
    code_commit, last_commit, _ = run_git(["log", "-1", "--oneline"])
    code_remote, remote, _ = run_git(["remote", "-v"])

    security_report = read_json(ROOT / "reports" / "security" / "latest_security_firewall_report.json")
    schema_report = read_json(ROOT / "reports" / "schema" / "latest_schema_guard_report.json")
    governance_report = read_json(ROOT / "reports" / "governance" / "latest_agent_permission_matrix_report.json")
    vault_report = read_json(ROOT / "reports" / "vault" / "latest_vault_guard_report.json")
    audit_pack = read_json(ROOT / "reports" / "audit" / "latest_audit_evidence_pack.json")

    checkpoint_total = len(checkpoints)
    checkpoint_ok = sum(1 for item in checkpoints if item["closure_ok"])

    blocker_count = 0
    blockers = []

    if git_status.strip():
        blockers.append({
            "type": "git_dirty",
            "message": "Working tree possui alteracoes pendentes.",
            "details": git_status,
        })
        blocker_count += 1

    if security_report and security_report.get("blocking_findings_count", 0):
        blockers.append({
            "type": "security_blocker",
            "message": "Security Firewall encontrou achados bloqueantes.",
            "details": security_report.get("blocking_findings_count"),
        })
        blocker_count += 1

    if schema_report and schema_report.get("blocking_errors_count", 0):
        blockers.append({
            "type": "schema_blocker",
            "message": "Schema Guard encontrou erros bloqueantes.",
            "details": schema_report.get("blocking_errors_count"),
        })
        blocker_count += 1

    readiness_score = 0
    if checkpoint_total:
        readiness_score = round((checkpoint_ok / checkpoint_total) * 100, 2)

    operational_state = "ready_for_next_checkpoint"
    if blocker_count > 0:
        operational_state = "needs_attention"
    elif checkpoint_ok < checkpoint_total - 1:
        operational_state = "incomplete_foundation"

    status = {
        "ok": blocker_count == 0,
        "checkpoint": "020",
        "module": "k_os_mission_control_2",
        "status": operational_state,
        "generated_at": now(),
        "readiness_score": readiness_score,
        "checkpoint_ok": checkpoint_ok,
        "checkpoint_total": checkpoint_total,
        "checkpoints": checkpoints,
        "git": {
            "branch": branch if code_branch == 0 else "",
            "last_commit": last_commit if code_commit == 0 else "",
            "remote": remote if code_remote == 0 else "",
            "status_short": git_status if code_status == 0 else "",
            "clean": git_status.strip() == "",
        },
        "security": {
            "firewall_report_exists": bool(security_report),
            "firewall_status": security_report.get("status") if security_report else "missing",
            "firewall_blocking": security_report.get("blocking_findings_count", 0) if security_report else "unknown",
        },
        "schema": {
            "schema_report_exists": bool(schema_report),
            "schema_status": schema_report.get("status") if schema_report else "missing",
            "schema_blocking": schema_report.get("blocking_errors_count", 0) if schema_report else "unknown",
        },
        "governance": {
            "matrix_report_exists": bool(governance_report),
            "matrix_status": governance_report.get("status") if governance_report else "missing",
            "agent_count": governance_report.get("agent_count") if governance_report else "unknown",
            "council_count": governance_report.get("council_count") if governance_report else "unknown",
        },
        "vault": {
            "vault_report_exists": bool(vault_report),
            "vault_status": vault_report.get("status") if vault_report else "missing",
            "raw_values_exposed": vault_report.get("raw_values_exposed") if vault_report else "unknown",
            "external_api_enabled": vault_report.get("external_api_enabled") if vault_report else "unknown",
        },
        "audit": {
            "audit_pack_exists": bool(audit_pack),
            "audit_status": audit_pack.get("status") if audit_pack else "missing",
            "audit_score": audit_pack.get("readiness", {}).get("score") if audit_pack else "unknown",
        },
        "blockers": blockers,
        "policy": config.get("policy", {}),
        "next_program": config.get("next_program", []),
        "recommended_next_step": "021 - K-AI Risk Classifier" if blocker_count == 0 else "Resolver blockers antes de continuar.",
    }

    return status


def write_status(status: dict[str, Any]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)

    LATEST_JSON.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Mission Control 2.0 Status",
        "",
        f"- Status: {status.get('status')}",
        f"- OK: {status.get('ok')}",
        f"- Readiness score: {status.get('readiness_score')}%",
        f"- Checkpoints OK: {status.get('checkpoint_ok')}/{status.get('checkpoint_total')}",
        f"- Generated at: {status.get('generated_at')}",
        "",
        "## Checkpoints",
        "",
    ]

    for item in status.get("checkpoints", []):
        lines.append(
            f"- {item.get('id')} - {item.get('name')} | closure_ok={item.get('closure_ok')} | page_exists={item.get('page_exists')}"
        )

    lines.extend([
        "",
        "## Blockers",
        "",
    ])

    if status.get("blockers"):
        for blocker in status.get("blockers", []):
            lines.append(f"- {blocker.get('type')}: {blocker.get('message')}")
    else:
        lines.append("- Nenhum blocker operacional encontrado.")

    lines.extend([
        "",
        "## Next Step",
        "",
        f"- {status.get('recommended_next_step')}",
    ])

    LATEST_MD.write_text("\n".join(lines), encoding="utf-8")

    with EVENTS_JSONL.open("a", encoding="utf-8") as file:
        file.write(json.dumps({
            "event": "mission_control.status_generated",
            "created_at": now(),
            "ok": status.get("ok"),
            "status": status.get("status"),
            "readiness_score": status.get("readiness_score"),
        }, ensure_ascii=False) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["generate", "show"], default="generate")
    args = parser.parse_args()

    if args.mode == "show":
        if LATEST_JSON.exists():
            print(LATEST_JSON.read_text(encoding="utf-8-sig"))
            return 0
        print("{}")
        return 0

    status = build_status()
    write_status(status)
    print(json.dumps(status, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())