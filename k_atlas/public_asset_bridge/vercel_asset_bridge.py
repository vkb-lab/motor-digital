from pathlib import Path
import json
import os
import re
import shutil
import subprocess
import urllib.request
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]

def _write_json(path, data):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return data

def _load_asset_package():
    path = ROOT / "reports" / "KOS_PHASE15_CREATIVE_ASSET_PACKAGE.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8-sig"))

def _find_deploy_command():
    vercel = shutil.which("vercel")
    if vercel:
        return [vercel, "deploy", "--yes"]

    npx = shutil.which("npx")
    if npx:
        return [npx, "vercel", "deploy", "--yes"]

    return []

def _save_asset_runtime(base_url):
    path = ROOT / "local_runtime" / "asset_runtime.env"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"KOS_PUBLIC_BASE_URL={base_url.rstrip('/')}\n", encoding="utf-8")
    return str(path)

def _verify_image_url(url):
    if not url:
        return {"status": "URL_EMPTY", "ok": False}

    try:
        req = urllib.request.Request(url, method="GET", headers={"User-Agent": "KOS/1.0"})
        with urllib.request.urlopen(req, timeout=30) as response:
            code = response.getcode()
            content_type = response.headers.get("content-type", "")
            sample = response.read(16)
        return {
            "status": "PUBLIC_IMAGE_REACHABLE" if code == 200 and sample.startswith(b"\x89PNG") else "PUBLIC_IMAGE_CHECK_WARNING",
            "ok": code == 200,
            "http_code": code,
            "content_type": content_type,
            "png_signature": sample.startswith(b"\x89PNG"),
        }
    except Exception as exc:
        return {"status": "PUBLIC_IMAGE_NOT_REACHABLE", "ok": False, "error": str(exc)}

def run_vercel_asset_bridge():
    asset = _load_asset_package()
    if not asset:
        result = {
            "status": "WAITING_PHASE15_ASSET",
            "real_action_executed": False,
            "external_call_executed": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        return _write_json("reports/KOS_PHASE16_PUBLIC_ASSET_URL_RESULT.json", result)

    public_path = asset.get("public_path", "")
    local_png = asset.get("local_png_path", "")

    if not Path(local_png).exists():
        result = {
            "status": "LOCAL_ASSET_MISSING",
            "local_png_path": local_png,
            "real_action_executed": False,
            "external_call_executed": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        return _write_json("reports/KOS_PHASE16_PUBLIC_ASSET_URL_RESULT.json", result)

    command = _find_deploy_command()

    if not command:
        result = {
            "status": "VERCEL_CLI_OR_NPX_MISSING",
            "message": "Instale Vercel CLI ou Node/NPM para gerar URL publica automaticamente.",
            "local_png_path": local_png,
            "public_path": public_path,
            "real_action_executed": False,
            "external_call_executed": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        return _write_json("reports/KOS_PHASE16_PUBLIC_ASSET_URL_RESULT.json", result)

    try:
        proc = subprocess.run(
            command,
            cwd=ROOT,
            capture_output=True,
            text=True,
            shell=False,
            timeout=240,
        )
        output = (proc.stdout or "") + "\n" + (proc.stderr or "")
        urls = re.findall(r"https://[^\s]+", output)
        deploy_url = urls[-1].rstrip("/") if proc.returncode == 0 and urls else ""
    except Exception as exc:
        result = {
            "status": "VERCEL_DEPLOY_FAILED",
            "error": str(exc),
            "command": command,
            "real_action_executed": False,
            "external_call_executed": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        return _write_json("reports/KOS_PHASE16_PUBLIC_ASSET_URL_RESULT.json", result)

    if not deploy_url:
        result = {
            "status": "VERCEL_DEPLOY_NO_URL",
            "command": command,
            "returncode": proc.returncode,
            "output_tail": output[-2000:],
            "real_action_executed": False,
            "external_call_executed": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        return _write_json("reports/KOS_PHASE16_PUBLIC_ASSET_URL_RESULT.json", result)

    runtime_path = _save_asset_runtime(deploy_url)
    image_url = deploy_url + public_path
    verify = _verify_image_url(image_url)

    result = {
        "status": "PUBLIC_ASSET_URL_READY" if verify.get("ok") else "PUBLIC_ASSET_URL_CREATED_VERIFY_WARNING",
        "deploy_url": deploy_url,
        "image_url_for_instagram": image_url,
        "public_path": public_path,
        "local_png_path": local_png,
        "runtime_path": runtime_path,
        "verify": verify,
        "real_action_executed": False,
        "external_call_executed": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    return _write_json("reports/KOS_PHASE16_PUBLIC_ASSET_URL_RESULT.json", result)
