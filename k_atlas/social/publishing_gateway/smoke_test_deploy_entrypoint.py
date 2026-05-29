from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


class DeployEntrypointSmokeTest(unittest.TestCase):
    def test_app_entrypoint_exists(self) -> None:
        self.assertTrue(Path("app_ksocial_gateway.py").exists())

    def test_render_yaml_exists(self) -> None:
        self.assertTrue(Path("render.yaml").exists())

    def test_local_ops_scripts_exist(self) -> None:
        self.assertTrue(Path("ops/run_ksocial_gateway_local.ps1").exists())
        self.assertTrue(Path("ops/install_ksocial_startup_task.ps1").exists())

    def test_streamlit_dependency_declared(self) -> None:
        text = Path("requirements.txt").read_text(encoding="utf-8").lower()
        self.assertIn("streamlit", text)

    def test_entrypoint_importable(self) -> None:
        spec = importlib.util.spec_from_file_location("app_ksocial_gateway", "app_ksocial_gateway.py")
        self.assertIsNotNone(spec)


if __name__ == "__main__":
    unittest.main(verbosity=2)