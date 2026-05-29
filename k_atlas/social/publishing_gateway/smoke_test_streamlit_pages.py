from __future__ import annotations

import py_compile
import unittest
from pathlib import Path


class StreamlitPagesSmokeTest(unittest.TestCase):
    def test_ksocial_page_exists(self) -> None:
        self.assertTrue(Path("pages/07_K_Social_Publishing_Gateway.py").exists())

    def test_stage_7_page_exists(self) -> None:
        self.assertTrue(Path("pages/08_Etapa_7_Independencia.py").exists())

    def test_pages_compile(self) -> None:
        py_compile.compile("pages/07_K_Social_Publishing_Gateway.py", doraise=True)
        py_compile.compile("pages/08_Etapa_7_Independencia.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)