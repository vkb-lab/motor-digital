from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.blackboard.blackboard_agent import BlackboardAgent
from k_atlas.core.blackboard.blackboard_store import BlackboardStore
from k_atlas.core.blackboard.command_policy import evaluate_command


MESSAGES_PATH = Path("memory/blackboard/messages.json")
COMMANDS_PATH = Path("memory/blackboard/command_queue.json")
RESULTS_PATH = Path("memory/blackboard/command_results.json")


def load_json_list(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []

    if isinstance(data, list):
        return data

    return []


st.set_page_config(page_title="K-Atlas Lousa Operacional", layout="wide")

st.title("K-Atlas Lousa Operacional")
st.caption("Lousa + fila de comandos + PowerShell Runner local. Execucao somente com aprovacao.")

store = BlackboardStore(MESSAGES_PATH, COMMANDS_PATH, RESULTS_PATH)
agent = BlackboardAgent(store)

messages = load_json_list(MESSAGES_PATH)
commands = load_json_list(COMMANDS_PATH)
results = load_json_list(RESULTS_PATH)

pending = [item for item in commands if item.get("approval_status") == "pending_approval"]
approved = [item for item in commands if item.get("approval_status") == "approved"]
finished = [item for item in commands if item.get("execution_status") in {"finished", "failed"}]

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Mensagens", len(messages))

with col2:
    st.metric("Comandos pendentes", len(pending))

with col3:
    st.metric("Aprovados", len(approved))

with col4:
    st.metric("Finalizados", len(finished))

st.divider()

tab_board, tab_plan, tab_queue, tab_results, tab_runner = st.tabs([
    "Lousa",
    "Gerar plano",
    "Fila PowerShell",
    "Resultados",
    "Runner local",
])

with tab_board:
    st.subheader("Mensagens da Lousa")

    new_message = st.text_area("Nova mensagem / objetivo", height=120)

    if st.button("Registrar na Lousa"):
        if new_message.strip():
            item = store.add_message(
                author="human_operator",
                role="user",
                content=new_message.strip(),
            )
            st.success("Mensagem registrada.")
            st.json(item)

    st.divider()

    for item in reversed(load_json_list(MESSAGES_PATH)[-50:]):
        with st.expander(f"{item.get('created_at')} | {item.get('author')}"):
            st.write(item.get("content"))
            st.json(item.get("metadata", {}))

with tab_plan:
    st.subheader("Gerar plano seguro")

    objective = st.text_input(
        "Objetivo",
        value="continuar evolucao supervisionada do K-Atlas OS",
    )

    if st.button("Gerar comandos diagnosticos seguros", type="primary"):
        result = agent.create_safe_plan(objective=objective, requested_by="streamlit_operator")
        st.success("Plano criado. Comandos aguardam aprovacao.")
        st.json(result)

with tab_queue:
    st.subheader("Fila de comandos PowerShell")

    reviewer = st.text_input("Revisor", value="k_supervisor")

    for item in reversed(load_json_list(COMMANDS_PATH)[-80:]):
        policy = evaluate_command(str(item.get("command", "")))
        label = f"{item.get('approval_status')} | {item.get('execution_status')} | {item.get('title')}"

        with st.expander(label):
            st.code(item.get("command", ""), language="powershell")
            st.json(item)
            st.json(policy.to_dict())

            if item.get("approval_status") == "pending_approval":
                if st.button("Aprovar comando", key=f"approve_{item.get('command_id')}"):
                    approved_item = store.approve_command(item["command_id"], reviewer=reviewer)
                    st.success("Comando aprovado para o runner local.")
                    st.json(approved_item)

with tab_results:
    st.subheader("Resultados do PowerShell Runner")

    rows = load_json_list(RESULTS_PATH)

    if not rows:
        st.info("Nenhum resultado registrado ainda.")
    else:
        for item in reversed(rows[-80:]):
            result = item.get("result", {})
            with st.expander(f"{item.get('created_at')} | {result.get('status')} | {result.get('command')}"):
                st.json(result)
                if result.get("stdout"):
                    st.text_area("stdout", result.get("stdout"), height=180)
                if result.get("stderr"):
                    st.text_area("stderr", result.get("stderr"), height=180)

with tab_runner:
    st.subheader("Como deixar o runner trabalhando")

    st.write("No PowerShell local, deixe este comando rodando:")

    st.code(
        'powershell -ExecutionPolicy Bypass -File "C:\\Users\\oi\\Desktop\\motor-digital\\ops\\start_blackboard_runner.ps1"',
        language="powershell",
    )

    st.warning(
        "O Render nao executa PowerShell do seu computador. Para executar comandos locais, o runner precisa estar aberto no Windows."
    )