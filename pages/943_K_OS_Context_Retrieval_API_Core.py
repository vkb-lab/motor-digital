from __future__ import annotations

import json
import subprocess
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT_ROOT / "ops" / "k_os_context_retrieval_api_core.py"
REPORT_PATH = PROJECT_ROOT / "reports" / "context_api" / "latest_context_retrieval_api_report.json"
CATALOG_PATH = PROJECT_ROOT / "reports" / "context_api" / "latest_context_api_catalog.json"
RETRIEVAL_PATH = PROJECT_ROOT / "reports" / "context_api" / "latest_context_retrieval_report.json"
POLICY_PATH = PROJECT_ROOT / "config" / "context_api" / "k_os_context_retrieval_api_policy.json"

st.set_page_config(page_title="K-OS Context Retrieval API", layout="wide")

st.title("K-OS Context Retrieval API Core")
st.caption("Checkpoint 043 - API local de recuperação de contexto para agentes e cockpit.")

st.warning(
    "API local em 127.0.0.1. Não retorna payload bruto. Não envia dados externos."
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


tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Retrieve", "API", "Policy"])

with tab1:
    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("Inicializar Context API", type="primary"):
            run(["--mode", "init"])

    with c2:
        if st.button("Gerar catálogo"):
            run(["--mode", "catalog"])

    with c3:
        if st.button("Auditar API"):
            run(["--mode", "audit"])

    report = read_json(REPORT_PATH)

    if report:
        m1, m2, m3, m4, m5 = st.columns(5)

        with m1:
            st.metric("Eventos", report.get("event_count", 0))

        with m2:
            st.metric("Contextos", report.get("context_item_count", 0))

        with m3:
            st.metric("Domínios", report.get("domain_count", 0))

        with m4:
            st.metric("Endpoints", report.get("endpoint_count", 0))

        with m5:
            st.metric("Local only", str(report.get("local_only", True)))

        st.subheader("Domínios")
        st.dataframe(
            [{"domain": domain, **values} for domain, values in report.get("domains", {}).items()],
            use_container_width=True
        )

        st.subheader("Recuperações recentes")
        st.dataframe(report.get("recent_retrievals", []), use_container_width=True)

with tab2:
    query = st.text_input("Query", value="agent")
    domain = st.text_input("Domain", value="")
    module_filter = st.text_input("Module", value="")
    event = st.text_input("Event", value="")
    limit = st.number_input("Limit", min_value=1, max_value=100, value=20)

    args = [
        "--mode", "retrieve",
        "--query", query,
        "--domain", domain,
        "--module-filter", module_filter,
        "--event", event,
        "--limit", str(limit)
    ]

    if st.button("Recuperar contexto", type="primary"):
        run(args)

    retrieval = read_json(RETRIEVAL_PATH)

    if retrieval:
        st.metric("Eventos encontrados", retrieval.get("event_match_count", 0))
        st.metric("Contextos encontrados", retrieval.get("context_match_count", 0))

        st.subheader("Eventos")
        st.dataframe(retrieval.get("events", []), use_container_width=True)

        st.subheader("Contextos")
        st.dataframe(retrieval.get("context_items", []), use_container_width=True)

with tab3:
    catalog = read_json(CATALOG_PATH)

    if catalog:
        st.json(catalog)
    else:
        st.info("Catálogo ainda não gerado.")

    st.subheader("Abrir API local")
    st.code("powershell -ExecutionPolicy Bypass -File ops\\open_k_os_context_retrieval_api.ps1", language="powershell")
    st.code("http://127.0.0.1:8583/health", language="text")
    st.code("http://127.0.0.1:8583/retrieve?query=agent&limit=10", language="text")

with tab4:
    if POLICY_PATH.exists():
        st.json(json.loads(POLICY_PATH.read_text(encoding="utf-8-sig")))
    else:
        st.info("Policy ainda não encontrada.")