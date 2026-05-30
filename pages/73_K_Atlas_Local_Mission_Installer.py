from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.local_mission_installer.installer import LocalMissionInstaller


st.set_page_config(page_title="K-Atlas Local Mission Installer", layout="wide")

st.title("K-Atlas Local Mission Installer")
st.caption("Instalador local declarativo para reduzir blocos gigantes no chat.")

installer = LocalMissionInstaller()
summary = installer.summary()
metrics = summary.get("summary", {})

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Missoes", metrics.get("mission_queue_total", 0))

with col2:
    st.metric("Aguardando humano", metrics.get("waiting_human_mission_approval", 0))

with col3:
    st.metric("Aprovadas", metrics.get("approved_for_manual_install", 0))

with col4:
    st.metric("Execucao automatica", str(metrics.get("automatic_execution_allowed", False)))

st.divider()

tab_demo, tab_import, tab_review, tab_install, tab_report = st.tabs([
    "Demo",
    "Importar",
    "Revisar",
    "Instalar",
    "Relatorio",
])

with tab_demo:
    st.subheader("Criar missao demo")
    if st.button("Criar e importar missao demo", type="primary"):
        demo = installer.build_demo_mission()
        imported = installer.import_mission_file(demo["mission_path"])
        st.success("Missao demo criada e importada.")
        st.json({"demo": demo, "imported": imported})

with tab_import:
    st.subheader("Importar missao local")
    mission_path = st.text_input(
        "Caminho do arquivo .kmission.json",
        value="live/local_mission_installer/inbox/mission.kmission.json",
    )
    if st.button("Importar missao"):
        result = installer.import_mission_file(mission_path)
        st.json(result)

with tab_review:
    st.subheader("Dry-run e aprovacao humana")
    mission_id = st.text_input("Mission ID opcional", value="")

    if st.button("Rodar dry-run"):
        result = installer.dry_run(mission_id or None)
        st.json(result)

    approval_notes = st.text_area("Notas da aprovacao", value="Aprovacao humana supervisionada.")
    if st.button("Aprovar primeira missao valida"):
        result = installer.approve_mission(mission_id or None, "k_atlas_operator", approval_notes)
        st.json(result)

with tab_install:
    st.warning("Instala somente missoes aprovadas e apenas passos declarativos seguros.")
    approve = st.checkbox("Eu aprovo manualmente instalar a missao aprovada.")
    mission_id_install = st.text_input("Mission ID para instalar opcional", value="", key="install_id")

    if st.button("Instalar manualmente"):
        result = installer.install_manual({
            "human_approved": approve,
            "install_mode": "manual",
            "auto_execute": False,
            "real_execution_enabled": False,
            "external_api_enabled": False,
            "auto_publish": False,
            "auto_send": False,
            "auto_deploy": False,
            "browser_automation": False,
            "mouse_automation": False,
        }, mission_id_install or None)
        st.json(result)

with tab_report:
    st.subheader("Resumo")
    st.json(installer.summary())
