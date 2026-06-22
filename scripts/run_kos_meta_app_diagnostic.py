from pathlib import Path
from datetime import datetime, timezone
import json
import os
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "local_runtime" / "kos_meta_diagnostics"
OUT_DIR.mkdir(parents=True, exist_ok=True)

TOKEN_PATHS = [
    ROOT / "local_runtime" / "kos_secrets" / "meta_access_token.txt",
    ROOT / "local_runtime" / "secrets" / "meta_access_token.txt",
    ROOT / "local_runtime" / "meta_access_token.txt",
    ROOT / "local_runtime" / "META_ACCESS_TOKEN.txt",
]

GRAPH_VERSION = os.environ.get("KOS_META_GRAPH_VERSION", "v25.0").strip() or "v25.0"

def read_token():
    for key in ["KOS_META_ACCESS_TOKEN", "META_ACCESS_TOKEN", "FACEBOOK_ACCESS_TOKEN"]:
        value = os.environ.get(key, "").strip()
        if value:
            return value, "env:" + key

    for path in TOKEN_PATHS:
        if path.exists():
            value = path.read_text(encoding="utf-8").strip()
            if value:
                return value, str(path.relative_to(ROOT))

    return "", "missing"

def mask(value):
    value = str(value or "")
    if len(value) <= 12:
        return "***"
    return value[:6] + "..." + value[-6:]

def graph_get(path, params, token):
    clean = dict(params or {})
    clean["access_token"] = token
    url = "https://graph.facebook.com/{}/{}?{}".format(
        GRAPH_VERSION,
        path.lstrip("/"),
        urllib.parse.urlencode(clean)
    )
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        body = ""
        try:
            body = exc.read().decode("utf-8")
        except Exception:
            body = str(exc)
        try:
            parsed = json.loads(body)
        except Exception:
            parsed = {"raw": body}
        return {
            "status": "KOS_META_GRAPH_API_ERROR",
            "path": path,
            "error": parsed
        }

def simplify_error(obj):
    if not isinstance(obj, dict):
        return obj
    if obj.get("status") == "KOS_META_GRAPH_API_ERROR":
        err = obj.get("error", {})
        if isinstance(err, dict) and "error" in err:
            e = err["error"]
            return {
                "message": e.get("message"),
                "type": e.get("type"),
                "code": e.get("code"),
                "fbtrace_id": e.get("fbtrace_id")
            }
        return err
    return None

def main():
    token, token_source = read_token()

    result = {
        "status": "KOS_META_APP_DIAGNOSTIC_STARTED",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "graph_version": GRAPH_VERSION,
        "token_present": bool(token),
        "token_source": token_source,
        "token_preview": mask(token) if token else "",
        "instagram_publish_executed": False,
        "read_only": True,
        "checks": {}
    }

    if not token:
        result["status"] = "KOS_META_TOKEN_MISSING"
        result["next_action"] = "Salvar token oficial em local_runtime/kos_secrets/meta_access_token.txt ou configurar KOS_META_ACCESS_TOKEN."
    else:
        debug = graph_get("debug_token", {
            "input_token": token
        }, token)

        me = graph_get("me", {
            "fields": "id,name"
        }, token)

        pages = graph_get("me/accounts", {
            "fields": "id,name,access_token,instagram_business_account{id,username,name,profile_picture_url},tasks",
            "limit": 100
        }, token)

        result["checks"]["debug_token"] = debug
        result["checks"]["me"] = me

        safe_pages = []
        hupmix_matches = []

        if isinstance(pages, dict) and isinstance(pages.get("data"), list):
            for page in pages["data"]:
                ig = page.get("instagram_business_account") or {}
                safe_page = {
                    "page_id": page.get("id"),
                    "page_name": page.get("name"),
                    "tasks": page.get("tasks", []),
                    "has_page_access_token": bool(page.get("access_token")),
                    "instagram_business_account": {
                        "id": ig.get("id"),
                        "username": ig.get("username"),
                        "name": ig.get("name"),
                        "has_profile_picture": bool(ig.get("profile_picture_url")),
                    } if ig else None
                }
                safe_pages.append(safe_page)

                ig_username = str(ig.get("username", "")).lower()
                if ig_username == "hupmix" or str(ig.get("id", "")) == "17841471706662294":
                    hupmix_matches.append(safe_page)

        result["checks"]["pages_and_instagram_accounts"] = {
            "count": len(safe_pages),
            "items": safe_pages
        }

        result["checks"]["hupmix_matches"] = hupmix_matches

        if debug.get("status") == "KOS_META_GRAPH_API_ERROR":
            result["status"] = "KOS_META_DEBUG_TOKEN_FAILED"
            result["error_summary"] = simplify_error(debug)
        elif pages.get("status") == "KOS_META_GRAPH_API_ERROR":
            result["status"] = "KOS_META_PAGES_LOOKUP_FAILED"
            result["error_summary"] = simplify_error(pages)
        elif hupmix_matches:
            result["status"] = "KOS_META_APP_HUPMIX_CONNECTED"
        else:
            result["status"] = "KOS_META_APP_CONNECTED_BUT_HUPMIX_NOT_FOUND"
            result["next_action"] = "No Business Manager, adicionar a Pagina/Instagram Hupmix ao System User e gerar token com permissoes corretas."

    latest = OUT_DIR / "latest_meta_app_diagnostic.json"
    timestamped = OUT_DIR / ("meta_app_diagnostic_" + datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S") + ".json")

    latest.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    timestamped.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({
        "status": result.get("status"),
        "token_present": result.get("token_present"),
        "token_source": result.get("token_source"),
        "graph_version": result.get("graph_version"),
        "pages_count": result.get("checks", {}).get("pages_and_instagram_accounts", {}).get("count"),
        "hupmix_matches_count": len(result.get("checks", {}).get("hupmix_matches", [])),
        "instagram_publish_executed": False,
        "report": str(latest)
    }, ensure_ascii=False, indent=2))

    return 0

if __name__ == "__main__":
    raise SystemExit(main())

