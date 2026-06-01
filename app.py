from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from k_atlas.agent_registry import register_default_agents
from k_atlas.campaign_engine import generate_campaign, list_campaigns
from k_atlas.events import read_events
from k_atlas.memory_store import MemoryStore
from k_atlas.paths import EVENTS_FILE, REQUIRED_DIRS, ensure_dirs, relative_to_root
from k_atlas.reporting import generate_report
from k_atlas.task_runner import TaskRunner


st.set_page_config(page_title="K-Atlas OS", layout="wide")
ensure_dirs()

registry = register_default_agents()
runner = TaskRunner(registry)
memory = MemoryStore()

st.title("K-Atlas OS")
st.caption("Cockpit operacional local do K-OS / Motor Digital")

tabs = st.tabs(
    [
        "Painel Geral",
        "Status do sistema",
        "Memoria operacional",
        "Executor de agentes",
        "Campanhas",
        "Relatorios",
        "Logs recentes",
    ]
)

with tabs[0]:
    st.subheader("Painel Geral")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Agentes", len(registry.names()))
    col2.metric("Memorias", len(memory.all()))
    col3.metric("Campanhas", len(list_campaigns()))
    col4.metric("Eventos", len(read_events(limit=1000)))
    st.write("Camada operacional modular pronta para operar com fallback local.")

with tabs[1]:
    st.subheader("Status do sistema")
    status_rows = [{"pasta": relative_to_root(path), "existe": path.exists()} for path in REQUIRED_DIRS]
    st.dataframe(status_rows, use_container_width=True)
    st.write({"app.py": Path("app.py").exists(), "events.jsonl": EVENTS_FILE.exists()})

with tabs[2]:
    st.subheader("Memoria operacional")
    with st.form("memory_form"):
        key = st.text_input("Chave", value="nota")
        value = st.text_area("Valor", value="Registro operacional local")
        submitted = st.form_submit_button("Gravar memoria")
    if submitted:
        memory.add(key, value, ["manual", "cockpit"])
        st.success("Memoria gravada")
    st.dataframe(memory.all(), use_container_width=True)

with tabs[3]:
    st.subheader("Executor de agentes")
    agent_name = st.selectbox("Agente", registry.names())
    task = st.text_input("Tarefa", value="verificar sistema")
    context_raw = st.text_area("Contexto JSON", value="{}")
    if st.button("Executar agente"):
        try:
            context = json.loads(context_raw or "{}")
            result = runner.run(agent_name, task, context)
            st.json(result)
        except Exception as exc:
            st.error(str(exc))

with tabs[4]:
    st.subheader("Campanhas")
    with st.form("campaign_form"):
        name = st.text_input("Nome", value="Campanha K-OS MVP")
        objective = st.text_input("Objetivo", value="Validar operacao local do Motor Digital")
        audience = st.text_input("Publico", value="operadores do K-OS")
        submitted_campaign = st.form_submit_button("Gerar campanha")
    if submitted_campaign:
        st.json(generate_campaign(name, objective, audience))
    for path in list_campaigns():
        with st.expander(relative_to_root(path)):
            st.code(path.read_text(encoding="utf-8"), language="json")

with tabs[5]:
    st.subheader("Relatorios")
    if st.button("Gerar relatorio operacional"):
        report_path = generate_report("K-OS Cockpit Report", {"source": "streamlit"})
        st.success(f"Relatorio criado: {relative_to_root(report_path)}")
    for path in sorted(Path("reports").glob("*.md")):
        with st.expander(relative_to_root(path)):
            st.markdown(path.read_text(encoding="utf-8"))

with tabs[6]:
    st.subheader("Logs recentes")
    events = read_events(limit=100)
    if events:
        st.dataframe(events, use_container_width=True)
    else:
        st.info("Sem eventos registrados.")

