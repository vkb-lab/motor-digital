from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.kos_base.workspace import render_kos_base_workspace_panel


st.set_page_config(page_title="K-OS BASE Workspace", layout="wide")
render_kos_base_workspace_panel()
