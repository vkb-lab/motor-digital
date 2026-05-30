from __future__ import annotations

import json

from .control_plane import KAtlasLocalControlPlane


if __name__ == "__main__":
    control_plane = KAtlasLocalControlPlane()
    report = control_plane.build_report({"mode": "recommend"})
    print(json.dumps(report, ensure_ascii=False, indent=2))
