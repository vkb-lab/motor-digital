from __future__ import annotations

import json
import subprocess
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT_ROOT / "ops" / "k_os_agent_permission_matrix.py"
MATRIX_PATH = PROJECT_ROOT / "config" / "governance" / "k_os_agent_permission_matrix.json"
REPORT_PATH = PROJECT_ROOT / "reports" / "governance" / "latest_agent_permission_matrix_report.json"

st.set_page_config(page_title="K-OS Agent Permission Matrix", layout="wide")

st.title("K-OS Agent Permission Matrix")
st.caption("Checkpoint 017 - permissões, limites e responsabilidade das IAs/agentes.")

st.warning(
    "Nenhum agente pode publicar, enviar mensagem externa ou acessar credenciais neste estágio. "
    "Toda ação crítica exige approval gate e evidência."
)


def python_exe() -> str:
    candidates = [
        PROJECT_ROOT / "venv" / "Scripts" / "python.exe",
        PROJECT_ROOT / ".venv" / "Scripts" / "python.exe",
    ]
    for item in candidates:
        if item.exists():
            return str(item)
    return "python"


def run_validate() -> None:
    completed = subprocess.run(
        [python_exe(), str(SCRIPT), "--mode", "validate"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    st.code(" ".join(completed.args), language="powershell")

    if completed.stdout:
        st.code(completed.stdout, language="json")

    if completed.stderr:
        st.code(completed.stderr, language="text")

    if completed.returncode == 0:
        st.success("OK")
    else:
        st.error(f"Bloqueado ou falhou. Código: {completed.returncode}")


if st.button("Validar matriz de permissões", type="primary"):
    run_validate()

st.divider()

if MATRIX_PATH.exists():
    matrix = json.loads(MATRIX_PATH.read_text(encoding="utf-8-sig"))

    agents = matrix.get("agents", [])
    councils = matrix.get("councils", [])

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("Agentes", len(agents))

    with c2:
        st.metric("Conselhos", len(councils))

    with c3:
        external_publish = any(agent.get("can_publish_external") for agent in agents)
        st.metric("Publicação externa", "BLOQUEADA" if not external_publish else "RISCO")

    with c4:
        external_send = any(agent.get("can_send_external") for agent in agents)
        st.metric("Envio externo", "BLOQUEADO" if not external_send else "RISCO")

    st.header("Conselhos")

    for council in councils:
        with st.expander(council.get("name", "Conselho"), expanded=False):
            st.json(council)

    st.header("Agentes")

    for agent in agents:
        with st.expander(f"{agent.get('name')} | risco: {agent.get('risk_level')} | autonomia: {agent.get('autonomy_level')}", expanded=False):
            st.json(agent)

else:
    st.error("Matriz não encontrada.")

st.divider()

st.header("Último relatório")

if REPORT_PATH.exists():
    st.json(json.loads(REPORT_PATH.read_text(encoding="utf-8-sig")))
else:
    st.info("Nenhum relatório encontrado ainda.")

st.caption("K-OS 017 - nenhuma IA sem permissão explícita, dono humano e evidência.")