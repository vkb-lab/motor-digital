from __future__ import annotations

import json
import subprocess
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT_ROOT / "ops" / "k_os_executive_cockpit_consolidation_layer.py"
REPORT_PATH = PROJECT_ROOT / "reports" / "cockpit" / "latest_executive_cockpit_report.json"
NAV_PATH = PROJECT_ROOT / "reports" / "cockpit" / "latest_cockpit_navigation_map.json"
HEALTH_PATH = PROJECT_ROOT / "reports" / "cockpit" / "latest_cockpit_health_snapshot.json"
POLICY_PATH = PROJECT_ROOT / "config" / "cockpit" / "k_os_executive_cockpit_policy.json"

st.set_page_config(page_title="K-OS Executive Cockpit", layout="wide")

st.title("K-OS Executive Cockpit")
st.caption("Checkpoint 037 - cockpit executivo central, navegação unificada e health operacional.")

st.warning(
    "Cockpit local e sanitizado. Não publica métricas, não exporta dados identificáveis e não ativa integrações externas."
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


tab1, tab2, tab3, tab4, tab5 = st.tabs(["Executive", "Módulos", "Navegação", "Health", "Policy"])

with tab1:
    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("Atualizar cockpit", type="primary"):
            run(["--mode", "audit"])

    with c2:
        if st.button("Atualizar navegação"):
            run(["--mode", "navigation"])

    with c3:
        if st.button("Atualizar health"):
            run(["--mode", "health"])

    report = read_json(REPORT_PATH)

    if report:
        health = report.get("cockpit_health", {})
        analytics = report.get("analytics", {})
        metrics = analytics.get("metrics", {})

        m1, m2, m3, m4, m5 = st.columns(5)

        with m1:
            st.metric("Health", health.get("health_level", "unknown"))

        with m2:
            st.metric("Completion", health.get("completion_score", 0))

        with m3:
            st.metric("Clientes", metrics.get("customer_count", 0))

        with m4:
            st.metric("MRR estimado", metrics.get("estimated_mrr_brl", 0))

        with m5:
            st.metric("Pipeline", metrics.get("weighted_pipeline_brl", 0))

        n1, n2, n3, n4, n5 = st.columns(5)

        with n1:
            st.metric("Tickets abertos", metrics.get("open_ticket_count", 0))

        with n2:
            st.metric("Tarefas abertas", metrics.get("open_task_count", 0))

        with n3:
            st.metric("Clientes risco", metrics.get("high_risk_customer_count", 0))

        with n4:
            st.metric("Features", metrics.get("feature_count", 0))

        with n5:
            st.metric("Releases", metrics.get("roadmap_release_count", 0))

        st.subheader("Resumo por domínio")
        st.dataframe(
            [{"domain": domain, **values} for domain, values in report.get("domain_summary", {}).items()],
            use_container_width=True
        )

with tab2:
    report = read_json(REPORT_PATH)

    if report:
        modules = report.get("modules", [])

        domain_filter = st.selectbox(
            "Filtrar domínio",
            ["todos"] + sorted({item.get("domain", "unknown") for item in modules})
        )

        if domain_filter != "todos":
            modules = [item for item in modules if item.get("domain") == domain_filter]

        st.dataframe(modules, use_container_width=True)

        st.subheader("Abertura rápida")
        for item in modules:
            page = item.get("page", "")
            label = f"{item.get('checkpoint')} - {item.get('name')}"
            if item.get("page_exists"):
                st.code(f"streamlit run {page}", language="powershell")
            else:
                st.error(f"Página ausente: {label}")
    else:
        st.info("Relatório do cockpit ainda não gerado.")

with tab3:
    nav = read_json(NAV_PATH)

    if nav:
        st.json(nav)
    else:
        st.info("Mapa de navegação ainda não gerado.")

with tab4:
    health = read_json(HEALTH_PATH)

    if health:
        st.metric("Health", health.get("health_level", "unknown"))
        st.metric("Completion score", health.get("completion_score", 0))
        st.json(health)
    else:
        st.info("Health snapshot ainda não gerado.")

with tab5:
    if POLICY_PATH.exists():
        st.json(json.loads(POLICY_PATH.read_text(encoding="utf-8-sig")))
    else:
        st.info("Policy ainda não encontrada.")