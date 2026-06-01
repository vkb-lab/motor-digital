from pathlib import Path
import json
import os

ROOT = Path(__file__).resolve().parents[2]

def _load_asset_runtime():
    path = ROOT / "local_runtime" / "asset_runtime.env"
    if not path.exists():
        return {"status": "ASSET_RUNTIME_MISSING", "loaded": [], "path": str(path)}

    loaded = []
    for raw in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if key and value and not os.getenv(key):
            os.environ[key] = value
            loaded.append(key)

    return {"status": "ASSET_RUNTIME_LOADED", "loaded": loaded, "path": str(path)}

def _read_last_vercel_url():
    path = ROOT / "reports" / "KOS_PHASE10_VERCEL_PREVIEW_RESULT.json"
    if not path.exists():
        return ""
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        return str(data.get("deploy_url") or "").strip()
    except Exception:
        return ""

def _base_url():
    _load_asset_runtime()
    value = os.getenv("KOS_PUBLIC_BASE_URL", "").strip().rstrip("/")
    if value:
        return value
    return _read_last_vercel_url().rstrip("/")

def inspect_public_asset_url(asset_package: dict | None = None):
    if asset_package is None:
        path = ROOT / "reports" / "KOS_PHASE15_CREATIVE_ASSET_PACKAGE.json"
        if not path.exists():
            return {
                "status": "WAITING_CREATIVE_ASSET",
                "public_url_ready": False,
                "public_url": "",
                "real_action_executed": False,
                "external_call_executed": False,
            }
        asset_package = json.loads(path.read_text(encoding="utf-8-sig"))

    base = _base_url()
    public_path = asset_package.get("public_path", "")

    if not base:
        status = "WAITING_PUBLIC_BASE_URL"
        public_url = ""
    else:
        status = "PUBLIC_ASSET_URL_READY"
        public_url = f"{base}{public_path}"

    result = {
        "status": status,
        "public_url_ready": bool(public_url),
        "public_url": public_url,
        "public_path": public_path,
        "local_png_path": asset_package.get("local_png_path", ""),
        "asset_status": asset_package.get("status"),
        "real_action_executed": False,
        "external_call_executed": False,
    }

    out = ROOT / "reports" / "KOS_PHASE15_PUBLIC_ASSET_URL.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    return result
