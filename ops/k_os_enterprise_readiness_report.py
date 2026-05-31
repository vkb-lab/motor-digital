# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path.cwd()

POLICY_PATH = ROOT / "config" / "enterprise" / "k_os_enterprise_readiness_policy.json"
REPORT_DIR = ROOT / "reports" / "enterprise"
MEMORY_DIR = ROOT / "memory" / "enterprise"
LATEST_JSON = REPORT_DIR / "latest_enterprise_readiness_report.json"
LATEST_MD = REPORT_DIR / "latest_enterprise_readiness_report.md"
DUE_DILIGENCE_MD = REPORT_DIR / "latest_enterprise_due_diligence_pack.md"
EVENTS_JSONL = MEMORY_DIR / "events.jsonl"


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        return {"_read_error": str(exc), "_path": str(path)}


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


def load_policy() -> dict[str, Any]:
    data = read_json(POLICY_PATH)
    if not data:
        raise RuntimeError("Enterprise readiness policy not found.")
    return data


def evidence_status(control: dict[str, Any]) -> dict[str, Any]:
    evidence_path = ROOT / control["evidence"]
    evidence = read_json(evidence_path)

    exists = evidence_path.exists()
    read_error = bool(evidence and evidence.get("_read_error"))

    ok = False
    status = "missing"

    if exists and not read_error:
        if evidence.get("ok") is True:
            ok = True
            status = evidence.get("status", "ok")
        elif control["id"] == "COM-001" and evidence.get("ok") is True:
            ok = True
            status = evidence.get("status", "ok")
        else:
            ok = False
            status = evidence.get("status", "present_but_not_ok") if isinstance(evidence, dict) else "present"

    if read_error:
        status = "read_error"

    return {
        "id": control["id"],
        "name": control["name"],
        "checkpoint": control["checkpoint"],
        "domain": control["domain"],
        "evidence": control["evidence"],
        "exists": exists,
        "ok": ok,
        "status": status,
        "read_error": read_error,
    }


def maturity_level(score: float) -> str:
    if score >= 90:
        return "enterprise_internal_ready"
    if score >= 75:
        return "advanced_internal_governance"
    if score >= 60:
        return "controlled_foundation"
    if score >= 40:
        return "partial_foundation"
    return "early_stage"


def build_report() -> dict[str, Any]:
    policy = load_policy()
    controls = [evidence_status(item) for item in policy.get("enterprise_controls", [])]

    total = len(controls)
    passed = sum(1 for item in controls if item.get("ok") is True)
    missing = [item for item in controls if not item.get("exists")]
    failed = [item for item in controls if item.get("exists") and not item.get("ok")]

    score = round((passed / total) * 100, 2) if total else 0.0

    code_branch, branch, _ = run_git(["branch", "--show-current"])
    code_status, git_status, _ = run_git(["status", "--short"])
    code_commit, last_commit, _ = run_git(["log", "-1", "--oneline"])

    git_clean = git_status.strip() == ""

    operational_blockers = []

    if not git_clean:
        operational_blockers.append({
            "type": "git_dirty",
            "message": "Working tree possui alteracoes pendentes.",
            "details": git_status,
        })

    for item in missing:
        operational_blockers.append({
            "type": "missing_evidence",
            "message": "Evidencia enterprise ausente.",
            "control": item.get("id"),
            "evidence": item.get("evidence"),
        })

    for item in failed:
        operational_blockers.append({
            "type": "failed_evidence",
            "message": "Evidencia existe, mas nao esta marcada como ok.",
            "control": item.get("id"),
            "status": item.get("status"),
        })

    recommended_actions = []

    if missing:
        recommended_actions.append("Completar evidencias ausentes antes de due diligence externa.")

    if failed:
        recommended_actions.append("Revalidar evidencias presentes que nao estao marcadas como ok.")

    recommended_actions.extend([
        "Criar runbook formal de incidente, rollback e continuidade.",
        "Preparar pacote juridico comercial para assinatura/licenciamento de agentes.",
        "Manter conectores externos reais bloqueados ate aprovacao formal.",
        "Contratar auditor externo se o objetivo for certificacao formal.",
    ])

    report = {
        "ok": len(operational_blockers) == 0,
        "checkpoint": "023",
        "module": "k_os_enterprise_readiness_report",
        "status": "generated",
        "generated_at": now(),
        "enterprise_readiness_score": score,
        "maturity_level": maturity_level(score),
        "controls_total": total,
        "controls_passed": passed,
        "controls_missing": len(missing),
        "controls_failed": len(failed),
        "controls": controls,
        "known_gaps": policy.get("known_gaps", []),
        "certification_policy": policy.get("certification_policy", {}),
        "enterprise_positioning": policy.get("enterprise_positioning", {}),
        "operational_blockers": operational_blockers,
        "recommended_actions": recommended_actions,
        "git": {
            "branch": branch if code_branch == 0 else "",
            "last_commit": last_commit if code_commit == 0 else "",
            "clean": git_clean,
            "status_short": git_status if code_status == 0 else "",
        },
        "statement": {
            "safe_claim": "K-OS possui base interna de governanca, seguranca, validacao, auditoria, risco, licenciamento e sandbox para operacao IA human-in-the-loop.",
            "restricted_claim": "Nao alegar certificacao formal SOC 2, ISO 27001, LGPD ou GDPR sem auditoria externa e emissao por terceiro competente.",
        },
        "next_checkpoint": "024 - K-Incident Response and Rollback Runbook",
    }

    return report


def write_reports(report: dict[str, Any]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)

    LATEST_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Enterprise Readiness Report",
        "",
        f"- Status: {report.get('status')}",
        f"- OK: {report.get('ok')}",
        f"- Enterprise readiness score: {report.get('enterprise_readiness_score')}%",
        f"- Maturity level: {report.get('maturity_level')}",
        f"- Controls passed: {report.get('controls_passed')}/{report.get('controls_total')}",
        f"- Generated at: {report.get('generated_at')}",
        "",
        "## Executive Summary",
        "",
        report.get("statement", {}).get("safe_claim", ""),
        "",
        "**Important limitation:** " + report.get("statement", {}).get("restricted_claim", ""),
        "",
        "## Control Matrix",
        "",
        "| Control | Domain | Checkpoint | OK | Evidence |",
        "|---|---|---:|---:|---|",
    ]

    for item in report.get("controls", []):
        lines.append(
            f"| {item.get('id')} - {item.get('name')} | {item.get('domain')} | {item.get('checkpoint')} | {item.get('ok')} | {item.get('evidence')} |"
        )

    lines.extend([
        "",
        "## Known Gaps",
        "",
    ])

    for gap in report.get("known_gaps", []):
        lines.append(f"- {gap}")

    lines.extend([
        "",
        "## Operational Blockers",
        "",
    ])

    if report.get("operational_blockers"):
        for blocker in report.get("operational_blockers", []):
            lines.append(f"- {blocker.get('type')}: {blocker.get('message')}")
    else:
        lines.append("- Nenhum blocker operacional encontrado no pacote enterprise.")

    lines.extend([
        "",
        "## Recommended Actions",
        "",
    ])

    for action in report.get("recommended_actions", []):
        lines.append(f"- {action}")

    lines.extend([
        "",
        "## Next Checkpoint",
        "",
        f"- {report.get('next_checkpoint')}",
    ])

    LATEST_MD.write_text("\n".join(lines), encoding="utf-8")

    dd = [
        "# K-OS Enterprise Due Diligence Pack",
        "",
        "## What K-OS is",
        "",
        "K-OS is an AI Business Operating System foundation with local execution, human approval gates, security controls, schema validation, agent permissions, vault guard, audit evidence, mission control, risk classification, commercial license gate and external API sandbox.",
        "",
        "## What can be shown",
        "",
        "- Internal governance foundation",
        "- Human-in-the-loop operating model",
        "- Evidence-based checkpoints",
        "- Local-first execution",
        "- Commercial license gate for agents",
        "- Emergency kill switch implemented as safe deactivation/revocation",
        "- External API dry-run sandbox",
        "",
        "## What must not be claimed yet",
        "",
        "- Formal SOC 2 certification",
        "- Formal ISO 27001 certification",
        "- Formal LGPD certification",
        "- Formal GDPR certification",
        "- External audit completion",
        "",
        "## Readiness",
        "",
        f"- Score: {report.get('enterprise_readiness_score')}%",
        f"- Maturity: {report.get('maturity_level')}",
        f"- Controls passed: {report.get('controls_passed')}/{report.get('controls_total')}",
        "",
        "## Required next layer",
        "",
        "- Incident response runbook",
        "- Rollback procedure",
        "- Legal/commercial templates",
        "- Vendor risk assessment",
        "- External auditor review when certification is required",
    ]

    DUE_DILIGENCE_MD.write_text("\n".join(dd), encoding="utf-8")

    with EVENTS_JSONL.open("a", encoding="utf-8") as file:
        file.write(json.dumps({
            "event": "enterprise_readiness.report_generated",
            "created_at": now(),
            "ok": report.get("ok"),
            "score": report.get("enterprise_readiness_score"),
            "maturity_level": report.get("maturity_level"),
        }, ensure_ascii=False) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["generate", "show"], default="generate")
    args = parser.parse_args()

    if args.mode == "show":
        if LATEST_JSON.exists():
            print(LATEST_JSON.read_text(encoding="utf-8-sig"))
        else:
            print("{}")
        return 0

    report = build_report()
    write_reports(report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())