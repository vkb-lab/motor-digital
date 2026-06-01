import streamlit as st
from k_atlas.ig_real_gate.readiness import inspect_ig_real_readiness

st.set_page_config(page_title="KOS Instagram Real Readiness", layout="wide")

st.title("KOS Instagram Real Readiness")
st.caption("Diagnostico da ponte real do Instagram. Nao exibe valores sensiveis.")

readiness = inspect_ig_real_readiness()

st.metric("Status", readiness["status"])
st.metric("Pode preparar", readiness["can_prepare"])
st.metric("Pode executar real", readiness["can_run_real"])
st.json(readiness)

st.warning("Para executar real, precisa das variaveis locais e OK humano final.")
