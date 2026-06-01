import streamlit as st
from k_atlas.ig_live_check.final_live_check import build_final_live_check

st.set_page_config(page_title="KOS Instagram Final Live Check", layout="wide")

st.title("KOS Instagram Final Live Check")
st.caption("Checklist final antes do primeiro post real.")

check = build_final_live_check(load_runtime=True)

st.metric("Status", check["status"])
st.metric("Pronto para real", check["ready_for_real_first_post"])
st.json(check)

if check["ready_for_real_first_post"]:
    st.success("Ambiente pronto. A Fase 14 pode executar o primeiro post real com confirmacao final.")
else:
    st.warning("Ainda bloqueado. Preencha local_runtime/ig_runtime.env e depois rode a Fase 14.")
