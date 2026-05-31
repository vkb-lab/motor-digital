from __future__ import annotations

import json
import subprocess
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT_ROOT / "ops" / "k_os_agent_safe_execution_router_core.py"
REPORT_PATH = PROJECT_ROOT / "reports" / "safe_execution_router" / "latest_agent_safe_execution_router_report.json"
ROUTE_PATH = PROJECT_ROOT / "reports" / "safe_execution_router" / "latest_safe_execution_route.json"
VALIDATION_PATH = PROJECT_ROOT / "reports" / "safe_execution_router" / "latest_safe_execution_route_validation_report.json"
POLICY_PATH = PROJECT_ROOT / "config" / "safe_execution_router" / "k_os_agent_safe_execution_router_policy.json"

st.set_page_config(page_title="K-OS Safe Execution Router", layout="wide")

st.title("K-OS Agent Safe Execution Router Core")
st.caption("Checkpoint 048 - roteamento seguro para executor allowlisted.")

st.warning(
    "O router não executa ação real. Ele valida aprovação, allowlist e segurança antes do executor."
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


tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Criar rota", "Validação", "Policy"])

with tab1:
    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("Inicializar", type="primary"):
            run(["--mode", "init"])

    with c2:
        if st.button("Auditar"):
            run(["--mode", "audit"])

    with c3:
        if st.button("Validar última"):
            run(["--mode", "validate-latest"])

    report = read_json(REPORT_PATH)

    if report:
        metrics = report.get("metrics", {})

        m1, m2, m3, m4 = st.columns(4)

        with m1:
            st.metric("Rotas", metrics.get("route_count", 0))

        with m2:
            st.metric("Prontas", metrics.get("ready_route_count", 0))

        with m3:
            st.metric("Bloqueadas", metrics.get("blocked_route_count", 0))

        with m4:
            st.metric("Execução router", metrics.get("real_execution_by_router_count", 0))

        st.subheader("Rotas recentes")
        st.dataframe(report.get("recent_routes", []), use_container_width=True)

with tab2:
    target = st.selectbox(
        "Route target",
        [
            "cockpit_audit",
            "analytics_audit",
            "security_scan_staged",
            "memory_bus_audit",
            "context_api_audit",
            "agent_runtime_audit",
            "agent_queue_audit",
            "command_center_dry_route",
            "safe_internal_noop"
        ]
    )
    operator = st.text_input("Operator", value="operator_k_os")
    reason = st.text_input("Reason", value="operator_safe_route_after_approval")

    if st.button("Criar rota segura", type="primary"):
        run(["--mode", "route", "--target", target, "--operator", operator, "--reason", reason])

    route = read_json(ROUTE_PATH)
    if route:
        st.subheader("Última rota")
        st.json(route)

with tab3:
    validation = read_json(VALIDATION_PATH)
    if validation:
        st.json(validation)
    else:
        st.info("Nenhuma validação registrada.")

with tab4:
    if POLICY_PATH.exists():
        st.json(json.loads(POLICY_PATH.read_text(encoding="utf-8-sig")))
    else:
        st.info("Policy ainda não encontrada.")