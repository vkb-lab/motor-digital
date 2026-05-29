# -*- coding: utf-8 -*-
"""K-Social content refinement queue.

Creates supervised creative refinement tasks from human-reviewed social operations.
It does not publish content, does not call external APIs and does not operate browsers.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


class SocialContentRefinementQueue:
    """Builds local creative refinement tasks from reviewed operations."""

    ELIGIBLE_STATUSES = {
        "approved_for_content_refinement",
        "needs_revision",
    }

    IGNORED_REPORT_FILES = {
        "social_dashboard_snapshot.json",
        "social_daily_report.json",
        "social_approval_queue.json",
    }

    REQUIRED_OPERATION_KEYS = {
        "system",
        "operation_status",
        "audience",
        "creative_brief",
        "campaign",
        "audit",
    }

    def __init__(
        self,
        reports_dir: Optional[Path] = None,
        memory_dir: Optional[Path] = None,
    ) -> None:
        base_dir = Path(__file__).resolve().parents[1]
        self.reports_dir = Path(reports_dir) if reports_dir else base_dir / "reports"
        self.memory_dir = Path(memory_dir) if memory_dir else base_dir / "memory"
        self.queue_file = self.memory_dir / "social_content_refinement_queue.json"

        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.memory_dir.mkdir(parents=True, exist_ok=True)

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _load_json(self, path: Path) -> Optional[Dict[str, Any]]:
        try:
            with path.open("r", encoding="utf-8-sig") as file:
                data = json.load(file)
        except (json.JSONDecodeError, OSError):
            return None

        if not isinstance(data, dict):
            return None

        return data

    def _save_json(self, path: Path, data: Dict[str, Any]) -> None:
        with path.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

    def _is_operation_report(self, data: Dict[str, Any]) -> bool:
        missing = self.REQUIRED_OPERATION_KEYS.difference(set(data.keys()))
        if missing:
            return False

        if data.get("publication_permission") is not False:
            return False

        if data.get("external_api_used") is not False:
            return False

        if data.get("human_review_required") is not True:
            return False

        if not isinstance(data.get("campaign", {}), dict):
            return False

        if not isinstance(data.get("audit", {}), dict):
            return False

        return True

    def _operation_paths(self) -> List[Path]:
        paths: List[Path] = []

        for path in sorted(self.reports_dir.glob("*.json")):
            if path.name in self.IGNORED_REPORT_FILES:
                continue

            data = self._load_json(path)
            if not data:
                continue

            if self._is_operation_report(data):
                paths.append(path)

        return paths

    def _approval_status(self, operation: Dict[str, Any]) -> str:
        metadata = operation.get("request_metadata", {})
        if not isinstance(metadata, dict):
            return "pending_human_review"

        return str(metadata.get("approval_status", "pending_human_review"))

    def _review_notes(self, operation: Dict[str, Any]) -> str:
        metadata = operation.get("request_metadata", {})
        if not isinstance(metadata, dict):
            return ""

        return str(metadata.get("last_review_notes", ""))

    def _build_tasks_for_operation(self, source_file: str, operation: Dict[str, Any]) -> List[Dict[str, Any]]:
        audience = operation.get("audience", {})
        campaign = operation.get("campaign", {})
        creative_brief = operation.get("creative_brief", {})

        product = audience.get("product", creative_brief.get("product", "produto nao informado"))
        objective = campaign.get("objective", creative_brief.get("objective", "objetivo nao informado"))
        approval_status = self._approval_status(operation)
        review_notes = self._review_notes(operation)

        channels = campaign.get("channels", [])
        content_calendar = campaign.get("content_calendar", [])
        if not isinstance(content_calendar, list):
            content_calendar = []

        tasks: List[Dict[str, Any]] = []

        base_context = {
            "source_file": source_file,
            "product": product,
            "objective": objective,
            "approval_status": approval_status,
            "review_notes": review_notes,
            "publication_permission": False,
            "external_api_used": False,
            "human_review_required": True,
            "approved_for_auto_publish": False,
        }

        task_templates = [
            {
                "task_type": "caption_refinement",
                "title": "Refinar legenda principal",
                "instructions": "Ajustar clareza, promessa, tom e chamada para acao sem publicar.",
            },
            {
                "task_type": "hook_variations",
                "title": "Criar variacoes de gancho",
                "instructions": "Criar alternativas de abertura para testar atencao inicial.",
            },
            {
                "task_type": "reel_script",
                "title": "Preparar roteiro de reel",
                "instructions": "Criar roteiro curto com gancho, desenvolvimento, prova e CTA supervisionado.",
            },
            {
                "task_type": "ai_image_prompt",
                "title": "Preparar prompt de imagem IA",
                "instructions": "Descrever cena visual sem usar marcas de terceiros sem autorizacao.",
            },
            {
                "task_type": "ai_video_prompt",
                "title": "Preparar prompt de video IA",
                "instructions": "Criar estrutura de cenas para video IA com revisao humana obrigatoria.",
            },
        ]

        for index, template in enumerate(task_templates, start=1):
            tasks.append(
                {
                    "task_id": f"{source_file}::task_{index:02d}",
                    "created_at": self._now(),
                    "status": "pending_refinement",
                    "channels": channels,
                    "content_items_available": len(content_calendar),
                    **base_context,
                    **template,
                }
            )

        return tasks

    def build_queue(self) -> Dict[str, Any]:
        tasks: List[Dict[str, Any]] = []

        for path in self._operation_paths():
            operation = self._load_json(path)
            if not operation:
                continue

            approval_status = self._approval_status(operation)

            if approval_status not in self.ELIGIBLE_STATUSES:
                continue

            tasks.extend(self._build_tasks_for_operation(path.name, operation))

        counts: Dict[str, int] = {
            "pending_refinement": 0,
            "in_progress": 0,
            "done": 0,
            "blocked": 0,
        }

        for task in tasks:
            status = task.get("status", "pending_refinement")
            if status in counts:
                counts[status] += 1

        return {
            "system": "K-Social Content Refinement Queue",
            "generated_at": self._now(),
            "total_tasks": len(tasks),
            "counts": counts,
            "eligible_statuses": sorted(self.ELIGIBLE_STATUSES),
            "publication_permission": False,
            "external_api_used": False,
            "human_review_required": True,
            "approved_for_auto_publish": False,
            "tasks": tasks,
        }

    def save_queue(self) -> Dict[str, Any]:
        queue = self.build_queue()
        self._save_json(self.queue_file, queue)
        return queue


def main() -> None:
    queue_manager = SocialContentRefinementQueue()
    queue = queue_manager.save_queue()

    print("K-Social content refinement queue generated.")
    print("Queue file:", queue_manager.queue_file)
    print("Total tasks:", queue["total_tasks"])
    print("Pending refinement:", queue["counts"]["pending_refinement"])
    print("Publication permission:", queue["publication_permission"])
    print("Approved for auto publish:", queue["approved_for_auto_publish"])


if __name__ == "__main__":
    main()
