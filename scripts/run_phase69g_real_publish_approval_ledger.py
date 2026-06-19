from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

HUPMIX_USERNAME = "hupmix"
HUPMIX_IG_ID = "17841471706662294"
PARADA_USERNAME = "paradaatlantida"
PARADA_IG_ID = "17841480166187766"

APPROVAL_PHRASE = "YES_CREATE_HUPMIX_REAL_PUBLISH_APPROVAL_LEDGER_ONLY"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def slug(value: str) -> str:
    value = value.strip() or "publish-approval"
    value = re.sub(r"[^A-Za-z0-9_\-]+", "-", value)
    return value[:120]


def normalize(value: str) -> str:
    return value.strip().lower().replace("@", "")


def is_hupmix(target: str) -> bool:
    value = normalize(target)
    return value in {HUPMIX_USERNAME, HUPMIX_IG_ID.lower(), "hupmix_test", "test_hupmix"}


def is_parada(target: str) -> bool:
    value = normalize(target)
    return value in {PARADA_USERNAME, PARADA_IG_ID.lower(), "parada", "parada-atlantida", "parada_atlantida"}


def read_latest_dry_run() -> dict:
    path = ROOT / "local_runtime" / "kos_publish_dry_run" / "hupmix" / "latest_publish_dry_run.json"
    if not path.exists():
        return {"status": "KOS_DRY_RUN_NOT_FOUND", "path": str(path)}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        return {"status": "KOS_DRY_RUN_READ_FAILED", "error": str(exc), "path": str(path)}


def build_approval_ledger(
    campaign_id: str,
    target: str,
    caption: str,
    asset_ref: str,
    operator: str,
    approval_phrase: str,
    note: str,
) -> dict:
    safe_campaign_id = slug(campaign_id)
    phrase_valid = approval_phrase.strip() == APPROVAL_PHRASE
    dry_run = read_latest_dry_run()

    base = {
        "phase": "69G",
        "campaign_id": safe_campaign_id,
        "target_requested": target,
        "operator": operator,
        "approval_phrase_required": APPROVAL_PHRASE,
        "approval_phrase_valid": phrase_valid,
        "caption_draft": caption,
        "asset_ref": asset_ref,
        "note": note,
        "latest_dry_run_status": dry_run.get("status"),
        "created_at": now_iso(),
    }

    blocked_common = {
        "approval_ledger_created": False,
        "eligible_for_future_real_publish_executor": False,
        "publish_endpoint_called": False,
        "http_post_used": False,
        "publish_execution_command_generated": False,
        "real_action_executed": False,
        "instagram_publish_executed": False,
        "browser_logged_account_automation_used": False,
        "paid_ai_call_executed": False,
    }

    if is_parada(target):
        return {
            **base,
            **blocked_common,
            "status": "KOS_REAL_PUBLISH_APPROVAL_LEDGER_BLOCKED",
            "reason": "blocked_target_parada_atlantida",
            "target": target,
        }

    if not is_hupmix(target):
        return {
            **base,
            **blocked_common,
            "status": "KOS_REAL_PUBLISH_APPROVAL_LEDGER_BLOCKED",
            "reason": "only_hupmix_test_account_allowed_in_this_phase",
            "target": target,
            "expected_target": HUPMIX_USERNAME,
        }

    if not phrase_valid:
        return {
            **base,
            **blocked_common,
            "status": "KOS_REAL_PUBLISH_APPROVAL_LEDGER_BLOCKED",
            "reason": "missing_or_invalid_approval_phrase",
            "target": HUPMIX_USERNAME,
        }

    if dry_run.get("status") != "KOS_HUMAN_CONFIRMED_PUBLISH_DRY_RUN_READY":
        return {
            **base,
            **blocked_common,
            "status": "KOS_REAL_PUBLISH_APPROVAL_LEDGER_BLOCKED",
            "reason": "latest_dry_run_not_ready",
            "target": HUPMIX_USERNAME,
        }

    return {
        **base,
        "status": "KOS_REAL_PUBLISH_APPROVAL_LEDGER_CREATED",
        "reason": "approval_record_created_for_future_executor_only",
        "target": HUPMIX_USERNAME,
        "ig_id": HUPMIX_IG_ID,
        "approval_ledger_created": True,
        "ledger": {
            "approved_target": HUPMIX_USERNAME,
            "approved_ig_id": HUPMIX_IG_ID,
            "approved_campaign_id": safe_campaign_id,
            "approved_caption_draft": caption,
            "approved_asset_ref": asset_ref,
            "operator": operator,
            "approval_note": note,
            "dry_run_reference_status": dry_run.get("status"),
            "dry_run_campaign_id": dry_run.get("campaign_id"),
            "future_executor_required": True,
        },
        "required_next_gate": "69H_REAL_PUBLISH_EXECUTOR_HUPMIX_ONLY_WITH_FINAL_CONFIRMATION",
        "eligible_for_future_real_publish_executor": True,
        "publish_endpoint_called": False,
        "http_post_used": False,
        "publish_execution_command_generated": False,
        "production_publish_locked": True,
        "paid_ai_locked": True,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "publish_executed": False,
        "instagram_publish_executed": False,
        "browser_logged_account_automation_used": False,
        "parada_atlantida_locked": True,
        "token_logged": False,
    }


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--campaign-id", default="KOS-REAL-PUBLISH-APPROVAL")
    parser.add_argument("--target", default="hupmix")
    parser.add_argument("--caption", default="Rascunho aprovado para ledger. Ainda nao publicar.")
    parser.add_argument("--asset-ref", default="KOS_LOCAL_TEST_ASSET")
    parser.add_argument("--operator", default="operator")
    parser.add_argument("--approval-phrase", default="")
    parser.add_argument("--note", default="approval ledger only")
    args = parser.parse_args()

    result = build_approval_ledger(
        campaign_id=args.campaign_id,
        target=args.target,
        caption=args.caption,
        asset_ref=args.asset_ref,
        operator=args.operator,
        approval_phrase=args.approval_phrase,
        note=args.note,
    )

    out = ROOT / "local_runtime" / "kos_publish_approval_ledger" / "hupmix" / (slug(args.campaign_id) + ".json")
    latest = ROOT / "local_runtime" / "kos_publish_approval_ledger" / "hupmix" / "latest_publish_approval_ledger.json"

    write_json(out, result)
    write_json(latest, result)

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
