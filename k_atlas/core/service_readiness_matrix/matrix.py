from __future__ import annotations

import json
import subprocess
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4

from .policy import validate_service_readiness_payload


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ServiceReadinessMatrix:
    def __init__(
        self,
        base_dir: str | Path = ".",
        reports_dir: str | Path = "reports/service_readiness_matrix",
        memory_dir: str | Path = "memory/service_readiness_matrix",
    ) -> None:
        self.base_dir = Path(base_dir)
        self.reports_dir = self.base_dir / reports_dir
        self.memory_dir = self.base_dir / memory_dir
        self.events_path = self.memory_dir / "events.jsonl"

    def default_payload(self) -> dict[str, Any]:
        return {
            "scope": "all",
            "objective": "consolidar prontidao dos servicos K-Atlas para operacao supervisionada",
            "live_call": False,
            "real_execute": False,
            "auto_publish": False,
            "auto_send": False,
            "auto_deploy": False,
            "mass_messaging": False,
            "browser_automation": False,
            "bypass_human_approval": False,
        }

    def event(self, event_type: str, payload: dict[str, Any]) -> None:
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        row = {
            "timestamp": utc_now(),
            "event_type": event_type,
            "payload": payload,
        }

        with self.events_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    def read_json(self, relative_path: str) -> dict[str, Any]:
        path = self.base_dir / relative_path

        if not path.exists():
            return {
                "ok": False,
                "status": "missing",
                "path": relative_path,
                "data": {},
            }

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                return {
                    "ok": False,
                    "status": "invalid_json_shape",
                    "path": relative_path,
                    "data": {},
                }

            return {
                "ok": True,
                "status": data.get("status", "loaded"),
                "path": relative_path,
                "data": data,
            }
        except Exception as exc:
            return {
                "ok": False,
                "status": "read_error",
                "path": relative_path,
                "error": f"{type(exc).__name__}: {exc}",
                "data": {},
            }

    def check_url(self, url: str) -> dict[str, Any]:
        try:
            with urllib.request.urlopen(url, timeout=5) as response:
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

    def run_git(self, args: list[str]) -> dict[str, Any]:
        try:
            result = subprocess.run(
                args,
                cwd=str(self.base_dir),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=30,
            )

            return {
                "ok": result.returncode == 0,
                "command": " ".join(args),
                "returncode": result.returncode,
                "stdout": result.stdout[-4000:],
                "stderr": result.stderr[-4000:],
            }
        except Exception as exc:
            return {
                "ok": False,
                "command": " ".join(args),
                "returncode": None,
                "stdout": "",
                "stderr": f"{type(exc).__name__}: {exc}",
            }

    def service_catalog(self) -> list[dict[str, Any]]:
        return [
            {
                "service": "local_daemon",
                "layer": "core",
                "risk": "medium",
                "required": True,
                "report_path": "memory/local_daemon/heartbeat.json",
            },
            {
                "service": "command_center",
                "layer": "core",
                "risk": "medium",
                "required": True,
                "report_path": "reports/command_center/latest_command_center_run.json",
            },
            {
                "service": "mission_planner",
                "layer": "core",
                "risk": "medium",
                "required": True,
                "report_path": "reports/mission_planner/latest_mission_plan.json",
            },
            {
                "service": "daily_operator",
                "layer": "ops",
                "risk": "low",
                "required": True,
                "report_path": "reports/daily_operator/latest_daily_operator_cockpit.json",
            },
            {
                "service": "external_api_adapter",
                "layer": "external",
                "risk": "high",
                "required": True,
                "report_path": "reports/external_api_adapter/latest_external_api_adapter_readiness.json",
            },
            {
                "service": "ai_provider_router",
                "layer": "external",
                "risk": "medium",
                "required": True,
                "report_path": "reports/ai_provider_router/latest_ai_provider_router.json",
            },
            {
                "service": "google_audiovisual_sandbox",
                "layer": "creative",
                "risk": "medium",
                "required": False,
                "report_path": "reports/google_audiovisual_adapter/latest_google_audiovisual_adapter_sandbox.json",
            },
            {
                "service": "instagram_graph_readiness",
                "layer": "social",
                "risk": "high",
                "required": True,
                "report_path": "reports/instagram_graph_readiness/latest_instagram_graph_readiness.json",
            },
            {
                "service": "whatsapp_cloud_readiness",
                "layer": "social",
                "risk": "high",
                "required": True,
                "report_path": "reports/whatsapp_cloud_readiness/latest_whatsapp_cloud_readiness.json",
            },
            {
                "service": "secure_publish_approval_gate",
                "layer": "external",
                "risk": "critical",
                "required": True,
                "report_path": "reports/publish_approval_gate/latest_publish_approval_gate.json",
            },
            {
                "service": "external_action_stub",
                "layer": "external",
                "risk": "high",
                "required": True,
                "report_path": "reports/external_action_stub/latest_external_action_stub.json",
            },
            {
                "service": "live_adapter_contract_registry",
                "layer": "external",
                "risk": "high",
                "required": True,
                "report_path": "reports/live_adapter_contract_registry/latest_live_adapter_contract_registry.json",
            },
            {
                "service": "adapter_dry_run_orchestrator",
                "layer": "external",
                "risk": "high",
                "required": True,
                "report_path": "reports/adapter_dry_run_orchestrator/latest_adapter_dry_run_orchestrator.json",
            },
            {
                "service": "saas_product_mission_pack",
                "layer": "saas",
                "risk": "medium",
                "required": False,
                "report_path": "reports/saas_product_mission_pack/latest_saas_product_mission_pack.json",
            },
            {
                "service": "social_growth_mission_pack",
                "layer": "social",
                "risk": "medium",
                "required": False,
                "report_path": "reports/social_growth_mission_pack/latest_social_growth_mission_pack.json",
            },
        ]

    def scope_match(self, item: Mapping[str, Any], scope: str) -> bool:
        if scope == "all":
            return True
        return item.get("layer") == scope

    def classify_service(self, item: Mapping[str, Any]) -> dict[str, Any]:
        loaded = self.read_json(str(item["report_path"]))
        data = loaded.get("data", {})

        ok = bool(loaded.get("ok"))

        live_flags = {
            "live_call_enabled": data.get("live_call_enabled"),
            "real_execution_enabled": data.get("real_execution_enabled"),
            "execution_enabled": data.get("execution_enabled"),
            "message_send_enabled": data.get("summary", {}).get("message_send_enabled"),
            "publishing_enabled": data.get("summary", {}).get("publishing_enabled"),
            "auto_deploy": data.get("auto_deploy"),
        }

        unsafe_flags = [
            name for name, value in live_flags.items()
            if value is True
        ]

        if unsafe_flags:
            readiness = "blocked_unsafe_flag"
            score = 0
        elif ok:
            readiness = "ready_supervised"
            score = 100
        elif item.get("required"):
            readiness = "missing_required_report"
            score = 35
        else:
            readiness = "optional_missing"
            score = 70

        blockers = []

        if not ok and item.get("required"):
            blockers.append("required_report_missing")

        if unsafe_flags:
            blockers.extend(unsafe_flags)

        return {
            "service": item.get("service"),
            "layer": item.get("layer"),
            "risk": item.get("risk"),
            "required": item.get("required"),
            "report_path": item.get("report_path"),
            "report_status": loaded.get("status"),
            "ok": ok and not unsafe_flags,
            "readiness": readiness,
            "score": score,
            "blockers": blockers,
            "loaded": loaded,
            "unsafe_flags": unsafe_flags,
            "external_side_effects": "none",
        }

    def build_layer_summary(self, rows: list[dict[str, Any]]) -> dict[str, Any]:
        layers: dict[str, dict[str, Any]] = {}

        for row in rows:
            layer = str(row.get("layer", "unknown"))

            if layer not in layers:
                layers[layer] = {
                    "total": 0,
                    "ready": 0,
                    "blocked": 0,
                    "missing_required": 0,
                    "avg_score": 0,
                    "scores": [],
                }

            layers[layer]["total"] += 1
            layers[layer]["scores"].append(row.get("score", 0))

            if row.get("ok"):
                layers[layer]["ready"] += 1

            if row.get("readiness") == "blocked_unsafe_flag":
                layers[layer]["blocked"] += 1

            if row.get("readiness") == "missing_required_report":
                layers[layer]["missing_required"] += 1

        for layer in layers.values():
            scores = layer.pop("scores", [])
            layer["avg_score"] = round(sum(scores) / len(scores), 2) if scores else 0

        return layers

    def build_recommendation(self, rows: list[dict[str, Any]], git_status: dict[str, Any], streamlit: dict[str, Any]) -> str:
        unsafe = [row for row in rows if row.get("readiness") == "blocked_unsafe_flag"]
        missing_required = [row for row in rows if row.get("readiness") == "missing_required_report"]
        git_dirty = bool(git_status.get("stdout", "").strip())

        if unsafe:
            return "bloquear avanço e corrigir flags inseguras antes de qualquer próximo checkpoint"

        if not streamlit.get("ok"):
            return "reiniciar Streamlit ou Local Daemon antes de operar pelo cockpit"

        if missing_required:
            return "rodar os demos dos módulos obrigatórios ausentes para popular relatórios"

        if git_dirty:
            return "revisar git status; existe alteração local fora do checkpoint atual"

        return "seguir para Checkpoint 59 - Operator Mission Queue"

    def generate(self, payload: Mapping[str, Any] | None = None) -> dict[str, Any]:
        run_id = str(uuid4())
        data = dict(payload or self.default_payload())
        validation = validate_service_readiness_payload(data)

        if not validation["ok"]:
            report = {
                "ok": False,
                "checkpoint": "58",
                "name": "Service Readiness Matrix",
                "run_id": run_id,
                "generated_at": utc_now(),
                "status": "blocked_by_policy",
                "payload": data,
                "validation": validation,
                "external_side_effects": "none",
            }
            self.save_report(report)
            return report

        scope = str(data.get("scope", "all"))
        catalog = [item for item in self.service_catalog() if self.scope_match(item, scope)]
        rows = [self.classify_service(item) for item in catalog]

        total = len(rows)
        ready = sum(1 for row in rows if row.get("ok"))
        blocked = sum(1 for row in rows if row.get("readiness") == "blocked_unsafe_flag")
        missing_required = sum(1 for row in rows if row.get("readiness") == "missing_required_report")
        avg_score = round(sum(row.get("score", 0) for row in rows) / total, 2) if total else 0

        git_status = self.run_git(["git", "status", "--short"])
        git_log = self.run_git(["git", "log", "--oneline", "-8"])
        streamlit = self.check_url("http://127.0.0.1:8501/_stcore/health")

        report = {
            "ok": blocked == 0,
            "checkpoint": "58",
            "name": "Service Readiness Matrix",
            "run_id": run_id,
            "generated_at": utc_now(),
            "status": "ready_supervised" if blocked == 0 else "blocked",
            "payload": data,
            "validation": validation,
            "summary": {
                "scope": scope,
                "services_total": total,
                "services_ready": ready,
                "services_blocked": blocked,
                "required_reports_missing": missing_required,
                "avg_score": avg_score,
                "streamlit_status": streamlit.get("status"),
                "git_dirty": bool(git_status.get("stdout", "").strip()),
                "external_side_effects": "none",
                "next_action": self.build_recommendation(rows, git_status, streamlit),
            },
            "layers": self.build_layer_summary(rows),
            "services": rows,
            "git": {
                "status": git_status,
                "log": git_log,
            },
            "network": {
                "streamlit": streamlit,
            },
            "guardrails": [
                "matriz apenas observa e consolida",
                "sem chamada externa real",
                "sem publicação automática",
                "sem envio automático",
                "sem deploy automático",
                "sem automação de navegador",
                "sem token em arquivo",
            ],
            "next_checkpoint": "59 - Operator Mission Queue",
        }

        self.save_report(report)

        self.event("service_readiness_matrix.generated", {
            "run_id": run_id,
            "status": report.get("status"),
            "services_total": total,
            "services_blocked": blocked,
            "missing_required": missing_required,
        })

        return report

    def save_report(self, report: dict[str, Any]) -> None:
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        latest_json = self.reports_dir / "latest_service_readiness_matrix.json"
        latest_md = self.reports_dir / "latest_service_readiness_matrix.md"
        run_json = self.reports_dir / f"{report.get('run_id', 'unknown')}.json"

        latest_json.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        run_json.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        latest_md.write_text(self.to_markdown(report), encoding="utf-8")

    def to_markdown(self, report: dict[str, Any]) -> str:
        summary = report.get("summary", {})

        lines = [
            "# K-Atlas Service Readiness Matrix",
            "",
            f"Checkpoint: {report.get('checkpoint')}",
            f"Status: {report.get('status')}",
            "",
            "## Summary",
            "",
            f"- Scope: {summary.get('scope')}",
            f"- Services total: {summary.get('services_total')}",
            f"- Services ready: {summary.get('services_ready')}",
            f"- Services blocked: {summary.get('services_blocked')}",
            f"- Required reports missing: {summary.get('required_reports_missing')}",
            f"- Avg score: {summary.get('avg_score')}",
            f"- Next action: {summary.get('next_action')}",
            "",
            "## Services",
            "",
        ]

        for row in report.get("services", []):
            lines.append(f"- {row.get('service')} | {row.get('layer')} | {row.get('risk')} | {row.get('readiness')} | score {row.get('score')}")

        lines.extend([
            "",
            "## Guardrails",
            "",
        ])

        for item in report.get("guardrails", []):
            lines.append(f"- {item}")

        return "\n".join(lines)
