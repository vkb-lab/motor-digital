from __future__ import annotations

import argparse
import importlib.util
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
AUDIT_SCRIPT = ROOT / "scripts" / "run_phase69e_publish_audit_gate.py"

CONFIRMATION_PHRASE = "YES_DRY_RUN_HUPMIX_PUBLISH_AUDIT_ONLY"
HUPMIX_USERNAME = "hupmix"
HUPMIX_IG_ID = "17841471706662294"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def slug(value: str) -> str:
    value = value.strip() or "publish-dry-run"
    value = re.sub(r"[^A-Za-z0-9_\-]+", "-", value)
    return value[:100]


def load_audit_module():
    spec = importlib.util.spec_from_file_location("phase69e_publish_audit", AUDIT_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("Nao foi possivel carregar o Publish Audit Gate.")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def build_dry_run(
    campaign_id: str,
    target: str,
    channel: str,
    caption: str,
    asset_ref: str,
    operator_note: str,
    confirmation: str,
) -> dict[str, Any]:
    human_confirmed = confirmation.strip() == CONFIRMATION_PHRASE

    audit_mod = load_audit_module()
    audit = audit_mod.build_publish_audit(
        campaign_id=campaign_id,
        target=target,
        channel=channel,
        caption=caption,
        asset_ref=asset_ref,
        operator_note=operator_note,
        human_confirmed=human_confirmed,
    )

    base = {
        "phase": "69F",
        "campaign_id": slug(campaign_id),
        "target": target,
        "channel": channel,
        "confirmation_phrase_required": CONFIRMATION_PHRASE,
        "confirmation_valid": human_confirmed,
        "publish_audit_status": audit.get("status"),
        "publish_audit": audit,
        "created_at": now_iso(),
    }

    if not human_confirmed:
        return {
            **base,
            "status": "KOS_HUMAN_CONFIRMED_PUBLISH_DRY_RUN_BLOCKED",
            "reason": "missing_or_invalid_dry_run_confirmation",
            "dry_run_package_ready": False,
            "eligible_for_real_publish_future_gate": False,
            "publish_endpoint_called": False,
            "http_post_used": False,
            "publish_execution_command_generated": False,
            "real_action_executed": False,
            "instagram_publish_executed": False,
            "browser_logged_account_automation_used": False,
            "paid_ai_call_executed": False,
        }

    if audit.get("status") != "KOS_PUBLISH_AUDIT_PACKAGE_READY":
        return {
            **base,
            "status": "KOS_HUMAN_CONFIRMED_PUBLISH_DRY_RUN_BLOCKED",
            "reason": "publish_audit_not_ready",
            "dry_run_package_ready": False,
            "eligible_for_real_publish_future_gate": False,
            "publish_endpoint_called": False,
            "http_post_used": False,
            "publish_execution_command_generated": False,
            "real_action_executed": False,
            "instagram_publish_executed": False,
            "browser_logged_account_automation_used": False,
            "paid_ai_call_executed": False,
        }

    if audit.get("target") != HUPMIX_USERNAME:
        return {
            **base,
            "status": "KOS_HUMAN_CONFIRMED_PUBLISH_DRY_RUN_BLOCKED",
            "reason": "target_not_hupmix",
            "dry_run_package_ready": False,
            "eligible_for_real_publish_future_gate": False,
            "publish_endpoint_called": False,
            "http_post_used": False,
            "publish_execution_command_generated": False,
            "real_action_executed": False,
            "instagram_publish_executed": False,
            "browser_logged_account_automation_used": False,
            "paid_ai_call_executed": False,
        }

    return {
        **base,
        "status": "KOS_HUMAN_CONFIRMED_PUBLISH_DRY_RUN_READY",
        "reason": "human_confirmation_valid_for_dry_run_only",
        "dry_run_package_ready": True,
        "dry_run_package": {
            "target": HUPMIX_USERNAME,
            "ig_id": HUPMIX_IG_ID,
            "channel": channel,
            "caption_draft": caption,
            "asset_ref": asset_ref,
            "operator_note": operator_note,
            "review_required_before_any_real_publish": True,
        },
        "future_real_publish_gate_required": True,
        "eligible_for_real_publish_future_gate": True,
        "publish_endpoint_called": False,
        "http_post_used": False,
        "publish_execution_command_generated": False,
        "real_action_executed": False,
        "instagram_publish_executed": False,
        "browser_logged_account_automation_used": False,
        "paid_ai_call_executed": False,
        "production_publish_locked": True,
        "paid_ai_locked": True,
        "token_logged": False,
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--campaign-id", default="KOS-PUBLISH-DRY-RUN")
    parser.add_argument("--target", default="hupmix")
    parser.add_argument("--channel", default="instagram")
    parser.add_argument("--caption", default="Rascunho seguro para dry-run auditado.")
    parser.add_argument("--asset-ref", default="KOS_LOCAL_TEST_ASSET")
    parser.add_argument("--operator-note", default="dry-run only")
    parser.add_argument("--confirmation", default="")
    args = parser.parse_args()

    result = build_dry_run(
        campaign_id=args.campaign_id,
        target=args.target,
        channel=args.channel,
        caption=args.caption,
        asset_ref=args.asset_ref,
        operator_note=args.operator_note,
        confirmation=args.confirmation,
    )

    out = ROOT / "local_runtime" / "kos_publish_dry_run" / "hupmix" / (slug(args.campaign_id) + ".json")
    latest = ROOT / "local_runtime" / "kos_publish_dry_run" / "hupmix" / "latest_publish_dry_run.json"

    write_json(out, result)
    write_json(latest, result)

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
