from __future__ import annotations

import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.core.principal_shell_cover.cover import PrincipalShellCover


class PrincipalShellCoverSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_shell_cover_"))
        required = [
            "k_atlas/core/local_os_release_capsule",
            "k_atlas/core/local_control_plane",
            "k_atlas/core/local_mission_installer",
            "k_atlas/core/mission_pipeline_runner",
            "k_atlas/core/remote_assist_readiness",
            "k_atlas/core/secure_local_api_runtime",
            "k_atlas/core/supervised_autonomy_dashboard",
            "ops/start_k_atlas_auto_update_watcher_hidden.ps1",
        ]
        for item in required:
            target = self.tmp / item
            if item.endswith(".ps1"):
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("demo", encoding="utf-8")
            else:
                target.mkdir(parents=True, exist_ok=True)
        self.cover = PrincipalShellCover(project_root=self.tmp)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_build_status(self) -> None:
        status = self.cover.build_status()
        self.assertTrue(status["ok"])
        self.assertEqual(status["checkpoint"], "123")
        self.assertTrue(status["summary"]["principal_shell_ready"])

    def test_render_text(self) -> None:
        text = self.cover.render_text()
        self.assertIn("K-ATLAS LOCAL OS", text)
        self.assertIn("PRINCIPAL SHELL", text)

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/123_K_Atlas_Principal_Shell_Cover.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
