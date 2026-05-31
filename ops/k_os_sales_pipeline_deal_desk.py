# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path.cwd()

POLICY_PATH = ROOT / "config" / "sales" / "k_os_sales_pipeline_deal_desk_policy.json"
SALES_DIR = ROOT / "local_secrets" / "k_os_sales"
SALES_PATH = SALES_DIR / "sales_pipeline.json"
REPORT_DIR = ROOT / "reports" / "sales"
MEMORY_DIR = ROOT / "memory" / "sales"
LATEST_JSON = REPORT_DIR / "latest_sales_pipeline_report.json"
LATEST_MD = REPORT_DIR / "latest_sales_pipeline_report.md"
APPROVAL_JSON = REPORT_DIR / "latest_deal_approval_dry_run.json"
APPROVAL_MD = REPORT_DIR / "latest_deal_approval_dry_run.md"
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
        raise RuntimeError("Sales pipeline policy not found.")
    return data


def ensure_pipeline() -> dict[str, Any]:
    SALES_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)

    if not SALES_PATH.exists():
        data = {
            "version": "1.0.0",
            "created_at": now(),
            "updated_at": now(),
            "local_only": True,
            "external_send_enabled": False,
            "automatic_close_enabled": False,
            "deals": [],
            "activities": [],
            "approvals": []
        }
        write_json(SALES_PATH, data)

    registry = read_json(SALES_PATH)
    if not registry:
        raise RuntimeError("Could not load sales pipeline.")
    return registry


def save_pipeline(data: dict[str, Any]) -> None:
    data["updated_at"] = now()
    write_json(SALES_PATH, data)


def safe_deal(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "deal_id": item.get("deal_id"),
        "customer_alias": item.get("customer_alias"),
        "customer_id": item.get("customer_id", ""),
        "agent_id": item.get("agent_id", ""),
        "stage": item.get("stage"),
        "priority": item.get("priority"),
        "estimated_mrr_brl": item.get("estimated_mrr_brl", 0.0),
        "estimated_setup_brl": item.get("estimated_setup_brl", 0.0),
        "probability": item.get("probability", 0),
        "weighted_mrr_brl": round(float(item.get("estimated_mrr_brl", 0.0)) * float(item.get("probability", 0)) / 100, 2),
        "next_action": item.get("next_action"),
        "commercial_owner": item.get("commercial_owner"),
        "proposal_id": item.get("proposal_id", ""),
        "subscription_id": item.get("subscription_id", ""),
        "license_id": item.get("license_id", ""),
        "approval_status": item.get("approval_status", "pending"),
        "created_at": item.get("created_at"),
        "last_stage_reason": item.get("last_stage_reason", "")
    }


def safe_activity(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "activity_id": item.get("activity_id"),
        "deal_id": item.get("deal_id"),
        "activity_type": item.get("activity_type"),
        "summary": item.get("summary"),
        "created_at": item.get("created_at"),
        "created_by": item.get("created_by"),
        "requires_follow_up": item.get("requires_follow_up", False)
    }


def compute_pipeline(deals: list[dict[str, Any]]) -> dict[str, Any]:
    stage_counts: dict[str, int] = {}
    priority_counts: dict[str, int] = {}

    total_mrr = 0.0
    weighted_mrr = 0.0
    total_setup = 0.0

    open_stages = {
        "lead",
        "qualified",
        "discovery",
        "proposal_draft",
        "proposal_sent",
        "negotiation",
        "legal_review",
        "commercial_approval",
        "won_pending_activation"
    }

    won_stages = {"won_pending_activation", "active"}
    lost_stages = {"lost"}

    for deal in deals:
        stage = deal.get("stage", "unknown")
        priority = deal.get("priority", "medium")
        stage_counts[stage] = stage_counts.get(stage, 0) + 1
        priority_counts[priority] = priority_counts.get(priority, 0) + 1

        mrr = float(deal.get("estimated_mrr_brl", 0.0) or 0.0)
        setup = float(deal.get("estimated_setup_brl", 0.0) or 0.0)
        prob = float(deal.get("probability", 0) or 0)

        if stage in open_stages:
            total_mrr += mrr
            weighted_mrr += mrr * prob / 100
            total_setup += setup

    return {
        "deal_count": len(deals),
        "open_deal_count": sum(1 for deal in deals if deal.get("stage") in open_stages),
        "won_count": sum(1 for deal in deals if deal.get("stage") in won_stages),
        "lost_count": sum(1 for deal in deals if deal.get("stage") in lost_stages),
        "stage_counts": stage_counts,
        "priority_counts": priority_counts,
        "open_mrr_estimate_brl": round(total_mrr, 2),
        "weighted_mrr_estimate_brl": round(weighted_mrr, 2),
        "open_setup_estimate_brl": round(total_setup, 2),
        "weighted_arr_estimate_brl": round(weighted_mrr * 12, 2)
    }


def create_demo() -> dict[str, Any]:
    pipeline = ensure_pipeline()

    existing = next((d for d in pipeline.get("deals", []) if d.get("customer_alias") == "demo_customer"), None)

    if not existing:
        deal_id = "deal_" + uuid.uuid4().hex[:12]
        deal = {
            "deal_id": deal_id,
            "customer_alias": "demo_customer",
            "customer_id": "linked_by_crm_demo",
            "agent_id": "marketplace_ia_agent",
            "stage": "proposal_draft",
            "priority": "medium",
            "estimated_mrr_brl": 997.0,
            "estimated_setup_brl": 1500.0,
            "probability": 35,
            "next_action": "revisar proposta demo e validar ordem comercial",
            "commercial_owner": "k_os_operator",
            "proposal_id": "demo_marketplace_ia",
            "subscription_id": "linked_by_billing_demo",
            "license_id": "pending_license_gate",
            "approval_status": "pending_operator_review",
            "created_at": now(),
            "last_stage_reason": "demo_created"
        }

        pipeline["deals"].append(deal)
        pipeline["activities"].append({
            "activity_id": "act_" + uuid.uuid4().hex[:12],
            "deal_id": deal_id,
            "activity_type": "deal_created",
            "summary": "Deal demo criado para validar Sales Pipeline and Deal Desk.",
            "created_at": now(),
            "created_by": "k_os_sales_pipeline",
            "requires_follow_up": True
        })

    save_pipeline(pipeline)
    event("sales.demo_created", {"customer_alias": "demo_customer"})
    return audit_report()


def add_deal(alias: str, agent_id: str, mrr: float, setup: float, priority: str, owner: str, next_action: str) -> dict[str, Any]:
    policy = load_policy()

    if priority not in set(policy.get("deal_priorities", [])):
        raise RuntimeError(f"Invalid priority: {priority}")

    pipeline = ensure_pipeline()

    deal_id = "deal_" + uuid.uuid4().hex[:12]
    deal = {
        "deal_id": deal_id,
        "customer_alias": alias,
        "customer_id": "",
        "agent_id": agent_id,
        "stage": "lead",
        "priority": priority,
        "estimated_mrr_brl": float(mrr),
        "estimated_setup_brl": float(setup),
        "probability": 10,
        "next_action": next_action or "qualificar oportunidade",
        "commercial_owner": owner or "k_os_operator",
        "proposal_id": "",
        "subscription_id": "",
        "license_id": "",
        "approval_status": "pending_operator_review",
        "created_at": now(),
        "last_stage_reason": "manual_create"
    }

    pipeline["deals"].append(deal)
    pipeline["activities"].append({
        "activity_id": "act_" + uuid.uuid4().hex[:12],
        "deal_id": deal_id,
        "activity_type": "deal_created",
        "summary": "Oportunidade registrada no Deal Desk.",
        "created_at": now(),
        "created_by": "operator",
        "requires_follow_up": True
    })

    save_pipeline(pipeline)
    event("sales.deal_created", {"deal_id": deal_id, "customer_alias": alias})
    return audit_report()


def update_stage(deal_id: str, stage: str, reason: str, probability: int | None) -> dict[str, Any]:
    policy = load_policy()

    if stage not in set(policy.get("deal_stages", [])):
        raise RuntimeError(f"Invalid stage: {stage}")

    pipeline = ensure_pipeline()
    found = False

    for deal in pipeline.get("deals", []):
        if deal.get("deal_id") == deal_id:
            if stage in {"won_pending_activation", "active"} and deal.get("approval_status") not in {"commercial_approved", "final_approved"}:
                raise RuntimeError("Deal cannot move to won/active without commercial approval.")

            if stage == "active":
                if not deal.get("subscription_id") or not deal.get("license_id"):
                    raise RuntimeError("Deal cannot become active without subscription_id and license_id.")

            deal["stage"] = stage
            deal["last_stage_reason"] = reason or "manual_stage_update"
            deal["stage_updated_at"] = now()

            if probability is not None:
                if probability < 0 or probability > 100:
                    raise RuntimeError("Probability must be between 0 and 100.")
                deal["probability"] = probability

            pipeline["activities"].append({
                "activity_id": "act_" + uuid.uuid4().hex[:12],
                "deal_id": deal_id,
                "activity_type": "stage_changed",
                "summary": f"Stage alterado para {stage}. Motivo: {reason or 'manual_stage_update'}",
                "created_at": now(),
                "created_by": "operator",
                "requires_follow_up": stage not in {"active", "lost", "cancelled"}
            })

            found = True

    if not found:
        raise RuntimeError(f"Deal not found: {deal_id}")

    save_pipeline(pipeline)
    event("sales.stage_changed", {"deal_id": deal_id, "stage": stage})
    return audit_report()


def approval_dry_run(deal_id: str) -> dict[str, Any]:
    pipeline = ensure_pipeline()
    policy = load_policy()

    deal = next((d for d in pipeline.get("deals", []) if d.get("deal_id") == deal_id), None)
    if not deal:
        raise RuntimeError(f"Deal not found: {deal_id}")

    blockers = []

    if not deal.get("customer_alias"):
        blockers.append("customer_alias_missing")

    if not deal.get("agent_id"):
        blockers.append("agent_id_missing")

    if float(deal.get("estimated_mrr_brl", 0.0) or 0.0) > 0 and not deal.get("proposal_id"):
        blockers.append("proposal_required_for_paid_deal")

    if deal.get("stage") in {"won_pending_activation", "active"} and not deal.get("subscription_id"):
        blockers.append("subscription_required_before_activation")

    if deal.get("stage") in {"won_pending_activation", "active"} and not deal.get("license_id"):
        blockers.append("license_gate_required_before_activation")

    if deal.get("approval_status") not in {"commercial_approved", "final_approved"}:
        blockers.append("commercial_approval_required")

    result = {
        "ok": True,
        "checkpoint": "028",
        "module": "k_os_sales_pipeline_deal_desk",
        "status": "approval_dry_run",
        "generated_at": now(),
        "deal": safe_deal(deal),
        "approval_decision": "blocked_until_requirements_met" if blockers else "ready_for_final_human_approval",
        "blockers": blockers,
        "required_gates_before_marking_active": policy.get("required_gates_before_marking_active", []),
        "real_customer_activation_performed": False,
        "external_send_performed": False,
        "commercial_close_performed": False,
        "manual_approval_required": True,
        "next_checkpoint": policy.get("next_checkpoint", "029 - K-Proposal Factory and Quote Builder")
    }

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    APPROVAL_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Deal Approval Dry Run",
        "",
        f"- Status: {result.get('status')}",
        f"- Decision: {result.get('approval_decision')}",
        f"- Deal: {deal_id}",
        f"- Customer: {deal.get('customer_alias')}",
        f"- External send performed: {result.get('external_send_performed')}",
        f"- Customer activation performed: {result.get('real_customer_activation_performed')}",
        "",
        "## Blockers",
        ""
    ]

    if blockers:
        for item in blockers:
            lines.append(f"- {item}")
    else:
        lines.append("- Nenhum blocker encontrado. Ainda exige aprovação humana final.")

    APPROVAL_MD.write_text("\n".join(lines), encoding="utf-8")
    event("sales.approval_dry_run", {"deal_id": deal_id, "blockers": blockers})
    return result


def audit_report() -> dict[str, Any]:
    pipeline = ensure_pipeline()
    policy = load_policy()

    deals = [safe_deal(item) for item in pipeline.get("deals", [])]
    activities = [safe_activity(item) for item in pipeline.get("activities", [])[-30:]]
    metrics = compute_pipeline(pipeline.get("deals", []))

    report = {
        "ok": True,
        "checkpoint": "028",
        "module": "k_os_sales_pipeline_deal_desk",
        "status": "audit_generated",
        "generated_at": now(),
        "sales_pipeline_path": "local_secrets/k_os_sales/sales_pipeline.json",
        "sales_pipeline_committed": False,
        "sanitized_reports_only": True,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "automatic_close_enabled": False,
        "automatic_customer_activation_enabled": False,
        "deals": deals,
        "recent_activities": activities,
        "pipeline": metrics,
        "required_gates_before_marking_active": policy.get("required_gates_before_marking_active", []),
        "blocked_actions": policy.get("blocked_actions", []),
        "next_checkpoint": policy.get("next_checkpoint", "029 - K-Proposal Factory and Quote Builder")
    }

    write_report(report)
    event("sales.audit_generated", {"deal_count": metrics["deal_count"]})
    return report


def write_report(report: dict[str, Any]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    LATEST_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Sales Pipeline and Deal Desk",
        "",
        f"- Status: {report.get('status')}",
        f"- OK: {report.get('ok')}",
        f"- Generated at: {report.get('generated_at')}",
        f"- Pipeline committed: {report.get('sales_pipeline_committed')}",
        f"- External send enabled: {report.get('external_send_enabled')}",
        f"- Automatic close enabled: {report.get('automatic_close_enabled')}",
        "",
        "## Pipeline",
        ""
    ]

    for key, value in report.get("pipeline", {}).items():
        lines.append(f"- {key}: {value}")

    lines.extend([
        "",
        "## Deals",
        ""
    ])

    if report.get("deals"):
        for item in report.get("deals", []):
            lines.append(
                f"- {item.get('deal_id')} | {item.get('customer_alias')} | {item.get('stage')} | "
                f"MRR={item.get('estimated_mrr_brl')} | prob={item.get('probability')}% | next={item.get('next_action')}"
            )
    else:
        lines.append("- Nenhum deal registrado.")

    lines.extend([
        "",
        "## Required gates before marking active",
        ""
    ])

    for gate in report.get("required_gates_before_marking_active", []):
        lines.append(f"- {gate}")

    lines.extend([
        "",
        "## Blocked actions",
        ""
    ])

    for action in report.get("blocked_actions", []):
        lines.append(f"- {action}")

    lines.extend([
        "",
        "## Next checkpoint",
        "",
        f"- {report.get('next_checkpoint')}"
    ])

    LATEST_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["init", "create-demo", "audit", "add-deal", "update-stage", "approval-dry-run", "show"], required=True)
    parser.add_argument("--customer-alias", default="")
    parser.add_argument("--agent-id", default="marketplace_ia_agent")
    parser.add_argument("--mrr", type=float, default=0.0)
    parser.add_argument("--setup", type=float, default=0.0)
    parser.add_argument("--priority", default="medium")
    parser.add_argument("--owner", default="k_os_operator")
    parser.add_argument("--next-action", default="qualificar oportunidade")
    parser.add_argument("--deal-id", default="")
    parser.add_argument("--stage", default="")
    parser.add_argument("--reason", default="")
    parser.add_argument("--probability", type=int, default=-1)
    args = parser.parse_args()

    if args.mode == "init":
        ensure_pipeline()
        result = audit_report()

    elif args.mode == "create-demo":
        result = create_demo()

    elif args.mode == "audit":
        result = audit_report()

    elif args.mode == "add-deal":
        if not args.customer_alias:
            raise SystemExit("Informe --customer-alias")
        result = add_deal(args.customer_alias, args.agent_id, args.mrr, args.setup, args.priority, args.owner, args.next_action)

    elif args.mode == "update-stage":
        if not args.deal_id:
            raise SystemExit("Informe --deal-id")
        if not args.stage:
            raise SystemExit("Informe --stage")
        probability = args.probability if args.probability >= 0 else None
        result = update_stage(args.deal_id, args.stage, args.reason, probability)

    elif args.mode == "approval-dry-run":
        if not args.deal_id:
            raise SystemExit("Informe --deal-id")
        result = approval_dry_run(args.deal_id)

    elif args.mode == "show":
        if LATEST_JSON.exists():
            print(LATEST_JSON.read_text(encoding="utf-8-sig"))
            return 0
        print("{}")
        return 0

    else:
        raise SystemExit(1)

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())