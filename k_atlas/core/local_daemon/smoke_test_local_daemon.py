from __future__ import annotations

import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.core.local_daemon.daemon import KAtlasLocalDaemon


class LocalDaemonSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_local_daemon_"))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_tick_dry_run(self) -> None:
        daemon = KAtlasLocalDaemon(state_dir=self.tmp)
        result = daemon.tick(manage=False)
        self.assertEqual(result["checkpoint"], "41")
        self.assertIn("streamlit", result["services"])
        self.assertTrue((self.tmp / "heartbeat.json").exists())

    def test_files_compile(self) -> None:
        py_compile.compile("k_atlas/core/local_daemon/daemon.py", doraise=True)
        py_compile.compile("k_atlas/core/local_daemon/run_once.py", doraise=True)
        py_compile.compile("pages/22_K_Atlas_Local_Daemon.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
