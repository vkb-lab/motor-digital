from __future__ import annotations

import json

from .ledger import LocalApiAuditLedger


if __name__ == "__main__":
    ledger = LocalApiAuditLedger()
    ledger.append("demo.local_api_audit_ledger", {"status": "ok"})
    print(json.dumps(ledger.summary(), ensure_ascii=False, indent=2, sort_keys=True))
