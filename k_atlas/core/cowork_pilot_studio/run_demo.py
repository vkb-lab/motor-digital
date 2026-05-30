from __future__ import annotations

import json

from .recorder import CoworkStoryRecorder
from .studio import CoworkPilotStudio


if __name__ == "__main__":
    recorder = CoworkStoryRecorder()
    session = recorder.create_session("K-Atlas Cowork Pilot Demo")
    recorder.log_event(
        event_type="checkpoint",
        title="Cowork Pilot Studio inicializado",
        details="Duas janelas operacionais organizadas em modo comando e retorno.",
        session_id=session["session_id"],
    )

    studio = CoworkPilotStudio()
    report = studio.save_report()

    print(json.dumps({
        "ok": True,
        "checkpoint": "67.5",
        "session": session,
        "studio": report,
    }, ensure_ascii=False, indent=2))
