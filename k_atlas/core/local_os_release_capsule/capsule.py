from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from k_atlas.core.local_os_mvp_readiness.readiness import LocalOSMVPReadiness


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class LocalOSReleaseCapsule:
    def __init__(
        self,
        project_root: str | Path = ".",
        reports_dir: str | Path = "reports/local_os_release_capsule",
        memory_dir: str | Path = "memory/local_os_release_capsule",
    ) -> None:
        self.project_root = Path(project_root)
        self.reports_dir = self.project_root / reports_dir
        self.memory_dir = self.project_root / memory_dir
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

    def build_capsule(self) -> dict[str, Any]:
        capsule_id = str(uuid4())
        readiness = LocalOSMVPReadiness(project_root=self.project_root)
        readiness_report = readiness.build_report()
        readiness_summary = readiness_report.get("summary", {})

        release_status = "release_candidate_ready" if readiness_report.get("ok") else "release_candidate_partial"

        capsule = {
            "ok": readiness_report.get("ok") is True,
            "checkpoint": "100",
            "name": "K-Atlas Local OS Release Capsule",
            "capsule_id": capsule_id,
            "generated_at": utc_now(),
            "status": release_status,
            "version": "0.1.0-local-os-mvp",
            "release_scope": [
                "cockpit visual",
                "local control plane",
                "mission installer",
                "mission generator",
                "mission bridge",
                "mission pipeline",
                "remote assist readiness",
                "secure local API runtime",
                "assisted execution layer",
                "supervised autonomy layer",
            ],
            "readiness_summary": readiness_summary,
            "operator_instruction": "usar o Local OS apenas em modo supervisionado, com aprovacao humana e rollback",
            "execution_enabled": False,
            "real_execution_enabled": False,
            "external_side_effects": "local_files_only",
            "release_guardrails": [
                "sem controle remoto real por padrao",
                "sem porta publica aberta por padrao",
                "sem execucao automatica",
                "sem envio automatico",
                "sem deploy automatico",
                "sem captura de senha",
                "sem movimento automatico de mouse",
                "com logs",
                "com GitHub como memoria persistente",
                "com aprovacao humana",
            ],
            "next_phase": {
                "name": "K-Atlas Local OS Alpha",
                "suggested_start": "101 - Local OS Launcher",
                "goal": "unificar paineis em um launcher central e reduzir atrito operacional",
            },
        }

        self.save_report(capsule)
        self.event("local_os_release_capsule.built", {
            "capsule_id": capsule_id,
            "status": release_status,
        })
        return capsule

    def save_report(self, capsule: dict[str, Any]) -> None:
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        (self.reports_dir / "latest_local_os_release_capsule.json").write_text(
            json.dumps(capsule, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        (self.reports_dir / "latest_local_os_release_capsule.md").write_text(
            self.to_markdown(capsule),
            encoding="utf-8",
        )

    def to_markdown(self, capsule: dict[str, Any]) -> str:
        summary = capsule.get("readiness_summary", {})
        next_phase = capsule.get("next_phase", {})
        lines = [
            "# K-Atlas Local OS Release Capsule",
            "",
            f"Checkpoint: {capsule.get('checkpoint')}",
            f"Version: {capsule.get('version')}",
            f"Status: {capsule.get('status')}",
            "",
            "## Readiness",
            "",
            f"- Components total: {summary.get('components_total')}",
            f"- Components operational: {summary.get('components_operational')}",
            f"- Readiness score: {summary.get('readiness_score')}",
            f"- Local OS ready: {summary.get('local_os_ready')}",
            "",
            "## Release scope",
            "",
        ]

        for item in capsule.get("release_scope", []):
            lines.append(f"- {item}")

        lines.extend(["", "## Guardrails", ""])
        for item in capsule.get("release_guardrails", []):
            lines.append(f"- {item}")

        lines.extend([
            "",
            "## Next phase",
            "",
            f"- Name: {next_phase.get('name')}",
            f"- Suggested start: {next_phase.get('suggested_start')}",
            f"- Goal: {next_phase.get('goal')}",
        ])

        return "\n".join(lines)
