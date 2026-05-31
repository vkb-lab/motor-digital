from __future__ import annotations

import json
import subprocess
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT_ROOT / "ops" / "k_os_analytics_executive_metrics_core.py"
REPORT_PATH = PROJECT_ROOT / "reports" / "analytics" / "latest_executive_metrics_report.json"
DASHBOARD_PATH = PROJECT_ROOT / "reports" / "analytics" / "latest_executive_dashboard_snapshot.json"
HEALTH_PATH = PROJECT_ROOT / "reports" / "analytics" / "latest_operational_health_snapshot.json"
POLICY_PATH = PROJECT_ROOT / "config" / "analytics" / "k_os_analytics_executive_metrics_policy.json"

st.set_page_config(page_title="K-OS Executive Analytics", layout="wide")

st.title("K-OS Analytics and Executive Metrics Core")
st.caption("Checkpoint 036 - métricas executivas sanitizadas e saúde operacional.")

st.warning(
    "Painel executivo sanitizado. Não exporta dados identificáveis. Não publica métricas externamente."
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


tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Health", "Sources", "Policy"])

with tab1:
    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("Inicializar Analytics", type="primary"):
            run(["--mode", "init"])

    with c2:
        if st.button("Atualizar Dashboard"):
            run(["--mode", "dashboard"])

    with c3:
        if st.button("Auditar métricas"):
            run(["--mode", "audit"])

    if DASHBOARD_PATH.exists():
        dashboard = json.loads(DASHBOARD_PATH.read_text(encoding="utf-8-sig"))
        kpis = dashboard.get("top_kpis", {})

        st.subheader("KPIs executivos")

        c1, c2, c3, c4, c5 = st.columns(5)

        with c1:
            st.metric("Clientes", kpis.get("customers", 0))

        with c2:
            st.metric("Assinaturas", kpis.get("subscriptions", 0))

        with c3:
            st.metric("MRR estimado", kpis.get("estimated_mrr_brl", 0))

        with c4:
            st.metric("Pipeline", kpis.get("weighted_pipeline_brl", 0))

        with c5:
            st.metric("Foundation", kpis.get("foundation_score", 0))

        c6, c7, c8, c9, c10 = st.columns(5)

        with c6:
            st.metric("Tickets abertos", kpis.get("open_tickets", 0))

        with c7:
            st.metric("Tarefas abertas", kpis.get("open_tasks", 0))

        with c8:
            st.metric("Clientes risco", kpis.get("high_risk_customers", 0))

        with c9:
            st.metric("Features", kpis.get("features", 0))

        with c10:
            st.metric("Releases", kpis.get("roadmap_releases", 0))

        st.json(dashboard)

    if REPORT_PATH.exists():
        report = json.loads(REPORT_PATH.read_text(encoding="utf-8-sig"))
        st.subheader("Relatório executivo completo")
        st.json(report)

with tab2:
    if st.button("Atualizar health snapshot", type="primary"):
        run(["--mode", "health"])

    if HEALTH_PATH.exists():
        health = json.loads(HEALTH_PATH.read_text(encoding="utf-8-sig"))
        st.metric("Health level", health.get("health_level", "unknown"))
        st.json(health)

with tab3:
    if REPORT_PATH.exists():
        report = json.loads(REPORT_PATH.read_text(encoding="utf-8-sig"))

        st.subheader("Fontes de dados")
        st.dataframe(report.get("data_sources", []), use_container_width=True)

        st.subheader("Controles foundation")
        st.dataframe(report.get("foundation_controls", []), use_container_width=True)
    else:
        st.info("Relatório ainda não gerado.")

with tab4:
    if POLICY_PATH.exists():
        st.json(json.loads(POLICY_PATH.read_text(encoding="utf-8-sig")))
    else:
        st.info("Policy ainda não encontrada.")