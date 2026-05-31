from __future__ import annotations

import json
import subprocess
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT_ROOT / "ops" / "k_os_command_center_action_router.py"
REPORT_PATH = PROJECT_ROOT / "reports" / "command_center" / "latest_command_center_action_router_report.json"
EXECUTION_PATH = PROJECT_ROOT / "reports" / "command_center" / "latest_action_execution_report.json"
CATALOG_PATH = PROJECT_ROOT / "reports" / "command_center" / "latest_action_catalog.json"
POLICY_PATH = PROJECT_ROOT / "config" / "command_center" / "k_os_command_center_action_router_policy.json"

st.set_page_config(page_title="K-OS Command Center", layout="wide")

st.title("K-OS Command Center Action Router")
st.caption("Checkpoint 038 - roteador central de ações controladas, dry-run, approval gate e auditoria.")

st.warning(
    "Apenas ações em allowlist. Comandos arbitrários são bloqueados. Dry-run é o padrão."
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


def run(args: list[str]) -> None:
    completed = subprocess.run(
        [python_exe(), str(SCRIPT), *args],
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
        st.error(f"Falhou: {completed.returncode}")


def read_json(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8-sig"))
    return {}


tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Executar ação", "Histórico", "Policy"])

with tab1:
    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("Inicializar Router", type="primary"):
            run(["--mode", "init"])

    with c2:
        if st.button("Atualizar catálogo"):
            run(["--mode", "catalog"])

    with c3:
        if st.button("Auditar Router"):
            run(["--mode", "audit"])

    report = read_json(REPORT_PATH)

    if report:
        m1, m2, m3, m4 = st.columns(4)

        with m1:
            st.metric("Ações", report.get("action_count", 0))

        with m2:
            st.metric("Scripts ausentes", report.get("script_missing_count", 0))

        with m3:
            st.metric("Dry-run default", str(report.get("dry_run_default", True)))

        with m4:
            st.metric("Shell arbitrário", str(report.get("arbitrary_shell_command_allowed", False)))

        st.subheader("Ações permitidas")
        st.dataframe(report.get("actions", []), use_container_width=True)

with tab2:
    catalog = read_json(CATALOG_PATH)
    if not catalog:
        catalog = read_json(REPORT_PATH)

    actions = catalog.get("actions", [])

    if actions:
        action_ids = [item.get("action_id") for item in actions]
        action_id = st.selectbox("Action ID", action_ids)

        selected = next((item for item in actions if item.get("action_id") == action_id), {})
        st.json(selected)

        approved = st.checkbox("Approval humano registrado")
        execute = st.checkbox("Executar de verdade, não apenas dry-run")
        reason = st.text_input("Motivo / aprovação", value="operator_review")

        args = ["--mode", "route", "--action-id", action_id]

        if approved:
            args.append("--approved")

        if reason:
            args.extend(["--reason", reason])

        if execute:
            args.append("--execute")

        if st.button("Rodar ação controlada", type="primary"):
            run(args)

        if EXECUTION_PATH.exists():
            st.subheader("Última execução")
            st.json(read_json(EXECUTION_PATH))
    else:
        st.info("Catálogo ainda não gerado.")

with tab3:
    report = read_json(REPORT_PATH)

    if report:
        st.dataframe(report.get("recent_executions", []), use_container_width=True)

    if EXECUTION_PATH.exists():
        st.subheader("Última execução")
        st.json(read_json(EXECUTION_PATH))

with tab4:
    if POLICY_PATH.exists():
        st.json(json.loads(POLICY_PATH.read_text(encoding="utf-8-sig")))
    else:
        st.info("Policy ainda não encontrada.")