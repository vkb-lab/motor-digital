# -*- coding: utf-8 -*-
"""Standalone Streamlit app for K-Social Cockpit.

This app is isolated from the main K-Atlas cockpit.
It only reads supervised JSON snapshots and renders them for human review.
It does not publish content, does not call external APIs and does not operate browsers.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict


PROJECT_ROOT = Path(__file__).resolve().parents[3]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from k_atlas.social.analytics.social_cockpit_adapter import SocialCockpitAdapter
from k_atlas.social.ui.social_cockpit_view import (
    build_social_cockpit_summary,
    load_social_snapshot,
    render_social_cockpit,
)


def ensure_snapshot_exists() -> Dict[str, Any]:
    """Generate a dashboard snapshot if one does not exist yet."""

    snapshot_path = (
        Path(__file__).resolve().parents[1]
        / "reports"
        / "social_dashboard_snapshot.json"
    )

    if snapshot_path.exists():
        snapshot = load_social_snapshot(snapshot_path)
        return build_social_cockpit_summary(snapshot)

    adapter = SocialCockpitAdapter()
    snapshot = adapter.save_snapshot()
    snapshot["snapshot_found"] = True
    return build_social_cockpit_summary(snapshot)


def main() -> None:
    """Render the standalone K-Social cockpit."""

    try:
        import streamlit as st
    except ImportError as exc:
        raise RuntimeError(
            "Streamlit nao esta instalado. Instale com: pip install streamlit"
        ) from exc

    st.set_page_config(
        page_title="K-Social Intelligence System",
        page_icon="KS",
        layout="wide",
    )

    st.title("K-Social Intelligence System")
    st.caption("Cockpit social supervisionado do K-Atlas OS")

    summary = ensure_snapshot_exists()

    with st.container():
        st.info(
            "Modo seguro ativo: sem publicacao automatica, sem APIs reais, sem navegador."
        )

    render_social_cockpit()

    with st.expander("Governanca operacional"):
        st.write("Revisao humana obrigatoria:", summary["human_review_required"])
        st.write("Permissao de publicacao:", summary["publication_permission"])
        st.write("APIs externas usadas:", summary["external_api_used"])
        st.write("Operacoes totais:", summary["total_operations"])
        st.write("Operacoes prontas para revisao:", summary["ready_for_review"])
        st.write("Operacoes bloqueadas:", summary["blocked_operations"])


if __name__ == "__main__":
    main()
