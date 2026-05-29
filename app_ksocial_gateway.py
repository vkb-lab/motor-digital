from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.social.publishing_gateway.publishing_gateway_panel import render_social_publishing_gateway_panel

render_social_publishing_gateway_panel()