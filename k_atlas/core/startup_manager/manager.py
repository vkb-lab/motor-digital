from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


STARTUP_TARGETS = [
    {
        "id": "local_control_plane",
        "name": "Local Control Plane",
        "page": "pages/77_K_Atlas_Local_Control_Plane.py",
        "port": 8507,
        "command": "powershell -ExecutionPolicy Bypass -File .\\ops\\open_local_control_plane.ps1",
        "autostart": False,
    },
    {
        "id": "local_os_shell",
        "name": "Local OS Shell",
        "page": "pages/83_K_Atlas_Local_OS_Shell.py",
        "port": 8508,
        "command": "powershell -ExecutionPolicy Bypass -File .\\ops\\open_k_atlas_local_os_shell.ps1",
        "autostart": False,
    },
    {
        "id": "release_capsule",
        "name": "Release Capsule",
        "page": "pages/100_K_Atlas_Local_OS_Release_Capsule.py",
        "port": 8510,
        "command": "streamlit run pages/100_K_Atlas_Local_OS_Release_Capsule.py --server.port 8510 --server.address 127.0.0.1",
        "autostart": False,
    },
    {
        "id": "operator_home",
        "name": "Operator Home",
        "page": "pages/104_K_Atlas_Operator_Home.py",
        "port": 8511,
        "command": "powershell -ExecutionPolicy Bypass -File .\\ops\\open_operator_home.ps1",
        "autostart": False,
    },
]


class StartupManager:
    def __init__(
        self,
        project_root: str | Path = ".",
        live_dir: str | Path = "live/startup_manager",
        reports_dir: str | Path = "reports/startup_manager",
    ) -> None:
        self.project_root = Path(project_root)
        self.live_dir = self.project_root / live_dir
        self.reports_dir = self.project_root / reports_dir
        self.config_path = self.live_dir / "startup_targets.json"

    def target_status(self) -> list[dict[str, Any]]:
        rows = []
        for item in STARTUP_TARGETS:
            exists = (self.project_root / item["page"]).exists()
            rows.append({**item, "ready": exists, "status": "ready" if exists else "missing"})
        return rows

    def build_config(self) -> dict[str, Any]:
        targets = self.target_status()
        config = {
            "ok": True,
            "checkpoint": "102",
            "name": "Startup Manager",
            "generated_at": utc_now(),
            "status": "operational",
            "summary": {
                "targets_total": len(targets),
                "targets_ready": len([item for item in targets if item["ready"]]),
                "autostart_enabled": False,
                "execution_enabled": False,
            },
            "targets": targets,
            "guardrails": [
                "startup manager nao habilita autostart sozinho",
                "somente lista comandos seguros",
                "operador escolhe o que abrir",
            ],
        }
        self.save(config)
        return config

    def save(self, config: dict[str, Any]) -> None:
        self.live_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(config, ensure_ascii=False, indent=2, sort_keys=True)
        self.config_path.write_text(payload, encoding="utf-8")
        (self.reports_dir / "latest_startup_manager.json").write_text(payload, encoding="utf-8")
