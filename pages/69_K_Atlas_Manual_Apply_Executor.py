from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.manual_apply_executor.executor import ManualApplyExecutor


st.set_page_config(page_title="K-Atlas Manual Apply Executor", layout="wide")

st.title("K-Atlas Manual Apply Executor")
st.caption("Aplicador manual supervisionado com dry-run, backup e manifesto.")

executor = ManualApplyExecutor()

tab_dry, tab_apply, tab_manifest = st.tabs(["Dry-run", "Aplicar manualmente", "Manifesto"])

with tab_dry:
    st.write("Executa simulacao sem alterar arquivos.")
    if st.button("Rodar dry-run", type="primary"):
        result = executor.dry_run()
        st.json(result)

with tab_apply:
    st.warning("Esta area aplica arquivos locais somente apos aprovacao humana explicita.")
    approve = st.checkbox("Eu aprovo manualmente aplicar o primeiro pacote validado pelo gate.")
    notes = st.text_area("Notas da aprovacao", value="Aprovacao humana supervisionada.")

    if st.button("Aplicar pacote manualmente"):
        result = executor.apply_manual({
            "human_approved": approve,
            "apply_mode": "manual",
            "notes": notes,
            "external_api_enabled": False,
            "auto_publish": False,
            "auto_send": False,
            "auto_deploy": False,
            "browser_automation": False,
            "mouse_automation": False,
        })
        st.json(result)

with tab_manifest:
    st.write("Manifesto de aplicacoes manuais.")
    st.json(executor.load_manifest())
