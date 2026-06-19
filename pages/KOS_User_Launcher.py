from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]

def read_json(path: Path) -> dict:
    if not path.exists():
        return {"status": "FILE_NOT_FOUND", "path": str(path)}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        return {"status": "READ_FAILED", "error": str(exc), "path": str(path)}

st.set_page_config(page_title="K-OS User Launcher", layout="wide")

st.title("K-OS User Launcher")

st.caption("Use o K-OS em poucos minutos. Acoes perigosas continuam bloqueadas por governanca.")

st.subheader("Abertura rapida")

st.code("powershell -ExecutionPolicy Bypass -File scripts\\start_kos_user_launcher.ps1 -Mode status", language="powershell")
st.code("powershell -ExecutionPolicy Bypass -File scripts\\start_kos_user_launcher.ps1 -Mode dashboard", language="powershell")
st.code("powershell -ExecutionPolicy Bypass -File scripts\\start_kos_user_launcher.ps1 -Mode market-radar", language="powershell")

st.subheader("Enviar comando seguro")

st.code('powershell -ExecutionPolicy Bypass -File scripts\\start_kos_user_launcher.ps1 -Mode operator-command -Text "registrar healthcheck operacional"', language="powershell")

st.subheader("Executar missao segura")

st.code('powershell -ExecutionPolicy Bypass -File scripts\\start_kos_user_launcher.ps1 -Mode mission -MissionText "verificar K-OS" -Objectives @("registrar runtime","registrar autonomia segura")', language="powershell")

st.subheader("Enfileirar missao")

st.code('powershell -ExecutionPolicy Bypass -File scripts\\start_kos_user_launcher.ps1 -Mode queue-mission -MissionText "missao automatica segura" -Objectives @("registrar fila","registrar autonomia")', language="powershell")

st.subheader("Kill Switch")

st.warning("Kill Switch deve ser acionado manualmente e de forma consciente.")

st.code('powershell -ExecutionPolicy Bypass -File scripts\\kos_autonomy_kill_switch.ps1 -Action engage -Reason "operator emergency stop"', language="powershell")
st.code('powershell -ExecutionPolicy Bypass -File scripts\\kos_autonomy_kill_switch.ps1 -Action disengage -Reason "operator restore" -RestartRuntime', language="powershell")

st.subheader("Agent OS Market Radar")

st.json(read_json(ROOT / "local_runtime" / "kos_agent_os_market" / "latest_market_radar_snapshot.json"))


# KOS_PHASE69E2_PUBLISH_AUDIT_PANEL_START
st.subheader("Publish Audit Panel")
st.code("powershell -ExecutionPolicy Bypass -File scripts\\open_kos_publish_audit_panel.ps1", language="powershell")
st.caption("Painel visual de auditoria Hupmix. Nao publica e nao usa POST.")
# KOS_PHASE69E2_PUBLISH_AUDIT_PANEL_END
