import json
from pathlib import Path
import streamlit as st

from k_atlas.safe_execution import run_approved_safe_execution

st.set_page_config(page_title="KOS Safe Execution Review", layout="wide")

st.title("KOS Safe Execution Review")
st.caption("Revisao final da execucao segura.")

ROOT = Path.cwd()
demo_path = ROOT / "reports" / "KOS_PHASE9_SAFE_EXECUTION_DEMO.json"

if st.button("Gerar revisao demo", use_container_width=True):
    result = run_approved_safe_execution()
    st.session_state["phase9_review"] = result
    st.success("Revisao gerada.")

if "phase9_review" in st.session_state:
    data = st.session_state["phase9_review"]
elif demo_path.exists():
    data = json.loads(demo_path.read_text(encoding="utf-8-sig"))
else:
    data = None

if data:
    st.metric("Status", data.get("status"))
    st.metric("Cliente", data.get("client_id"))
    st.subheader("Review")
    st.json(data.get("review", {}))
    st.subheader("Recibos")
    st.json(data.get("receipts", {}))
    st.warning("Nenhuma publicacao real foi executada. Proxima etapa: conexao real controlada.")
else:
    st.info("Nenhuma revisao encontrada.")
