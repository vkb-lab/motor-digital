from __future__ import annotations

import py_compile
import unittest
from pathlib import Path

class ProductSmokeTest(unittest.TestCase):
    def test_files_exist(self) -> None:
        self.assertTrue(Path("app.py").exists())
        self.assertTrue(Path("product.json").exists())
        self.assertTrue(Path("modules/core.py").exists())

    def test_compile(self) -> None:
        py_compile.compile("app.py", doraise=True)
        py_compile.compile("modules/core.py", doraise=True)

if __name__ == "__main__":
    unittest.main(verbosity=2)
