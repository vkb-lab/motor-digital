from __future__ import annotations

import json

from .launcher import OneClickLauncher


if __name__ == "__main__":
    print(json.dumps(OneClickLauncher().build_launch_plan(), ensure_ascii=False, indent=2))
