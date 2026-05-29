# -*- coding: utf-8 -*-
"""Smoke tests for K-Social cockpit operation builder integration."""

from __future__ import annotations

import py_compile
import unittest
from pathlib import Path


class TestSocialCockpitBuilderIntegration(unittest.TestCase):
    """Validates cockpit builder integration without launching Streamlit."""

    def test_ui_file_contains_builder_entrypoint(self) -> None:
        ui_path = Path("k_atlas/social/ui/social_cockpit_view.py")

        self.assertTrue(ui_path.exists())
        py_compile.compile(str(ui_path), doraise=True)

        content = ui_path.read_text(encoding="utf-8")

        self.assertIn("render_social_operation_builder", content)
        self.assertIn("Nova operacao social", content)
        self.assertIn("run_from_request_data", content)
        self.assertIn("Publicacao automatica", content)

    def test_builder_file_contains_data_entrypoint(self) -> None:
        builder_path = Path("k_atlas/social/campaign_factory/social_operation_builder.py")

        self.assertTrue(builder_path.exists())
        py_compile.compile(str(builder_path), doraise=True)

        content = builder_path.read_text(encoding="utf-8")

        self.assertIn("run_from_request_data", content)
        self.assertIn("validate_request", content)
        self.assertIn("publication_permission", content)


if __name__ == "__main__":
    unittest.main(verbosity=2)
