from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4

from .policy import is_review_approved_for_package, validate_apply_package_request


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


class AutoprogrammingApplyPackageBuilder:
    def __init__(
        self,
        review_queue_path: str | Path = "live/autoprogramming_proposal_reviewer/proposal_review_queue.json",
        live_dir: str | Path = "live/autoprogramming_apply_package_builder",
        memory_dir: str | Path = "memory/autoprogramming_apply_package_builder",
        reports_dir: str | Path = "reports/autoprogramming_apply_package_builder",
    ) -> None:
        self.review_queue_path = Path(review_queue_path)
        self.live_dir = Path(live_dir)
        self.memory_dir = Path(memory_dir)
        self.reports_dir = Path(reports_dir)

        self.package_queue_path = self.live_dir / "apply_package_queue.json"
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

    def extract_file_plans(self, review: Mapping[str, Any]) -> list[dict[str, Any]]:
        proposal = review.get("proposal_snapshot", {})
        if not isinstance(proposal, dict):
            return []

        raw_plans = proposal.get("file_plans", [])
        if not isinstance(raw_plans, list):
            return []

        normalized: list[dict[str, Any]] = []

        for item in raw_plans:
            if not isinstance(item, dict):
                continue

            content = str(item.get("content", ""))
            path = str(item.get("path", "")).replace("\\", "/").strip()
            action = str(item.get("action", "create_module")).strip()

            normalized.append({
                "action": action,
                "path": path,
                "purpose": item.get("purpose"),
                "content": content,
                "content_sha256": sha256_text(content),
                "content_size": len(content),
                "apply_status": "not_applied",
                "validated_for_future_apply": False,
            })

        return normalized

    def build_package_from_review(self, review: Mapping[str, Any]) -> dict[str, Any]:
        file_plans = self.extract_file_plans(review)

        return {
            "apply_package_id": str(uuid4()),
            "source": "autoprogramming_proposal_reviewer",
            "source_review_id": review.get("review_id"),
            "source_proposal_id": review.get("proposal_id"),
            "checkpoint": review.get("checkpoint"),
            "objective": review.get("objective"),
            "created_at": utc_now(),
            "status": "waiting_execution_gate_validation",
            "file_plans": file_plans,
            "file_count": len(file_plans),
            "package_hash": sha256_text(json.dumps(file_plans, ensure_ascii=False, sort_keys=True)),
            "execution_enabled": False,
            "real_execution_enabled": False,
            "external_api_enabled": False,
            "auto_publish": False,
            "auto_send": False,
            "auto_deploy": False,
            "browser_automation": False,
            "mouse_automation": False,
            "requires_execution_gate_validation": True,
            "requires_human_approval": True,
            "apply_now": False,
            "guardrails": [
                "pacote nao aplica arquivos",
                "pacote nao executa codigo",
                "pacote nao chama API externa",
                "pacote nao publica",
                "pacote nao envia mensagem",
                "pacote nao faz deploy",
                "pacote exige execution gate futuro",
            ],
        }

    def build_apply_packages(self, payload: Mapping[str, Any] | None = None) -> dict[str, Any]:
        run_id = str(uuid4())
        data = dict(payload or {})
        validation = validate_apply_package_request(data)

        if not validation["ok"]:
            report = {
                "ok": False,
                "checkpoint": "67",
                "name": "Autoprogramming Apply Package Builder",
                "run_id": run_id,
                "generated_at": utc_now(),
                "status": "blocked_by_policy",
                "validation": validation,
                "payload": data,
                "external_side_effects": "none",
            }
            self.save_report(report)
            return report

        reviews = self.load_list(self.review_queue_path)
        packages = self.load_list(self.package_queue_path)

        existing_review_ids = {
            item.get("source_review_id")
            for item in packages
            if item.get("source_review_id")
        }

        candidates = [
            review for review in reviews
            if is_review_approved_for_package(review)
            and review.get("review_id") not in existing_review_ids
        ]

        created = [self.build_package_from_review(review) for review in candidates]
        packages.extend(created)
        self.save_list(self.package_queue_path, packages)

        report = {
            "ok": True,
            "checkpoint": "67",
            "name": "Autoprogramming Apply Package Builder",
            "run_id": run_id,
            "generated_at": utc_now(),
            "status": "apply_package_queue_built",
            "summary": {
                "reviews_total": len(reviews),
                "approved_candidates": len(candidates),
                "packages_created": len(created),
                "package_queue_total": len(packages),
                "execution_enabled": False,
                "real_execution_enabled": False,
                "external_side_effects": "local_files_only",
                "next_action": "validar pacotes no Execution Gate antes de qualquer aplicacao real",
            },
            "created_packages": created,
            "package_queue_path": str(self.package_queue_path).replace("\\", "/"),
            "validation": validation,
            "guardrails": [
                "nao aplica alteracoes",
                "nao executa codigo",
                "nao chama API externa",
                "nao publica",
                "nao envia",
                "nao faz deploy",
                "pacotes aguardam execution gate",
            ],
            "next_checkpoint": "68 - Autoprogramming Apply Package Gate",
        }

        self.save_report(report)
        self.event("autoprogramming_apply_package_builder.queue_built", {
            "run_id": run_id,
            "packages_created": len(created),
        })

        return report

    def summary(self) -> dict[str, Any]:
        reviews = self.load_list(self.review_queue_path)
        packages = self.load_list(self.package_queue_path)

        return {
            "ok": True,
            "checkpoint": "67",
            "name": "Autoprogramming Apply Package Builder",
            "generated_at": utc_now(),
            "status": "operational",
            "summary": {
                "reviews_total": len(reviews),
                "package_queue_total": len(packages),
                "waiting_execution_gate_validation": len([
                    item for item in packages
                    if item.get("status") == "waiting_execution_gate_validation"
                ]),
                "execution_enabled": False,
                "real_execution_enabled": False,
            },
            "packages": packages,
        }

    def save_report(self, report: dict[str, Any] | None = None) -> dict[str, Any]:
        final_report = report or self.summary()
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        json_path = self.reports_dir / "latest_autoprogramming_apply_package_builder.json"
        md_path = self.reports_dir / "latest_autoprogramming_apply_package_builder.md"
        next_prompt_path = self.reports_dir / "stage_068_next_prompt.md"

        json_path.write_text(
            json.dumps(final_report, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        md_path.write_text(self.to_markdown(final_report), encoding="utf-8")
        next_prompt_path.write_text(self.next_prompt(), encoding="utf-8")

        return final_report

    def to_markdown(self, report: dict[str, Any]) -> str:
        summary = report.get("summary", {})

        lines = [
            "# K-Atlas Autoprogramming Apply Package Builder",
            "",
            f"Checkpoint: {report.get('checkpoint')}",
            f"Status: {report.get('status')}",
            "",
            "## Summary",
            "",
            f"- Reviews total: {summary.get('reviews_total')}",
            f"- Approved candidates: {summary.get('approved_candidates')}",
            f"- Packages created: {summary.get('packages_created')}",
            f"- Package queue total: {summary.get('package_queue_total')}",
            f"- Execution enabled: {summary.get('execution_enabled')}",
            f"- Next action: {summary.get('next_action')}",
            "",
            "## Guardrails",
            "",
        ]

        for item in report.get("guardrails", []):
            lines.append(f"- {item}")

        return "\n".join(lines)

    def next_prompt(self) -> str:
        return """Checkpoint 67 verificado com sucesso.

Gere o Checkpoint 68 do K-Atlas.

Objetivo:
criar o Autoprogramming Apply Package Gate, que valida pacotes de aplicacao antes de qualquer escrita real em arquivos.

Regras:
- portugues
- unico bloco PowerShell completo
- Windows PowerShell
- UTF-8
- smoke test
- commit
- push
- logs e relatorios
- sem API externa real
- sem publicacao automatica
- sem deploy automatico
- sem envio automatico
- sem token em texto puro
- manter governanca humana
"""
