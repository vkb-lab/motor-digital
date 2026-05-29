# -*- coding: utf-8 -*-
"""Smoke tests for K-Social approval queue UI view."""

from __future__ import annotations

import py_compile
import unittest
from pathlib import Path


class TestSocialApprovalView(unittest.TestCase):
    """Validates approval view readiness without launching Streamlit."""

    def test_approval_view_compiles(self) -> None:
        view_path = Path("k_atlas/social/ui/social_approval_view.py")

        self.assertTrue(view_path.exists())
        py_compile.compile(str(view_path), doraise=True)

        content = view_path.read_text(encoding="utf-8")

        self.assertIn("render_social_approval_queue", content)
        self.assertIn("approved_for_content_refinement", content)
        self.assertIn("Publicacao automatica", content)
        self.assertIn("Salvar decisao", content)


if __name__ == "__main__":
    unittest.main(verbosity=2)
