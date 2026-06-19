from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

HUPMIX_IG_ID = "17841471706662294"
EXPECTED_USERNAME = "hupmix"

TOKEN_FILES = [
    "local_runtime/kos_secrets/meta_access_token.txt",
    "local_runtime/secrets/meta_access_token.txt",
    "local_runtime/meta_access_token.txt",
    "local_runtime/META_ACCESS_TOKEN.txt",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


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

    raise RuntimeError("Meta token ausente. Configure KOS_META_ACCESS_TOKEN ou arquivo local_runtime/kos_secrets/meta_access_token.txt.")


def graph_get(path: str, params: dict[str, Any]) -> dict[str, Any]:
    token = get_token()
    version = os.environ.get("KOS_META_GRAPH_VERSION", "v25.0").strip() or "v25.0"

    safe_params = dict(params)
    safe_params["access_token"] = token

    url = f"https://graph.facebook.com/{version}/{path}?{urllib.parse.urlencode(safe_params)}"
    request = urllib.request.Request(url, method="GET")

    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            body = response.read().decode("utf-8")
            return json.loads(body)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(body)
        except Exception:
            payload = {"raw_error": body[:500]}
        return {
            "status": "KOS_META_GRAPH_API_ERROR",
            "http_status": exc.code,
            "error": payload,
        }


def summarize_media(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    summary = []
    for item in items:
        caption = str(item.get("caption", ""))
        if len(caption) > 220:
            caption = caption[:220] + "..."
        summary.append({
            "id": item.get("id"),
            "media_type": item.get("media_type"),
            "timestamp": item.get("timestamp"),
            "permalink": item.get("permalink"),
            "like_count": item.get("like_count"),
            "comments_count": item.get("comments_count"),
            "caption_preview": caption,
        })
    return summary


def build_audit() -> dict[str, Any]:
    profile = graph_get(
        HUPMIX_IG_ID,
        {
            "fields": "id,username,account_type,media_count,followers_count,follows_count,biography,website,name",
        },
    )

    if profile.get("status") == "KOS_META_GRAPH_API_ERROR":
        return {
            "status": "KOS_HUPMIX_INSTAGRAM_AUDIT_FAILED",
            "reason": "profile_graph_api_error",
            "graph_error": profile,
            "hupmix_expected_ig_id": HUPMIX_IG_ID,
            "publish_executed": False,
            "instagram_publish_executed": False,
            "browser_logged_account_automation_used": False,
            "created_at": now_iso(),
        }

    id_match = str(profile.get("id")) == HUPMIX_IG_ID
    username_match = str(profile.get("username", "")).lower() == EXPECTED_USERNAME

    if not id_match or not username_match:
        return {
            "status": "KOS_HUPMIX_INSTAGRAM_AUDIT_BLOCKED_WRONG_ACCOUNT",
            "reason": "returned_account_does_not_match_hupmix",
            "expected_ig_id": HUPMIX_IG_ID,
            "expected_username": EXPECTED_USERNAME,
            "returned_id": profile.get("id"),
            "returned_username": profile.get("username"),
            "publish_executed": False,
            "instagram_publish_executed": False,
            "browser_logged_account_automation_used": False,
            "created_at": now_iso(),
        }

    media = graph_get(
        f"{HUPMIX_IG_ID}/media",
        {
            "fields": "id,caption,media_type,permalink,timestamp,like_count,comments_count",
            "limit": 5,
        },
    )

    media_error = media.get("status") == "KOS_META_GRAPH_API_ERROR"
    media_items = [] if media_error else media.get("data", [])

    audit = {
        "status": "KOS_HUPMIX_INSTAGRAM_AUDIT_CONNECTED",
        "phase": "69D",
        "target": "hupmix",
        "ig_id": HUPMIX_IG_ID,
        "username": profile.get("username"),
        "account_type": profile.get("account_type"),
        "media_count": profile.get("media_count"),
        "followers_count": profile.get("followers_count"),
        "follows_count": profile.get("follows_count"),
        "profile_fields_read": True,
        "recent_media_read": not media_error,
        "recent_media_count": len(media_items),
        "recent_media_summary": summarize_media(media_items),
        "media_error": media if media_error else None,
        "audit_checks": {
            "id_match": id_match,
            "username_match": username_match,
            "safe_test_account": True,
            "parada_atlantida_locked": True,
            "read_only_graph_calls": True,
            "publish_endpoint_called": False,
            "post_request_used": False,
            "token_printed": False,
        },
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
    audit = build_audit()
    out = ROOT / "local_runtime" / "kos_instagram_audit" / "hupmix" / "latest_hupmix_instagram_audit.json"
    write_json(out, audit)
    print(json.dumps(audit, indent=2, ensure_ascii=False))

    if audit["status"] == "KOS_HUPMIX_INSTAGRAM_AUDIT_CONNECTED":
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
