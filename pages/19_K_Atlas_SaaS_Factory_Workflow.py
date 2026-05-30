from __future__ import annotations

import json
import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.saas_factory.workflows.factory_workflow import SaaSFactoryWorkflowRunner
from k_atlas.saas_factory.workflows.workflow_spec import build_default_saas_workflow_payload, validate_saas_workflow_payload


REPORTS_ROOT = Path("reports/saas_factory/workflows")
LATEST_REPORT = REPORTS_ROOT / "latest_saas_factory_workflow.json"

st.set_page_config(page_title="K-Atlas SaaS Factory Workflow", layout="wide")

st.title("K-Atlas SaaS Factory Workflow")
st.caption("Workflow real para criar MVP SaaS supervisionado.")

reports = list(REPORTS_ROOT.glob("*.json")) if REPORTS_ROOT.exists() else []
latest = json.loads(LATEST_REPORT.read_text(encoding="utf-8")) if LATEST_REPORT.exists() else {}

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Relatórios", len(reports))

with col2:
    st.metric("Último status", latest.get("status", "none"))

with col3:
    st.metric("Deploy", "supervisionado")

st.divider()

tab_run, tab_latest, tab_reports = st.tabs(["Rodar workflow", "Último relatório", "Histórico"])

with tab_run:
    st.subheader("Criar MVP via SaaS Factory")

    default_payload = build_default_saas_workflow_payload()

    payload_text = st.text_area(
        "Payload JSON",
        value=json.dumps(default_payload, ensure_ascii=False, indent=2),
        height=360,
    )

    if st.button("Rodar SaaS Factory Workflow", type="primary"):
        try:
            payload = json.loads(payload_text)
        except json.JSONDecodeError as exc:
            st.error(f"JSON inválido: {exc}")
        else:
            validation = validate_saas_workflow_payload(payload)
            if not validation["ok"]:
                st.error("Payload bloqueado pela política.")
                st.json(validation)
            else:
                result = SaaSFactoryWorkflowRunner().run(payload, requested_by="streamlit_operator")
                if result["ok"]:
                    st.success("Workflow SaaS concluído.")
                else:
                    st.error("Workflow falhou.")
                st.json(result)

with tab_latest:
    st.subheader("Último relatório")

    if not latest:
        st.info("Nenhum workflow executado ainda.")
    else:
        st.json(latest)

with tab_reports:
    st.subheader("Histórico")

    if not reports:
        st.info("Nenhum relatório salvo.")
    else:
        for path in sorted(reports, key=lambda item: item.stat().st_mtime, reverse=True)[:50]:
            with st.expander(path.name):
                st.json(json.loads(path.read_text(encoding="utf-8")))
