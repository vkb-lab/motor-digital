from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.autoprogramming_proposal_reviewer.reviewer import AutoprogrammingProposalReviewer


st.set_page_config(page_title="K-Atlas Proposal Reviewer", layout="wide")

st.title("K-Atlas Autoprogramming Proposal Reviewer")
st.caption("Revisa propostas da autoprogramacao assistida antes de qualquer aplicacao real.")

reviewer = AutoprogrammingProposalReviewer()
summary = reviewer.summary()
metrics = summary.get("summary", {})

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Propostas", metrics.get("proposals_total", 0))

with col2:
    st.metric("Reviews", metrics.get("reviews_total", 0))

with col3:
    st.metric("Aguardando decisao", metrics.get("waiting_human_decision", 0))

with col4:
    st.metric("Execucao real", str(metrics.get("real_execution_enabled", False)))

st.divider()

tab_build, tab_review, tab_report = st.tabs(["Construir fila", "Revisar", "Relatorio"])

with tab_build:
    st.write("Cria itens de revisao para propostas ainda nao revisadas.")
    if st.button("Construir fila de revisao", type="primary"):
        result = reviewer.build_review_queue()
        st.success("Fila de revisao atualizada.")
        st.json(result)

with tab_review:
    current = reviewer.summary()
    reviews = current.get("reviews", [])

    if not reviews:
        st.info("Nenhum item de revisao encontrado.")
    else:
        for item in reviews:
            title = f"{item.get('checkpoint')} | {item.get('status')} | {item.get('objective')}"
            with st.expander(title):
                st.json(item)

                if item.get("status") == "waiting_human_decision":
                    decision = st.selectbox(
                        "Decisao",
                        ["hold", "approve_for_apply_package", "request_changes", "deny"],
                        key=f"decision_{item.get('review_id')}",
                    )
                    notes = st.text_area(
                        "Notas",
                        value="Revisao humana supervisionada.",
                        key=f"notes_{item.get('review_id')}",
                    )

                    if st.button("Registrar decisao", key=f"button_{item.get('review_id')}"):
                        result = reviewer.decide(
                            review_id=item.get("review_id"),
                            decision=decision,
                            reviewer="k_atlas_operator",
                            notes=notes,
                        )
                        st.json(result)

with tab_report:
    st.json(reviewer.save_report())
