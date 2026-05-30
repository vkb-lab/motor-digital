from __future__ import annotations

import json
from .gate import RemoteTunnelGate

if __name__ == "__main__":
    gate = RemoteTunnelGate()
    item = gate.create_request({"provider": "manual", "start_tunnel": False, "public_exposure": False, "store_token": False})
    print(json.dumps(item, ensure_ascii=False, indent=2))
