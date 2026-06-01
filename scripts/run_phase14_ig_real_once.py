from pathlib import Path
import sys
import argparse

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from k_atlas.ig_final_run import build_phase14_final_package, execute_phase14_if_confirmed

parser = argparse.ArgumentParser()
parser.add_argument("--execute-real-confirmed", action="store_true")
parser.add_argument("--typed-confirmation", default="")
parser.add_argument("--image-url", default="https://placehold.co/1080x1080/png")
parser.add_argument("--caption", default="Primeiro teste controlado preparado pelo K-OS.")
args = parser.parse_args()

package = build_phase14_final_package(
    image_url=args.image_url,
    caption=args.caption,
    load_runtime=True,
)

result = execute_phase14_if_confirmed(
    package,
    typed_confirmation=args.typed_confirmation,
    execute_real_confirmed=args.execute_real_confirmed,
)

print(result["status"])
print("real_action_executed:", result.get("real_action_executed"))
print("external_call_executed:", result.get("external_call_executed"))
