# -*- coding: utf-8 -*-
"""K-Social campaign package viewer.

Displays indexed campaign packages in Streamlit.
It does not publish content, does not call external APIs and does not operate browsers.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional


DEFAULT_CAMPAIGN_PACKAGES_DIR = (
    Path(__file__).resolve().parents[1]
    / "reports"
    / "campaign_packages"
)

INDEX_FILE_NAME = "campaign_package_index.json"


def load_campaign_package_index(
    packages_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """Load campaign package index."""

    directory = Path(packages_dir) if packages_dir else DEFAULT_CAMPAIGN_PACKAGES_DIR
    index_path = directory / INDEX_FILE_NAME

    if not index_path.exists():
        return {
            "system": "K-Social Campaign Package Index",
            "index_found": False,
            "packages_dir": str(directory),
            "total_packages": 0,
            "latest_package": {},
            "recent_packages": [],
            "all_packages": [],
            "governance": {
                "human_review_required": True,
                "publication_permission": False,
                "external_api_used": False,
                "approved_for_auto_publish": False,
                "requires_final_approval": True,
            },
        }

    with index_path.open("r", encoding="utf-8-sig") as file:
        data = json.load(file)

    data["index_found"] = True
    return data



def load_campaign_packages(packages_dir: Optional[Path] = None) -> Dict[str, Any]:
    """Backward-compatible alias for older imports."""

    return load_campaign_package_index(packages_dir=packages_dir)


def render_social_campaign_packages() -> None:
    """Render campaign package index viewer in Streamlit."""

    try:
        import streamlit as st
    except ImportError as exc:
        raise RuntimeError("Streamlit nao esta instalado neste ambiente.") from exc

    from k_atlas.social.campaign_factory.social_campaign_package_indexer import (
        SocialCampaignPackageIndexer,
    )

    indexer = SocialCampaignPackageIndexer()
    index = indexer.save_index()

    st.subheader("Pacotes de campanha K-Social")
    st.caption("Indice limpo dos pacotes finais locais. Revisao final obrigatoria.")

    governance = index.get("governance", {})
    latest = index.get("latest_package", {})
    recent_packages = index.get("recent_packages", [])

    col1, col2, col3 = st.columns(3)
    col1.metric("Total de pacotes", index.get("total_packages", 0))
    col2.metric("Recentes exibidos", len(recent_packages))
    col3.metric("Auto publish", "Bloqueado")

    st.caption("APIs externas: bloqueadas")
    st.caption("Publicacao automatica: bloqueada")
    st.caption("Revisao final: obrigatoria")

    if latest:
        with st.expander("Ultimo pacote"):
            st.write("Nome:", latest.get("package_name", "nao informado"))
            st.write("Assets:", latest.get("total_assets", 0))
            st.write("JSON:", latest.get("json_path", ""))
            st.write("Markdown:", latest.get("markdown_path", ""))
            st.write("Revisao humana:", latest.get("human_review_required", True))
            st.write("Publicacao automatica:", latest.get("publication_permission", False))

    if recent_packages:
        with st.expander("Pacotes recentes"):
            for package in recent_packages:
                st.write("Nome:", package.get("package_name", "nao informado"))
                st.write("Assets:", package.get("total_assets", 0))
                st.write("Criado em:", package.get("generated_at", ""))
                st.write("Arquivo:", package.get("file_name", ""))
                st.divider()
    else:
        st.info("Nenhum pacote de campanha encontrado.")

    with st.expander("Governanca dos pacotes"):
        st.write("Revisao humana obrigatoria:", governance.get("human_review_required", True))
        st.write("Permissao de publicacao:", governance.get("publication_permission", False))
        st.write("API externa usada:", governance.get("external_api_used", False))
        st.write("Auto publish aprovado:", governance.get("approved_for_auto_publish", False))
        st.write("Aprovacao final obrigatoria:", governance.get("requires_final_approval", True))
