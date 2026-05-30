from __future__ import annotations

import json
import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

HEARTBEAT = Path("memory/local_daemon/heartbeat.json")
EVENTS = Path("memory/local_daemon/events.jsonl")

st.set_page_config(page_title="K-Atlas Local Daemon 24/7", layout="wide")

st.title("K-Atlas Local Daemon 24/7")
st.caption("Streamlit + Runner local + heartbeat + sync Git/Render.")

heartbeat = json.loads(HEARTBEAT.read_text(encoding="utf-8")) if HEARTBEAT.exists() else {}

services = heartbeat.get("services", {})
public = heartbeat.get("public", {})

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Daemon", heartbeat.get("status", "offline"))

with col2:
    st.metric("Streamlit", services.get("streamlit", {}).get("status", "unknown"))

with col3:
    st.metric("Runner", services.get("blackboard_runner", {}).get("status", "unknown"))

with col4:
    st.metric("Render", public.get("status", "unknown"))

st.divider()

tab_status, tab_events, tab_commands = st.tabs(["Status", "Eventos", "Comandos"])

with tab_status:
    if heartbeat:
        st.json(heartbeat)
    else:
        st.warning("Nenhum heartbeat. Inicie o daemon local.")

with tab_events:
    if not EVENTS.exists():
        st.info("Sem eventos ainda.")
    else:
        rows = []
        for line in EVENTS.read_text(encoding="utf-8").splitlines()[-60:]:
            if line.strip():
                rows.append(json.loads(line))
        for row in reversed(rows):
            with st.expander(row.get("timestamp", "evento")):
                st.json(row)

with tab_commands:
    st.code('powershell -ExecutionPolicy Bypass -File "C:\\Users\\oi\\Desktop\\motor-digital\\ops\\start_k_atlas_daemon_window.ps1"', language="powershell")
    st.code('powershell -ExecutionPolicy Bypass -File "C:\\Users\\oi\\Desktop\\motor-digital\\ops\\stop_k_atlas_daemon.ps1"', language="powershell")
    st.code('powershell -ExecutionPolicy Bypass -File "C:\\Users\\oi\\Desktop\\motor-digital\\ops\\install_k_atlas_daemon_startup.ps1"', language="powershell")
