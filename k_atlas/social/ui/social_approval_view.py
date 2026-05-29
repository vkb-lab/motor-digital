# -*- coding: utf-8 -*-
"""K-Social approval queue Streamlit view.

This module renders human approval controls.
It does not publish content, does not call external APIs and does not operate browsers.
"""

from __future__ import annotations


def render_social_approval_queue() -> None:
    """Render K-Social human approval queue in Streamlit."""

    try:
        import streamlit as st
    except ImportError as exc:
        raise RuntimeError("Streamlit nao esta instalado neste ambiente.") from exc

    from k_atlas.social.audit.social_approval_queue import SocialApprovalQueue

    queue_manager = SocialApprovalQueue()
    queue = queue_manager.save_queue()

    st.subheader("Fila de aprovacao humana")
    st.caption("Aprovacao aqui nao libera publicacao automatica.")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Na fila", queue["total_items"])
    col2.metric("Pendentes", queue["counts"]["pending_human_review"])
    col3.metric("Para revisar", queue["counts"]["needs_revision"])
    col4.metric("Rejeitadas", queue["counts"]["rejected"])

    st.caption("Publicacao automatica: bloqueada")
    st.caption("Aprovacao maxima neste checkpoint: refinamento de conteudo")

    items = queue.get("items", [])

    if not items:
        st.info("Nenhuma operacao social na fila de aprovacao.")
        return

    for item in items:
        label = item.get("product", "Produto nao informado") + " | " + item.get("approval_status", "unknown")

        with st.expander(label):
            st.write("Arquivo:", item.get("source_file", "nao informado"))
            st.write("Mercado:", item.get("market", "nao informado"))
            st.write("Objetivo:", item.get("objective", "nao informado"))
            st.write("Auditoria:", item.get("audit_status", "unknown"))
            st.write("Status de aprovacao:", item.get("approval_status", "unknown"))
            st.write("Canais:", ", ".join(item.get("channels", [])))
            st.write("Itens de conteudo:", item.get("content_items", 0))
            st.write("Publicacao automatica:", item.get("publication_permission", False))

            source_file = item.get("source_file", "")

            decision = st.selectbox(
                "Decisao humana",
                [
                    "pending_human_review",
                    "approved_for_content_refinement",
                    "needs_revision",
                    "rejected",
                ],
                index=0,
                key="approval_decision_" + source_file,
            )

            notes = st.text_area(
                "Notas da revisao",
                value="",
                key="approval_notes_" + source_file,
            )

            if st.button("Salvar decisao", key="approval_save_" + source_file):
                try:
                    queue_manager.update_decision(
                        source_file=source_file,
                        decision=decision,
                        reviewer="K-Atlas Operator",
                        notes=notes,
                    )
                    st.success("Decisao salva. Atualize a pagina para ver a fila atualizada.")
                except Exception as exc:
                    st.error("Falha ao salvar decisao.")
                    st.caption(str(exc))
