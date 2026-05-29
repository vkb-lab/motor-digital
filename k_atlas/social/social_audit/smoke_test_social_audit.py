from __future__ import annotations

import py_compile
import unittest
from pathlib import Path


class SocialAuditSmokeTest(unittest.TestCase):
    def test_profile_audit_compiles(self) -> None:
        self.assertTrue(Path("k_atlas/social/social_audit/profile_audit.py").exists())
        py_compile.compile("k_atlas/social/social_audit/profile_audit.py", doraise=True)

    def test_streamlit_page_compiles(self) -> None:
        self.assertTrue(Path("pages/12_K_Atlas_Social_Audit_Local.py").exists())
        py_compile.compile("pages/12_K_Atlas_Social_Audit_Local.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)