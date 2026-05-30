from __future__ import annotations

import json

from .readiness import WhatsAppCloudReadiness


if __name__ == "__main__":
    result = WhatsAppCloudReadiness().generate()
    print(json.dumps(result, ensure_ascii=False, indent=2))
