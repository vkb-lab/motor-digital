from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4

from .policy import validate_autoprog_request, validate_file_plan


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class AssistedAutoprogrammingKernel:
    def __init__(
        self,
        memory_dir: str | Path = "memory/assisted_autoprogramming",
        reports_dir: str | Path = "reports/assisted_autoprogramming",
        package_dir: str | Path = "live/assisted_autoprogramming",
    ) -> None:
        self.memory_dir = Path(memory_dir)
        self.reports_dir = Path(reports_dir)
        self.package_dir = Path(package_dir)

        self.events_path = self.memory_dir / "events.jsonl"
        self.proposals_path = self.memory_dir / "proposal_queue.json"
        self.package_queue_path = self.package_dir / "autoprog_package_queue.json"

    def event(self, event_type: str, payload: dict[str, Any]) -> None:
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        row = {
            "timestamp": utc_now(),
            "event_type": event_type,
            "payload": payload,
        }
        with self.events_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    def load_list(self, path: Path) -> list[dict[str, Any]]:
        if not path.exists():
            return []

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except Exception:
            return []

    def save_list(self, path: Path, rows: list[dict[str, Any]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(rows, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    def build_file_plans(self, checkpoint: str, objective: str) -> list[dict[str, Any]]:
        safe_checkpoint = checkpoint.replace(".", "_").replace("-", "_")

        return [
            {
                "action": "create_module",
                "path": f"k_atlas/core/autoprog_generated/checkpoint_{safe_checkpoint}/README.md",
                "purpose": "documentar proposta de autoprogramacao assistida",
                "content": f"# Checkpoint {checkpoint}\n\nObjetivo proposto:\n\n{objective}\n\nStatus: proposta aguardando aprovacao humana.\n",
            },
            {
                "action": "create_report",
                "path": f"reports/autoprog_generated/checkpoint_{safe_checkpoint}_proposal.json",
                "purpose": "registrar proposta futura em formato auditavel",
                "content": "{}",
            },
        ]

    def create_proposal(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        run_id = str(uuid4())
        data = dict(payload or {})
        validation = validate_autoprog_request(data)

        if not validation["ok"]:
            report = {
                "ok": False,
                "checkpoint": "65",
                "name": "Assisted Autoprogramming Kernel",
                "run_id": run_id,
                "generated_at": utc_now(),
                "status": "blocked_by_policy",
                "validation": validation,
                "payload": data,
                "external_side_effects": "none",
            }
            self.save_report(report)
            return report

        objective = str(data.get("objective", "")).strip()
        checkpoint = str(data.get("checkpoint", "65")).strip()
        action = str(data.get("action", "create_module")).strip()

        file_plans = self.build_file_plans(checkpoint=checkpoint, objective=objective)
        file_validations = [validate_file_plan(item) for item in file_plans]

        proposal = {
            "proposal_id": str(uuid4()),
            "checkpoint": checkpoint,
            "action": action,
            "objective": objective,
            "created_at": utc_now(),
            "status": "waiting_human_review",
            "source": "assisted_autoprogramming_kernel",
            "file_plans": file_plans,
            "file_validations": file_validations,
            "execution_enabled": False,
            "real_execution_enabled": False,
            "human_approval_required": True,
            "guardrails": [
                "nao executa codigo arbitrario",
                "nao chama API externa",
                "nao publica",
                "nao envia mensagem",
                "nao faz deploy",
                "nao usa token em texto puro",
                "gera apenas proposta e pacote auditavel",
            ],
        }

        queue = self.load_list(self.proposals_path)
        queue.append(proposal)
        self.save_list(self.proposals_path, queue)

        package = {
            "package_id": str(uuid4()),
            "proposal_id": proposal["proposal_id"],
            "checkpoint": checkpoint,
            "created_at": utc_now(),
            "status": "waiting_professor_or_operator_approval",
            "package_type": "assisted_autoprogramming_plan",
            "objective": objective,
            "file_count": len(file_plans),
            "execution_enabled": False,
            "real_execution_enabled": False,
            "approval_required_before_apply": True,
        }

        packages = self.load_list(self.package_queue_path)
        packages.append(package)
        self.save_list(self.package_queue_path, packages)

        report = {
            "ok": True,
            "checkpoint": "65",
            "name": "Assisted Autoprogramming Kernel",
            "run_id": run_id,
            "generated_at": utc_now(),
            "status": "proposal_created",
            "proposal": proposal,
            "package": package,
            "summary": {
                "proposal_queue_total": len(queue),
                "package_queue_total": len(packages),
                "files_planned": len(file_plans),
                "execution_enabled": False,
                "real_execution_enabled": False,
                "external_side_effects": "local_files_only",
                "next_action": "revisar proposta antes de aplicar qualquer alteracao real",
            },
            "guardrails": proposal["guardrails"],
        }

        self.save_report(report)
        self.event("assisted_autoprogramming.proposal_created", {
            "run_id": run_id,
            "proposal_id": proposal["proposal_id"],
            "checkpoint": checkpoint,
        })

        return report

    def summary(self) -> dict[str, Any]:
        proposals = self.load_list(self.proposals_path)
        packages = self.load_list(self.package_queue_path)

        return {
            "ok": True,
            "checkpoint": "65",
            "name": "Assisted Autoprogramming Kernel",
            "generated_at": utc_now(),
            "status": "operational",
            "summary": {
                "proposal_queue_total": len(proposals),
                "package_queue_total": len(packages),
                "waiting_human_review": len([item for item in proposals if item.get("status") == "waiting_human_review"]),
                "execution_enabled": False,
                "real_execution_enabled": False,
                "next_action": "criar ou revisar proposta de autoprogramacao assistida",
            },
            "proposals": proposals,
            "packages": packages,
        }

    def save_report(self, report: dict[str, Any] | None = None) -> dict[str, Any]:
        final_report = report or self.summary()
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        json_path = self.reports_dir / "latest_assisted_autoprogramming.json"
        md_path = self.reports_dir / "latest_assisted_autoprogramming.md"

        json_path.write_text(
            json.dumps(final_report, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        md_path.write_text(self.to_markdown(final_report), encoding="utf-8")

        return final_report

    def to_markdown(self, report: dict[str, Any]) -> str:
        summary = report.get("summary", {})
        lines = [
            "# K-Atlas Assisted Autoprogramming Kernel",
            "",
            f"Checkpoint: {report.get('checkpoint')}",
            f"Status: {report.get('status')}",
            "",
            "## Summary",
            "",
            f"- Proposal queue total: {summary.get('proposal_queue_total')}",
            f"- Package queue total: {summary.get('package_queue_total')}",
            f"- Files planned: {summary.get('files_planned')}",
            f"- Execution enabled: {summary.get('execution_enabled')}",
            f"- Next action: {summary.get('next_action')}",
            "",
            "## Guardrails",
            "",
        ]

        for item in report.get("guardrails", []):
            lines.append(f"- {item}")

        return "\n".join(lines)
