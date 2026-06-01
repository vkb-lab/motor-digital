from pathlib import Path
import json
from datetime import datetime, timezone

from k_atlas.ig_live_check.env_plan import build_env_plan
from k_atlas.ig_live_check.final_live_check import build_final_live_check
from k_atlas.ig_first_post import build_first_post_package

ROOT = Path(__file__).resolve().parents[2]

def _write_report(path_name: str, data: dict):
    path = ROOT / "reports" / path_name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    data["path"] = str(path)
    return data

def ensure_local_runtime_template():
    path = ROOT / "local_runtime" / "ig_runtime.env"
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(
            "# K-OS local runtime - nao versionar\n"
            "IG_BUSINESS_ACCOUNT_ID=\n"
            "META_ACCESS_KEY=\n"
            "KOS_REAL_IG_PUBLISH_ENABLED=false\n"
            "KOS_HUMAN_OK_FOR_IG_REAL=\n"
            "KOS_PHASE12_REAL_RUN=\n"
            "KOS_PHASE13_REAL_RUN=\n",
            encoding="utf-8"
        )
    return str(path)

def build_live_ready_package():
    template_path = ensure_local_runtime_template()
    env_plan = build_env_plan()
    final_check = build_final_live_check(load_runtime=True)
    first_post_package = build_first_post_package()

    package = {
        "status": "READY_FOR_REAL_FIRST_POST" if final_check["ready_for_real_first_post"] else "WAITING_LIVE_ENV",
        "template_path": template_path,
        "env_plan": env_plan,
        "final_check": final_check,
        "first_post_package": first_post_package,
        "real_action_executed": False,
        "external_call_executed": False,
        "next_step": "Preencher local_runtime/ig_runtime.env e confirmar execucao real na Fase 14.",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    return _write_report("KOS_PHASE13_IG_LIVE_CHECK_PACKAGE.json", package)

def run_phase13_live_check_demo():
    package = build_live_ready_package()
    result = {
        "status": "PHASE13_LIVE_CHECK_READY",
        "package": package,
        "ready_for_real_first_post": package["final_check"]["ready_for_real_first_post"],
        "real_action_executed": False,
        "external_call_executed": False,
    }
    return _write_report("KOS_PHASE13_IG_LIVE_CHECK_DEMO.json", result)
