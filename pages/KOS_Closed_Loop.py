import streamlit as st

from k_atlas.kaizen.closed_loop import run_closed_loop, summarize_last_reports
from k_atlas.kaizen.human_approval import DRY_RUN_CONFIRMATION

st.set_page_config(page_title="KOS Closed Loop", layout="wide")

st.title("KOS Closed Loop Autonomy")
st.caption("Missao -> Plano -> Aprovacao -> Executor Sandbox -> Relatorio. Sem acao externa real.")

st.subheader("Novo ciclo fechado seguro")

title = st.text_input("Titulo", value="Nova missao closed loop")
description = st.text_area(
    "Descricao",
    value="Executar ciclo seguro em sandbox sem publicacao, sem IA paga e sem segredos."
)
priority = st.selectbox("Prioridade", ["high", "medium", "low"], index=0)

actions = st.multiselect(
    "Acoes seguras",
    ["git_branch", "git_status", "pytest_phase37"],
    default=["git_branch", "git_status"]
)

typed = st.text_input("Confirmacao", value="")

if st.button("Rodar ciclo fechado seguro", use_container_width=True):
    result = run_closed_loop(
        title=title,
        description=description,
        priority=priority,
        typed_confirmation=typed,
        safe_actions=actions,
    )
    st.json(result)

st.info(f"Confirmacao exigida para dry-run sandbox: {DRY_RUN_CONFIRMATION}")
st.warning("Nao publica, nao usa IA paga, nao executa Codex automaticamente e nao acessa segredos.")

st.subheader("Ultimos ciclos")
st.json(summarize_last_reports())
