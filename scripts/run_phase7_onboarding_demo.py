from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from k_atlas.live_onboarding import generate_client_onboarding
print(generate_client_onboarding("parada_atlantida")["status"])
