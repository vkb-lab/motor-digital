import streamlit as st
from k_atlas.ig_real_gate.readiness import inspect_ig_real_readiness
from k_atlas.ig_first_post.arming_gate import inspect_phase12_arming

st.set_page_config(page_title="KOS Instagram Final Arming Check", layout="wide")

st.title("KOS Instagram Final Arming Check")
st.caption("Checklist final antes de qualquer publicacao real.")

readiness = inspect_ig_real_readiness()
arming = inspect_phase12_arming()

st.subheader("Instagram readiness")
st.json(readiness)

st.subheader("Phase 12 arming")
st.json(arming)

ready = readiness.get("can_run_real") and arming.get("armed")

st.metric("Pronto para real", ready)

if ready:
    st.success("Ambiente armado. Executar somente com revisao humana final.")
else:
    st.warning("Ainda bloqueado. Isso e esperado ate configurar ambiente e armar a execucao.")
