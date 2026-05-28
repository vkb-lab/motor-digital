
# -*- coding: utf-8 -*-
from pathlib import Path
import json
import streamlit as st

ROOT = Path(__file__).resolve().parent
DATA_FILE = ROOT / "data" / "wardrobe_items.json"

DEFAULT_ITEMS = [
    {"nome": "Camisa branca", "categoria": "blusa", "cor": "branco", "ocasiao": "trabalho", "favorita": True},
    {"nome": "Calca jeans", "categoria": "calca", "cor": "azul", "ocasiao": "casual", "favorita": True},
    {"nome": "Blazer preto", "categoria": "casaco", "cor": "preto", "ocasiao": "trabalho", "favorita": False},
    {"nome": "Vestido floral", "categoria": "vestido", "cor": "colorido", "ocasiao": "evento", "favorita": True}
]

def load_items():
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        DATA_FILE.write_text(json.dumps(DEFAULT_ITEMS, ensure_ascii=False, indent=2), encoding="utf-8")
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))

def save_items(items):
    DATA_FILE.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")

def suggest_look(items, ocasiao):
    tops = [i for i in items if i["categoria"] in ["blusa", "camisa"] and i["ocasiao"] in [ocasiao, "casual", "trabalho"]]
    bottoms = [i for i in items if i["categoria"] in ["calca", "saia", "short"]]
    dresses = [i for i in items if i["categoria"] == "vestido" and i["ocasiao"] in [ocasiao, "evento"]]
    layers = [i for i in items if i["categoria"] in ["casaco", "blazer"]]

    looks = []

    for dress in dresses:
        look = [dress]
        if layers:
            look.append(layers[0])
        looks.append(look)

    for top in tops:
        for bottom in bottoms:
            look = [top, bottom]
            if layers:
                look.append(layers[0])
            looks.append(look)

    return looks[:5]

st.set_page_config(page_title="Closet Pilot", layout="wide")

st.title("Closet Pilot")
st.caption("Micro-SaaS local para organizar guarda-roupa feminino e sugerir looks simples.")

items = load_items()

col1, col2, col3 = st.columns(3)
col1.metric("Pecas cadastradas", len(items))
col2.metric("Favoritas", len([i for i in items if i.get("favorita")]))
col3.metric("Categorias", len(set(i["categoria"] for i in items)))

tab1, tab2, tab3 = st.tabs(["Cadastrar", "Guarda-roupa", "Sugestoes"])

with tab1:
    st.subheader("Cadastrar nova peca")

    with st.form("nova_peca"):
        nome = st.text_input("Nome da peca")
        categoria = st.selectbox("Categoria", ["blusa", "camisa", "calca", "saia", "vestido", "casaco", "blazer", "sapato", "acessorio"])
        cor = st.text_input("Cor")
        ocasiao = st.selectbox("Ocasiao", ["trabalho", "casual", "evento", "viagem", "rotina"])
        favorita = st.checkbox("Favorita")
        salvar = st.form_submit_button("Salvar")

    if salvar:
        if not nome.strip():
            st.error("Nome obrigatorio.")
        else:
            items.append({
                "nome": nome.strip(),
                "categoria": categoria,
                "cor": cor.strip().lower(),
                "ocasiao": ocasiao,
                "favorita": favorita
            })
            save_items(items)
            st.success("Peca salva. Atualize a pagina para ver nas metricas.")

with tab2:
    st.subheader("Guarda-roupa")
    st.dataframe(items, width="stretch")

with tab3:
    st.subheader("Sugestoes de look")
    ocasiao = st.selectbox("Escolha a ocasiao", ["trabalho", "casual", "evento", "viagem", "rotina"])
    looks = suggest_look(items, ocasiao)

    if not looks:
        st.warning("Ainda nao ha pecas suficientes para sugestao.")
    else:
        for idx, look in enumerate(looks, start=1):
            with st.expander("Look " + str(idx)):
                st.dataframe(look, width="stretch")
