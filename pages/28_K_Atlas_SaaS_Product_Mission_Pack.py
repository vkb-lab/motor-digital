from __future__ import annotations

import json
import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.saas_factory.product_mission_pack.pack import SaasProductMissionPack
from k_atlas.saas_factory.product_mission_pack.policy import validate_saas_product_payload


REPORT = Path("reports/saas_product_mission_pack/latest_saas_product_mission_pack.json")

st.set_page_config(page_title="K-Atlas SaaS Product Mission Pack", layout="wide")

st.title("K-Atlas SaaS Product Mission Pack")
st.caption("Transforma ideia de SaaS em MVP, landing, monetização e missão para o Command Center.")

pack = SaasProductMissionPack()
latest = json.loads(REPORT.read_text(encoding="utf-8")) if REPORT.exists() else {}

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Status", latest.get("status", "none"))

with col2:
    st.metric("Produto", latest.get("payload", {}).get("product_name", "none") if latest else "none")

with col3:
    st.metric("Módulos", len(latest.get("mvp_modules", [])) if latest else 0)

with col4:
    st.metric("Missão", latest.get("mission_result", {}).get("status", "none") if latest else "none")

st.divider()

tab_create, tab_modules, tab_landing, tab_money, tab_report = st.tabs([
    "Gerar pack",
    "MVP",
    "Landing",
    "Monetização",
    "Relatório",
])

with tab_create:
    payload_text = st.text_area(
        "Payload",
        value=json.dumps(pack.default_payload(), ensure_ascii=False, indent=2),
        height=420,
    )

    enqueue = st.checkbox("Enviar missão para Mission Planner / Command Center", value=True)

    if st.button("Gerar SaaS Product Mission Pack", type="primary"):
        try:
            payload = json.loads(payload_text)
        except json.JSONDecodeError as exc:
            st.error(f"JSON inválido: {exc}")
        else:
            validation = validate_saas_product_payload(payload)
            if not validation["ok"]:
                st.error("Payload bloqueado pela política.")
                st.json(validation)
            else:
                result = pack.generate(payload, enqueue_mission=enqueue)
                st.success("SaaS Product Mission Pack gerado.")
                st.json(result)

with tab_modules:
    if not latest:
        st.info("Nenhum pack gerado ainda.")
    else:
        for item in latest.get("mvp_modules", []):
            with st.expander(f"{item.get('priority')} | {item.get('name')}"):
                st.json(item)

with tab_landing:
    if latest:
        st.json(latest.get("landing_spec", {}))
    else:
        st.info("Nenhuma landing planejada ainda.")

with tab_money:
    if latest:
        st.json(latest.get("monetization", {}))
    else:
        st.info("Nenhuma monetização planejada ainda.")

with tab_report:
    if latest:
        st.json(latest)
    else:
        st.info("Nenhum relatório ainda.")
