from __future__ import annotations

import json
import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.assisted_autonomy.orchestrator import AssistedAutonomyOrchestrator
from k_atlas.core.assisted_autonomy.policy import validate_autonomy_payload


REPORT_JSON = Path("reports/assisted_autonomy/k_atlas_assisted_autonomy_v1.json")
REPORT_MD = Path("reports/assisted_autonomy/k_atlas_assisted_autonomy_v1.md")

st.set_page_config(page_title="K-Atlas Assisted Autonomy", layout="wide")

st.title("K-Atlas Assisted Autonomy v1")
st.caption("Orquestração assistida: valida, audita, simula, reporta e bloqueia riscos altos.")

latest = json.loads(REPORT_JSON.read_text(encoding="utf-8")) if REPORT_JSON.exists() else {}

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Status", latest.get("status", "none"))

with col2:
    st.metric("Autonomia", latest.get("autonomy_level", "none"))

with col3:
    st.metric("Módulos OK", f"{latest.get('metrics', {}).get('modules_ok', 0)}/{latest.get('metrics', {}).get('modules_total', 0)}")

with col4:
    st.metric("Smoke OK", f"{latest.get('metrics', {}).get('smoke_tests_ok', 0)}/{latest.get('metrics', {}).get('smoke_tests_total', 0)}")

st.divider()

tab_run, tab_report, tab_markdown = st.tabs(["Rodar autonomia", "Relatório JSON", "Relatório Markdown"])

with tab_run:
    st.subheader("Executar Assisted Autonomy v1")

    payload_text = st.text_area(
        "Payload JSON",
        value=json.dumps({
            "mode": "assisted_autonomy_v1",
            "official_publish": False,
            "auto_publish": False,
            "auto_deploy": False,
            "external_api_enabled": False,
            "mass_messaging": False,
            "browser_automation": False,
            "run_deep_checks": True
        }, ensure_ascii=False, indent=2),
        height=300,
    )

    if st.button("Rodar Autonomia Assistida", type="primary"):
        try:
            payload = json.loads(payload_text)
        except json.JSONDecodeError as exc:
            st.error(f"JSON inválido: {exc}")
        else:
            validation = validate_autonomy_payload(payload)
            if not validation["ok"]:
                st.error("Payload bloqueado pela política.")
                st.json(validation)
            else:
                result = AssistedAutonomyOrchestrator().run(payload, requested_by="streamlit_operator")
                if result["ok"]:
                    st.success("Autonomia assistida validada.")
                else:
                    st.warning("Autonomia assistida precisa de revisão.")
                st.json(result)

with tab_report:
    st.subheader("Último relatório JSON")

    if latest:
        st.json(latest)
    else:
        st.info("Nenhum relatório gerado ainda.")

with tab_markdown:
    st.subheader("Relatório Markdown")

    if REPORT_MD.exists():
        st.markdown(REPORT_MD.read_text(encoding="utf-8"))
    else:
        st.info("Nenhum relatório Markdown gerado ainda.")
