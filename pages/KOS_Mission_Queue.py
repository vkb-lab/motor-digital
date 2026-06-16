import json
from pathlib import Path
import streamlit as st

from k_atlas.kaizen.mission_queue import create_mission, plan_mission, approve_mission, summarize_queue

st.set_page_config(page_title="KOS Mission Queue", layout="wide")

st.title("KOS Mission Queue")
st.caption("Fila de missoes com aprovacao humana. Nao executa acoes reais nesta fase.")

summary = summarize_queue()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total", summary["total"])
col2.metric("Draft", summary["draft"])
col3.metric("Planned", summary["planned"])
col4.metric("Execution allowed", summary["execution_allowed_count"])

st.subheader("Criar missao")
title = st.text_input("Titulo", value="Nova missao K-OS")
description = st.text_area("Descricao", value="Planejar uma melhoria segura sem executar automaticamente.")
priority = st.selectbox("Prioridade", ["high", "medium", "low"], index=1)

if st.button("Criar missao", use_container_width=True):
    mission = create_mission(title, description, priority)
    st.success(f"Missao criada: {mission['id']}")
    st.rerun()

st.subheader("Missoes")
summary = summarize_queue()
missions = summary.get("missions", [])

if not missions:
    st.info("Nenhuma missao criada ainda.")
else:
    for mission in missions:
        with st.expander(f"{mission.get('id')} - {mission.get('title')}"):
            st.json(mission)

            if st.button(f"Planejar {mission.get('id')}", key="plan_" + mission.get("id")):
                result = plan_mission(mission.get("id"))
                st.json(result)
                st.rerun()

            typed = st.text_input(
                "Confirmacao dry-run",
                key="approve_input_" + mission.get("id"),
                value=""
            )

            if st.button(f"Aprovar dry-run {mission.get('id')}", key="approve_" + mission.get("id")):
                result = approve_mission(mission.get("id"), typed)
                st.json(result)
                st.rerun()

st.warning("Esta pagina nao publica, nao chama IA paga e nao executa Codex automaticamente.")
