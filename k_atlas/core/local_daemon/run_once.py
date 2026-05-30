from __future__ import annotations

import json
from .daemon import KAtlasLocalDaemon

if __name__ == "__main__":
    print(json.dumps(KAtlasLocalDaemon().tick(manage=False), ensure_ascii=False, indent=2))
