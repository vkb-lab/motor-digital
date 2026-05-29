# -*- coding: utf-8 -*-
"""Smoke tests for K-Social content refinement UI view."""

from __future__ import annotations

import py_compile
import unittest
from pathlib import Path


class TestSocialContentRefinementView(unittest.TestCase):
    """Validates content refinement view readiness without launching Streamlit."""

    def test_refinement_view_compiles(self) -> None:
        view_path = Path("k_atlas/social/ui/social_content_refinement_view.py")

        self.assertTrue(view_path.exists())
        py_compile.compile(str(view_path), doraise=True)

        content = view_path.read_text(encoding="utf-8")

        self.assertIn("render_social_content_refinement_queue", content)
        self.assertIn("Fila de refinamento criativo", content)
        self.assertIn("Imagem IA", content)
        self.assertIn("Publicacao automatica", content)


if __name__ == "__main__":
    unittest.main(verbosity=2)
