# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from pathlib import Path

import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports" / "system" / "079_system_health_monitor"
HEALTH_PATH = REPORT_DIR / "079_system_health_report.json"
CLOSURE_PATH = REPORT_DIR / "079_closure_report.json"
HEALTH_MD_PATH = REPORT_DIR / "079_system_health_report.md"


def read_json(path: Path):
    try:
        with path.open("r", encoding="utf-8-sig") as handle:
            return json.load(handle)
    except Exception:
        return None


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8-sig")
    except Exception:
        return ""


st.set_page_config(
    page_title="079 - K-OS System Health Monitor",
    layout="wide",
)

st.title("079 - K-OS System Health Monitor Core")
st.caption("Pagina somente leitura. Diagnostico local sem auto-fix, recovery, rollback, drill ou shell.")

health = read_json(HEALTH_PATH)
closure = read_json(CLOSURE_PATH)

if not isinstance(health, dict):
    st.warning("Relatorio de saude ainda nao encontrado. Execute o checkpoint 079.")
    st.stop()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Checkpoint", health.get("checkpoint", "079"))
col2.metric("Camada", health.get("layer", "K-OS Core"))
col3.metric("Status", health.get("status", "unknown"))
col4.metric("Dominios atencao", len(health.get("attention_domains", [])))

st.subheader("Decisao operacional")
st.json(health.get("operational_decision", {}))

st.subheader("Dominios")
domains = []
for name, data in health.get("domain_checks", {}).items():
    domains.append({
        "domain": name,
        "status": data.get("status", "unknown") if isinstance(data, dict) else "unknown",
    })
if domains:
    st.dataframe(domains, use_container_width=True)

st.subheader("Dominios com atencao")
attention = health.get("attention_domains", [])
if attention:
    for item in attention:
        st.write(f"- {item}")
else:
    st.success("Nenhum dominio com atencao.")

st.subheader("Diretorios criticos")
critical_dirs = health.get("domain_checks", {}).get("critical_directories", {}).get("items", [])
if critical_dirs:
    st.dataframe(critical_dirs, use_container_width=True)

st.subheader("Arquivos criticos")
critical_files = health.get("domain_checks", {}).get("critical_files", {}).get("items", [])
if critical_files:
    st.dataframe(critical_files, use_container_width=True)

st.subheader("Streamlit")
st.json(health.get("domain_checks", {}).get("streamlit_entrypoint", {}))

st.subheader("Memoria e seguranca local")
st.json(health.get("domain_checks", {}).get("memory_safety", {}))

st.subheader("Evidencias Resilience")
resilience = health.get("domain_checks", {}).get("resilience_closure_evidence", {})
st.json({
    "status": resilience.get("status"),
    "expected_count": resilience.get("expected_count"),
    "found_count": resilience.get("found_count"),
})
items = resilience.get("items", [])
if items:
    st.dataframe(items, use_container_width=True)

st.subheader("Garantias de nao execucao")
st.json(health.get("execution_guard", {}))

st.subheader("Closure report")
if isinstance(closure, dict):
    st.json(closure)
else:
    st.info("Closure report ainda nao carregado.")

st.subheader("Relatorio Markdown")
markdown_content = read_text(HEALTH_MD_PATH)
if markdown_content:
    st.markdown(markdown_content)
else:
    st.info("Arquivo markdown do relatorio nao encontrado.")