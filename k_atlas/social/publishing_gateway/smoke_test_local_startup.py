from __future__ import annotations

import unittest
from pathlib import Path


class LocalStartupSmokeTest(unittest.TestCase):
    def test_watchdog_script_exists(self) -> None:
        self.assertTrue(Path("ops/start_ksocial_gateway_forever.ps1").exists())

    def test_bat_launcher_exists(self) -> None:
        self.assertTrue(Path("ops/start_ksocial_gateway_local.bat").exists())

    def test_entrypoint_exists(self) -> None:
        self.assertTrue(Path("app_ksocial_gateway.py").exists())

    def test_requirements_has_streamlit(self) -> None:
        text = Path("requirements.txt").read_text(encoding="utf-8").lower()
        self.assertIn("streamlit", text)


if __name__ == "__main__":
    unittest.main(verbosity=2)