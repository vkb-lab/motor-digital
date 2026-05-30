from __future__ import annotations

import json

from .validation import MVPValidationReport


if __name__ == "__main__":
    print(json.dumps(MVPValidationReport().build_report(), ensure_ascii=False, indent=2))
