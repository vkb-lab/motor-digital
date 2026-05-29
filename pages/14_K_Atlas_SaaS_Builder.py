from __future__ import annotations

import json
import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.saas_factory.builder_agent.builder import SaaSBuilderAgent

PRODUCTS_ROOT = Path("k_atlas/saas_factory/products")


def list_products() -> list[Path]:
    if not PRODUCTS_ROOT.exists():
        return []
    return sorted([p for p in PRODUCTS_ROOT.iterdir() if p.is_dir()], key=lambda item: item.stat().st_mtime, reverse=True)


st.set_page_config(page_title="K-Atlas SaaS Builder", layout="wide")
st.title("K-Atlas SaaS Builder")
st.caption("Criacao supervisionada de MVPs SaaS em Streamlit, JSON e arquitetura modular.")

products = list_products()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Produtos gerados", len(products))
with col2:
    st.metric("API externa", "bloqueada")
with col3:
    st.metric("Deploy", "supervisionado")

st.divider()

tab_new, tab_products = st.tabs(["Novo MVP", "Produtos"])

with tab_new:
    st.subheader("Gerar MVP SaaS")
    product_name = st.text_input("Nome do produto", value="K-Atlas Demo SaaS")
    audience = st.text_area("Publico", value="fundadores, operadores e negocios locais", height=80)
    problem = st.text_area("Problema", value="falta de cockpit digital simples para validar operacoes com IA", height=80)
    solution = st.text_area("Solucao", value="MVP Streamlit com dashboard, modulos e estado JSON", height=80)
    monetization = st.text_input("Monetizacao", value="assinatura mensal + setup")
    modules_text = st.text_area("Modulos, um por linha", value="dashboard\nlead_capture\ncampaigns\nreports\nadmin", height=130)

    if st.button("Gerar estrutura do MVP", type="primary"):
        payload = {
            "product_name": product_name,
            "audience": audience,
            "problem": problem,
            "solution": solution,
            "monetization": monetization,
            "modules": [line.strip() for line in modules_text.splitlines() if line.strip()],
        }
        result = SaaSBuilderAgent().generate_app_module(payload)
        st.success("MVP gerado.")
        st.json(result)

with tab_products:
    st.subheader("Produtos gerados")
    products = list_products()
    if not products:
        st.info("Nenhum produto gerado ainda.")
    else:
        for product_dir in products:
            with st.expander(product_dir.name):
                product_json = product_dir / "product.json"
                readme = product_dir / "README.md"
                if product_json.exists():
                    st.json(json.loads(product_json.read_text(encoding="utf-8")))
                if readme.exists():
                    st.markdown(readme.read_text(encoding="utf-8"))
