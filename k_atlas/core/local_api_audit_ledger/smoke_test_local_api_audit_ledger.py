from __future__ import annotations

import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path

from k_atlas.core.local_api_audit_ledger.ledger import LocalApiAuditLedger


class LocalApiAuditLedgerSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="k_api_audit_"))
        self.ledger = LocalApiAuditLedger(project_root=self.tmp)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_append(self) -> None:
        row = self.ledger.append("test.event", {"ok": True})
        self.assertEqual(row["event_type"], "test.event")
        self.assertTrue((self.tmp / "memory" / "local_api_audit_ledger" / "api_audit_ledger.jsonl").exists())

    def test_summary(self) -> None:
        self.ledger.append("test.event", {})
        summary = self.ledger.summary()
        self.assertEqual(summary["summary"]["audit_events_total"], 1)

    def test_page_compiles(self) -> None:
        py_compile.compile("pages/92_K_Atlas_API_Audit_Ledger.py", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
