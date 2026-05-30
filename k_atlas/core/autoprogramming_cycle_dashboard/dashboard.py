from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class AutoprogrammingCycleDashboard:
    def __init__(
        self,
        project_root: str | Path = ".",
        reports_dir: str | Path = "reports/autoprogramming_cycle_dashboard",
        memory_dir: str | Path = "memory/autoprogramming_cycle_dashboard",
    ) -> None:
        self.project_root = Path(project_root)
        self.reports_dir = self.project_root / reports_dir
        self.memory_dir = self.project_root / memory_dir
        self.events_path = self.memory_dir / "events.jsonl"

    def exists(self, path: str) -> bool:
        return (self.project_root / path).exists()

    def load_json(self, path: str) -> Any:
        target = self.project_root / path
        if not target.exists():
            return None
        try:
            return json.loads(target.read_text(encoding="utf-8"))
        except Exception:
            return None

    def count_json_list(self, path: str) -> int:
        data = self.load_json(path)
        return len(data) if isinstance(data, list) else 0

    def event(self, event_type: str, payload: dict[str, Any]) -> None:
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        row = {
            "timestamp": utc_now(),
            "event_type": event_type,
            "payload": payload,
        }
        with self.events_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    def build_checkpoint_rows(self) -> list[dict[str, Any]]:
        rows = [
            {
                "checkpoint": "65",
                "name": "Assisted Autoprogramming Kernel",
                "module": "k_atlas/core/assisted_autoprogramming",
                "page": None,
                "readme": None,
                "role": "propor mudancas",
            },
            {
                "checkpoint": "66",
                "name": "Autoprogramming Proposal Reviewer",
                "module": "k_atlas/core/autoprogramming_proposal_reviewer",
                "page": None,
                "readme": None,
                "role": "revisar propostas",
            },
            {
                "checkpoint": "67",
                "name": "Autoprogramming Apply Package Builder",
                "module": "k_atlas/core/autoprogramming_apply_package_builder",
                "page": None,
                "readme": None,
                "role": "empacotar aplicacao",
            },
            {
                "checkpoint": "68",
                "name": "Autoprogramming Apply Package Gate",
                "module": "k_atlas/core/autoprogramming_apply_package_gate",
                "page": "pages/68_K_Atlas_Autoprogramming_Apply_Package_Gate.py",
                "readme": "README_AUTOPROGRAMMING_APPLY_PACKAGE_GATE.md",
                "role": "validar pacote",
            },
            {
                "checkpoint": "69",
                "name": "Manual Apply Executor",
                "module": "k_atlas/core/manual_apply_executor",
                "page": "pages/69_K_Atlas_Manual_Apply_Executor.py",
                "readme": "README_MANUAL_APPLY_EXECUTOR.md",
                "role": "aplicar manualmente",
            },
            {
                "checkpoint": "70",
                "name": "Manual Apply Rollback Executor",
                "module": "k_atlas/core/manual_apply_rollback_executor",
                "page": "pages/70_K_Atlas_Manual_Apply_Rollback_Executor.py",
                "readme": "README_MANUAL_APPLY_ROLLBACK_EXECUTOR.md",
                "role": "reverter manualmente",
            },
        ]

        final_rows: list[dict[str, Any]] = []

        for row in rows:
            module_exists = self.exists(row["module"])
            page_exists = True if row["page"] is None else self.exists(row["page"])
            readme_exists = True if row["readme"] is None else self.exists(row["readme"])

            final_rows.append({
                **row,
                "module_exists": module_exists,
                "page_exists": page_exists,
                "readme_exists": readme_exists,
                "status": "operational" if module_exists and page_exists and readme_exists else "incomplete",
            })

        return final_rows

    def build_queue_summary(self) -> dict[str, Any]:
        return {
            "review_queue": self.count_json_list("live/autoprogramming_proposal_reviewer/review_queue.json"),
            "apply_package_queue": self.count_json_list("live/autoprogramming_apply_package_builder/apply_package_queue.json"),
            "apply_package_gate_queue": self.count_json_list("live/autoprogramming_apply_package_gate/apply_package_gate_queue.json"),
            "manual_apply_manifest": self.count_json_list("memory/manual_apply_executor/apply_manifest.json"),
            "manual_rollback_manifest": self.count_json_list("memory/manual_apply_rollback_executor/rollback_manifest.json"),
        }

    def build_cowork_summary(self) -> dict[str, Any]:
        return {
            "milestone_report_exists": self.exists("reports/cowork_pilot_studio/milestone_cycle_65_70.md"),
            "recording_index_exists": self.exists("reports/cowork_pilot_studio/cowork_session_65_70_index.md"),
            "latest_recording_report_exists": self.exists("reports/cowork_pilot_studio/latest_recording.json"),
        }

    def build_report(self) -> dict[str, Any]:
        checkpoints = self.build_checkpoint_rows()
        queue_summary = self.build_queue_summary()
        cowork_summary = self.build_cowork_summary()

        operational = len([item for item in checkpoints if item["status"] == "operational"])

        report = {
            "ok": operational == len(checkpoints),
            "checkpoint": "71",
            "name": "Autoprogramming Cycle Dashboard",
            "generated_at": utc_now(),
            "status": "operational" if operational == len(checkpoints) else "partial",
            "summary": {
                "checkpoints_total": len(checkpoints),
                "checkpoints_operational": operational,
                "cycle_ready": operational == len(checkpoints),
                "execution_enabled": False,
                "external_side_effects": "local_files_only",
                "cycle": "propose -> review -> package -> gate -> manual_apply -> manual_rollback",
                "next_checkpoint": "72 - Autoprogramming Cycle Controller",
            },
            "checkpoints": checkpoints,
            "queues": queue_summary,
            "cowork": cowork_summary,
            "guardrails": [
                "dashboard nao aplica arquivos",
                "dashboard nao executa rollback",
                "dashboard nao chama API externa",
                "dashboard nao publica",
                "dashboard nao envia mensagens",
                "dashboard apenas observa estado local",
            ],
        }

        self.save_report(report)
        self.event("autoprogramming_cycle_dashboard.report_built", {
            "status": report["status"],
            "checkpoints_operational": operational,
        })

        return report

    def save_report(self, report: dict[str, Any]) -> None:
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        json_path = self.reports_dir / "latest_autoprogramming_cycle_dashboard.json"
        md_path = self.reports_dir / "latest_autoprogramming_cycle_dashboard.md"

        json_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )

        md_path.write_text(self.to_markdown(report), encoding="utf-8")

    def to_markdown(self, report: dict[str, Any]) -> str:
        summary = report.get("summary", {})
        lines = [
            "# K-Atlas Autoprogramming Cycle Dashboard",
            "",
            f"Checkpoint: {report.get('checkpoint')}",
            f"Status: {report.get('status')}",
            "",
            "## Summary",
            "",
            f"- Checkpoints total: {summary.get('checkpoints_total')}",
            f"- Checkpoints operational: {summary.get('checkpoints_operational')}",
            f"- Cycle ready: {summary.get('cycle_ready')}",
            f"- Cycle: {summary.get('cycle')}",
            f"- Next checkpoint: {summary.get('next_checkpoint')}",
            "",
            "## Checkpoints",
            "",
        ]

        for item in report.get("checkpoints", []):
            lines.append(f"- {item.get('checkpoint')} - {item.get('name')} - {item.get('status')}")

        lines.extend([
            "",
            "## Guardrails",
            "",
        ])

        for item in report.get("guardrails", []):
            lines.append(f"- {item}")

        return "\n".join(lines)
