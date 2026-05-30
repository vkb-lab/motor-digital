from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class CoworkStoryRecorder:
    def __init__(
        self,
        memory_dir: str | Path = "memory/cowork_pilot_studio",
        reports_dir: str | Path = "reports/cowork_pilot_studio",
    ) -> None:
        self.memory_dir = Path(memory_dir)
        self.reports_dir = Path(reports_dir)
        self.sessions_dir = self.memory_dir / "sessions"
        self.events_path = self.memory_dir / "story_events.jsonl"

    def detect_tools(self) -> dict[str, Any]:
        ffmpeg = shutil.which("ffmpeg")
        obs_candidates = [
            Path("C:/Program Files/obs-studio/bin/64bit/obs64.exe"),
            Path("C:/Program Files (x86)/obs-studio/bin/64bit/obs64.exe"),
        ]

        obs = None
        for candidate in obs_candidates:
            if candidate.exists():
                obs = str(candidate)
                break

        return {
            "ffmpeg_available": ffmpeg is not None,
            "ffmpeg_path": ffmpeg,
            "obs_available": obs is not None,
            "obs_path": obs,
            "recording_recommendation": "ffmpeg" if ffmpeg else ("obs" if obs else "manual"),
        }

    def create_session(self, title: str = "K-Atlas Cowork Pilot Session") -> dict[str, Any]:
        session_id = str(uuid4())
        session_dir = self.sessions_dir / session_id
        session_dir.mkdir(parents=True, exist_ok=True)

        session = {
            "ok": True,
            "session_id": session_id,
            "title": title,
            "created_at": utc_now(),
            "status": "session_created",
            "session_dir": str(session_dir).replace("\\", "/"),
            "tools": self.detect_tools(),
            "guardrails": [
                "gravacao supervisionada",
                "sem envio automatico",
                "sem publicacao automatica",
                "sem API externa",
                "sem exposicao de tokens",
            ],
        }

        (session_dir / "session.json").write_text(
            json.dumps(session, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )

        self.log_event(
            event_type="session_created",
            title=title,
            details="Sessao cowork criada para documentar piloto automatico supervisionado.",
            session_id=session_id,
        )

        self.save_report(session)

        return session

    def log_event(
        self,
        event_type: str,
        title: str,
        details: str,
        session_id: str | None = None,
        artifact_path: str | None = None,
    ) -> dict[str, Any]:
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        event = {
            "event_id": str(uuid4()),
            "timestamp": utc_now(),
            "session_id": session_id,
            "event_type": event_type,
            "title": title,
            "details": details,
            "artifact_path": artifact_path,
        }

        with self.events_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")

        return event

    def read_events(self, limit: int = 50) -> list[dict[str, Any]]:
        if not self.events_path.exists():
            return []

        rows: list[dict[str, Any]] = []

        for line in self.events_path.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                rows.append(json.loads(line))
            except Exception:
                continue

        return rows[-limit:]

    def save_report(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        report = {
            "ok": True,
            "checkpoint": "67.5",
            "name": "K-Atlas Cowork Story Recorder",
            "generated_at": utc_now(),
            "status": "operational",
            "payload": payload or {},
            "tools": self.detect_tools(),
            "events": self.read_events(),
            "external_side_effects": "local_files_only",
        }

        path = self.reports_dir / "latest_cowork_story_recorder.json"
        path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )

        return report
