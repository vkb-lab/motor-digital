# -*- coding: utf-8 -*-
"""K-Social local content refinement executor.

Generates supervised creative draft files from refinement queue tasks.
It does not publish content, does not call external APIs and does not operate browsers.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


class SocialContentRefinementExecutor:
    """Executes local refinement tasks into Markdown draft files."""

    def __init__(
        self,
        queue_file: Optional[Path] = None,
        output_dir: Optional[Path] = None,
    ) -> None:
        base_dir = Path(__file__).resolve().parents[1]
        self.queue_file = (
            Path(queue_file)
            if queue_file
            else base_dir / "memory" / "social_content_refinement_queue.json"
        )
        self.output_dir = (
            Path(output_dir)
            if output_dir
            else base_dir / "reports" / "refinement_outputs"
        )
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _slugify(self, value: str) -> str:
        value = value.lower().strip()
        value = re.sub(r"[^a-z0-9]+", "-", value)
        value = value.strip("-")
        return value or "refinement-output"

    def load_queue(self) -> Dict[str, Any]:
        """Load refinement queue safely."""

        if not self.queue_file.exists():
            return {
                "system": "K-Social Content Refinement Queue",
                "total_tasks": 0,
                "tasks": [],
                "publication_permission": False,
                "external_api_used": False,
                "human_review_required": True,
                "approved_for_auto_publish": False,
            }

        with self.queue_file.open("r", encoding="utf-8-sig") as file:
            data = json.load(file)

        if not isinstance(data, dict):
            return {
                "system": "K-Social Content Refinement Queue",
                "total_tasks": 0,
                "tasks": [],
                "publication_permission": False,
                "external_api_used": False,
                "human_review_required": True,
                "approved_for_auto_publish": False,
            }

        data.setdefault("tasks", [])
        return data

    def _generate_content(self, task: Dict[str, Any]) -> str:
        """Generate deterministic local draft content for a task."""

        task_type = task.get("task_type", "unknown")
        product = task.get("product", "Produto nao informado")
        objective = task.get("objective", "Objetivo nao informado")
        channels = ", ".join(task.get("channels", []))
        review_notes = task.get("review_notes", "")
        instructions = task.get("instructions", "")

        lines: List[str] = []

        lines.append(f"# {task.get('title', 'Tarefa de refinamento')}")
        lines.append("")
        lines.append(f"Generated at: {self._now()}")
        lines.append("")
        lines.append("## Context")
        lines.append("")
        lines.append(f"- Product: {product}")
        lines.append(f"- Objective: {objective}")
        lines.append(f"- Task type: {task_type}")
        lines.append(f"- Channels: {channels}")
        lines.append(f"- Approval status: {task.get('approval_status', 'unknown')}")
        lines.append(f"- Review notes: {review_notes}")
        lines.append("")
        lines.append("## Governance")
        lines.append("")
        lines.append("- Human review required: True")
        lines.append("- Publication permission: False")
        lines.append("- External API used: False")
        lines.append("- Approved for auto publish: False")
        lines.append("")
        lines.append("## Instructions")
        lines.append("")
        lines.append(instructions or "Refinar conteudo com clareza e seguranca.")
        lines.append("")

        if task_type == "caption_refinement":
            lines.extend(
                [
                    "## Caption Draft",
                    "",
                    f"{product}: proposta revisada para comunicar valor com clareza.",
                    "",
                    "CTA sugerido: revisar com humano antes de qualquer publicacao.",
                    "",
                ]
            )
        elif task_type == "hook_variations":
            lines.extend(
                [
                    "## Hook Variations",
                    "",
                    "1. O que muda quando seu processo fica mais claro?",
                    "2. Antes de publicar, revise a mensagem com seguranca.",
                    "3. Uma ponte comercial precisa de confianca antes de escala.",
                    "4. O primeiro passo e organizar a comunicacao.",
                    "5. Menos improviso, mais revisao e consistencia.",
                    "",
                ]
            )
        elif task_type == "reel_script":
            lines.extend(
                [
                    "## Reel Script",
                    "",
                    "Cena 1: Gancho direto sobre a dor do publico.",
                    "Cena 2: Explicacao simples do valor da solucao.",
                    "Cena 3: Exemplo supervisionado de aplicacao.",
                    "Cena 4: Chamada para revisao ou contato humano.",
                    "",
                    "Legenda na tela: Conteudo em rascunho. Revisao humana obrigatoria.",
                    "",
                ]
            )
        elif task_type == "ai_image_prompt":
            lines.extend(
                [
                    "## AI Image Prompt Draft",
                    "",
                    f"Create a clean commercial visual concept for {product}.",
                    "Scene: professional marketplace context, trustworthy, organized, local business atmosphere.",
                    "Style: premium, clear, realistic, no third-party logos, no copyrighted brand references.",
                    "Safety: human review required before use.",
                    "",
                ]
            )
        elif task_type == "ai_video_prompt":
            lines.extend(
                [
                    "## AI Video Prompt Draft",
                    "",
                    f"Create a short supervised video concept for {product}.",
                    "Scene 1: audience problem.",
                    "Scene 2: organized solution workflow.",
                    "Scene 3: trust and human review.",
                    "Scene 4: soft call to action.",
                    "Safety: do not publish automatically.",
                    "",
                ]
            )
        else:
            lines.extend(
                [
                    "## Draft",
                    "",
                    "Conteudo de refinamento pendente de definicao.",
                    "",
                ]
            )

        return "\n".join(lines)

    def execute(self) -> Dict[str, Any]:
        """Generate output files for pending refinement tasks."""

        queue = self.load_queue()
        tasks = queue.get("tasks", [])

        generated_files: List[str] = []

        for task in tasks:
            if task.get("status") != "pending_refinement":
                continue

            product_slug = self._slugify(str(task.get("product", "produto")))
            task_type_slug = self._slugify(str(task.get("task_type", "task")))
            output_file = self.output_dir / f"{product_slug}_{task_type_slug}.md"

            output_file.write_text(self._generate_content(task), encoding="utf-8")
            generated_files.append(str(output_file))

        summary = {
            "system": "K-Social Content Refinement Executor",
            "generated_at": self._now(),
            "queue_file": str(self.queue_file),
            "output_dir": str(self.output_dir),
            "tasks_found": len(tasks),
            "files_generated": len(generated_files),
            "generated_files": generated_files,
            "publication_permission": False,
            "external_api_used": False,
            "human_review_required": True,
            "approved_for_auto_publish": False,
        }

        summary_file = self.output_dir / "refinement_execution_summary.json"
        summary_file.write_text(
            json.dumps(summary, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        return summary


def main() -> None:
    executor = SocialContentRefinementExecutor()
    summary = executor.execute()

    print("K-Social refinement executor completed.")
    print("Tasks found:", summary["tasks_found"])
    print("Files generated:", summary["files_generated"])
    print("Output dir:", summary["output_dir"])
    print("Publication permission:", summary["publication_permission"])
    print("Approved for auto publish:", summary["approved_for_auto_publish"])


if __name__ == "__main__":
    main()
