from __future__ import annotations

import json
import subprocess
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT_ROOT / "ops" / "k_os_memory_event_bus_context_index_core.py"
REPORT_PATH = PROJECT_ROOT / "reports" / "memory_bus" / "latest_memory_event_bus_report.json"
INDEX_PATH = PROJECT_ROOT / "reports" / "memory_bus" / "latest_context_index_snapshot.json"
SEARCH_PATH = PROJECT_ROOT / "reports" / "memory_bus" / "latest_memory_search_report.json"
POLICY_PATH = PROJECT_ROOT / "config" / "memory_bus" / "k_os_memory_event_bus_policy.json"

st.set_page_config(page_title="K-OS Memory Event Bus", layout="wide")

st.title("K-OS Memory Event Bus and Context Index")
st.caption("Checkpoint 042 - barramento de eventos, índice de contexto e busca local sanitizada.")

st.warning(
    "Memória local e sanitizada. Payload bruto não é publicado. Estado local fica fora do GitHub."
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


tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Busca", "Fontes", "Policy"])

with tab1:
    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("Inicializar Memory Bus", type="primary"):
            run(["--mode", "init"])

    with c2:
        if st.button("Reconstruir índice"):
            run(["--mode", "build-index"])

    with c3:
        if st.button("Auditar memória"):
            run(["--mode", "audit"])

    report = read_json(REPORT_PATH)

    if report:
        metrics = report.get("metrics", {})

        m1, m2, m3, m4, m5 = st.columns(5)

        with m1:
            st.metric("Eventos", metrics.get("event_count", 0))

        with m2:
            st.metric("Contextos", metrics.get("context_item_count", 0))

        with m3:
            st.metric("Contextos OK", metrics.get("context_ok_count", 0))

        with m4:
            st.metric("Ausentes", metrics.get("missing_context_count", 0))

        with m5:
            st.metric("Domínios", metrics.get("domain_count", 0))

        st.subheader("Resumo por domínio")
        st.dataframe(
            [{"domain": domain, **values} for domain, values in report.get("domain_summary", {}).items()],
            use_container_width=True
        )

        st.subheader("Eventos recentes")
        st.dataframe(report.get("latest_events", []), use_container_width=True)

        st.subheader("Contextos indexados")
        st.dataframe(report.get("context_items", []), use_container_width=True)

with tab2:
    query = st.text_input("Busca local", value="agent")

    if st.button("Buscar", type="primary"):
        run(["--mode", "search", "--query", query])

    search = read_json(SEARCH_PATH)

    if search:
        st.metric("Eventos encontrados", search.get("event_match_count", 0))
        st.metric("Contextos encontrados", search.get("context_match_count", 0))

        st.subheader("Eventos")
        st.dataframe(search.get("events", []), use_container_width=True)

        st.subheader("Contextos")
        st.dataframe(search.get("context_items", []), use_container_width=True)

with tab3:
    report = read_json(REPORT_PATH)

    if report:
        st.subheader("Event sources")
        st.dataframe(report.get("event_sources", []), use_container_width=True)

        st.subheader("Report sources")
        st.dataframe(report.get("report_sources", []), use_container_width=True)

    index = read_json(INDEX_PATH)
    if index:
        st.subheader("Snapshot")
        st.json(index)

with tab4:
    if POLICY_PATH.exists():
        st.json(json.loads(POLICY_PATH.read_text(encoding="utf-8-sig")))
    else:
        st.info("Policy ainda não encontrada.")