from __future__ import annotations

import py_compile
import unittest
from pathlib import Path


class ControlPlanePageSmokeTest(unittest.TestCase):
    def test_control_plane_page_exists(self) -> None:
        self.assertTrue(Path("pages/09_K_Atlas_Control_Plane.py").exists())

    def test_control_plane_page_compiles(self) -> None:
        py_compile.compile("pages/09_K_Atlas_Control_Plane.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)