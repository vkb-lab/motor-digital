from __future__ import annotations

import json
import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.ai_provider_router.router import AIProviderRouter
from k_atlas.core.ai_provider_router.policy import validate_router_payload


REPORT = Path("reports/ai_provider_router/latest_ai_provider_router.json")
MATRIX = Path("reports/ai_provider_router/latest_ai_provider_router_matrix.json")

st.set_page_config(page_title="K-Atlas AI Provider Router", layout="wide")

st.title("K-Atlas AI Provider Router")
st.caption("Roteia tarefas IA entre OpenAI, Google AI, Vertex e stub local. Sem chamada externa real.")

router = AIProviderRouter()

if st.button("Gerar matriz de rotas", type="primary"):
    result = router.build_matrix()
    st.success("Matriz gerada.")
    st.json(result)

latest = json.loads(REPORT.read_text(encoding="utf-8")) if REPORT.exists() else {}
matrix = json.loads(MATRIX.read_text(encoding="utf-8")) if MATRIX.exists() else {}

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Status", latest.get("status", "none"))

with col2:
    st.metric("Task", latest.get("task_type", "none"))

with col3:
    st.metric("Provider", latest.get("selected_provider", "none"))

with col4:
    st.metric("Live API", str(latest.get("live_call_enabled", False)))

st.divider()

tab_route, tab_matrix, tab_report = st.tabs(["Roteador", "Matriz", "Relatório"])

with tab_route:
    payload_text = st.text_area(
        "Payload",
        value=json.dumps(router.default_payload(), ensure_ascii=False, indent=2),
        height=300,
    )

    if st.button("Planejar rota"):
        try:
            payload = json.loads(payload_text)
        except json.JSONDecodeError as exc:
            st.error(f"JSON inválido: {exc}")
        else:
            validation = validate_router_payload(payload)
            if not validation["ok"]:
                st.error("Payload bloqueado pela política.")
                st.json(validation)
            else:
                result = router.route(payload)
                st.success("Rota planejada.")
                st.json(result)

with tab_matrix:
    if not matrix:
        st.info("Nenhuma matriz ainda.")
    else:
        for item in matrix.get("routes", []):
            with st.expander(f"{item.get('task_type')} -> {item.get('selected_provider')}"):
                st.json(item)

with tab_report:
    if latest:
        st.json(latest)
    else:
        st.info("Nenhum relatório ainda.")
