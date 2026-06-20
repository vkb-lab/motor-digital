from __future__ import annotations

import argparse
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

HUPMIX_IG_ID = "17841471706662294"
HUPMIX_USERNAME = "hupmix"
PARADA_IG_ID = "17841480166187766"
PARADA_USERNAME = "paradaatlantida"

FINAL_CONFIRMATION = "YES_EXECUTE_REAL_HUPMIX_INSTAGRAM_PUBLISH_NOW"
REAL_FLAG_ENV = "KOS_REAL_HUPMIX_PUBLISH_ENABLED"

TOKEN_FILES = [
    "local_runtime/kos_secrets/meta_access_token.txt",
    "local_runtime/secrets/meta_access_token.txt",
    "local_runtime/meta_access_token.txt",
    "local_runtime/META_ACCESS_TOKEN.txt",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def slug(value: str) -> str:
    value = value.strip() or "hupmix-real-publish"
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


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"status": "FILE_NOT_FOUND", "path": str(path)}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        return {"status": "READ_FAILED", "path": str(path), "error": str(exc)}


def latest_ledger() -> dict[str, Any]:
    return read_json(ROOT / "local_runtime" / "kos_publish_approval_ledger" / "hupmix" / "latest_publish_approval_ledger.json")


def get_token() -> str:
    for key in ["KOS_META_ACCESS_TOKEN", "META_ACCESS_TOKEN", "FACEBOOK_ACCESS_TOKEN"]:
        value = os.environ.get(key, "").strip()
        if value:
            return value

    for relpath in TOKEN_FILES:
        path = ROOT / relpath
        if path.exists():
            value = path.read_text(encoding="utf-8-sig").strip()
            if value:
                return value

    raise RuntimeError("Meta token ausente. Configure KOS_META_ACCESS_TOKEN ou local_runtime/kos_secrets/meta_access_token.txt.")


def graph_version() -> str:
    return os.environ.get("KOS_META_GRAPH_VERSION", "v25.0").strip() or "v25.0"


def graph_request(method: str, path: str, params: dict[str, Any]) -> dict[str, Any]:
    token = get_token()
    clean_params = dict(params)
    clean_params["access_token"] = token

    encoded = urllib.parse.urlencode(clean_params).encode("utf-8")
    url = f"https://graph.facebook.com/{graph_version()}/{path}"

    if method == "GET":
        request = urllib.request.Request(url + "?" + encoded.decode("utf-8"), method="GET")
    elif method == "POST":
        request = urllib.request.Request(url, data=encoded, method="POST")
    else:
        raise RuntimeError("Metodo HTTP nao permitido.")

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            body = response.read().decode("utf-8")
            return json.loads(body)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(body)
        except Exception:
            payload = {"raw_error": body[:800]}
        return {
            "status": "KOS_META_GRAPH_API_ERROR",
            "http_status": exc.code,
            "error": payload,
            "token_logged": False,
        }


def validate_request(target: str, caption: str, image_url: str, confirmation: str, execute_real_publish: bool) -> dict[str, Any]:
    ledger = latest_ledger()
    confirmation_valid = confirmation.strip() == FINAL_CONFIRMATION
    real_flag_enabled = os.environ.get(REAL_FLAG_ENV, "").strip().lower() == "true"

    base = {
        "phase": "69H",
        "target_requested": target,
        "confirmation_phrase_required": FINAL_CONFIRMATION,
        "confirmation_valid": confirmation_valid,
        "real_flag_env": REAL_FLAG_ENV,
        "real_flag_enabled": real_flag_enabled,
        "execute_real_publish_requested": execute_real_publish,
        "latest_ledger_status": ledger.get("status"),
        "created_at": now_iso(),
    }

    blocked_common = {
        "allowed_to_call_publish_endpoint": False,
        "publish_endpoint_called": False,
        "container_created": False,
        "media_published": False,
        "http_post_used": False,
        "real_action_executed": False,
        "instagram_publish_executed": False,
        "browser_logged_account_automation_used": False,
        "paid_ai_call_executed": False,
        "token_logged": False,
    }

    if is_parada(target):
        return {**base, **blocked_common, "status": "KOS_HUPMIX_REAL_PUBLISH_EXECUTOR_BLOCKED", "reason": "blocked_target_parada_atlantida"}

    if not is_hupmix(target):
        return {**base, **blocked_common, "status": "KOS_HUPMIX_REAL_PUBLISH_EXECUTOR_BLOCKED", "reason": "only_hupmix_test_account_allowed"}

    if ledger.get("status") != "KOS_REAL_PUBLISH_APPROVAL_LEDGER_CREATED":
        return {**base, **blocked_common, "status": "KOS_HUPMIX_REAL_PUBLISH_EXECUTOR_BLOCKED", "reason": "approval_ledger_not_ready"}

    if not caption.strip() or len(caption) > 2200:
        return {**base, **blocked_common, "status": "KOS_HUPMIX_REAL_PUBLISH_EXECUTOR_BLOCKED", "reason": "invalid_caption"}

    if not image_url.startswith("https://"):
        return {**base, **blocked_common, "status": "KOS_HUPMIX_REAL_PUBLISH_EXECUTOR_BLOCKED", "reason": "image_url_must_be_public_https"}

    if not execute_real_publish:
        return {
            **base,
            **blocked_common,
            "status": "KOS_HUPMIX_REAL_PUBLISH_EXECUTOR_READY_DRY_RUN",
            "reason": "executor_ready_but_real_publish_not_requested",
            "target": HUPMIX_USERNAME,
            "ig_id": HUPMIX_IG_ID,
            "future_real_publish_requires_final_confirmation": True,
        }

    if not confirmation_valid:
        return {**base, **blocked_common, "status": "KOS_HUPMIX_REAL_PUBLISH_EXECUTOR_BLOCKED", "reason": "missing_or_invalid_final_confirmation"}

    if not real_flag_enabled:
        return {**base, **blocked_common, "status": "KOS_HUPMIX_REAL_PUBLISH_EXECUTOR_BLOCKED", "reason": "real_publish_env_flag_not_enabled"}

    return {
        **base,
        "status": "KOS_HUPMIX_REAL_PUBLISH_EXECUTOR_AUTHORIZED",
        "reason": "all_final_gates_passed",
        "target": HUPMIX_USERNAME,
        "ig_id": HUPMIX_IG_ID,
        "allowed_to_call_publish_endpoint": True,
        "publish_endpoint_called": False,
        "container_created": False,
        "media_published": False,
        "http_post_used": False,
        "real_action_executed": False,
        "instagram_publish_executed": False,
        "browser_logged_account_automation_used": False,
        "paid_ai_call_executed": False,
        "token_logged": False,
    }


def execute_publish(campaign_id: str, caption: str, image_url: str, operator: str) -> dict[str, Any]:
    profile = graph_request("GET", HUPMIX_IG_ID, {"fields": "id,username,account_type,media_count"})

    if profile.get("status") == "KOS_META_GRAPH_API_ERROR":
        return {
            "status": "KOS_HUPMIX_REAL_PUBLISH_EXECUTOR_FAILED",
            "reason": "profile_check_failed",
            "profile_error": profile,
            "publish_endpoint_called": False,
            "http_post_used": False,
            "instagram_publish_executed": False,
            "token_logged": False,
            "created_at": now_iso(),
        }

    if str(profile.get("id")) != HUPMIX_IG_ID or str(profile.get("username", "")).lower() != HUPMIX_USERNAME:
        return {
            "status": "KOS_HUPMIX_REAL_PUBLISH_EXECUTOR_BLOCKED",
            "reason": "graph_profile_not_hupmix",
            "returned_id": profile.get("id"),
            "returned_username": profile.get("username"),
            "publish_endpoint_called": False,
            "http_post_used": False,
            "instagram_publish_executed": False,
            "token_logged": False,
            "created_at": now_iso(),
        }

    container = graph_request(
        "POST",
        f"{HUPMIX_IG_ID}/media",
        {
            "image_url": image_url,
            "caption": caption,
        },
    )

    if container.get("status") == "KOS_META_GRAPH_API_ERROR" or not container.get("id"):
        return {
            "status": "KOS_HUPMIX_REAL_PUBLISH_EXECUTOR_FAILED",
            "reason": "container_create_failed",
            "container_response": container,
            "publish_endpoint_called": True,
            "container_created": False,
            "media_published": False,
            "http_post_used": True,
            "instagram_publish_executed": False,
            "token_logged": False,
            "created_at": now_iso(),
        }

    container_id = container["id"]

    status_checks = []
    for _ in range(3):
        time.sleep(2)
        status_payload = graph_request("GET", container_id, {"fields": "status_code"})
        status_checks.append(status_payload)
        if status_payload.get("status_code") in {"FINISHED", "PUBLISHED"}:
            break

    published = graph_request(
        "POST",
        f"{HUPMIX_IG_ID}/media_publish",
        {
            "creation_id": container_id,
        },
    )

    if published.get("status") == "KOS_META_GRAPH_API_ERROR" or not published.get("id"):
        return {
            "status": "KOS_HUPMIX_REAL_PUBLISH_EXECUTOR_FAILED",
            "reason": "media_publish_failed",
            "container_id": container_id,
            "container_status_checks": status_checks,
            "publish_response": published,
            "publish_endpoint_called": True,
            "container_created": True,
            "media_published": False,
            "http_post_used": True,
            "real_action_executed": True,
            "instagram_publish_executed": False,
            "token_logged": False,
            "created_at": now_iso(),
        }

    return {
        "status": "KOS_HUPMIX_REAL_PUBLISH_EXECUTED",
        "phase": "69H",
        "campaign_id": slug(campaign_id),
        "target": HUPMIX_USERNAME,
        "ig_id": HUPMIX_IG_ID,
        "operator": operator,
        "container_id": container_id,
        "published_media_id": published.get("id"),
        "container_status_checks": status_checks,
        "publish_endpoint_called": True,
        "container_created": True,
        "media_published": True,
        "http_post_used": True,
        "real_action_executed": True,
        "instagram_publish_executed": True,
        "browser_logged_account_automation_used": False,
        "paid_ai_call_executed": False,
        "parada_atlantida_locked": True,
        "token_logged": False,
        "created_at": now_iso(),
    }


def build_executor_result(
    campaign_id: str,
    target: str,
    caption: str,
    image_url: str,
    operator: str,
    confirmation: str,
    execute_real_publish: bool,
) -> dict[str, Any]:
    validation = validate_request(target, caption, image_url, confirmation, execute_real_publish)

    if validation.get("status") != "KOS_HUPMIX_REAL_PUBLISH_EXECUTOR_AUTHORIZED":
        return validation

    published = execute_publish(campaign_id, caption, image_url, operator)

    return {
        **validation,
        "status": published.get("status"),
        "publish_result": published,
        "publish_endpoint_called": published.get("publish_endpoint_called", False),
        "container_created": published.get("container_created", False),
        "media_published": published.get("media_published", False),
        "http_post_used": published.get("http_post_used", False),
        "real_action_executed": published.get("real_action_executed", False),
        "instagram_publish_executed": published.get("instagram_publish_executed", False),
        "browser_logged_account_automation_used": False,
        "paid_ai_call_executed": False,
        "token_logged": False,
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--campaign-id", default="KOS-HUPMIX-REAL-PUBLISH")
    parser.add_argument("--target", default="hupmix")
    parser.add_argument("--caption", required=True)
    parser.add_argument("--image-url", required=True)
    parser.add_argument("--operator", default="operator")
    parser.add_argument("--confirmation", default="")
    parser.add_argument("--execute-real-publish", action="store_true")
    args = parser.parse_args()

    result = build_executor_result(
        campaign_id=args.campaign_id,
        target=args.target,
        caption=args.caption,
        image_url=args.image_url,
        operator=args.operator,
        confirmation=args.confirmation,
        execute_real_publish=args.execute_real_publish,
    )

    out = ROOT / "local_runtime" / "kos_real_publish_executor" / "hupmix" / (slug(args.campaign_id) + ".json")
    latest = ROOT / "local_runtime" / "kos_real_publish_executor" / "hupmix" / "latest_real_publish_executor_result.json"

    write_json(out, result)
    write_json(latest, result)

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result.get("status") in {
        "KOS_HUPMIX_REAL_PUBLISH_EXECUTOR_READY_DRY_RUN",
        "KOS_HUPMIX_REAL_PUBLISH_EXECUTOR_BLOCKED",
        "KOS_HUPMIX_REAL_PUBLISH_EXECUTED",
        "KOS_HUPMIX_REAL_PUBLISH_EXECUTOR_FAILED",
    } else 1


if __name__ == "__main__":
    raise SystemExit(main())
