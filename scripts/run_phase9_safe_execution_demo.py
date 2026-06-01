from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from k_atlas.safe_execution import run_approved_safe_execution

result = run_approved_safe_execution()
print(result["status"])
