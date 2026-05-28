# -*- coding: utf-8 -*-
"""Smoke test for standalone K-Social Streamlit app file.

This test avoids launching Streamlit.
It verifies that the app file exists, compiles and exposes the expected functions.
"""

from __future__ import annotations

import py_compile
import unittest
from pathlib import Path


class TestSocialCockpitStandaloneApp(unittest.TestCase):
    """Validates standalone Streamlit app readiness."""

    def test_app_file_exists_and_compiles(self) -> None:
        app_path = Path("k_atlas/social/ui/social_cockpit_app.py")

        self.assertTrue(app_path.exists())
        py_compile.compile(str(app_path), doraise=True)

        content = app_path.read_text(encoding="utf-8")

        self.assertIn("def main()", content)
        self.assertIn("ensure_snapshot_exists", content)
        self.assertIn("render_social_cockpit", content)
        self.assertIn("sem publicacao automatica", content)


if __name__ == "__main__":
    unittest.main(verbosity=2)
