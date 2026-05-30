from __future__ import annotations

import json

from .manager import StartupManager


if __name__ == "__main__":
    print(json.dumps(StartupManager().build_config(), ensure_ascii=False, indent=2))
