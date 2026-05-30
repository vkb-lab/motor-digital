from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class LocalOSMVPReadiness:
    def __init__(
        self,
        project_root: str | Path = ".",
        reports_dir: str | Path = "reports/local_os_mvp_readiness",
        memory_dir: str | Path = "memory/local_os_mvp_readiness",
    ) -> None:
        self.project_root = Path(project_root)
        self.reports_dir = self.project_root / reports_dir
        self.memory_dir = self.project_root / memory_dir
        self.events_path = self.memory_dir / "events.jsonl"

    def exists(self, path: str) -> bool:
        return (self.project_root / path).exists()

    def event(self, event_type: str, payload: dict[str, Any]) -> None:
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        row = {
            "timestamp": utc_now(),
            "event_type": event_type,
            "payload": payload,
        }
        with self.events_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    def components(self) -> list[dict[str, Any]]:
        return [
            {
                "checkpoint": "73",
                "name": "Local Mission Installer",
                "module": "k_atlas/core/local_mission_installer",
                "page": "pages/73_K_Atlas_Local_Mission_Installer.py",
                "role": "instalar missoes locais com aprovacao humana",
            },
            {
                "checkpoint": "74",
                "name": "Mission Pack Generator",
                "module": "k_atlas/core/mission_pack_generator",
                "page": "pages/74_K_Atlas_Mission_Pack_Generator.py",
                "role": "gerar mission packs declarativos",
            },
            {
                "checkpoint": "75",
                "name": "Mission Pack Bridge",
                "module": "k_atlas/core/mission_pack_bridge",
                "page": "pages/75_K_Atlas_Mission_Pack_Bridge.py",
                "role": "converter mission pack em missao local",
            },
            {
                "checkpoint": "76",
                "name": "Mission Pipeline Runner",
                "module": "k_atlas/core/mission_pipeline_runner",
                "page": "pages/76_K_Atlas_Mission_Pipeline_Runner.py",
                "role": "orquestrar geracao, bridge e instalacao",
            },
            {
                "checkpoint": "77",
                "name": "Local Control Plane",
                "module": "k_atlas/core/local_control_plane",
                "page": "pages/77_K_Atlas_Local_Control_Plane.py",
                "role": "control plane do Local OS",
            },
            {
                "checkpoint": "78",
                "name": "Remote Assist Readiness",
                "module": "k_atlas/core/remote_assist_readiness",
                "page": "pages/78_K_Atlas_Remote_Assist_Readiness.py",
                "role": "preparacao segura para rede/remoto",
            },
            {
                "checkpoint": "79",
                "name": "Secure Local API Readiness",
                "module": "k_atlas/core/secure_local_api_readiness",
                "page": "pages/79_K_Atlas_Secure_Local_API_Readiness.py",
                "role": "readiness da API local segura",
            },
            {
                "checkpoint": "80",
                "name": "Operator Approval Console",
                "module": "k_atlas/core/operator_approval_console",
                "page": "pages/80_K_Atlas_Operator_Approval_Console.py",
                "role": "console de aprovacao humana",
            },
            {
                "checkpoint": "81",
                "name": "LAN Cockpit Access",
                "module": "k_atlas/core/lan_cockpit_access",
                "page": "pages/81_K_Atlas_LAN_Cockpit_Access.py",
                "role": "preparacao de acesso LAN",
            },
            {
                "checkpoint": "82",
                "name": "Remote Tunnel Gate",
                "module": "k_atlas/core/remote_tunnel_gate",
                "page": "pages/82_K_Atlas_Remote_Tunnel_Gate.py",
                "role": "gate para tunel remoto aprovado",
            },
            {
                "checkpoint": "83",
                "name": "Local OS Shell",
                "module": "k_atlas/core/local_os_shell",
                "page": "pages/83_K_Atlas_Local_OS_Shell.py",
                "role": "shell visual do Local OS",
            },
            {
                "checkpoint": "84",
                "name": "Local Action Contract Registry",
                "module": "k_atlas/core/local_action_contracts",
                "page": "pages/84_K_Atlas_Local_Action_Contracts.py",
                "role": "contratos de acao local",
            },
            {
                "checkpoint": "85",
                "name": "Local Action Router",
                "module": "k_atlas/core/local_action_router",
                "page": "pages/85_K_Atlas_Local_Action_Router.py",
                "role": "roteamento de acoes locais assistidas",
            },
            {
                "checkpoint": "86",
                "name": "Local Execution Queue",
                "module": "k_atlas/core/local_execution_queue",
                "page": "pages/86_K_Atlas_Local_Execution_Queue.py",
                "role": "fila local de execucao supervisionada",
            },
            {
                "checkpoint": "87",
                "name": "Local Action Audit Ledger",
                "module": "k_atlas/core/local_action_audit_ledger",
                "page": "pages/87_K_Atlas_Local_Action_Audit_Ledger.py",
                "role": "ledger de auditoria de acoes",
            },
            {
                "checkpoint": "88",
                "name": "Assisted Execution Dashboard",
                "module": "k_atlas/core/assisted_execution_dashboard",
                "page": "pages/88_K_Atlas_Assisted_Execution_Dashboard.py",
                "role": "dashboard de execucao assistida",
            },
            {
                "checkpoint": "89",
                "name": "Secure Local API Runtime",
                "module": "k_atlas/core/secure_local_api_runtime",
                "page": "pages/89_K_Atlas_Secure_Local_API_Runtime.py",
                "role": "runtime local seguro da API",
            },
            {
                "checkpoint": "90",
                "name": "Local API Auth Policy",
                "module": "k_atlas/core/local_api_auth_policy",
                "page": "pages/90_K_Atlas_Local_API_Auth_Policy.py",
                "role": "politica de autenticacao da API local",
            },
            {
                "checkpoint": "91",
                "name": "API Approval Bridge",
                "module": "k_atlas/core/api_approval_bridge",
                "page": "pages/91_K_Atlas_API_Approval_Bridge.py",
                "role": "ponte entre API e aprovacao humana",
            },
            {
                "checkpoint": "92",
                "name": "API Audit Ledger",
                "module": "k_atlas/core/api_audit_ledger",
                "page": "pages/92_K_Atlas_API_Audit_Ledger.py",
                "role": "ledger de auditoria da API",
            },
            {
                "checkpoint": "93",
                "name": "Secure Local API Dashboard",
                "module": "k_atlas/core/secure_local_api_dashboard",
                "page": "pages/93_K_Atlas_Secure_Local_API_Dashboard.py",
                "role": "dashboard da API local segura",
            },
            {
                "checkpoint": "94",
                "name": "Autonomy Policy Engine",
                "module": "k_atlas/core/autonomy_policy_engine",
                "page": "pages/94_K_Atlas_Autonomy_Policy_Engine.py",
                "role": "politica de autonomia supervisionada",
            },
            {
                "checkpoint": "95",
                "name": "Safe Task Planner",
                "module": "k_atlas/core/safe_task_planner",
                "page": "pages/95_K_Atlas_Safe_Task_Planner.py",
                "role": "planejamento seguro de tarefas",
            },
            {
                "checkpoint": "96",
                "name": "Supervised Autonomy Queue",
                "module": "k_atlas/core/supervised_autonomy_queue",
                "page": "pages/96_K_Atlas_Supervised_Autonomy_Queue.py",
                "role": "fila de autonomia supervisionada",
            },
            {
                "checkpoint": "97",
                "name": "Autonomy Audit Monitor",
                "module": "k_atlas/core/autonomy_audit_monitor",
                "page": "pages/97_K_Atlas_Autonomy_Audit_Monitor.py",
                "role": "monitor de auditoria de autonomia",
            },
            {
                "checkpoint": "98",
                "name": "Supervised Autonomy Dashboard",
                "module": "k_atlas/core/supervised_autonomy_dashboard",
                "page": "pages/98_K_Atlas_Supervised_Autonomy_Dashboard.py",
                "role": "dashboard de autonomia supervisionada",
            },
        ]

    def build_report(self) -> dict[str, Any]:
        rows: list[dict[str, Any]] = []

        for item in self.components():
            module_exists = self.exists(item["module"])
            page_exists = self.exists(item["page"])
            rows.append({
                **item,
                "module_exists": module_exists,
                "page_exists": page_exists,
                "status": "operational" if module_exists and page_exists else "incomplete",
            })

        operational = len([item for item in rows if item["status"] == "operational"])
        total = len(rows)
        score = round((operational / total) * 100, 2) if total else 0

        report = {
            "ok": operational == total,
            "checkpoint": "99",
            "name": "K-Atlas Local OS MVP Readiness",
            "generated_at": utc_now(),
            "status": "mvp_ready" if operational == total else "mvp_partial",
            "summary": {
                "components_total": total,
                "components_operational": operational,
                "readiness_score": score,
                "local_os_ready": operational == total,
                "execution_enabled": False,
                "real_execution_enabled": False,
                "external_side_effects": "local_files_only",
                "next_checkpoint": "100 - K-Atlas Local OS Release Capsule",
            },
            "components": rows,
            "guardrails": [
                "readiness nao executa acao real",
                "readiness nao abre porta publica",
                "readiness nao controla mouse",
                "readiness nao chama API externa",
                "readiness apenas observa arquivos locais",
            ],
        }

        self.save_report(report)
        self.event("local_os_mvp_readiness.report_built", report["summary"])
        return report

    def save_report(self, report: dict[str, Any]) -> None:
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        (self.reports_dir / "latest_local_os_mvp_readiness.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        (self.reports_dir / "latest_local_os_mvp_readiness.md").write_text(
            self.to_markdown(report),
            encoding="utf-8",
        )

    def to_markdown(self, report: dict[str, Any]) -> str:
        summary = report.get("summary", {})
        lines = [
            "# K-Atlas Local OS MVP Readiness",
            "",
            f"Checkpoint: {report.get('checkpoint')}",
            f"Status: {report.get('status')}",
            "",
            "## Summary",
            "",
            f"- Components total: {summary.get('components_total')}",
            f"- Components operational: {summary.get('components_operational')}",
            f"- Readiness score: {summary.get('readiness_score')}",
            f"- Local OS ready: {summary.get('local_os_ready')}",
            f"- Execution enabled: {summary.get('execution_enabled')}",
            "",
            "## Components",
            "",
        ]

        for item in report.get("components", []):
            lines.append(f"- {item.get('checkpoint')} - {item.get('name')} - {item.get('status')}")

        lines.extend(["", "## Guardrails", ""])
        for item in report.get("guardrails", []):
            lines.append(f"- {item}")

        return "\n".join(lines)
