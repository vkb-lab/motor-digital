from __future__ import annotations

import json

from .registry import LiveAdapterContractRegistry


if __name__ == "__main__":
    result = LiveAdapterContractRegistry().register_contracts()
    print(json.dumps(result, ensure_ascii=False, indent=2))
