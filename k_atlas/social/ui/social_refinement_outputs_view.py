# -*- coding: utf-8 -*-
"""K-Social refinement outputs viewer.

Displays generated local creative refinement files in Streamlit.
It does not publish content, does not call external APIs and does not operate browsers.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional


DEFAULT_REFINEMENT_OUTPUTS_DIR = (
    Path(__file__).resolve().parents[1]
    / "reports"
    / "refinement_outputs"
)


def load_refinement_outputs(
    outputs_dir: Optional[Path] = None,
) -> Dict[str, object]:
    """Load generated refinement Markdown files."""

    directory = Path(outputs_dir) if outputs_dir else DEFAULT_REFINEMENT_OUTPUTS_DIR
    directory.mkdir(parents=True, exist_ok=True)

    files: List[Dict[str, str]] = []

    for path in sorted(directory.glob("*.md")):
        try:
            content = path.read_text(encoding="utf-8-sig")
        except OSError:
            continue

        files.append(
            {
                "file_name": path.name,
                "path": str(path),
                "content": content,
            }
        )

    return {
        "system": "K-Social Refinement Outputs Viewer",
        "outputs_dir": str(directory),
        "total_files": len(files),
        "publication_permission": False,
        "external_api_used": False,
        "human_review_required": True,
        "approved_for_auto_publish": False,
        "files": files,
    }


def render_social_refinement_outputs() -> None:
    """Render refinement outputs in Streamlit."""

    try:
        import streamlit as st
    except ImportError as exc:
        raise RuntimeError("Streamlit nao esta instalado neste ambiente.") from exc

    data = load_refinement_outputs()

    st.subheader("Refinamentos criativos gerados")
    st.caption("Arquivos locais em Markdown. Revisao humana obrigatoria.")

    col1, col2, col3 = st.columns(3)
    col1.metric("Arquivos", data["total_files"])
    col2.metric("API externa", "Nao")
    col3.metric("Auto publish", "Bloqueado")

    files = data.get("files", [])

    if not files:
        st.info("Nenhum refinamento gerado ainda.")
        return

    for file_info in files:
        with st.expander(str(file_info.get("file_name", "arquivo"))):
            st.caption(str(file_info.get("path", "")))
            st.markdown(str(file_info.get("content", "")))
