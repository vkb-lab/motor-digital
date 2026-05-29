# -*- coding: utf-8 -*-
"""K-Social content refinement Streamlit view."""

from __future__ import annotations


def render_social_content_refinement_queue() -> None:
    """Render content refinement queue in Streamlit."""

    try:
        import streamlit as st
    except ImportError as exc:
        raise RuntimeError("Streamlit nao esta instalado neste ambiente.") from exc

    from k_atlas.social.creative_engine.social_content_refinement_queue import (
        SocialContentRefinementQueue,
    )

    queue_manager = SocialContentRefinementQueue()
    queue = queue_manager.save_queue()

    st.subheader("Fila de refinamento criativo")
    st.caption("Tarefas criativas supervisionadas. Nada e publicado automaticamente.")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Tarefas", queue["total_tasks"])
    col2.metric("Pendentes", queue["counts"]["pending_refinement"])
    col3.metric("Em progresso", queue["counts"]["in_progress"])
    col4.metric("Bloqueadas", queue["counts"]["blocked"])

    st.caption("Imagem IA, video IA, reels e anuncios: preparados apenas como briefing.")

    tasks = queue.get("tasks", [])

    if not tasks:
        st.info("Nenhuma tarefa de refinamento disponivel. Marque uma operacao como needs_revision ou approved_for_content_refinement.")
        return

    for task in tasks:
        label = task.get("title", "Tarefa") + " | " + task.get("product", "Produto")

        with st.expander(label):
            st.write("Tipo:", task.get("task_type", "nao informado"))
            st.write("Produto:", task.get("product", "nao informado"))
            st.write("Objetivo:", task.get("objective", "nao informado"))
            st.write("Status da aprovacao:", task.get("approval_status", "nao informado"))
            st.write("Notas da revisao:", task.get("review_notes", ""))
            st.write("Canais:", ", ".join(task.get("channels", [])))
            st.write("Itens disponiveis:", task.get("content_items_available", 0))
            st.write("Instrucoes:", task.get("instructions", ""))
            st.write("Publicacao automatica:", task.get("publication_permission", False))
