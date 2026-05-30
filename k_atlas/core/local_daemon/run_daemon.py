from __future__ import annotations

from .daemon import KAtlasLocalDaemon

if __name__ == "__main__":
    KAtlasLocalDaemon().run_forever()
