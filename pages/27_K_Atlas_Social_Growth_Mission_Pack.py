from __future__ import annotations

import json
import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.social.growth_mission_pack.pack import SocialGrowthMissionPack
from k_atlas.social.growth_mission_pack.policy import validate_social_growth_payload


REPORT = Path("reports/social_growth_mission_pack/latest_social_growth_mission_pack.json")

st.set_page_config(page_title="K-Atlas Social Growth Mission Pack", layout="wide")

st.title("K-Atlas Social Growth Mission Pack")
st.caption("Planejamento social do K-Atlas: calendário, criativos, missão e governança. Sem publicação automática.")

pack = SocialGrowthMissionPack()
latest = json.loads(REPORT.read_text(encoding="utf-8")) if REPORT.exists() else {}

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Status", latest.get("status", "none"))

with col2:
    st.metric("Canal", latest.get("payload", {}).get("channel", "none") if latest else "none")

with col3:
    st.metric("Posts", len(latest.get("calendar", [])) if latest else 0)

with col4:
    st.metric("Criativos", len(latest.get("creative_briefs", [])) if latest else 0)

st.divider()

tab_create, tab_calendar, tab_creatives, tab_report = st.tabs(["Gerar pack", "Calendário", "Criativos", "Relatório"])

with tab_create:
    payload_text = st.text_area(
        "Payload",
        value=json.dumps(pack.default_payload(), ensure_ascii=False, indent=2),
        height=380,
    )

    enqueue = st.checkbox("Enviar missão para o Mission Planner / Command Center", value=True)

    if st.button("Gerar Social Growth Mission Pack", type="primary"):
        try:
            payload = json.loads(payload_text)
        except json.JSONDecodeError as exc:
            st.error(f"JSON inválido: {exc}")
        else:
            validation = validate_social_growth_payload(payload)
            if not validation["ok"]:
                st.error("Payload bloqueado pela política.")
                st.json(validation)
            else:
                result = pack.generate(payload, enqueue_mission=enqueue)
                st.success("Social Growth Mission Pack gerado.")
                st.json(result)

with tab_calendar:
    if not latest:
        st.info("Nenhum pack gerado ainda.")
    else:
        for item in latest.get("calendar", []):
            with st.expander(f"Dia {item.get('day')} | {item.get('format')} | {item.get('theme')}"):
                st.json(item)

with tab_creatives:
    if not latest:
        st.info("Nenhum criativo planejado ainda.")
    else:
        for item in latest.get("creative_briefs", []):
            with st.expander(item.get("asset", "asset")):
                st.json(item)

with tab_report:
    if latest:
        st.json(latest)
    else:
        st.info("Nenhum relatório ainda.")
