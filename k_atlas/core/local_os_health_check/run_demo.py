from __future__ import annotations

import json

from .health import LocalOSHealthCheck


if __name__ == "__main__":
    print(json.dumps(LocalOSHealthCheck().collect(), ensure_ascii=False, indent=2))
