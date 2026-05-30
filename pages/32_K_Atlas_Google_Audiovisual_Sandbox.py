from __future__ import annotations

import json
import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.creative.google_audiovisual_adapter.policy import validate_audiovisual_payload
from k_atlas.creative.google_audiovisual_adapter.sandbox import GoogleAudiovisualAdapterSandbox


REPORT = Path("reports/google_audiovisual_adapter/latest_google_audiovisual_adapter_sandbox.json")

st.set_page_config(page_title="K-Atlas Google Audiovisual Sandbox", layout="wide")

st.title("K-Atlas Google Audiovisual Adapter Sandbox")
st.caption("Prompts, shotlists e specs audiovisuais. Sem chamada externa real.")

adapter = GoogleAudiovisualAdapterSandbox()
latest = json.loads(REPORT.read_text(encoding="utf-8")) if REPORT.exists() else {}

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Status", latest.get("status", "none"))

with col2:
    st.metric("Asset", latest.get("payload", {}).get("asset_format", "none") if latest else "none")

with col3:
    st.metric("Provider", latest.get("router", {}).get("selected_provider", "none") if latest else "none")

with col4:
    st.metric("Live API", str(latest.get("live_call_enabled", False)))

st.divider()

tab_generate, tab_prompts, tab_shots, tab_report = st.tabs(["Gerar sandbox", "Prompts", "Shotlist", "Relatório"])

with tab_generate:
    payload_text = st.text_area(
        "Payload audiovisual",
        value=json.dumps(adapter.default_payload(), ensure_ascii=False, indent=2),
        height=420,
    )

    if st.button("Gerar audiovisual sandbox", type="primary"):
        try:
            payload = json.loads(payload_text)
        except json.JSONDecodeError as exc:
            st.error(f"JSON inválido: {exc}")
        else:
            validation = validate_audiovisual_payload(payload)
            if not validation["ok"]:
                st.error("Payload bloqueado pela política.")
                st.json(validation)
            else:
                result = adapter.generate(payload)
                st.success("Sandbox audiovisual gerado.")
                st.json(result)

with tab_prompts:
    if not latest:
        st.info("Nenhum sandbox gerado ainda.")
    else:
        st.subheader("Video prompt")
        st.code(latest.get("video_prompt", ""), language="text")

        st.subheader("Image prompt")
        st.code(latest.get("image_prompt", ""), language="text")

with tab_shots:
    if not latest:
        st.info("Nenhum shotlist ainda.")
    else:
        for item in latest.get("shotlist", []):
            with st.expander(f"Shot {item.get('shot')} | {item.get('duration')}"):
                st.json(item)

with tab_report:
    if latest:
        st.json(latest)
    else:
        st.info("Nenhum relatório ainda.")
