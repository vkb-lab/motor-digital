from pathlib import Path
import sys
import json
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from k_atlas.live_onboarding.readiness_matrix import build_readiness_matrix
result = build_readiness_matrix("parada_atlantida")
(ROOT / "reports/KOS_PHASE7_LIVE_READINESS_MATRIX.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(result["status"])
