from __future__ import annotations

import json
import subprocess
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class DailyOperatorCockpit:
    def __init__(
        self,
        reports_dir: str | Path = "reports/daily_operator",
        memory_dir: str | Path = "memory/daily_operator",
    ) -> None:
        self.reports_dir = Path(reports_dir)
        self.memory_dir = Path(memory_dir)
        self.events_path = self.memory_dir / "events.jsonl"

    def read_json(self, path: str) -> dict[str, Any]:
        target = Path(path)

        if not target.exists():
            return {
                "ok": False,
                "status": "missing",
                "path": path,
            }

        try:
            data = json.loads(target.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return {
                    "ok": True,
                    "status": data.get("status", "loaded"),
                    "path": path,
                    "data": data,
                }

            return {
                "ok": False,
                "status": "invalid_json_shape",
                "path": path,
            }
        except Exception as exc:
            return {
                "ok": False,
                "status": "read_error",
                "path": path,
                "error": f"{type(exc).__name__}: {exc}",
            }

    def run_git(self, args: list[str]) -> dict[str, Any]:
        try:
            result = subprocess.run(
                args,
                cwd=str(Path.cwd()),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=45,
            )

            return {
                "ok": result.returncode == 0,
                "command": " ".join(args),
                "returncode": result.returncode,
                "stdout": result.stdout[-5000:],
                "stderr": result.stderr[-5000:],
            }
        except Exception as exc:
            return {
                "ok": False,
                "command": " ".join(args),
                "returncode": None,
                "stdout": "",
                "stderr": f"{type(exc).__name__}: {exc}",
            }

    def check_url(self, url: str) -> dict[str, Any]:
        try:
            with urllib.request.urlopen(url, timeout=6) as response:
                return {
                    "ok": 200 <= response.status < 500,
                    "status": "reachable",
                    "http_status": response.status,
                    "url": url,
                }
        except Exception as exc:
            return {
                "ok": False,
                "status": "unreachable",
                "url": url,
                "error": f"{type(exc).__name__}: {exc}",
            }

    def collect(self) -> dict[str, Any]:
        modules = {
            "local_daemon": self.read_json("memory/local_daemon/heartbeat.json"),
            "command_scheduler": self.read_json("memory/command_center_scheduler/scheduler_state.json"),
            "command_center": self.read_json("reports/command_center/latest_command_center_run.json"),
            "mission_planner": self.read_json("reports/mission_planner/latest_mission_plan.json"),
            "mission_executor_bridge": self.read_json("reports/mission_executor_bridge/latest_mission_executor_bridge.json"),
            "social_growth_pack": self.read_json("reports/social_growth_mission_pack/latest_social_growth_mission_pack.json"),
            "saas_product_pack": self.read_json("reports/saas_product_mission_pack/latest_saas_product_mission_pack.json"),
            "autoreporter": self.read_json("reports/autoreporter/k_atlas_central_report.json"),
        }

        git_status = self.run_git(["git", "status", "--short"])
        git_log = self.run_git(["git", "log", "--oneline", "-8"])

        streamlit = self.check_url("http://127.0.0.1:8501/_stcore/health")
        render = self.check_url("https://k-atlas-os.onrender.com")

        healthy_modules = sum(1 for item in modules.values() if item.get("ok"))
        total_modules = len(modules)

        dirty_git = bool(git_status.get("stdout", "").strip())

        if not streamlit.get("ok"):
            next_action = "reiniciar Local Daemon ou Streamlit"
        elif dirty_git:
            next_action = "revisar git status e limpar runtime antes de novo checkpoint"
        elif healthy_modules < total_modules:
            next_action = "rodar demos dos modulos ausentes para popular relatórios"
        else:
            next_action = "seguir para Checkpoint 49 - External API Adapter Readiness"

        report = {
            "ok": True,
            "checkpoint": "48",
            "name": "Daily Operator Cockpit",
            "generated_at": utc_now(),
            "status": "operational",
            "summary": {
                "healthy_modules": healthy_modules,
                "total_modules": total_modules,
                "streamlit": streamlit.get("status"),
                "render": render.get("status"),
                "git_dirty": dirty_git,
                "next_action": next_action,
            },
            "modules": modules,
            "git": {
                "status": git_status,
                "log": git_log,
            },
            "network": {
                "streamlit": streamlit,
                "render": render,
            },
            "guardrails": [
                "cockpit apenas observa e consolida",
                "sem publicacao automatica",
                "sem deploy automatico",
                "sem mensagem em massa",
                "sem API externa real",
                "sem token em texto puro",
            ],
        }

        self.save_report(report)
        return report

    def save_report(self, report: dict[str, Any]) -> None:
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        latest_json = self.reports_dir / "latest_daily_operator_cockpit.json"
        latest_md = self.reports_dir / "latest_daily_operator_cockpit.md"

        latest_json.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )

        latest_md.write_text(self.to_markdown(report), encoding="utf-8")

        event = {
            "timestamp": utc_now(),
            "event_type": "daily_operator.report.generated",
            "payload": {
                "checkpoint": report.get("checkpoint"),
                "status": report.get("status"),
                "next_action": report.get("summary", {}).get("next_action"),
            },
        }

        with self.events_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")

    def to_markdown(self, report: dict[str, Any]) -> str:
        summary = report.get("summary", {})

        lines = [
            "# K-Atlas Daily Operator Cockpit",
            "",
            f"Checkpoint: {report.get('checkpoint')}",
            f"Status: {report.get('status')}",
            f"Generated at: {report.get('generated_at')}",
            "",
            "## Summary",
            "",
            f"- Healthy modules: {summary.get('healthy_modules')}/{summary.get('total_modules')}",
            f"- Streamlit: {summary.get('streamlit')}",
            f"- Render: {summary.get('render')}",
            f"- Git dirty: {summary.get('git_dirty')}",
            f"- Next action: {summary.get('next_action')}",
            "",
            "## Modules",
            "",
        ]

        for name, item in report.get("modules", {}).items():
            lines.append(f"- {name}: {item.get('status')}")

        lines.extend([
            "",
            "## Guardrails",
            "",
        ])

        for item in report.get("guardrails", []):
            lines.append(f"- {item}")

        return "\n".join(lines)
