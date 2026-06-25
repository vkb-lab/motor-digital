from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "memory" / "kos_governance" / "KOS_RENDER_CLOUD_RUNTIME_POLICY.json"


def build_status() -> dict:
    data = json.loads(POLICY.read_text(encoding="utf-8"))
    app_render = ROOT / str(data.get("cloud_entrypoint", "app_render.py"))
    blueprint = ROOT / str(data.get("blueprint", "render.yaml"))
    return {
        "status": "KOS_RENDER_DEPLOY_READINESS_STATUS_READY",
        "policy_status": data.get("status"),
        "cloud_entrypoint_exists": app_render.exists(),
        "blueprint_exists": blueprint.exists(),
        "deploy_executed": False,
        "render_yaml_changed": False,
        "secrets_read": False,
        "forbidden": data.get("forbidden", []),
        "next_step": data.get("next_step"),
    }


def main() -> None:
    print(json.dumps(build_status(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
