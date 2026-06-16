import streamlit as st
from k_atlas.kaizen.safe_executor import list_safe_actions, run_safe_bundle

st.set_page_config(page_title="KOS Safe Executor", layout="wide")

st.title("KOS Safe Executor Sandbox")
st.caption("Executa apenas acoes allowlist locais. Nao publica, nao usa IA paga, nao executa Codex automaticamente.")

actions = list_safe_actions()

st.subheader("Acoes permitidas")
st.json(actions)

selected = st.multiselect(
    "Selecionar acoes seguras",
    list(actions.keys()),
    default=["git_branch", "git_status"]
)

dry_run = st.checkbox("Dry-run apenas", value=True)

if st.button("Executar bundle seguro", use_container_width=True):
    result = run_safe_bundle("streamlit_safe_bundle", selected, dry_run=dry_run)
    st.json(result)

st.warning("Acoes reais continuam bloqueadas. Publicacao externa exige fase propria e confirmacao humana.")
