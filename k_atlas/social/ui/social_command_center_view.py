# -*- coding: utf-8 -*-
"""K-Social command center Streamlit view."""

from __future__ import annotations


def render_social_command_center() -> None:
    """Render K-Social command center in Streamlit."""

    try:
        import streamlit as st
    except ImportError as exc:
        raise RuntimeError("Streamlit nao esta instalado neste ambiente.") from exc

    from k_atlas.social.analytics.social_command_center import SocialCommandCenter

    command_center = SocialCommandCenter()
    data = command_center.save()

    st.subheader("K-Social Command Center")
    st.caption("Resumo operacional do sistema social. Auto publish permanece bloqueado.")

    operations = data["operations"]
    approval = data["approval_queue"]
    refinement = data["refinement_queue"]
    packages = data["campaign_packages"]
    package_approval = data["package_approval"]
    governance = data["governance"]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Operacoes", operations["total"])
    col2.metric("Aprovacoes pendentes", approval["pending"])
    col3.metric("Refinamentos", refinement["total_tasks"])
    col4.metric("Pacotes", packages["total"])

    col5, col6, col7, col8 = st.columns(4)
    col5.metric("Uso manual aprovado", package_approval["approved_for_manual_use"])
    col6.metric("Revisao pacote", package_approval["needs_package_revision"])
    col7.metric("Riscos relatorio", data["daily_report"]["risks"])
    col8.metric("Auto publish", "Bloqueado")

    with st.expander("Governanca do Command Center"):
        st.write("Revisao humana obrigatoria:", governance["human_review_required"])
        st.write("Permissao de publicacao:", governance["publication_permission"])
        st.write("API externa usada:", governance["external_api_used"])
        st.write("Auto publish aprovado:", governance["approved_for_auto_publish"])
        st.write("Uso manual apenas apos aprovacao final:", governance["manual_use_only_after_final_approval"])
