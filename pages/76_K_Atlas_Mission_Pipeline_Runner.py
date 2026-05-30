from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.mission_pipeline_runner.runner import MissionPipelineRunner


st.set_page_config(page_title="K-Atlas Mission Pipeline Runner", layout="wide")

st.title("K-Atlas Mission Pipeline Runner")
st.caption("Pipeline: gerar mission pack -> converter para missao local -> instalar com aprovacao humana.")

runner = MissionPipelineRunner()
plan = runner.build_plan()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Pipeline ready", str(plan.get("ok", False)))

with col2:
    st.metric("Steps", len(plan.get("steps", [])))

with col3:
    st.metric("Execucao real", "False")

with col4:
    st.metric("Side effects", plan.get("external_side_effects", "none"))

st.divider()

tab_plan, tab_dry, tab_supervised, tab_report = st.tabs([
    "Plano",
    "Dry-run",
    "Supervisionado",
    "Relatorio",
])

with tab_plan:
    st.subheader("Componentes")
    st.json(plan.get("components", {}))

    st.subheader("Etapas")
    for step in plan.get("steps", []):
        with st.expander(f"{step.get('order')} | {step.get('name')} | ready={step.get('ready')}"):
            st.json(step)

with tab_dry:
    if st.button("Rodar dry-run", type="primary"):
        report = runner.dry_run({"mode": "dry_run"})
        st.success("Dry-run concluido. Nada foi instalado.")
        st.json(report)

with tab_supervised:
    st.warning("Este painel apenas registra supervisao. A execucao operacional usa ops/run_mission_pipeline.ps1.")
    approve = st.checkbox("Aprovacao humana para registrar execucao supervisionada.")
    install = st.checkbox("Registrar intencao de instalacao local.")
    if st.button("Registrar supervisao"):
        report = runner.run_supervised({
            "mode": "supervised",
            "human_approved": approve,
            "install": install,
            "auto_execute": False,
            "real_execution_enabled": False,
            "external_api_enabled": False,
            "auto_publish": False,
            "auto_send": False,
            "auto_deploy": False,
            "browser_automation": False,
            "mouse_automation": False,
        })
        st.json(report)

with tab_report:
    st.json(runner.dry_run({"mode": "dry_run"}))
