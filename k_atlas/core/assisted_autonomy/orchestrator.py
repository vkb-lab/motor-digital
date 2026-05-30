from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4

from k_atlas.core.autoreporter.report_builder import AutoReporterCentral
from k_atlas.core.deploy_pipeline.pipeline import DeployPipelineAssistant
from k_atlas.core.sandbox_api_adapter.adapter import SandboxAPIAdapter
from k_atlas.core.sandbox_api_adapter.audit import SandboxAPIAuditLog

from .policy import validate_autonomy_payload


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def path_exists(path: str) -> bool:
    return Path(path).exists()


def run_command(args: list[str], timeout: int = 180) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            args,
            cwd=str(Path.cwd()),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )

        return {
            "ok": completed.returncode == 0,
            "command": " ".join(args),
            "returncode": completed.returncode,
            "stdout": completed.stdout[-6000:],
            "stderr": completed.stderr[-6000:],
        }
    except Exception as exc:
        return {
            "ok": False,
            "command": " ".join(args),
            "returncode": None,
            "stdout": "",
            "stderr": f"{type(exc).__name__}: {exc}",
        }


class AssistedAutonomyOrchestrator:
    def __init__(self, reports_root: str | Path = "reports/assisted_autonomy") -> None:
        self.reports_root = Path(reports_root)

    def run(self, payload: Mapping[str, Any] | None = None, requested_by: str = "human_operator") -> dict[str, Any]:
        run_id = str(uuid4())
        started_at = utc_now_iso()

        data = dict(payload or {
            "mode": "assisted_autonomy_v1",
            "official_publish": False,
            "auto_publish": False,
            "auto_deploy": False,
            "external_api_enabled": False,
            "mass_messaging": False,
            "browser_automation": False,
            "run_deep_checks": True,
        })

        validation = validate_autonomy_payload(data)

        modules = {
            "control_plane": path_exists("k_atlas/core/control_plane"),
            "blackboard": path_exists("k_atlas/core/blackboard"),
            "workflows": path_exists("k_atlas/core/workflows"),
            "supervisor_autopilot": path_exists("k_atlas/core/supervisor_autopilot"),
            "credential_vault": path_exists("k_atlas/core/credential_vault"),
            "sandbox_api_adapter": path_exists("k_atlas/core/sandbox_api_adapter"),
            "autoreporter": path_exists("k_atlas/core/autoreporter"),
            "deploy_pipeline": path_exists("k_atlas/core/deploy_pipeline"),
            "saas_builder": path_exists("k_atlas/saas_factory/builder_agent"),
            "saas_factory_workflow": path_exists("k_atlas/saas_factory/workflows"),
            "creative_media_gateway": path_exists("k_atlas/creative/media_gateway"),
            "social_publishing_gateway": path_exists("k_atlas/social/publishing_gateway"),
            "social_audit": path_exists("k_atlas/social/social_audit"),
        }

        smoke_results: list[dict[str, Any]] = []

        if data.get("run_deep_checks", True):
            smoke_modules = [
                "k_atlas.core.credential_vault.smoke_test_credential_vault",
                "k_atlas.core.sandbox_api_adapter.smoke_test_sandbox_api_adapter",
                "k_atlas.core.autoreporter.smoke_test_autoreporter_central",
                "k_atlas.core.deploy_pipeline.smoke_test_deploy_pipeline",
                "k_atlas.core.supervisor_autopilot.smoke_test_supervisor_autopilot",
                "k_atlas.saas_factory.workflows.smoke_test_saas_factory_workflow",
            ]

            for module in smoke_modules:
                smoke_results.append(run_command([sys.executable, "-m", module], timeout=240))

        reporter_result = AutoReporterCentral(
            output_dir=self.reports_root / "autoreporter"
        ).generate()

        deploy_result = DeployPipelineAssistant(
            reports_root=self.reports_root / "deploy_pipeline"
        ).run_assisted_check({
            "target": "render",
            "service": "k-atlas-os",
            "auto_deploy": False,
            "force_push": False,
            "production_mutation": False,
            "official_publish": False,
        })

        sandbox_result = SandboxAPIAdapter(
            SandboxAPIAuditLog(self.reports_root / "sandbox_api_requests.json")
        ).execute(
            provider_id="google_ai_sandbox",
            operation="plan_video_generation",
            payload={
                "objective": "Validar audiovisual do K-Atlas OS em modo sandbox.",
                "external_api_enabled": False,
                "official_publish": False,
                "auto_publish": False,
                "real_network": False,
            },
            requested_by="assisted_autonomy_v1",
        )

        smoke_ok = all(item["ok"] for item in smoke_results) if smoke_results else True
        modules_ok = len([value for value in modules.values() if value])
        modules_total = len(modules)

        guardrails = [
            "sem publicação oficial automática",
            "sem auto deploy",
            "sem mensagem em massa",
            "sem browser automation para operação oficial",
            "sem API externa sem Credential Vault",
            "sem token em texto puro",
            "execução real continua supervisionada",
        ]

        autonomy_level = "level_3_assisted_autonomy_v1"

        if validation["ok"] and smoke_ok and modules_ok >= 10 and sandbox_result["ok"]:
            status = "validated"
        else:
            status = "needs_review"

        report = {
            "ok": status == "validated",
            "checkpoint": "40",
            "name": "K-Atlas Assisted Autonomy v1",
            "run_id": run_id,
            "started_at": started_at,
            "finished_at": utc_now_iso(),
            "requested_by": requested_by,
            "status": status,
            "autonomy_level": autonomy_level,
            "validation": validation,
            "modules": modules,
            "metrics": {
                "modules_ok": modules_ok,
                "modules_total": modules_total,
                "smoke_tests_total": len(smoke_results),
                "smoke_tests_ok": len([item for item in smoke_results if item["ok"]]),
            },
            "smoke_results": smoke_results,
            "autoreporter": {
                "ok": reporter_result["ok"],
                "json_path": reporter_result["json_path"],
                "md_path": reporter_result["md_path"],
            },
            "deploy_pipeline": deploy_result,
            "sandbox_api": sandbox_result,
            "guardrails": guardrails,
            "side_effects": "reports_and_sandbox_only_no_real_publish_no_auto_deploy",
            "next_cycle": [
                "Conectar Runner local com fila online de forma sincronizada",
                "Criar Creative Media API Adapter real com Credential Vault",
                "Preparar Instagram oficial com API Meta, ainda em rascunho",
                "Criar SaaS deploy assistant por produto",
                "Criar observabilidade 24/7",
            ],
        }

        self._save_report(run_id, report)
        return report

    def _save_report(self, run_id: str, report: dict[str, Any]) -> None:
        self.reports_root.mkdir(parents=True, exist_ok=True)

        latest_json = self.reports_root / "k_atlas_assisted_autonomy_v1.json"
        latest_md = self.reports_root / "k_atlas_assisted_autonomy_v1.md"
        run_json = self.reports_root / f"{run_id}.json"

        latest_json.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )

        run_json.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )

        latest_md.write_text(self._to_markdown(report), encoding="utf-8")

    def _to_markdown(self, report: dict[str, Any]) -> str:
        lines = [
            "# K-Atlas Assisted Autonomy v1",
            "",
            f"Checkpoint: {report['checkpoint']}",
            f"Status: {report['status']}",
            f"Autonomy level: {report['autonomy_level']}",
            f"Generated at: {report['finished_at']}",
            "",
            "## Metrics",
            "",
            f"- Modules OK: {report['metrics']['modules_ok']} / {report['metrics']['modules_total']}",
            f"- Smoke tests OK: {report['metrics']['smoke_tests_ok']} / {report['metrics']['smoke_tests_total']}",
            "",
            "## Guardrails",
            "",
        ]

        for item in report["guardrails"]:
            lines.append(f"- {item}")

        lines.extend([
            "",
            "## Modules",
            "",
        ])

        for key, value in report["modules"].items():
            lines.append(f"- {key}: {value}")

        lines.extend([
            "",
            "## Next cycle",
            "",
        ])

        for item in report["next_cycle"]:
            lines.append(f"- {item}")

        return "\n".join(lines)
