from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "local_runtime" / "kos_saas_product_mission_pack"
LATEST = OUT_DIR / "latest_saas_product_mission_pack_alias.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default="draft")
    parser.add_argument("--idea", default="SaaS local gerado pelo K-OS")
    args = parser.parse_args()

    module = "k_atlas.saas_factory.product_mission_pack.run_pack_demo"
    completed = subprocess.run(
        [sys.executable, "-m", module],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
        check=False,
    )

    payload = {
        "status": "KOS_SAAS_PRODUCT_MISSION_PACK_ALIAS_READY" if completed.returncode == 0 else "KOS_SAAS_PRODUCT_MISSION_PACK_ALIAS_ATTENTION_REQUIRED",
        "created_at": now_iso(),
        "mode": args.mode,
        "idea": args.idea,
        "module": module,
        "returncode": completed.returncode,
        "stdout_tail": (completed.stdout or "")[-4000:],
        "stderr_tail": (completed.stderr or "")[-4000:],
        "real_action_executed": False,
        "external_side_effects_executed": False,
        "paid_ai_call_executed": False,
        "deploy_executed": False,
    }
    write_json(LATEST, payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if completed.returncode == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
