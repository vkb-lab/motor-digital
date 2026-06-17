
from pathlib import Path
import sys
import json
import argparse

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from k_atlas.kaizen.engineer_handoff_bridge import validate_engineer_command_file

parser = argparse.ArgumentParser()
parser.add_argument("-CommandFile", "--command-file", required=True)
args = parser.parse_args()

result = validate_engineer_command_file(args.command_file)
print(json.dumps(result, ensure_ascii=False, indent=2))
sys.exit(0 if result.get("valid") else 2)
