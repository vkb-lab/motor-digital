from __future__ import annotations

import json
import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.live_adapter_contract_registry.registry import LiveAdapterContractRegistry


REPORT = Path("reports/live_adapter_contract_registry/latest_live_adapter_contract_registry.json")

st.set_page_config(page_title="K-Atlas Live Adapter Contract Registry", layout="wide")

st.title("K-Atlas Live Adapter Contract Registry")
st.caption("Contratos de adapters reais. Nenhum adapter live habilitado.")

registry = LiveAdapterContractRegistry()

if st.button("Registrar contratos", type="primary"):
    result = registry.register_contracts()
    st.success("Contratos registrados em modo seguro.")
    st.json(result)

latest = json.loads(REPORT.read_text(encoding="utf-8")) if REPORT.exists() else registry.load_latest()
summary = latest.get("summary", {}) if latest else {}

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Contratos", summary.get("contracts_total", 0))

with col2:
    st.metric("Permitidos", summary.get("contracts_allowed", 0))

with col3:
    st.metric("Bloqueados", summary.get("contracts_blocked", 0))

with col4:
    st.metric("Live execution", str(summary.get("live_execution_enabled", False)))

st.divider()

tab_contracts, tab_env, tab_guardrails, tab_report = st.tabs(["Contratos", "Env", "Guardrails", "Relatório"])

with tab_contracts:
    for item in latest.get("contracts", []):
        contract = item.get("contract", {})
        validation = item.get("validation", {})
        with st.expander(f"{contract.get('adapter_id')} | {contract.get('provider')} | {validation.get('status')}"):
            st.json(item)

with tab_env:
    for item in latest.get("contracts", []):
        contract = item.get("contract", {})
        st.subheader(contract.get("adapter_id", "adapter"))
        for env in item.get("env_status", []):
            st.write(f"- {env.get('name')}: {env.get('value_preview')}")

with tab_guardrails:
    for item in latest.get("guardrails", []):
        st.write(f"- {item}")

with tab_report:
    st.json(latest)
