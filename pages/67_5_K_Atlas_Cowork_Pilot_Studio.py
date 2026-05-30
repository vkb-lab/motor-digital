from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.cowork_pilot_studio.recorder import CoworkStoryRecorder
from k_atlas.core.cowork_pilot_studio.studio import CoworkPilotStudio


st.set_page_config(page_title="K-Atlas Cowork Pilot Studio", layout="wide")

st.title("K-Atlas Cowork Pilot Studio")
st.caption("Lousa operacional: comando na esquerda, retorno na direita, historia embaixo.")

studio = CoworkPilotStudio()
recorder = CoworkStoryRecorder()
state = studio.collect_state()
recorder_report = recorder.save_report()

col_a, col_b, col_c, col_d = st.columns(4)

with col_a:
    st.metric("Checkpoint", state.get("checkpoint"))

with col_b:
    st.metric("Status", state.get("status"))

with col_c:
    st.metric("FFmpeg", str(recorder_report.get("tools", {}).get("ffmpeg_available", False)))

with col_d:
    st.metric("OBS", str(recorder_report.get("tools", {}).get("obs_available", False)))

st.divider()

left, right = st.columns(2)

with left:
    st.subheader("Esquerda: comando / plano")
    script_path = state.get("latest_runner_script_path")
    if script_path:
        st.caption(script_path)
    st.code(state.get("latest_runner_script") or "Nenhum script do runner encontrado ainda.", language="powershell")

with right:
    st.subheader("Direita: retorno / logs")
    log_path = state.get("latest_runner_log_path")
    if log_path:
        st.caption(log_path)
    st.code(state.get("latest_runner_log") or "Nenhum log do runner encontrado ainda.", language="text")

st.divider()

tab_story, tab_reports, tab_git, tab_recording = st.tabs(["Story", "Reports", "Git", "Gravacao"])

with tab_story:
    st.subheader("Timeline da operacao")
    events = recorder.read_events()
    if not events:
        st.info("Nenhum evento registrado ainda.")
    else:
        for event in reversed(events):
            with st.expander(f"{event.get('timestamp')} | {event.get('title')}"):
                st.json(event)

    title = st.text_input("Titulo do evento", value="Marco operacional K-Atlas")
    details = st.text_area("Detalhes", value="Evento observado durante cowork supervisionado.")

    if st.button("Registrar evento na historia"):
        event = recorder.log_event(
            event_type="manual_story",
            title=title,
            details=details,
        )
        st.success("Evento registrado.")
        st.json(event)

with tab_reports:
    st.subheader("Sinais dos modulos")
    for item in state.get("report_signals", []):
        with st.expander(f"{item.get('path')} | {item.get('status')}"):
            st.json(item)

with tab_git:
    st.subheader("Git status")
    st.code(state.get("git_status") or "limpo", language="text")
    st.subheader("Git log")
    st.code(state.get("git_log") or "", language="text")

with tab_recording:
    st.subheader("Gravacao supervisionada")
    st.write("A gravacao fica fora da logica critica. Use o script PowerShell abaixo.")
    st.code('powershell -ExecutionPolicy Bypass -File "C:\\Users\\oi\\Desktop\\motor-digital\\ops\\start_cowork_story_recording.ps1" -Mode ffmpeg', language="powershell")
    st.json(recorder_report.get("tools", {}))
