# -*- coding: utf-8 -*-
"""K-Social cockpit UI layer.

This module prepares dashboard data and optional Streamlit rendering for K-Social.
It does not publish content, does not call external APIs and does not operate browsers.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional


DEFAULT_SNAPSHOT_PATH = (
    Path(__file__).resolve().parents[1]
    / "reports"
    / "social_dashboard_snapshot.json"
)


def load_social_snapshot(snapshot_path: Optional[Path] = None) -> Dict[str, Any]:
    """Load the K-Social dashboard snapshot from JSON."""

    path = Path(snapshot_path) if snapshot_path else DEFAULT_SNAPSHOT_PATH

    if not path.exists():
        return {
            "system": "K-Social Cockpit Snapshot",
            "snapshot_found": False,
            "message": "Snapshot social ainda nao foi gerado.",
            "total_operations": 0,
            "ready_for_review": 0,
            "blocked_operations": 0,
            "total_content_items": 0,
            "publication_permission": False,
            "external_api_used": False,
            "human_review_required": True,
            "operations": [],
        }

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    data["snapshot_found"] = True
    return data


def build_social_cockpit_summary(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    """Build a compact summary for cockpit rendering."""

    operations = snapshot.get("operations", [])

    return {
        "system": snapshot.get("system", "K-Social Cockpit Snapshot"),
        "snapshot_found": snapshot.get("snapshot_found", True),
        "total_operations": int(snapshot.get("total_operations", len(operations))),
        "ready_for_review": int(snapshot.get("ready_for_review", 0)),
        "blocked_operations": int(snapshot.get("blocked_operations", 0)),
        "total_content_items": int(snapshot.get("total_content_items", 0)),
        "publication_permission": bool(snapshot.get("publication_permission", False)),
        "external_api_used": bool(snapshot.get("external_api_used", False)),
        "human_review_required": bool(snapshot.get("human_review_required", True)),
        "operations": operations,
    }


def render_social_cockpit(snapshot_path: Optional[Path] = None) -> None:
    """Render K-Social dashboard section in Streamlit.

    Streamlit is imported only inside this function to keep smoke tests independent.
    """

    try:
        import streamlit as st
    except ImportError as exc:
        raise RuntimeError("Streamlit nao esta instalado neste ambiente.") from exc

    snapshot = load_social_snapshot(snapshot_path)
    summary = build_social_cockpit_summary(snapshot)

    st.subheader("K-Social Intelligence System")

    if not summary["snapshot_found"]:
        st.info(summary.get("message", "Snapshot social ainda nao foi gerado."))
        return

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Operacoes", summary["total_operations"])
    col2.metric("Para revisao", summary["ready_for_review"])
    col3.metric("Bloqueadas", summary["blocked_operations"])
    col4.metric("Itens", summary["total_content_items"])

    st.caption("Publicacao automatica: bloqueada")
    st.caption("APIs externas: bloqueadas neste checkpoint")
    st.caption("Revisao humana: obrigatoria")

    operations = summary["operations"]

    if not operations:
        st.warning("Nenhuma operacao social encontrada.")
        return

    for operation in operations:
        with st.expander(operation.get("product", "Produto nao informado")):
            st.write("Mercado:", operation.get("market", "nao informado"))
            st.write("Objetivo:", operation.get("objective", "nao informado"))
            st.write("Status:", operation.get("operation_status", "unknown"))
            st.write("Auditoria:", operation.get("audit_status", "unknown"))
            st.write("Canais:", ", ".join(operation.get("channels", [])))
            st.write("Duracao:", operation.get("duration_days", 0), "dias")
            st.write("Itens de conteudo:", operation.get("content_items", 0))
            st.write("Revisao humana obrigatoria:", operation.get("human_review_required", True))
            st.write("Permissao de publicacao:", operation.get("publication_permission", False))
