from __future__ import annotations

import json
import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.deploy_pipeline.pipeline import DeployPipelineAssistant
from k_atlas.core.deploy_pipeline.policy import validate_deploy_payload


REPORTS_ROOT = Path("reports/deploy_pipeline")
LATEST_REPORT = REPORTS_ROOT / "latest_deploy_pipeline_report.json"

st.set_page_config(page_title="K-Atlas Deploy Pipeline", layout="wide")

st.title("K-Atlas Deploy Pipeline")
st.caption("Deploy assistido, reversível e com revisão humana.")

reports = list(REPORTS_ROOT.glob("*.json")) if REPORTS_ROOT.exists() else []
latest = json.loads(LATEST_REPORT.read_text(encoding="utf-8")) if LATEST_REPORT.exists() else {}

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Relatórios", len(reports))

with col2:
    st.metric("Último status", latest.get("status", "none"))

with col3:
    st.metric("Auto deploy", "bloqueado")

st.divider()

tab_run, tab_latest, tab_history = st.tabs(["Rodar check", "Último relatório", "Histórico"])

with tab_run:
    st.subheader("Rodar Deploy Pipeline Assistido")

    payload_text = st.text_area(
        "Payload JSON",
        value=json.dumps({
            "target": "render",
            "service": "k-atlas-os",
            "auto_deploy": False,
            "force_push": False,
            "production_mutation": False,
            "official_publish": False
        }, ensure_ascii=False, indent=2),
        height=220,
    )

    if st.button("Rodar check de deploy", type="primary"):
        try:
            payload = json.loads(payload_text)
        except json.JSONDecodeError as exc:
            st.error(f"JSON inválido: {exc}")
        else:
            validation = validate_deploy_payload(payload)
            if not validation["ok"]:
                st.error("Payload bloqueado.")
                st.json(validation)
            else:
                result = DeployPipelineAssistant().run_assisted_check(payload)
                st.success("Deploy check gerado.")
                st.json(result)

with tab_latest:
    st.subheader("Último relatório")

    if not latest:
        st.info("Nenhum relatório ainda.")
    else:
        st.json(latest)

with tab_history:
    st.subheader("Histórico")

    if not reports:
        st.info("Nenhum relatório salvo.")
    else:
        for path in sorted(reports, key=lambda item: item.stat().st_mtime, reverse=True)[:50]:
            with st.expander(path.name):
                st.json(json.loads(path.read_text(encoding="utf-8")))
