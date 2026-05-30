from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.mission_pack_generator.generator import MissionPackGenerator


st.set_page_config(page_title="K-Atlas Mission Pack Generator", layout="wide")

st.title("K-Atlas Mission Pack Generator")
st.caption("Gera pacotes de missao local validados. Nao executa nada automaticamente.")

generator = MissionPackGenerator()
summary = generator.summary()
metrics = summary.get("summary", {})

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Packs gerados", metrics.get("generated_packs_total", 0))

with col2:
    st.metric("Latest pack", str(metrics.get("latest_pack_exists", False)))

with col3:
    st.metric("Auto execute", "False")

with col4:
    st.metric("Side effects", "none")

st.divider()

tab_generate, tab_latest, tab_report = st.tabs(["Gerar pack", "Ultimo pack", "Resumo"])

with tab_generate:
    st.subheader("Nova missao local declarativa")
    objective = st.text_input(
        "Objetivo",
        value="Criar relatorio operacional seguro",
    )
    target_path = st.text_input(
        "Arquivo alvo seguro",
        value="reports/autoprog_generated/generated_from_dashboard.md",
    )

    if st.button("Gerar mission pack", type="primary"):
        result = generator.generate_pack(objective=objective, target_path=target_path)
        if result.get("ok"):
            st.success("Mission pack gerado. Nenhuma execucao real foi feita.")
        else:
            st.error("Mission pack gerado, mas bloqueado pela policy.")
        st.json(result)

with tab_latest:
    st.subheader("Ultimo pacote")
    st.json(generator.summary().get("latest_pack"))

with tab_report:
    st.subheader("Resumo")
    st.json(generator.summary())
