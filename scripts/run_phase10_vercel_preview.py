from pathlib import Path
import sys
import json
import subprocess
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from k_atlas.deploy_bridge import export_public_status, inspect_vercel_readiness

export_public_status()
readiness = inspect_vercel_readiness()

result = {
    "status": "VERCEL_PREVIEW_NOT_ATTEMPTED",
    "vercel": readiness,
    "deploy_url": "",
    "real_publish_enabled": False,
    "external_call_executed": False,
}

if readiness.get("can_attempt_deploy"):
    cli = readiness.get("cli_path") or shutil.which("vercel")
    try:
        proc = subprocess.run(
            [cli, "deploy", "--yes"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            shell=False,
            timeout=180,
        )
        output = (proc.stdout or "") + "\n" + (proc.stderr or "")
        urls = re.findall(r"https://[^\s]+", output)
        result["status"] = "VERCEL_PREVIEW_READY" if proc.returncode == 0 and urls else "VERCEL_PREVIEW_FAILED"
        result["deploy_url"] = urls[-1] if urls else ""
        result["vercel_output_tail"] = output[-2000:]
    except Exception as exc:
        result["status"] = "VERCEL_PREVIEW_FAILED"
        result["error"] = str(exc)
else:
    result["status"] = readiness["status"]

out = ROOT / "reports" / "KOS_PHASE10_VERCEL_PREVIEW_RESULT.json"
out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(result["status"])
if result.get("deploy_url"):
    print(result["deploy_url"])
