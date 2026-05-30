from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.auto_update_notification_bridge.notification_bridge import AutoUpdateNotificationBridge

st.set_page_config(page_title="K-Atlas Update Notification", layout="wide")
st.title("K-Atlas Auto Update Notification Bridge")

bridge = AutoUpdateNotificationBridge()
status = st.selectbox("Status", ["ok", "erro", "info"])
message = st.text_input("Mensagem", value="ok")

if st.button("Gerar notificacao"):
    st.json(bridge.build_notification(status, message))
