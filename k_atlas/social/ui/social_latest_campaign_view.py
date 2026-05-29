# -*- coding: utf-8 -*-
"""K-Social latest campaign viewer."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional


DEFAULT_LATEST_CAMPAIGN_PATH = (
    Path(__file__).resolve().parents[1]
    / "reports"
    / "campaign_packages"
    / "latest_manual_approved_campaign.json"
)


def load_latest_manual_approved_campaign(
    latest_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """Load latest manually approved campaign pointer."""

    path = Path(latest_path) if latest_path else DEFAULT_LATEST_CAMPAIGN_PATH

    if not path.exists():
        return {
            "system": "K-Social Latest Manual Approved Campaign",
            "latest_found": False,
            "campaign": {},
            "governance": {
                "human_review_required": True,
                "publication_permission": False,
                "external_api_used": False,
                "approved_for_auto_publish": False,
                "manual_use_only": True,
            },
        }

    with path.open("r", encoding="utf-8-sig") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        return {
            "system": "K-Social Latest Manual Approved Campaign",
            "latest_found": False,
            "campaign": {},
            "governance": {
                "human_review_required": True,
                "publication_permission": False,
                "external_api_used": False,
                "approved_for_auto_publish": False,
                "manual_use_only": True,
            },
        }

    return data


def render_latest_manual_approved_campaign() -> None:
    """Render latest manually approved campaign in Streamlit."""

    try:
        import streamlit as st
    except ImportError as exc:
        raise RuntimeError("Streamlit nao esta instalado neste ambiente.") from exc

    data = load_latest_manual_approved_campaign()
    campaign = data.get("campaign", {})
    governance = data.get("governance", {})

    st.subheader("Campanha principal aprovada")
    st.caption("Pacote principal liberado apenas para uso manual supervisionado.")

    if not data.get("latest_found", False):
        st.info("Nenhuma campanha aprovada manualmente encontrada.")
        return

    col1, col2, col3 = st.columns(3)
    col1.metric("Assets", campaign.get("total_assets", 0))
    col2.metric("Status", campaign.get("approval_status", "nao informado"))
    col3.metric("Auto publish", "Bloqueado")

    with st.expander("Detalhes da campanha principal"):
        st.write("Nome:", campaign.get("package_name", "nao informado"))
        st.write("Filtro:", campaign.get("product_filter", "nao informado"))
        st.write("Aprovado em:", campaign.get("approval_time", "nao informado"))
        st.write("JSON:", campaign.get("json_path", ""))
        st.write("Markdown:", campaign.get("markdown_path", ""))
        st.write("Uso manual apenas:", campaign.get("manual_use_only", True))
        st.write("Publicacao automatica:", governance.get("publication_permission", False))
