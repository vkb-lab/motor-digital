from __future__ import annotations

import argparse
import importlib.util
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
GATE_SCRIPT = ROOT / "scripts" / "run_phase69c_requested_autonomy_action_gate.py"

HUPMIX_IG_ID = "17841471706662294"
HUPMIX_USERNAME = "hupmix"
PARADA_IG_ID = "17841480166187766"
PARADA_USERNAME = "paradaatlantida"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def slug(value: str) -> str:
    value = value.strip() or "publish-audit"
    value = re.sub(r"[^A-Za-z0-9_\-]+", "-", value)
    return value[:100]


def load_gate_module():
    spec = importlib.util.spec_from_file_location("phase69c_gate", GATE_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("Nao foi possivel carregar o Requested Autonomy Action Gate.")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def normalize_target(target: str) -> str:
    return target.strip().lower().replace("@", "")


def is_hupmix(target: str) -> bool:
    value = normalize_target(target)
    return value in {HUPMIX_USERNAME, HUPMIX_IG_ID.lower(), "hupmix_test", "test_hupmix"}


def is_parada(target: str) -> bool:
    value = normalize_target(target)
    return value in {PARADA_USERNAME, PARADA_IG_ID.lower(), "parada", "parada-atlantida", "parada_atlantida"}


def build_publish_audit(
    campaign_id: str,
    target: str,
    channel: str,
    caption: str,
    asset_ref: str,
    operator_note: str,
    human_confirmed: bool = False,
) -> dict[str, Any]:
    safe_campaign_id = slug(campaign_id)

    if is_parada(target):
        return {
            "status": "KOS_PUBLISH_AUDIT_BLOCKED",
            "phase": "69E",
            "reason": "blocked_target_parada_atlantida",
            "campaign_id": safe_campaign_id,
            "target": target,
            "publish_executed": False,
            "instagram_publish_executed": False,
            "browser_logged_account_automation_used": False,
            "created_at": now_iso(),
        }

    if not is_hupmix(target):
        return {
            "status": "KOS_PUBLISH_AUDIT_BLOCKED",
            "phase": "69E",
            "reason": "only_hupmix_test_account_allowed_in_this_phase",
            "campaign_id": safe_campaign_id,
            "target": target,
            "expected_target": HUPMIX_USERNAME,
            "publish_executed": False,
            "instagram_publish_executed": False,
            "browser_logged_account_automation_used": False,
            "created_at": now_iso(),
        }

    gate = load_gate_module()

    prepare_gate = gate.validate_request("campaign_publish_prepare", "prepare_only", False)
    publish_without_human = gate.validate_request("instagram_publish", "human_confirmed_only", False)
    publish_with_current_flag = gate.validate_request("instagram_publish", "human_confirmed_only", human_confirmed)

    risk_flags: list[str] = []
    if len(caption.strip()) < 8:
        risk_flags.append("caption_too_short")
    if len(caption) > 2200:
        risk_flags.append("caption_too_long_for_instagram")
    if not asset_ref.strip():
        risk_flags.append("missing_asset_ref")

    status = "KOS_PUBLISH_AUDIT_PACKAGE_READY"
    if risk_flags:
        status = "KOS_PUBLISH_AUDIT_ATTENTION_REQUIRED"

    if not prepare_gate.get("allowed"):
        status = "KOS_PUBLISH_AUDIT_BLOCKED"

    audit = {
        "status": status,
        "phase": "69E",
        "campaign_id": safe_campaign_id,
        "target": HUPMIX_USERNAME,
        "ig_id": HUPMIX_IG_ID,
        "channel": channel,
        "caption_draft": caption,
        "asset_ref": asset_ref,
        "operator_note": operator_note,
        "human_confirmed": human_confirmed,
        "gates": {
            "campaign_publish_prepare": prepare_gate,
            "instagram_publish_without_human_confirmation": publish_without_human,
            "instagram_publish_with_current_human_confirmation_flag": publish_with_current_flag,
        },
        "audit_checklist": [
            {"item": "target_is_hupmix_test_account", "passed": True},
            {"item": "parada_atlantida_locked", "passed": True},
            {"item": "caption_present", "passed": bool(caption.strip())},
            {"item": "asset_reference_present", "passed": bool(asset_ref.strip())},
            {"item": "human_confirmation_required_for_real_publish", "passed": True},
            {"item": "publish_endpoint_not_called", "passed": True},
            {"item": "browser_logged_account_not_used", "passed": True},
        ],
        "risk_flags": risk_flags,
        "ready_for_human_review": True,
        "eligible_for_human_confirmed_publish": bool(human_confirmed and publish_with_current_flag.get("allowed") and not risk_flags),
        "publish_execution_command_generated": False,
        "publish_endpoint_called": False,
        "http_post_used": False,
        "token_logged": False,
        "production_publish_locked": True,
        "paid_ai_locked": True,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "publish_executed": False,
        "instagram_publish_executed": False,
        "browser_logged_account_automation_used": False,
        "created_at": now_iso(),
    }

    return audit


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--campaign-id", default="KOS-PUBLISH-AUDIT")
    parser.add_argument("--target", default="hupmix")
    parser.add_argument("--channel", default="instagram")
    parser.add_argument("--caption", default="Rascunho seguro para revisao humana antes de publicar.")
    parser.add_argument("--asset-ref", default="KOS_LOCAL_TEST_ASSET")
    parser.add_argument("--operator-note", default="publish audit only")
    parser.add_argument("--human-confirmed", action="store_true")
    args = parser.parse_args()

    audit = build_publish_audit(
        campaign_id=args.campaign_id,
        target=args.target,
        channel=args.channel,
        caption=args.caption,
        asset_ref=args.asset_ref,
        operator_note=args.operator_note,
        human_confirmed=args.human_confirmed,
    )

    out = ROOT / "local_runtime" / "kos_publish_audit" / "hupmix" / (slug(args.campaign_id) + ".json")
    latest = ROOT / "local_runtime" / "kos_publish_audit" / "hupmix" / "latest_publish_audit.json"

    write_json(out, audit)
    write_json(latest, audit)

    print(json.dumps(audit, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
