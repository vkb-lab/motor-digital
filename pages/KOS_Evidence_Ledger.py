import streamlit as st

from k_atlas.kaizen.evidence_ledger import append_evidence, summarize_evidence

st.set_page_config(page_title="KOS Evidence Ledger", layout="wide")

st.title("KOS Autonomy Evidence Ledger")
st.caption("Historico auditavel local dos ciclos autonomos do K-OS.")

summary = summarize_evidence(limit=20)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Ledger", "SIM" if summary.get("ledger_exists") else "NAO")
col2.metric("Entries", summary.get("entries_returned", 0))
col3.metric("Health", summary.get("latest_health_status", "N/A"))
col4.metric("Risk", summary.get("latest_risk_level", "N/A"))

if st.button("Registrar evidencia agora", use_container_width=True):
    entry = append_evidence(source="streamlit_manual", note="Registro manual pelo cockpit.")
    st.json(entry)
    st.rerun()

st.subheader("Resumo")
st.json(summary)

st.warning("Ledger local read-only/append-only. Nao publica, nao usa IA paga e nao executa Codex.")
