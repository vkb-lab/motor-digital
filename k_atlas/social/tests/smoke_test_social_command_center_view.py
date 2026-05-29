# -*- coding: utf-8 -*-
"""Smoke tests for K-Social Command Center UI."""

from __future__ import annotations

import py_compile
import unittest
from pathlib import Path


class TestSocialCommandCenterView(unittest.TestCase):
    """Validates command center view readiness."""

    def test_command_center_view_compiles(self) -> None:
        view_path = Path("k_atlas/social/ui/social_command_center_view.py")

        self.assertTrue(view_path.exists())
        py_compile.compile(str(view_path), doraise=True)

        content = view_path.read_text(encoding="utf-8")

        self.assertIn("render_social_command_center", content)
        self.assertIn("K-Social Command Center", content)
        self.assertIn("Auto publish", content)


if __name__ == "__main__":
    unittest.main(verbosity=2)
