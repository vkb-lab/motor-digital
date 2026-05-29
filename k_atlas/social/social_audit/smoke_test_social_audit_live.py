from __future__ import annotations

import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.social.social_audit.live_status import SocialAuditLiveStatus


class SocialAuditLiveSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_social_live_"))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_live_status_writes_and_reads(self) -> None:
        live = SocialAuditLiveStatus(
            status_path=self.tmp / "live_status.json",
            events_path=self.tmp / "live_events.jsonl",
        )

        live.update(
            run_id="test",
            status="running",
            step="load",
            message="testing",
            data={"ok": True},
        )

        self.assertEqual(live.load()["step"], "load")
        self.assertEqual(len(live.load_events()), 1)

    def test_profile_audit_compiles(self) -> None:
        py_compile.compile("k_atlas/social/social_audit/profile_audit.py", doraise=True)

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/12_K_Atlas_Social_Audit_Local.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)