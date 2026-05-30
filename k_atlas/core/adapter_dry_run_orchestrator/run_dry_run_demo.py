from __future__ import annotations

import json

from .orchestrator import AdapterDryRunOrchestrator


if __name__ == "__main__":
    result = AdapterDryRunOrchestrator().run()
    print(json.dumps(result, ensure_ascii=False, indent=2))
