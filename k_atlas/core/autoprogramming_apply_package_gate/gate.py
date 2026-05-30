from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from .policy import validate_apply_package


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class AutoprogrammingApplyPackageGate:
    def __init__(
        self,
        package_queue_path: str | Path = "live/autoprogramming_apply_package_builder/apply_package_queue.json",
        live_dir: str | Path = "live/autoprogramming_apply_package_gate",
        memory_dir: str | Path = "memory/autoprogramming_apply_package_gate",
        reports_dir: str | Path = "reports/autoprogramming_apply_package_gate",
    ) -> None:
        self.package_queue_path = Path(package_queue_path)
        self.live_dir = Path(live_dir)
        self.memory_dir = Path(memory_dir)
        self.reports_dir = Path(reports_dir)
        self.gate_queue_path = self.live_dir / "apply_package_gate_queue.json"
        self.events_path = self.memory_dir / "events.jsonl"

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

    def build_gate_queue(self) -> dict[str, Any]:
        run_id = str(uuid4())
        packages = self.load_list(self.package_queue_path)
        existing = self.load_list(self.gate_queue_path)

        existing_ids = {
            item.get("apply_package_id")
            for item in existing
            if item.get("apply_package_id")
        }

        created: list[dict[str, Any]] = []

        for package in packages:
            package_id = package.get("apply_package_id")
            if not package_id or package_id in existing_ids:
                continue

            validation = validate_apply_package(package)

            item = {
                "gate_id": str(uuid4()),
                "apply_package_id": package_id,
                "source_review_id": package.get("source_review_id"),
                "source_proposal_id": package.get("source_proposal_id"),
                "checkpoint": package.get("checkpoint"),
                "objective": package.get("objective"),
                "created_at": utc_now(),
                "status": "waiting_human_apply_approval" if validation["ok"] else "blocked_by_gate",
                "validation": validation,
                "package_snapshot": package,
                "manual_apply_allowed_after_approval": validation["ok"],
                "automatic_apply_allowed": False,
                "execution_enabled": False,
                "real_execution_enabled": False,
                "external_side_effects": "none",
                "guardrails": [
                    "gate nao aplica arquivos",
                    "gate nao executa codigo",
                    "gate apenas valida pacote",
                    "gate exige aprovacao humana futura",
                    "gate bloqueia automacao externa",
                    "gate bloqueia tokens em texto puro",
                ],
            }

            created.append(item)

        existing.extend(created)
        self.save_list(self.gate_queue_path, existing)

        report = {
            "ok": True,
            "checkpoint": "68",
            "name": "Autoprogramming Apply Package Gate",
            "run_id": run_id,
            "generated_at": utc_now(),
            "status": "gate_queue_built",
            "summary": {
                "packages_total": len(packages),
                "gate_items_created": len(created),
                "gate_queue_total": len(existing),
                "waiting_human_apply_approval": len([
                    item for item in existing
                    if item.get("status") == "waiting_human_apply_approval"
                ]),
                "blocked_by_gate": len([
                    item for item in existing
                    if item.get("status") == "blocked_by_gate"
                ]),
                "execution_enabled": False,
                "real_execution_enabled": False,
                "external_side_effects": "local_files_only",
                "next_action": "revisar gate e decidir se criaremos aplicador manual no checkpoint 69",
            },
            "created_gate_items": created,
            "gate_queue_path": str(self.gate_queue_path).replace("\\", "/"),
            "guardrails": [
                "nao aplica alteracoes",
                "nao executa codigo",
                "nao chama API externa",
                "nao publica",
                "nao envia",
                "nao faz deploy",
                "aplicacao real permanece bloqueada",
            ],
            "next_checkpoint": "69 - Manual Apply Executor",
        }

        self.save_report(report)
        self.event("autoprogramming_apply_package_gate.queue_built", {
            "run_id": run_id,
            "created": len(created),
        })

        return report

    def summary(self) -> dict[str, Any]:
        packages = self.load_list(self.package_queue_path)
        gates = self.load_list(self.gate_queue_path)

        return {
            "ok": True,
            "checkpoint": "68",
            "name": "Autoprogramming Apply Package Gate",
            "generated_at": utc_now(),
            "status": "operational",
            "summary": {
                "packages_total": len(packages),
                "gate_queue_total": len(gates),
                "waiting_human_apply_approval": len([
                    item for item in gates
                    if item.get("status") == "waiting_human_apply_approval"
                ]),
                "blocked_by_gate": len([
                    item for item in gates
                    if item.get("status") == "blocked_by_gate"
                ]),
                "execution_enabled": False,
                "real_execution_enabled": False,
            },
            "gate_items": gates,
        }

    def save_report(self, report: dict[str, Any] | None = None) -> dict[str, Any]:
        final_report = report or self.summary()
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        json_path = self.reports_dir / "latest_autoprogramming_apply_package_gate.json"
        md_path = self.reports_dir / "latest_autoprogramming_apply_package_gate.md"

        json_path.write_text(
            json.dumps(final_report, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        md_path.write_text(self.to_markdown(final_report), encoding="utf-8")

        return final_report

    def to_markdown(self, report: dict[str, Any]) -> str:
        summary = report.get("summary", {})
        lines = [
            "# K-Atlas Autoprogramming Apply Package Gate",
            "",
            f"Checkpoint: {report.get('checkpoint')}",
            f"Status: {report.get('status')}",
            "",
            "## Summary",
            "",
            f"- Packages total: {summary.get('packages_total')}",
            f"- Gate items created: {summary.get('gate_items_created')}",
            f"- Gate queue total: {summary.get('gate_queue_total')}",
            f"- Waiting human apply approval: {summary.get('waiting_human_apply_approval')}",
            f"- Blocked by gate: {summary.get('blocked_by_gate')}",
            f"- Execution enabled: {summary.get('execution_enabled')}",
            f"- Next action: {summary.get('next_action')}",
            "",
            "## Guardrails",
            "",
        ]

        for item in report.get("guardrails", []):
            lines.append(f"- {item}")

        return "\n".join(lines)
