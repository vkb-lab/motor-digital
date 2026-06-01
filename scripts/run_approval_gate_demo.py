from pathlib import Path
import sys
import json
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from k_atlas.real_execution_gate import request_real_execution
result = request_real_execution("parada_atlantida", "instagram", "publish_instagram", {"demo": True})
(ROOT / "reports/KOS_PHASE7_APPROVAL_GATE_DEMO.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(result["status"])
