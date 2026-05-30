from __future__ import annotations

import json
import socket
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4

from .policy import validate_control_plane_request


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class KAtlasLocalControlPlane:
    def __init__(
        self,
        project_root: str | Path = ".",
        live_dir: str | Path = "live/local_control_plane",
        memory_dir: str | Path = "memory/local_control_plane",
        reports_dir: str | Path = "reports/local_control_plane",
    ) -> None:
        self.project_root = Path(project_root)
        self.live_dir = self.project_root / live_dir
        self.memory_dir = self.project_root / memory_dir
        self.reports_dir = self.project_root / reports_dir
        self.events_path = self.memory_dir / "events.jsonl"
        self.state_path = self.live_dir / "control_plane_state.json"

    def event(self, event_type: str, payload: dict[str, Any]) -> None:
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        row = {
            "timestamp": utc_now(),
            "event_type": event_type,
            "payload": payload,
        }
        with self.events_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    def exists(self, path: str) -> bool:
        return (self.project_root / path).exists()

    def load_json(self, path: str) -> Any:
        target = self.project_root / path
        if not target.exists():
            return None

        try:
            return json.loads(target.read_text(encoding="utf-8-sig"))
        except Exception:
            return None

    def count_json_list(self, path: str) -> int:
        data = self.load_json(path)
        return len(data) if isinstance(data, list) else 0

    def port_open(self, host: str, port: int, timeout: float = 0.15) -> bool:
        try:
            with socket.create_connection((host, port), timeout=timeout):
                return True
        except OSError:
            return False

    def git_status_short(self) -> list[str]:
        try:
            result = subprocess.run(
                ["git", "status", "--short"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=8,
            )
            if result.returncode != 0:
                return [f"git_status_failed:{result.returncode}"]
            return [line for line in result.stdout.splitlines() if line.strip()]
        except Exception as exc:
            return [f"git_status_error:{type(exc).__name__}"]

    def module_rows(self) -> list[dict[str, Any]]:
        rows = [
            {
                "name": "Autoprogramming Cycle Dashboard",
                "checkpoint": "71",
                "path": "k_atlas/core/autoprogramming_cycle_dashboard",
                "page": "pages/71_K_Atlas_Autoprogramming_Cycle_Dashboard.py",
                "role": "visualizar ciclo 65-71",
            },
            {
                "name": "Autoprogramming Cycle Controller",
                "checkpoint": "72",
                "path": "k_atlas/core/autoprogramming_cycle_controller",
                "page": "pages/72_K_Atlas_Autoprogramming_Cycle_Controller.py",
                "role": "recomendar proxima acao segura",
            },
            {
                "name": "Local Mission Installer",
                "checkpoint": "73",
                "path": "k_atlas/core/local_mission_installer",
                "page": "pages/73_K_Atlas_Local_Mission_Installer.py",
                "role": "instalar missoes locais com aprovacao humana",
            },
            {
                "name": "Mission Pack Generator",
                "checkpoint": "74",
                "path": "k_atlas/core/mission_pack_generator",
                "page": "pages/74_K_Atlas_Mission_Pack_Generator.py",
                "role": "gerar pacotes de missao",
            },
            {
                "name": "Mission Pack Bridge",
                "checkpoint": "75",
                "path": "k_atlas/core/mission_pack_bridge",
                "page": "pages/75_K_Atlas_Mission_Pack_Bridge.py",
                "role": "converter pacote para missao local",
            },
            {
                "name": "Mission Pipeline Runner",
                "checkpoint": "76",
                "path": "k_atlas/core/mission_pipeline_runner",
                "page": "pages/76_K_Atlas_Mission_Pipeline_Runner.py",
                "role": "orquestrar 74 -> 75 -> 73",
            },
        ]

        final_rows: list[dict[str, Any]] = []
        for row in rows:
            module_exists = self.exists(row["path"])
            page_exists = self.exists(row["page"])
            final_rows.append({
                **row,
                "module_exists": module_exists,
                "page_exists": page_exists,
                "ready": module_exists and page_exists,
                "status": "ready" if module_exists and page_exists else "missing",
            })

        return final_rows

    def queue_summary(self) -> dict[str, Any]:
        return {
            "cycle_decisions": self.count_json_list("live/autoprogramming_cycle_controller/cycle_decision_queue.json"),
            "mission_packs": self.count_json_list("live/mission_pack_generator/mission_pack_queue.json"),
            "bridge_missions": self.count_json_list("live/mission_pack_bridge/local_mission_queue.json"),
            "local_missions": self.count_json_list("live/local_mission_installer/local_mission_queue.json"),
            "pipeline_runs": self.count_json_list("live/mission_pipeline_runner/pipeline_runs.json"),
            "install_manifest": self.count_json_list("memory/local_mission_installer/install_manifest.json"),
        }

    def cockpit_summary(self) -> dict[str, Any]:
        ports = [8501, 8502, 8503, 8504]
        return {
            "localhost_ports": [
                {
                    "port": port,
                    "open": self.port_open("127.0.0.1", port),
                    "url": f"http://127.0.0.1:{port}",
                }
                for port in ports
            ],
            "streamlit_main_known_ports": ports,
            "network_access_default": "localhost_only",
        }

    def lan_readiness(self) -> dict[str, Any]:
        return {
            "ready_for_lan_design": True,
            "public_internet_exposure": False,
            "remote_control_enabled": False,
            "firewall_change_required_now": False,
            "recommended_next_checkpoint": "78 - Remote Assist Readiness",
            "safe_first_step": "expor apenas dashboard em rede local com aprovacao humana e sem execucao real",
            "blocked_until_gate": [
                "controle de mouse",
                "captura de senha",
                "porta publica na internet",
                "execucao automatica remota",
                "tunnel publico sem approval gate",
            ],
        }

    def pending_actions(self, state: Mapping[str, Any]) -> list[dict[str, Any]]:
        modules = list(state.get("modules", []) or [])
        queues = dict(state.get("queues", {}) or {})
        actions: list[dict[str, Any]] = []

        missing = [item for item in modules if item.get("ready") is not True]
        if missing:
            actions.append({
                "priority": "high",
                "action": "repair_missing_modules",
                "reason": "existem modulos do ciclo local sem pagina ou pasta",
                "human_instruction": "Verificar lista de modulos missing no painel 77.",
                "automatic_execution_allowed": False,
            })

        if queues.get("mission_packs", 0) > queues.get("bridge_missions", 0):
            actions.append({
                "priority": "medium",
                "action": "bridge_pending_mission_pack",
                "reason": "existem mission packs que podem precisar conversao para kmission",
                "human_instruction": "Abrir checkpoint 75 ou rodar bridge supervisionado.",
                "automatic_execution_allowed": False,
            })

        if queues.get("bridge_missions", 0) > queues.get("install_manifest", 0):
            actions.append({
                "priority": "medium",
                "action": "review_local_mission_install",
                "reason": "existem missoes locais que podem precisar aprovacao humana",
                "human_instruction": "Abrir checkpoint 73 e revisar dry-run antes de instalar.",
                "automatic_execution_allowed": False,
            })

        if not actions:
            actions.append({
                "priority": "medium",
                "action": "prepare_remote_assist_readiness",
                "reason": "control plane local operacional",
                "human_instruction": "Criar checkpoint 78 para readiness de acesso assistido em rede, sem controle remoto ainda.",
                "automatic_execution_allowed": False,
            })

        return actions

    def build_state(self) -> dict[str, Any]:
        modules = self.module_rows()
        queues = self.queue_summary()
        cockpit = self.cockpit_summary()

        state = {
            "ok": True,
            "generated_at": utc_now(),
            "modules": modules,
            "modules_ready": len([item for item in modules if item.get("ready")]),
            "modules_total": len(modules),
            "queues": queues,
            "cockpit": cockpit,
            "lan_readiness": self.lan_readiness(),
            "git_status_short": self.git_status_short(),
            "execution_enabled": False,
            "real_execution_enabled": False,
            "external_side_effects": "none",
        }

        state["pending_actions"] = self.pending_actions(state)
        state["control_plane_ready"] = state["modules_ready"] == state["modules_total"]

        return state

    def build_report(self, request: Mapping[str, Any] | None = None) -> dict[str, Any]:
        request_data = dict(request or {"mode": "observe"})
        validation = validate_control_plane_request(request_data)
        run_id = str(uuid4())

        if not validation["ok"]:
            report = {
                "ok": False,
                "checkpoint": "77",
                "name": "K-Atlas Local Control Plane",
                "run_id": run_id,
                "generated_at": utc_now(),
                "status": "blocked_by_policy",
                "request_validation": validation,
                "execution_enabled": False,
                "real_execution_enabled": False,
                "external_side_effects": "none",
            }
            self.save_report(report)
            return report

        state = self.build_state()
        report = {
            "ok": True,
            "checkpoint": "77",
            "name": "K-Atlas Local Control Plane",
            "run_id": run_id,
            "generated_at": utc_now(),
            "status": "operational" if state.get("control_plane_ready") else "partial",
            "mode": request_data.get("mode", "observe"),
            "state": state,
            "summary": {
                "control_plane_ready": state.get("control_plane_ready"),
                "modules_ready": state.get("modules_ready"),
                "modules_total": state.get("modules_total"),
                "pending_actions": len(state.get("pending_actions", [])),
                "execution_enabled": False,
                "real_execution_enabled": False,
                "external_side_effects": "local_observation_only",
                "next_checkpoint": "78 - Remote Assist Readiness",
            },
            "guardrails": [
                "control plane observa e recomenda",
                "control plane nao executa missao automaticamente",
                "control plane nao controla mouse",
                "control plane nao abre porta publica",
                "control plane nao captura senha",
                "control plane nao chama API externa",
                "qualquer acao real exige approval gate humano",
            ],
        }

        self.save_report(report)
        self.save_state(state)
        self.event("local_control_plane.report_built", {
            "run_id": run_id,
            "status": report["status"],
            "control_plane_ready": state.get("control_plane_ready"),
        })
        return report

    def save_state(self, state: dict[str, Any]) -> None:
        self.live_dir.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(
            json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    def save_report(self, report: dict[str, Any]) -> dict[str, Any]:
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        json_path = self.reports_dir / "latest_local_control_plane.json"
        md_path = self.reports_dir / "latest_local_control_plane.md"

        json_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        md_path.write_text(self.to_markdown(report), encoding="utf-8")
        return report

    def to_markdown(self, report: dict[str, Any]) -> str:
        summary = report.get("summary", {}) or {}
        state = report.get("state", {}) or {}
        lines = [
            "# K-Atlas Local Control Plane",
            "",
            f"Checkpoint: {report.get('checkpoint')}",
            f"Status: {report.get('status')}",
            "",
            "## Summary",
            "",
            f"- Control plane ready: {summary.get('control_plane_ready')}",
            f"- Modules ready: {summary.get('modules_ready')}/{summary.get('modules_total')}",
            f"- Pending actions: {summary.get('pending_actions')}",
            f"- Execution enabled: {summary.get('execution_enabled')}",
            f"- Next checkpoint: {summary.get('next_checkpoint')}",
            "",
            "## Modules",
            "",
        ]

        for item in state.get("modules", []):
            lines.append(f"- {item.get('checkpoint')} - {item.get('name')} - {item.get('status')}")

        lines.extend([
            "",
            "## Pending actions",
            "",
        ])

        for item in state.get("pending_actions", []):
            lines.append(f"- {item.get('priority')} - {item.get('action')} - {item.get('human_instruction')}")

        lines.extend([
            "",
            "## Guardrails",
            "",
        ])

        for item in report.get("guardrails", []):
            lines.append(f"- {item}")

        return "\n".join(lines)
