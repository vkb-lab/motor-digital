from pathlib import Path
import sys
import json

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from k_atlas.launch_sandbox import run_launch_sandbox

result = run_launch_sandbox()
out = ROOT / "reports" / "KOS_PHASE8_LAUNCH_SANDBOX_DEMO.json"
out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(result["status"])
