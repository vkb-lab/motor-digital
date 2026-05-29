# -*- coding: utf-8 -*-
"""K-Social package approval Streamlit view."""

from __future__ import annotations


def render_social_campaign_package_approval_queue() -> None:
    """Render final approval queue for campaign packages."""

    try:
        import streamlit as st
    except ImportError as exc:
        raise RuntimeError("Streamlit nao esta instalado neste ambiente.") from exc

    from k_atlas.social.audit.social_campaign_package_approval_queue import (
        SocialCampaignPackageApprovalQueue,
    )

    queue_manager = SocialCampaignPackageApprovalQueue()
    queue = queue_manager.save_queue()

    st.subheader("Aprovacao final de pacotes")
    st.caption("Aprovacao final libera apenas uso manual. Auto publish continua bloqueado.")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Pacotes", queue["total_items"])
    col2.metric("Pendentes", queue["counts"]["pending_final_review"])
    col3.metric("Uso manual", queue["counts"]["approved_for_manual_use"])
    col4.metric("Revisao", queue["counts"]["needs_package_revision"])

    st.caption("Publicacao automatica: bloqueada")
    st.caption("Aprovacao maxima: uso manual supervisionado")

    items = queue.get("items", [])

    if not items:
        st.info("Nenhum pacote aguardando aprovacao final.")
        return

    for item in items:
        source_file = item.get("source_file", "")
        label = item.get("package_name", "Pacote") + " | " + item.get("final_approval_status", "unknown")

        with st.expander(label):
            st.write("Arquivo:", source_file)
            st.write("Assets:", item.get("total_assets", 0))
            st.write("Status final:", item.get("final_approval_status", "unknown"))
            st.write("Revisao humana:", item.get("human_review_required", True))
            st.write("Publicacao automatica:", item.get("publication_permission", False))

            decision = st.selectbox(
                "Decisao final",
                [
                    "pending_final_review",
                    "approved_for_manual_use",
                    "needs_package_revision",
                    "rejected",
                ],
                index=0,
                key="package_final_decision_" + source_file,
            )

            notes = st.text_area(
                "Notas da aprovacao final",
                value="",
                key="package_final_notes_" + source_file,
            )

            if st.button("Salvar aprovacao final", key="package_final_save_" + source_file):
                try:
                    queue_manager.update_decision(
                        source_file=source_file,
                        decision=decision,
                        reviewer="K-Atlas Operator",
                        notes=notes,
                    )
                    st.success("Aprovacao final salva. Atualize a pagina para ver o status atualizado.")
                except Exception as exc:
                    st.error("Falha ao salvar aprovacao final.")
                    st.caption(str(exc))
