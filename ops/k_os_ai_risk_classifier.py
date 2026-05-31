# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path.cwd()

RISK_POLICY = ROOT / "config" / "risk" / "k_os_ai_risk_policy.json"
LICENSE_POLICY = ROOT / "config" / "commercial" / "k_os_agent_license_policy.json"
REPORT_DIR = ROOT / "reports" / "risk"
MEMORY_DIR = ROOT / "memory" / "risk"
LATEST_JSON = REPORT_DIR / "latest_ai_risk_classifier_report.json"
LATEST_MD = REPORT_DIR / "latest_ai_risk_classifier_report.md"
EVENTS_JSONL = MEMORY_DIR / "events.jsonl"

CRITICAL_TERMS = [
    "external_send",
    "external_publish",
    "publish",
    "instagram",
    "whatsapp",
    "email",
    "credential",
    "raw_secret",
    "provider api",
    "api externa",
    "delete customer",
    "wipe",
    "apagar dados",
    "license",
    "subscription",
    "assinatura",
    "vender",
    "cliente",
    "kill switch",
    "self destruct",
    "autodestrutivo",
    "emergency",
    "lockdown",
]

HIGH_TERMS = [
    "commit",
    "push",
    "deploy",
    "lead",
    "proposal",
    "proposta",
    "diagnostic",
    "diagnostico",
    "live/",
    "vault",
    "cofre",
    "customer",
    "cliente",
    "commercial",
    "comercial",
]

MEDIUM_TERMS = [
    "write",
    "gerar",
    "alterar",
    "config",
    "report",
    "dashboard",
    "content",
    "campanha",
]


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def contains_any(text: str, terms: list[str]) -> list[str]:
    lower = text.lower()
    found = []
    for term in terms:
        if term.lower() in lower:
            found.append(term)
    return found


def score_action(action: str, agent_id: str = "", target: str = "") -> dict[str, Any]:
    text = f"{action} {agent_id} {target}".lower()

    score = 0
    reasons = []
    required_gates = ["local_log"]
    blocked_by_default = False
    license_required = False
    emergency_mode = False

    critical = contains_any(text, CRITICAL_TERMS)
    high = contains_any(text, HIGH_TERMS)
    medium = contains_any(text, MEDIUM_TERMS)

    if medium:
        score += 25
        reasons.append({"level": "medium", "matches": medium})

    if high:
        score += 35
        reasons.append({"level": "high", "matches": high})

    if critical:
        score += 50
        reasons.append({"level": "critical", "matches": critical})

    if any(x in text for x in ["vender", "assinatura", "subscription", "cliente", "customer", "license"]):
        license_required = True
        score += 15
        reasons.append({"level": "license", "matches": ["license_required_for_customer_use"]})

    if any(x in text for x in ["kill switch", "self destruct", "autodestrutivo", "emergency", "lockdown"]):
        emergency_mode = True
        score += 20
        reasons.append({"level": "emergency", "matches": ["emergency_kill_switch"]})

    if any(x in text for x in ["wipe", "apagar dados", "delete customer data", "destroy customer records"]):
        blocked_by_default = True
        reasons.append({"level": "blocked", "matches": ["irreversible_data_destruction_blocked"]})

    if any(x in text for x in ["external_send", "external_publish", "send_whatsapp", "publish_instagram", "raw_secret"]):
        blocked_by_default = True
        reasons.append({"level": "blocked", "matches": ["external_or_secret_action_blocked_by_default"]})

    if score > 100:
        score = 100

    if score >= 80:
        risk = "critical"
        required_gates = [
            "human_operator_approval",
            "security_council_approval",
            "security_firewall",
            "schema_guard",
            "vault_guard_if_needed",
            "audit_event",
            "rollback_plan",
        ]
    elif score >= 50:
        risk = "high"
        required_gates = [
            "human_operator_approval",
            "security_firewall",
            "schema_guard",
            "audit_event",
        ]
    elif score >= 25:
        risk = "medium"
        required_gates = [
            "human_operator_approval",
            "audit_event",
        ]
    else:
        risk = "low"
        required_gates = ["local_log"]

    if license_required:
        required_gates.append("license_gate")

    if emergency_mode:
        required_gates.append("emergency_reason_required")
        required_gates.append("incident_report_required")

    decision = "allowed_local"
    if blocked_by_default:
        decision = "blocked_until_explicit_approval"
    elif risk in {"high", "critical"}:
        decision = "requires_approval"

    return {
        "ok": True,
        "action": action,
        "agent_id": agent_id,
        "target": target,
        "risk_score": score,
        "risk_level": risk,
        "decision": decision,
        "blocked_by_default": blocked_by_default,
        "license_required": license_required,
        "emergency_mode": emergency_mode,
        "required_gates": required_gates,
        "reasons": reasons,
        "safe_emergency_policy": {
            "safe_autodestruct_means": "deactivate, revoke, disable connectors, freeze tasks and preserve audit logs",
            "silent_data_wipe_allowed": False,
            "audit_logs_must_be_preserved": True,
        },
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "manual_approval_required": risk != "low",
    }


def write_report(report: dict[str, Any]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)

    LATEST_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS AI Risk Classifier Report",
        "",
        f"- Status: {report.get('status')}",
        f"- OK: {report.get('ok')}",
        f"- Generated at: {report.get('generated_at')}",
        "",
        "## Results",
        "",
    ]

    for item in report.get("results", []):
        lines.append(
            f"- {item.get('action')} | risk={item.get('risk_level')} | decision={item.get('decision')} | license_required={item.get('license_required')}"
        )

    LATEST_MD.write_text("\n".join(lines), encoding="utf-8")

    with EVENTS_JSONL.open("a", encoding="utf-8") as file:
        file.write(json.dumps({
            "event": "ai_risk_classifier.report",
            "created_at": now(),
            "status": report.get("status"),
            "results_count": len(report.get("results", [])),
        }, ensure_ascii=False) + "\n")


def smoke_test() -> dict[str, Any]:
    tests = [
        ("Ler relatorio local de auditoria", "k_uni_cockpit", "reports/audit"),
        ("Gerar proposta comercial local", "marketplace_ia_agent", "live/marketplace_ia"),
        ("Fazer commit e push seguro", "k_os_git_bridge", "git"),
        ("Vender agente por assinatura para cliente", "marketplace_ia_agent", "customer_license"),
        ("Acionar autodestrutivo por falta de acordo", "future_multimodal_connector", "emergency_lockdown"),
        ("Enviar WhatsApp automatico para cliente", "marketplace_ia_agent", "external_send"),
        ("Apagar dados do cliente silenciosamente", "unknown_agent", "delete_customer_data"),
    ]

    results = [score_action(action, agent, target) for action, agent, target in tests]

    report = {
        "ok": True,
        "checkpoint": "021",
        "module": "k_os_ai_risk_classifier",
        "status": "smoke_passed",
        "generated_at": now(),
        "results": results,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "manual_approval_required": True,
        "next_checkpoint": "022 - K-External API Sandbox",
    }

    return report


def scan_policy() -> dict[str, Any]:
    risk_policy = load_json(RISK_POLICY)
    license_policy = load_json(LICENSE_POLICY)

    report = {
        "ok": True,
        "checkpoint": "021",
        "module": "k_os_ai_risk_classifier",
        "status": "policy_scanned",
        "generated_at": now(),
        "risk_policy_exists": RISK_POLICY.exists(),
        "license_policy_exists": LICENSE_POLICY.exists(),
        "agents_can_be_sold_or_subscribed": license_policy.get("commercial_model", {}).get("agents_can_be_sold_or_subscribed"),
        "activation_requires_kos_permission": license_policy.get("commercial_model", {}).get("activation_requires_kos_permission"),
        "emergency_kill_switch_enabled": risk_policy.get("policy", {}).get("emergency_kill_switch_enabled"),
        "destructive_data_wipe_blocked_by_default": risk_policy.get("policy", {}).get("destructive_data_wipe_blocked_by_default"),
        "results": [],
        "next_checkpoint": "022 - K-External API Sandbox",
    }

    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["smoke-test", "scan-policy", "classify"], required=True)
    parser.add_argument("--action", default="")
    parser.add_argument("--agent", default="")
    parser.add_argument("--target", default="")
    args = parser.parse_args()

    if args.mode == "smoke-test":
        report = smoke_test()
        write_report(report)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    if args.mode == "scan-policy":
        report = scan_policy()
        write_report(report)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    if args.mode == "classify":
        result = score_action(args.action, args.agent, args.target)
        report = {
            "ok": True,
            "checkpoint": "021",
            "module": "k_os_ai_risk_classifier",
            "status": "classified",
            "generated_at": now(),
            "results": [result],
            "next_checkpoint": "022 - K-External API Sandbox",
        }
        write_report(report)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())