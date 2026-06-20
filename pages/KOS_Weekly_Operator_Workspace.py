from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
LATEST = ROOT / "local_runtime" / "kos_weekly_ops" / "latest_weekly_operator_workspace.json"


def read_json(path: Path) -> dict:
    if not path.exists():
        return {"status": "MISSING", "path": str(path)}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        return {"status": "READ_ERROR", "error": str(exc), "path": str(path)}


st.set_page_config(page_title="K-OS Weekly Workspace", layout="wide")

st.title("K-OS Weekly Operator Workspace")
st.caption("Painel semanal para administração, SaaS, redes sociais e operação segura.")

data = read_json(LATEST)

if data.get("status") == "MISSING":
    st.warning("Workspace semanal ainda não foi gerado.")
    st.code("python scripts\\run_phase72a_weekly_operator_workspace.py", language="powershell")
    st.stop()

st.success(data.get("status", "READY"))

c1, c2, c3, c4 = st.columns(4)
c1.metric("Semana", data.get("week_id", "n/d"))
c2.metric("Publicação automática", "bloqueada")
c3.metric("Conta teste", "Hupmix")
c4.metric("Parada Atlântida", "bloqueada")

tab_today, tab_week, tab_social, tab_saas, tab_admin, tab_commands = st.tabs(
    ["Hoje", "Semana", "Redes", "SaaS", "Admin", "Comandos"]
)

with tab_today:
    st.subheader("Protocolo diário")
    for item in data.get("daily_protocol", []):
        st.checkbox(item, value=False)

    st.subheader("Escolha uma prioridade")
    st.info("Escolha só uma prioridade principal por bloco de trabalho.")

with tab_week:
    st.subheader("Plano de 7 dias")
    for day in data.get("days", []):
        with st.expander(f"Dia {day.get('day')} - {day.get('theme')}"):
            st.write("Foco:")
            for item in day.get("focus", []):
                st.write("- " + item)
            st.success("Resultado esperado: " + day.get("success", ""))

with tab_social:
    st.subheader("Redes sociais")
    st.json(data.get("tracks", {}).get("social", {}))
    st.warning("Não publicar sem readiness, ledger e confirmação humana.")

with tab_saas:
    st.subheader("Projetos SaaS")
    st.json(data.get("tracks", {}).get("saas", {}))
    st.info("Meta da semana: escolher 1 SaaS pequeno e transformar em escopo MVP.")

with tab_admin:
    st.subheader("Administração")
    st.json(data.get("tracks", {}).get("admin", {}))
    st.info("Meta da semana: reduzir pendências e manter uma rotina mínima.")

with tab_commands:
    st.subheader("Comandos seguros")
    for cmd in data.get("safe_commands", []):
        st.caption(cmd.get("label", "comando"))
        st.code(cmd.get("command", ""), language="powershell")

    st.subheader("Guardrails")
    st.json(data.get("guardrails", {}))
