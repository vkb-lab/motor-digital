from __future__ import annotations

import json
import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.credential_vault.env_contract import build_env_contract
from k_atlas.core.credential_vault.policy import validate_secret_payload
from k_atlas.core.credential_vault.vault import CredentialVault


st.set_page_config(page_title="K-Atlas Credential Vault", layout="wide")

st.title("K-Atlas Credential Vault")
st.caption("Validação de credenciais por referência. Nunca expõe tokens.")

vault = CredentialVault()
contract = build_env_contract()

future_names = [item["name"] for item in contract["future_optional"]]
inspections = vault.inspect_many(future_names)

available = [item for item in inspections if item["exists"]]
missing = [item for item in inspections if not item["exists"]]

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Credenciais futuras", len(future_names))

with col2:
    st.metric("Encontradas", len(available))

with col3:
    st.metric("Ausentes", len(missing))

st.divider()

tab_overview, tab_inspect, tab_policy = st.tabs(["Contrato", "Inspeção ENV", "Teste de política"])

with tab_overview:
    st.subheader("Contrato de credenciais")
    st.json(contract)

with tab_inspect:
    st.subheader("Variáveis de ambiente esperadas")
    st.warning("Valores reais nunca são exibidos. Apenas preview mascarado.")

    for item in inspections:
        with st.expander(f"{item['key']} | exists={item['exists']}"):
            st.json(item)

with tab_policy:
    st.subheader("Validar payload contra segredo em texto puro")

    payload_text = st.text_area(
        "Payload JSON",
        value=json.dumps({
            "external_api_enabled": True,
            "credential_vault_ref": "vault://env/GOOGLE_AI_API_KEY"
        }, ensure_ascii=False, indent=2),
        height=180,
    )

    if st.button("Validar payload", type="primary"):
        try:
            payload = json.loads(payload_text)
        except json.JSONDecodeError as exc:
            st.error(f"JSON inválido: {exc}")
        else:
            result = validate_secret_payload(payload)
            if result["ok"]:
                st.success("Payload aprovado pela política de segredo.")
            else:
                st.error("Payload bloqueado.")
            st.json(result)
