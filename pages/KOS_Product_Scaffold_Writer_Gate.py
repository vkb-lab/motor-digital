import streamlit as st

from k_atlas.product_factory.scaffold_writer_gate import (
    get_latest_scaffold_preview,
    build_scaffold_writer_gate,
    evaluate_confirmation,
    save_gate_report,
    summarize_writer_gate,
    CONFIRMATION_PHRASE,
)

st.set_page_config(page_title="KOS Product Scaffold Writer Gate", layout="wide")

st.title("KOS Product Scaffold Writer Gate")
st.caption("Gate humano para futura criacao local de scaffold. Fase 55 nao cria arquivos reais.")

preview = get_latest_scaffold_preview()

if not preview:
    st.warning("Nenhum scaffold preview local encontrado.")
else:
    gate = build_scaffold_writer_gate(preview)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Tipo", gate.get("product_type"))
    col2.metric("Arquivos", gate.get("files_count"))
    col3.metric("Criar arquivos", "BLOQUEADO")
    col4.metric("Deploy", "BLOQUEADO")

    st.subheader("Gate")
    st.json(gate)

    st.subheader("Confirmacao futura")
    st.code(CONFIRMATION_PHRASE)

    confirmation = st.text_input("Digite a confirmacao para avaliar dry-run", "")

    if st.button("Avaliar confirmacao sem criar arquivos", use_container_width=True):
        event = evaluate_confirmation(gate, confirmation)
        saved = save_gate_report(gate, event)
        st.json({"event": event, "saved": saved})

st.subheader("Resumo")
st.json(summarize_writer_gate())

st.warning("Gate-only. Nao cria arquivos reais, nao executa build, nao usa IA paga, nao publica.")
