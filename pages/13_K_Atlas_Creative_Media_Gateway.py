from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.creative.media_gateway.brief import build_custom_brief, build_default_k_atlas_brief
from k_atlas.creative.media_gateway.package_builder import build_creative_media_package


REPORTS_ROOT = Path("reports/creative_media")


def list_packages() -> list[Path]:
    if not REPORTS_ROOT.exists():
        return []
    return sorted(REPORTS_ROOT.glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True)


st.set_page_config(page_title="K-Atlas Creative Media Gateway", layout="wide")

st.title("K-Atlas Creative Media Gateway")
st.caption("Brief -> prompts -> assets -> pacote criativo. Sem API externa. Sem publicacao.")

packages = list_packages()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Pacotes salvos", len(packages))

with col2:
    st.metric("API externa", "bloqueada")

with col3:
    st.metric("Publicacao oficial", "bloqueada")

st.divider()

tab_new, tab_default, tab_packages = st.tabs([
    "Novo pacote",
    "Pacote K-Atlas",
    "Pacotes salvos",
])

with tab_new:
    st.subheader("Criar pacote criativo")

    project_name = st.text_input("Projeto", value="K-Atlas OS")
    objective = st.text_area(
        "Objetivo",
        value="Criar pacote criativo para apresentar o K-Atlas como sistema operacional de agentes IA.",
        height=120,
    )
    target_audience = st.text_area(
        "Público",
        value="empreendedores, founders, builders, operadores de marketing e empresas que querem escalar com IA.",
        height=100,
    )
    offer = st.text_area(
        "Oferta",
        value="acompanhar e usar um ecossistema que cria SaaS, campanhas, automações e produtos digitais com supervisão humana.",
        height=100,
    )
    channel = st.text_input("Canal", value="instagram_official")
    tone = st.text_input("Tom", value="arrojado, técnico, direto e growth-minded")
    visual_style = st.text_input("Direção visual", value="futurista limpo, cockpit operacional, prints reais e motion graphics")

    if st.button("Gerar pacote criativo", type="primary"):
        brief = build_custom_brief(
            project_name=project_name,
            objective=objective,
            target_audience=target_audience,
            offer=offer,
            channel=channel,
            tone=tone,
            visual_style=visual_style,
        )
        package = build_creative_media_package(brief)

        REPORTS_ROOT.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = REPORTS_ROOT / f"creative_package_{stamp}.json"
        path.write_text(json.dumps(package, ensure_ascii=False, indent=2), encoding="utf-8")

        st.success(f"Pacote salvo em {path}")
        st.json(package)

with tab_default:
    st.subheader("Pacote padrão K-Atlas")

    brief = build_default_k_atlas_brief()
    package = build_creative_media_package(brief)

    st.json(package)

with tab_packages:
    st.subheader("Pacotes salvos")

    packages = list_packages()

    if not packages:
        st.info("Nenhum pacote salvo ainda.")
    else:
        for path in packages:
            with st.expander(path.name):
                try:
                    st.json(json.loads(path.read_text(encoding="utf-8")))
                except Exception as exc:
                    st.error(f"Falha ao ler pacote: {exc}")