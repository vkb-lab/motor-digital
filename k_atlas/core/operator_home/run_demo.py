from __future__ import annotations

import json

from .home import OperatorHome


if __name__ == "__main__":
    print(json.dumps(OperatorHome().build_home(), ensure_ascii=False, indent=2))
