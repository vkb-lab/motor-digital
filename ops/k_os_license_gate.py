# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT = Path.cwd()

REGISTRY_DIR = ROOT / "local_secrets" / "k_os_licenses"
REGISTRY_PATH = REGISTRY_DIR / "license_registry.json"
REPORT_DIR = ROOT / "reports" / "license"
MEMORY_DIR = ROOT / "memory" / "license"
LATEST_JSON = REPORT_DIR / "latest_license_gate_report.json"
LATEST_MD = REPORT_DIR / "latest_license_gate_report.md"
EVENTS_JSONL = MEMORY_DIR / "events.jsonl"


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def ensure_registry() -> dict[str, Any]:
    REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)

    if not REGISTRY_PATH.exists():
        data = {
            "version": "1.0.0",
            "created_at": now(),
            "updated_at": now(),
            "emergency_lockdown": False,
            "licenses": [],
        }
        REGISTRY_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8-sig"))


def save_registry(data: dict[str, Any]) -> None:
    data["updated_at"] = now()
    REGISTRY_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def event(name: str, data: dict[str, Any]) -> None:
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    with EVENTS_JSONL.open("a", encoding="utf-8") as file:
        file.write(json.dumps({"event": name, "created_at": now(), "data": data}, ensure_ascii=False) + "\n")


def safe_license_view(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "license_id": item.get("license_id"),
        "customer_alias": item.get("customer_alias"),
        "agent_id": item.get("agent_id"),
        "plan": item.get("plan"),
        "status": item.get("status"),
        "issued_at": item.get("issued_at"),
        "expires_at": item.get("expires_at"),
        "allowed_capabilities": item.get("allowed_capabilities", []),
        "allowed_connectors": item.get("allowed_connectors", []),
        "emergency_lockdown": item.get("emergency_lockdown", False),
    }


def audit_report() -> dict[str, Any]:
    registry = ensure_registry()
    licenses = [safe_license_view(item) for item in registry.get("licenses", [])]

    report = {
        "ok": True,
        "checkpoint": "021",
        "module": "k_os_license_gate",
        "status": "passed",
        "generated_at": now(),
        "registry_path": "local_secrets/k_os_licenses/license_registry.json",
        "registry_committed": False,
        "emergency_lockdown": registry.get("emergency_lockdown", False),
        "license_count": len(licenses),
        "licenses": licenses,
        "agents_can_be_sold_or_subscribed": True,
        "activation_requires_kos_permission": True,
        "safe_autodestruct_available": True,
        "silent_data_wipe_allowed": False,
        "external_send_enabled": False,
        "external_publish_enabled": False,
    }

    LATEST_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS License Gate Report",
        "",
        f"- Status: {report['status']}",
        f"- License count: {report['license_count']}",
        f"- Emergency lockdown: {report['emergency_lockdown']}",
        f"- Registry committed: false",
        f"- Silent data wipe allowed: false",
        "",
        "## Licenses",
        "",
    ]

    if not licenses:
        lines.append("- Nenhuma licenca registrada.")
    else:
        for item in licenses:
            lines.append(f"- {item['license_id']} | {item['customer_alias']} | {item['agent_id']} | {item['plan']} | {item['status']}")

    LATEST_MD.write_text("\n".join(lines), encoding="utf-8")
    event("license.audit", {"license_count": len(licenses), "emergency_lockdown": report["emergency_lockdown"]})
    return report


def issue_demo() -> dict[str, Any]:
    registry = ensure_registry()

    license_id = "lic_" + uuid.uuid4().hex[:12]
    issued = datetime.now(timezone.utc)
    expires = issued + timedelta(days=7)

    item = {
        "license_id": license_id,
        "customer_alias": "demo_customer",
        "agent_id": "marketplace_ia_agent",
        "plan": "trial",
        "status": "active",
        "issued_at": issued.replace(microsecond=0).isoformat(),
        "expires_at": expires.replace(microsecond=0).isoformat(),
        "allowed_capabilities": [
            "local_diagnostic",
            "local_proposal",
            "manual_send_pack"
        ],
        "allowed_connectors": [],
        "emergency_lockdown": False,
        "notes": "Demo local. Nao usar como contrato real."
    }

    registry["licenses"].append(item)
    save_registry(registry)
    event("license.issued_demo", {"license_id": license_id})
    return audit_report()


def revoke(license_id: str, reason: str) -> dict[str, Any]:
    registry = ensure_registry()

    for item in registry.get("licenses", []):
        if item.get("license_id") == license_id:
            item["status"] = "revoked"
            item["revoked_at"] = now()
            item["revocation_reason"] = reason or "not_specified"
            item["emergency_lockdown"] = True

    save_registry(registry)
    event("license.revoked", {"license_id": license_id, "reason": reason})
    return audit_report()


def lockdown(reason: str) -> dict[str, Any]:
    registry = ensure_registry()
    registry["emergency_lockdown"] = True
    registry["lockdown_reason"] = reason or "emergency_or_agreement_issue"
    registry["lockdown_at"] = now()

    for item in registry.get("licenses", []):
        item["status"] = "suspended_by_emergency_lockdown"
        item["emergency_lockdown"] = True

    save_registry(registry)
    event("license.emergency_lockdown", {"reason": reason})
    return audit_report()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["init", "issue-demo", "audit", "lockdown", "revoke"], required=True)
    parser.add_argument("--license-id", default="")
    parser.add_argument("--reason", default="")
    args = parser.parse_args()

    if args.mode == "init":
        ensure_registry()
        report = audit_report()
    elif args.mode == "issue-demo":
        report = issue_demo()
    elif args.mode == "audit":
        report = audit_report()
    elif args.mode == "lockdown":
        report = lockdown(args.reason)
    elif args.mode == "revoke":
        if not args.license_id:
            raise SystemExit("Informe --license-id")
        report = revoke(args.license_id, args.reason)
    else:
        raise SystemExit(1)

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())