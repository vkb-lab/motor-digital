from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4

from .policy import validate_review_payload


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class AutoprogrammingProposalReviewer:
    def __init__(
        self,
        proposals_path: str | Path = "memory/assisted_autoprogramming/proposal_queue.json",
        review_dir: str | Path = "memory/autoprogramming_proposal_reviewer",
        reports_dir: str | Path = "reports/autoprogramming_proposal_reviewer",
        live_dir: str | Path = "live/autoprogramming_proposal_reviewer",
    ) -> None:
        self.proposals_path = Path(proposals_path)
        self.review_dir = Path(review_dir)
        self.reports_dir = Path(reports_dir)
        self.live_dir = Path(live_dir)

        self.review_queue_path = self.live_dir / "proposal_review_queue.json"
        self.events_path = self.review_dir / "events.jsonl"

    def event(self, event_type: str, payload: dict[str, Any]) -> None:
        self.review_dir.mkdir(parents=True, exist_ok=True)
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

    def score_proposal(self, proposal: Mapping[str, Any]) -> dict[str, Any]:
        score = 100
        warnings: list[str] = []
        blockers: list[str] = []

        file_plans = proposal.get("file_plans", [])
        validations = proposal.get("file_validations", [])

        if not proposal.get("objective"):
            score -= 30
            blockers.append("objective_missing")

        if not file_plans:
            score -= 25
            blockers.append("file_plans_missing")

        if proposal.get("real_execution_enabled") is True:
            score -= 40
            blockers.append("real_execution_enabled_blocked")

        if proposal.get("execution_enabled") is True:
            score -= 30
            blockers.append("execution_enabled_blocked")

        invalid_files = [
            item for item in validations
            if isinstance(item, dict) and not item.get("ok", False)
        ]

        if invalid_files:
            score -= 35
            blockers.append("invalid_file_plan_detected")

        if len(file_plans) > 12:
            score -= 10
            warnings.append("too_many_files_for_assisted_mode")

        if score >= 85 and not blockers:
            recommendation = "approve_for_apply_package"
        elif blockers:
            recommendation = "request_changes"
        else:
            recommendation = "hold"

        return {
            "score": max(score, 0),
            "recommendation": recommendation,
            "warnings": warnings,
            "blockers": blockers,
            "human_review_required": True,
            "automatic_apply_allowed": False,
        }

    def create_review_item(self, proposal: Mapping[str, Any]) -> dict[str, Any]:
        review = self.score_proposal(proposal)

        return {
            "review_id": str(uuid4()),
            "proposal_id": proposal.get("proposal_id"),
            "checkpoint": proposal.get("checkpoint"),
            "objective": proposal.get("objective"),
            "created_at": utc_now(),
            "status": "waiting_human_decision",
            "review": review,
            "proposal_snapshot": dict(proposal),
            "decision_options": [
                "approve_for_apply_package",
                "request_changes",
                "deny",
                "hold",
            ],
            "execution_enabled": False,
            "real_execution_enabled": False,
            "external_side_effects": "none",
            "guardrails": [
                "revisao nao aplica alteracoes",
                "revisao nao executa codigo",
                "revisao nao chama API externa",
                "revisao nao publica",
                "revisao nao envia mensagem",
                "revisao nao faz deploy",
                "decisao humana continua obrigatoria",
            ],
        }

    def build_review_queue(self) -> dict[str, Any]:
        run_id = str(uuid4())
        proposals = self.load_list(self.proposals_path)
        existing_reviews = self.load_list(self.review_queue_path)

        existing_ids = {
            item.get("proposal_id")
            for item in existing_reviews
            if item.get("proposal_id")
        }

        candidates = [
            item for item in proposals
            if item.get("status") == "waiting_human_review"
            and item.get("proposal_id") not in existing_ids
        ]

        created = [self.create_review_item(item) for item in candidates]
        existing_reviews.extend(created)
        self.save_list(self.review_queue_path, existing_reviews)

        report = {
            "ok": True,
            "checkpoint": "66",
            "name": "Autoprogramming Proposal Reviewer",
            "run_id": run_id,
            "generated_at": utc_now(),
            "status": "review_queue_built",
            "summary": {
                "proposals_total": len(proposals),
                "existing_reviews_total": len(existing_reviews),
                "reviews_created": len(created),
                "execution_enabled": False,
                "real_execution_enabled": False,
                "external_side_effects": "local_files_only",
                "next_action": "operador revisa propostas e decide antes de criar apply package",
            },
            "created_reviews": created,
            "review_queue_path": str(self.review_queue_path).replace("\\", "/"),
            "guardrails": [
                "nao aplica alteracoes",
                "nao executa codigo",
                "nao chama API externa",
                "nao publica",
                "nao envia",
                "nao faz deploy",
            ],
            "next_checkpoint": "67 - Autoprogramming Apply Package Builder",
        }

        self.save_report(report)
        self.event("autoprogramming_proposal_reviewer.review_queue_built", {
            "run_id": run_id,
            "reviews_created": len(created),
        })

        return report

    def decide(self, review_id: str, decision: str, reviewer: str = "operator", notes: str = "") -> dict[str, Any]:
        validation = validate_review_payload({
            "decision": decision,
            "reviewer": reviewer,
            "notes": notes,
            "real_execution_enabled": False,
            "external_api_enabled": False,
            "auto_publish": False,
            "auto_send": False,
            "auto_deploy": False,
            "browser_automation": False,
            "mouse_automation": False,
        })

        reviews = self.load_list(self.review_queue_path)

        target = None
        for item in reviews:
            if item.get("review_id") == review_id:
                target = item
                break

        if target is None:
            return {
                "ok": False,
                "checkpoint": "66",
                "status": "review_not_found",
                "review_id": review_id,
            }

        if not validation["ok"]:
            return {
                "ok": False,
                "checkpoint": "66",
                "status": "decision_blocked_by_policy",
                "validation": validation,
            }

        target["status"] = "decided"
        target["decision"] = {
            "decision": decision,
            "reviewer": reviewer,
            "notes": notes,
            "decided_at": utc_now(),
            "apply_package_enabled": decision == "approve_for_apply_package",
            "real_execution_enabled": False,
        }

        self.save_list(self.review_queue_path, reviews)

        report = {
            "ok": True,
            "checkpoint": "66",
            "name": "Autoprogramming Proposal Reviewer",
            "generated_at": utc_now(),
            "status": "decision_registered",
            "review_id": review_id,
            "decision": target["decision"],
            "external_side_effects": "local_files_only",
        }

        self.save_report(report)
        self.event("autoprogramming_proposal_reviewer.decision_registered", report)
        return report

    def summary(self) -> dict[str, Any]:
        proposals = self.load_list(self.proposals_path)
        reviews = self.load_list(self.review_queue_path)

        return {
            "ok": True,
            "checkpoint": "66",
            "name": "Autoprogramming Proposal Reviewer",
            "generated_at": utc_now(),
            "status": "operational",
            "summary": {
                "proposals_total": len(proposals),
                "reviews_total": len(reviews),
                "waiting_human_decision": len([item for item in reviews if item.get("status") == "waiting_human_decision"]),
                "decided": len([item for item in reviews if item.get("status") == "decided"]),
                "execution_enabled": False,
                "real_execution_enabled": False,
            },
            "reviews": reviews,
        }

    def save_report(self, report: dict[str, Any] | None = None) -> dict[str, Any]:
        final_report = report or self.summary()
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        json_path = self.reports_dir / "latest_autoprogramming_proposal_reviewer.json"
        md_path = self.reports_dir / "latest_autoprogramming_proposal_reviewer.md"

        json_path.write_text(
            json.dumps(final_report, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        md_path.write_text(self.to_markdown(final_report), encoding="utf-8")

        return final_report

    def to_markdown(self, report: dict[str, Any]) -> str:
        summary = report.get("summary", {})
        lines = [
            "# K-Atlas Autoprogramming Proposal Reviewer",
            "",
            f"Checkpoint: {report.get('checkpoint')}",
            f"Status: {report.get('status')}",
            "",
            "## Summary",
            "",
            f"- Proposals total: {summary.get('proposals_total')}",
            f"- Reviews total: {summary.get('reviews_total', summary.get('existing_reviews_total'))}",
            f"- Reviews created: {summary.get('reviews_created')}",
            f"- Execution enabled: {summary.get('execution_enabled')}",
            f"- Next action: {summary.get('next_action')}",
            "",
            "## Guardrails",
            "",
        ]

        for item in report.get("guardrails", []):
            lines.append(f"- {item}")

        return "\n".join(lines)
