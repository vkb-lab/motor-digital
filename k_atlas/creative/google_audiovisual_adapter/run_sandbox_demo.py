from __future__ import annotations

import json

from .sandbox import GoogleAudiovisualAdapterSandbox


if __name__ == "__main__":
    result = GoogleAudiovisualAdapterSandbox().generate()
    print(json.dumps(result, ensure_ascii=False, indent=2))
