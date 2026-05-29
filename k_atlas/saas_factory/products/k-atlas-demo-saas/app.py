from __future__ import annotations

import streamlit as st

from modules.core import load_state, summarize_product

st.set_page_config(page_title="K-Atlas Demo SaaS", layout="wide")
st.title("K-Atlas Demo SaaS")
st.caption("MVP gerado pelo K-Atlas SaaS Builder Agent.")

state = load_state()
summary = summarize_product()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Leads hoje", state.get("metrics", {}).get("leads_today", 0))

with col2:
    st.metric("Receita semana", state.get("metrics", {}).get("revenue_week", 0))

with col3:
    st.metric("Tarefas pendentes", state.get("metrics", {}).get("pending_tasks", 0))

st.divider()
st.subheader("Resumo")
st.json(summary)
st.subheader("Modulos planejados")
st.json(['dashboard', 'lead_capture', 'campaigns', 'reports', 'admin'])
