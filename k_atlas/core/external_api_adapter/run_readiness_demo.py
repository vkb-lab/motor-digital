from __future__ import annotations

import json

from .readiness import ExternalAPIAdapterReadiness


if __name__ == "__main__":
    result = ExternalAPIAdapterReadiness().generate()
    print(json.dumps(result, ensure_ascii=False, indent=2))
