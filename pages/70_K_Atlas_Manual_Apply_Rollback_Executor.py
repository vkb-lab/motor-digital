from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.manual_apply_rollback_executor.rollback import ManualApplyRollbackExecutor


st.set_page_config(page_title="K-Atlas Manual Apply Rollback", layout="wide")

st.title("K-Atlas Manual Apply Rollback Executor")
st.caption("Rollback manual supervisionado com dry-run e manifesto.")

executor = ManualApplyRollbackExecutor()

tab_dry, tab_rollback, tab_manifest = st.tabs(["Dry-run", "Rollback manual", "Manifesto"])

with tab_dry:
    st.write("Simula rollback sem alterar arquivos.")
    if st.button("Rodar dry-run de rollback", type="primary"):
        result = executor.dry_run()
        st.json(result)

with tab_rollback:
    st.warning("Esta area desfaz alteracoes locais somente com aprovacao humana explicita.")
    approve = st.checkbox("Eu aprovo manualmente executar rollback do ultimo apply disponivel.")
    if st.button("Executar rollback manual"):
        result = executor.rollback_manual({
            "human_approved": approve,
            "rollback_mode": "manual",
            "external_api_enabled": False,
            "auto_publish": False,
            "auto_send": False,
            "auto_deploy": False,
            "browser_automation": False,
            "mouse_automation": False,
        })
        st.json(result)

with tab_manifest:
    st.subheader("Apply manifest")
    st.json(executor.load_apply_manifest())

    st.subheader("Rollback manifest")
    st.json(executor.load_rollback_manifest())
