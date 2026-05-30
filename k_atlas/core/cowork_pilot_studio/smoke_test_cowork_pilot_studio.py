from __future__ import annotations

import json
import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.core.cowork_pilot_studio.recorder import CoworkStoryRecorder
from k_atlas.core.cowork_pilot_studio.studio import CoworkPilotStudio


class CoworkPilotStudioSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_cowork_studio_"))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_story_session(self) -> None:
        recorder = CoworkStoryRecorder(
            memory_dir=self.tmp / "memory",
            reports_dir=self.tmp / "reports",
        )

        session = recorder.create_session("Teste Cowork")
        event = recorder.log_event(
            event_type="test",
            title="Evento teste",
            details="Detalhe teste",
            session_id=session["session_id"],
        )

        self.assertTrue(session["ok"])
        self.assertEqual(event["event_type"], "test")
        self.assertTrue((self.tmp / "memory" / "story_events.jsonl").exists())
        self.assertTrue((self.tmp / "reports" / "latest_cowork_story_recorder.json").exists())

    def test_studio_report(self) -> None:
        studio = CoworkPilotStudio(
            root=self.tmp,
            reports_dir="reports",
        )

        report = studio.save_report()

        self.assertTrue(report["ok"])
        self.assertEqual(report["checkpoint"], "67.5")
        self.assertTrue((self.tmp / "reports" / "latest_cowork_pilot_studio.json").exists())

        loaded = json.loads((self.tmp / "reports" / "latest_cowork_pilot_studio.json").read_text(encoding="utf-8"))
        self.assertEqual(loaded["checkpoint"], "67.5")

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/67_5_K_Atlas_Cowork_Pilot_Studio.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
