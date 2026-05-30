from __future__ import annotations

import json

from .installer import LocalMissionInstaller


if __name__ == "__main__":
    installer = LocalMissionInstaller()
    demo = installer.build_demo_mission()
    imported = installer.import_mission_file(demo["mission_path"])
    dry = installer.dry_run()
    result = {
        "demo": demo,
        "imported": imported,
        "dry_run": dry,
        "summary": installer.summary(),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
