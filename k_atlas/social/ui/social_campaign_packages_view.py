# -*- coding: utf-8 -*-
"""K-Social campaign package viewer.

Displays exported campaign packages in Streamlit.
It does not publish content, does not call external APIs and does not operate browsers.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


DEFAULT_CAMPAIGN_PACKAGES_DIR = (
    Path(__file__).resolve().parents[1]
    / "reports"
    / "campaign_packages"
)


def load_campaign_packages(
    packages_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """Load campaign package JSON and Markdown files."""

    directory = Path(packages_dir) if packages_dir else DEFAULT_CAMPAIGN_PACKAGES_DIR
    directory.mkdir(parents=True, exist_ok=True)

    json_packages: List[Dict[str, Any]] = []
    markdown_packages: List[Dict[str, str]] = []

    for path in sorted(directory.glob("*.json")):
        try:
            with path.open("r", encoding="utf-8-sig") as file:
                data = json.load(file)
        except (json.JSONDecodeError, OSError):
            continue

        if not isinstance(data, dict):
            continue

        json_packages.append(
            {
                "file_name": path.name,
                "path": str(path),
                "package_name": data.get("package_name", "pacote sem nome"),
                "total_assets": data.get("total_assets", 0),
                "governance": data.get("governance", {}),
                "data": data,
            }
        )

    for path in sorted(directory.glob("*.md")):
        try:
            content = path.read_text(encoding="utf-8-sig")
        except OSError:
            continue

        markdown_packages.append(
            {
                "file_name": path.name,
                "path": str(path),
                "content": content,
            }
        )

    return {
        "system": "K-Social Campaign Package Viewer",
        "packages_dir": str(directory),
        "total_json_packages": len(json_packages),
        "total_markdown_packages": len(markdown_packages),
        "publication_permission": False,
        "external_api_used": False,
        "human_review_required": True,
        "approved_for_auto_publish": False,
        "json_packages": json_packages,
        "markdown_packages": markdown_packages,
    }


def render_social_campaign_packages() -> None:
    """Render campaign package viewer in Streamlit."""

    try:
        import streamlit as st
    except ImportError as exc:
        raise RuntimeError("Streamlit nao esta instalado neste ambiente.") from exc

    data = load_campaign_packages()

    st.subheader("Pacotes de campanha K-Social")
    st.caption("Pacotes finais locais. Revisao final obrigatoria antes de qualquer uso real.")

    col1, col2, col3 = st.columns(3)
    col1.metric("JSON", data["total_json_packages"])
    col2.metric("Markdown", data["total_markdown_packages"])
    col3.metric("Auto publish", "Bloqueado")

    st.caption("APIs externas: bloqueadas")
    st.caption("Publicacao automatica: bloqueada")
    st.caption("Revisao final: obrigatoria")

    json_packages = data.get("json_packages", [])
    markdown_packages = data.get("markdown_packages", [])

    if not json_packages and not markdown_packages:
        st.info("Nenhum pacote de campanha encontrado.")
        return

    if json_packages:
        with st.expander("Pacotes JSON"):
            for package in json_packages:
                st.write("Arquivo:", package.get("file_name", "nao informado"))
                st.write("Nome:", package.get("package_name", "nao informado"))
                st.write("Assets:", package.get("total_assets", 0))
                st.write("Governanca:", package.get("governance", {}))
                st.divider()

    if markdown_packages:
        with st.expander("Pacotes Markdown"):
            for package in markdown_packages:
                with st.expander(str(package.get("file_name", "arquivo"))):
                    st.caption(str(package.get("path", "")))
                    st.markdown(str(package.get("content", "")))
