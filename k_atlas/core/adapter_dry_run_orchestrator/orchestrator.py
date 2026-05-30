from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4

from k_atlas.core.live_adapter_contract_registry.registry import LiveAdapterContractRegistry

from .policy import validate_adapter_dry_run_payload


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class AdapterDryRunOrchestrator:
    def __init__(
        self,
        reports_dir: str | Path = "reports/adapter_dry_run_orchestrator",
        memory_dir: str | Path = "memory/adapter_dry_run_orchestrator",
        registry: LiveAdapterContractRegistry | None = None,
    ) -> None:
        self.reports_dir = Path(reports_dir)
        self.memory_dir = Path(memory_dir)
        self.events_path = self.memory_dir / "events.jsonl"
        self.registry = registry or LiveAdapterContractRegistry()

    def default_payload(self) -> dict[str, Any]:
        return {
            "scope": "all",
            "objective": "validar contratos de adapters reais em modo seco sem efeitos externos",
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

    def load_registry(self) -> dict[str, Any]:
        return self.registry.load_latest()

    def match_scope(self, contract: Mapping[str, Any], scope: str) -> bool:
        if scope == "all":
            return True

        adapter_id = str(contract.get("adapter_id", ""))
        provider = str(contract.get("provider", ""))

        if scope in adapter_id:
            return True

        if scope in provider:
            return True

        if scope == "google" and provider in {"google_ai", "google_vertex"}:
            return True

        if scope == "meta" and provider == "meta":
            return True

        return False

    def build_dry_run_steps(self, contract: Mapping[str, Any]) -> list[dict[str, Any]]:
        return [
            {
                "step": "contract_loaded",
                "ok": True,
                "detail": "Contrato carregado do registry.",
            },
            {
                "step": "adapter_disabled_check",
                "ok": contract.get("enabled") is False,
                "detail": "Adapter deve permanecer desabilitado nesta fase.",
            },
            {
                "step": "approval_gate_check",
                "ok": contract.get("requires_approval_gate") is True and contract.get("requires_human_approval") is True,
                "detail": "Approval Gate humano obrigatorio.",
            },
            {
                "step": "real_execution_check",
                "ok": contract.get("real_execution_enabled") is False and contract.get("live_call") is False,
                "detail": "Execucao real e live call devem estar bloqueados.",
            },
            {
                "step": "env_names_only_check",
                "ok": all(isinstance(item, str) and "=" not in item for item in contract.get("env_vars", [])),
                "detail": "Somente nomes de variaveis de ambiente, sem valores.",
            },
            {
                "step": "side_effect_check",
                "ok": True,
                "detail": "Dry run nao gera efeito externo.",
            },
        ]

    def dry_run_contract(self, registry_row: Mapping[str, Any]) -> dict[str, Any]:
        dry_run_id = str(uuid4())
        contract = dict(registry_row.get("contract", {}))
        validation = dict(registry_row.get("validation", {}))
        env_status = list(registry_row.get("env_status", []))
        steps = self.build_dry_run_steps(contract)

        passed = bool(validation.get("ok")) and all(step.get("ok") for step in steps)

        return {
            "dry_run_id": dry_run_id,
            "adapter_id": contract.get("adapter_id"),
            "provider": contract.get("provider"),
            "risk_level": contract.get("risk_level"),
            "status": "dry_run_passed" if passed else "dry_run_failed",
            "ok": passed,
            "validation": validation,
            "env_status": env_status,
            "steps": steps,
            "planned_future_actions": contract.get("allowed_actions_future", []),
            "execution_enabled": False,
            "real_execution_enabled": False,
            "live_call_enabled": False,
            "external_side_effects": "none",
        }

    def run(self, payload: Mapping[str, Any] | None = None) -> dict[str, Any]:
        run_id = str(uuid4())
        data = dict(payload or self.default_payload())
        validation = validate_adapter_dry_run_payload(data)

        if not validation["ok"]:
            report = {
                "ok": False,
                "checkpoint": "57",
                "name": "Adapter Dry Run Orchestrator",
                "run_id": run_id,
                "generated_at": utc_now(),
                "status": "blocked_by_policy",
                "payload": data,
                "validation": validation,
                "external_side_effects": "none",
            }
            self.save_report(report)
            return report

        registry_report = self.load_registry()
        scope = data.get("scope", "all")

        candidates = []
        for row in registry_report.get("contracts", []):
            contract = row.get("contract", {})
            if self.match_scope(contract, scope):
                candidates.append(row)

        dry_runs = [self.dry_run_contract(row) for row in candidates]
        passed = sum(1 for item in dry_runs if item.get("ok"))
        failed = len(dry_runs) - passed

        report = {
            "ok": failed == 0,
            "checkpoint": "57",
            "name": "Adapter Dry Run Orchestrator",
            "run_id": run_id,
            "generated_at": utc_now(),
            "status": "dry_run_completed" if failed == 0 else "dry_run_needs_review",
            "payload": data,
            "validation": validation,
            "summary": {
                "scope": scope,
                "registry_status": registry_report.get("status"),
                "contracts_checked": len(dry_runs),
                "dry_run_passed": passed,
                "dry_run_failed": failed,
                "execution_enabled": False,
                "real_execution_enabled": False,
                "external_side_effects": "none",
                "next_action": "corrigir contratos com falha ou seguir para Service Readiness Matrix",
            },
            "registry_snapshot": {
                "checkpoint": registry_report.get("checkpoint"),
                "status": registry_report.get("status"),
                "contracts_total": registry_report.get("summary", {}).get("contracts_total"),
            },
            "dry_runs": dry_runs,
            "guardrails": [
                "dry run nao chama API externa",
                "dry run nao publica",
                "dry run nao envia WhatsApp",
                "dry run nao faz deploy",
                "dry run nao cria release",
                "dry run nao usa token",
                "execucao real continua bloqueada",
            ],
            "next_checkpoint": "58 - Service Readiness Matrix",
        }

        self.save_report(report)

        self.event("adapter_dry_run.completed", {
            "run_id": run_id,
            "status": report["status"],
            "contracts_checked": len(dry_runs),
            "failed": failed,
        })

        return report

    def save_report(self, report: dict[str, Any]) -> None:
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        latest_json = self.reports_dir / "latest_adapter_dry_run_orchestrator.json"
        latest_md = self.reports_dir / "latest_adapter_dry_run_orchestrator.md"
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
            "# K-Atlas Adapter Dry Run Orchestrator",
            "",
            f"Checkpoint: {report.get('checkpoint')}",
            f"Status: {report.get('status')}",
            "",
            "## Summary",
            "",
            f"- Scope: {summary.get('scope')}",
            f"- Contracts checked: {summary.get('contracts_checked')}",
            f"- Dry run passed: {summary.get('dry_run_passed')}",
            f"- Dry run failed: {summary.get('dry_run_failed')}",
            f"- Execution enabled: {summary.get('execution_enabled')}",
            f"- External side effects: {summary.get('external_side_effects')}",
            "",
            "## Dry runs",
            "",
        ]

        for item in report.get("dry_runs", []):
            lines.append(f"- {item.get('adapter_id')} | {item.get('provider')} | {item.get('status')}")

        lines.extend([
            "",
            "## Guardrails",
            "",
        ])

        for guardrail in report.get("guardrails", []):
            lines.append(f"- {guardrail}")

        return "\n".join(lines)
