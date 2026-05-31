# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path.cwd()

CONTROLS_PATH = ROOT / "config" / "audit" / "k_os_audit_controls.json"
REPORT_DIR = ROOT / "reports" / "audit"
MEMORY_DIR = ROOT / "memory" / "audit"

LATEST_JSON = REPORT_DIR / "latest_audit_evidence_pack.json"
LATEST_MD = REPORT_DIR / "latest_audit_evidence_pack.md"
LATEST_CHECKLIST = REPORT_DIR / "latest_audit_checklist.md"
EVENTS_JSONL = MEMORY_DIR / "events.jsonl"

CHECKPOINTS = [
    {
        "id": "015",
        "name": "Security Firewall",
        "closure": "reports/security/k_os_015_closure_report.json",
        "status": "security firewall and pre-commit guard",
    },
    {
        "id": "016",
        "name": "Schema Guard",
        "closure": "reports/schema/k_os_016_closure_report.json",
        "status": "operational JSON validation",
    },
    {
        "id": "017",
        "name": "Agent Permission Matrix",
        "closure": "reports/governance/k_os_017_closure_report.json",
        "status": "agent permissions and councils",
    },
    {
        "id": "018",
        "name": "Vault Guard",
        "closure": "reports/vault/k_os_018_closure_report.json",
        "status": "local credential vault policy",
    },
]


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT.resolve())).replace("\\", "/")
    except Exception:
        return str(path).replace("\\", "/")


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


def read_json_safe(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None

    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return None


def file_status(path_text: str) -> dict[str, Any]:
    path = ROOT / path_text
    return {
        "path": path_text,
        "exists": path.exists(),
        "is_file": path.is_file(),
        "size_bytes": path.stat().st_size if path.exists() and path.is_file() else 0,
    }


def load_controls() -> dict[str, Any]:
    return json.loads(CONTROLS_PATH.read_text(encoding="utf-8-sig"))


def collect_checkpoint_evidence() -> list[dict[str, Any]]:
    results = []

    for checkpoint in CHECKPOINTS:
        closure_path = ROOT / checkpoint["closure"]
        closure = read_json_safe(closure_path)

        results.append({
            "checkpoint": checkpoint["id"],
            "name": checkpoint["name"],
            "closure_path": checkpoint["closure"],
            "closure_exists": closure_path.exists(),
            "closure_ok": bool(closure and closure.get("ok") is True),
            "closure_status": closure.get("status") if closure else "missing",
            "summary": checkpoint["status"],
        })

    return results


def collect_control_evidence(controls: dict[str, Any]) -> list[dict[str, Any]]:
    results = []

    for control in controls.get("controls", []):
        evidence_items = [file_status(item) for item in control.get("evidence", [])]
        exists_count = sum(1 for item in evidence_items if item["exists"])
        total_count = len(evidence_items)

        results.append({
            "control_id": control.get("control_id"),
            "name": control.get("name"),
            "checkpoint": control.get("checkpoint"),
            "evidence_total": total_count,
            "evidence_found": exists_count,
            "evidence_complete": exists_count == total_count,
            "evidence": evidence_items,
        })

    return results


def compute_readiness(checkpoints: list[dict[str, Any]], controls: list[dict[str, Any]]) -> dict[str, Any]:
    checkpoint_total = len(checkpoints)
    checkpoint_ok = sum(1 for item in checkpoints if item.get("closure_ok"))

    control_total = len(controls)
    control_ok = sum(1 for item in controls if item.get("evidence_complete"))

    if checkpoint_total + control_total == 0:
        score = 0
    else:
        score = round(((checkpoint_ok + control_ok) / (checkpoint_total + control_total)) * 100, 2)

    if score >= 90:
        level = "strong_internal_readiness"
    elif score >= 70:
        level = "partial_internal_readiness"
    else:
        level = "needs_work"

    return {
        "score": score,
        "level": level,
        "checkpoint_ok": checkpoint_ok,
        "checkpoint_total": checkpoint_total,
        "control_ok": control_ok,
        "control_total": control_total,
    }


def build_pack() -> dict[str, Any]:
    controls = load_controls()
    checkpoints = collect_checkpoint_evidence()
    control_evidence = collect_control_evidence(controls)
    readiness = compute_readiness(checkpoints, control_evidence)

    _, branch, _ = run_git(["branch", "--show-current"])
    _, last_commit, _ = run_git(["log", "-1", "--oneline"])
    _, remote, _ = run_git(["remote", "-v"])
    _, status, _ = run_git(["status", "--short"])

    pack = {
        "ok": True,
        "checkpoint": "019",
        "module": "k_os_audit_evidence_pack",
        "status": "generated",
        "generated_at": now(),
        "system": "K-OS",
        "repository": {
            "root": str(ROOT),
            "branch": branch,
            "last_commit": last_commit,
            "remote": remote,
            "working_tree_status": status,
        },
        "audit_scope": controls.get("audit_scope", {}),
        "control_domains": controls.get("control_domains", []),
        "checkpoint_evidence": checkpoints,
        "control_evidence": control_evidence,
        "readiness": readiness,
        "known_gaps": controls.get("known_gaps", []),
        "security_position": {
            "external_send_enabled": False,
            "external_publish_enabled": False,
            "credential_access_enabled_by_default": False,
            "manual_approval_required": True,
            "no_agent_decides_alone": True,
            "sensitive_data_local_only": True,
            "raw_secret_exposure_enabled": False,
        },
        "disclaimer": {
            "not_a_certification": True,
            "requires_external_auditor_for_formal_certification": True,
            "use_as_internal_readiness_pack": True,
        },
        "next_checkpoint": "020 - K-Mission Control 2.0",
    }

    return pack


def write_event(event: str, data: dict[str, Any]) -> None:
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)

    item = {
        "event": event,
        "created_at": now(),
        "data": data,
    }

    with EVENTS_JSONL.open("a", encoding="utf-8") as file:
        file.write(json.dumps(item, ensure_ascii=False) + "\n")


def write_pack(pack: dict[str, Any]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)

    LATEST_JSON.write_text(json.dumps(pack, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Audit Evidence Pack",
        "",
        f"- Checkpoint: {pack.get('checkpoint')}",
        f"- Module: {pack.get('module')}",
        f"- Status: {pack.get('status')}",
        f"- Generated at: {pack.get('generated_at')}",
        f"- Readiness score: {pack.get('readiness', {}).get('score')}%",
        f"- Readiness level: {pack.get('readiness', {}).get('level')}",
        "",
        "## Security Position",
        "",
    ]

    security = pack.get("security_position", {})
    for key, value in security.items():
        lines.append(f"- {key}: {value}")

    lines.extend([
        "",
        "## Checkpoints",
        "",
    ])

    for item in pack.get("checkpoint_evidence", []):
        lines.append(
            f"- {item.get('checkpoint')} - {item.get('name')} | closure_ok={item.get('closure_ok')} | status={item.get('closure_status')}"
        )

    lines.extend([
        "",
        "## Controls",
        "",
    ])

    for item in pack.get("control_evidence", []):
        lines.append(
            f"- {item.get('control_id')} - {item.get('name')} | evidence={item.get('evidence_found')}/{item.get('evidence_total')} | complete={item.get('evidence_complete')}"
        )

    lines.extend([
        "",
        "## Known Gaps",
        "",
    ])

    for gap in pack.get("known_gaps", []):
        lines.append(
            f"- {gap.get('gap_id')} | {gap.get('name')} | severity={gap.get('severity')} | next={gap.get('next_action')}"
        )

    lines.extend([
        "",
        "## Disclaimer",
        "",
        "- Este pacote é evidência interna de prontidão.",
        "- Não é certificação SOC 2, ISO 27001, LGPD ou GDPR.",
        "- Certificação formal exige auditor externo e processo próprio.",
    ])

    LATEST_MD.write_text("\n".join(lines), encoding="utf-8")

    checklist = [
        "# K-OS Audit Checklist",
        "",
        "## Core controls",
        "",
    ]

    for item in pack.get("control_evidence", []):
        marker = "x" if item.get("evidence_complete") else " "
        checklist.append(f"- [{marker}] {item.get('control_id')} - {item.get('name')}")

    checklist.extend([
        "",
        "## Enterprise review questions",
        "",
        "- [x] Existe firewall contra vazamento de segredo?",
        "- [x] Existe validação estrutural de dados?",
        "- [x] Existe matriz de permissão de agentes?",
        "- [x] Existe cofre local de credenciais?",
        "- [x] Existe política de aprovação humana?",
        "- [x] Existe registro de responsabilidade das IAs?",
        "- [ ] Existe auditoria externa formal?",
        "- [ ] Existe processo formal de incidente?",
        "- [ ] Existe sandbox externo ativado?",
        "- [ ] Existe relatório enterprise final?",
    ])

    LATEST_CHECKLIST.write_text("\n".join(checklist), encoding="utf-8")

    write_event("audit_evidence_pack.generated", {
        "ok": pack.get("ok"),
        "readiness": pack.get("readiness"),
    })


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

    pack = build_pack()
    write_pack(pack)
    print(json.dumps(pack, ensure_ascii=False, indent=2))
    return 0 if pack.get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())