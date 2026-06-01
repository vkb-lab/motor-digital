import json
from pathlib import Path
import streamlit as st

from k_atlas.deploy_bridge import export_public_status, inspect_vercel_readiness

st.set_page_config(page_title="KOS Production Deploy Bridge", layout="wide")

st.title("KOS Production Deploy Bridge")
st.caption("Ponte de producao para Vercel. Nenhuma publicacao real nesta fase.")

if st.button("Gerar pacote publico", use_container_width=True):
    exported = export_public_status()
    st.session_state["phase10_exported"] = exported
    st.success("Pacote publico gerado.")

readiness = inspect_vercel_readiness()
st.subheader("Vercel readiness")
st.json(readiness)

exported = st.session_state.get("phase10_exported")
if exported:
    st.subheader("Export")
    st.json(exported)
else:
    status_path = Path("public/kos/status.json")
    if status_path.exists():
        st.json(json.loads(status_path.read_text(encoding="utf-8-sig")))

st.warning("A etapa real de publicacao no Instagram ainda nao esta ativa. Proxima fase conecta canal real com trava.")
