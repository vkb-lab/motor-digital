from __future__ import annotations

import json
import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.sandbox_api_adapter.adapter import SandboxAPIAdapter
from k_atlas.core.sandbox_api_adapter.audit import SandboxAPIAuditLog
from k_atlas.core.sandbox_api_adapter.providers import build_provider_registry


AUDIT_PATH = Path("memory/sandbox_api_adapter/requests.json")

st.set_page_config(page_title="K-Atlas Sandbox API Adapter", layout="wide")

st.title("K-Atlas Sandbox API Adapter")
st.caption("Simula integrações externas sem rede, sem token e sem efeitos colaterais.")

adapter = SandboxAPIAdapter(SandboxAPIAuditLog(AUDIT_PATH))
providers = build_provider_registry()
audit_rows = SandboxAPIAuditLog(AUDIT_PATH).load()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Providers", len(providers))

with col2:
    st.metric("Requests simuladas", len(audit_rows))

with col3:
    st.metric("Rede externa", "bloqueada")

st.divider()

tab_run, tab_providers, tab_logs = st.tabs(["Simular chamada", "Providers", "Logs"])

with tab_run:
    provider_id = st.selectbox(
        "Provider",
        options=list(providers.keys()),
        format_func=lambda key: providers[key].name,
    )

    provider = providers[provider_id]

    operation = st.selectbox("Operação", options=provider.operations)

    payload_text = st.text_area(
        "Payload JSON",
        value=json.dumps({
            "objective": "Criar pacote audiovisual do K-Atlas OS",
            "external_api_enabled": False,
            "official_publish": False,
            "auto_publish": False,
            "real_network": False,
        }, ensure_ascii=False, indent=2),
        height=240,
    )

    if st.button("Simular no sandbox", type="primary"):
        try:
            payload = json.loads(payload_text)
        except json.JSONDecodeError as exc:
            st.error(f"JSON inválido: {exc}")
        else:
            result = adapter.execute(
                provider_id=provider_id,
                operation=operation,
                payload=payload,
                requested_by="streamlit_operator",
            )
            if result["ok"]:
                st.success("Simulação concluída sem efeitos externos.")
            else:
                st.error("Simulação bloqueada pela política.")
            st.json(result)

with tab_providers:
    st.subheader("Providers registrados")
    for provider in providers.values():
        with st.expander(provider.name):
            st.json(provider.to_dict())

with tab_logs:
    st.subheader("Audit log")

    rows = SandboxAPIAuditLog(AUDIT_PATH).load()

    if not rows:
        st.info("Nenhuma simulação registrada.")
    else:
        for row in reversed(rows[-50:]):
            with st.expander(f"{row.get('created_at')} | {row.get('provider_id')} | {row.get('operation')}"):
                st.json(row)
