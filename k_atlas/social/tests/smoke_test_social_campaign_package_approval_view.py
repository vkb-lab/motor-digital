# -*- coding: utf-8 -*-
"""Smoke tests for K-Social package approval UI view."""

from __future__ import annotations

import py_compile
import unittest
from pathlib import Path


class TestSocialCampaignPackageApprovalView(unittest.TestCase):
    """Validates package approval view readiness."""

    def test_package_approval_view_compiles(self) -> None:
        view_path = Path("k_atlas/social/ui/social_campaign_package_approval_view.py")

        self.assertTrue(view_path.exists())
        py_compile.compile(str(view_path), doraise=True)

        content = view_path.read_text(encoding="utf-8")

        self.assertIn("render_social_campaign_package_approval_queue", content)
        self.assertIn("approved_for_manual_use", content)
        self.assertIn("Salvar aprovacao final", content)
        self.assertIn("Publicacao automatica", content)


if __name__ == "__main__":
    unittest.main(verbosity=2)
