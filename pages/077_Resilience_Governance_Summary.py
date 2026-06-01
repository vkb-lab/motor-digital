# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from pathlib import Path

import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports" / "resilience" / "077_resilience_governance_summary"
SUMMARY_PATH = REPORT_DIR / "077_governance_summary.json"
CLOSURE_PATH = REPORT_DIR / "077_closure_report.json"
SUMMARY_MD_PATH = REPORT_DIR / "077_governance_summary.md"


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
    page_title="077 - Resilience Governance Summary",
    layout="wide",
)

st.title("077 - K-Agent Resilience Governance Summary Core")
st.caption("Pagina somente leitura. Nao executa drill, recovery, rollback ou shell.")

summary = read_json(SUMMARY_PATH)
closure = read_json(CLOSURE_PATH)

if not isinstance(summary, dict):
    st.warning("Resumo de governanca ainda nao encontrado. Execute o checkpoint 077.")
    st.stop()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Checkpoint", summary.get("checkpoint", "077"))
col2.metric("Camada", summary.get("layer", "Resilience"))
col3.metric("Status", summary.get("status", "unknown"))
col4.metric("Evidencias", summary.get("evidence", {}).get("total_evidence_files", 0))

st.subheader("Controles consolidados")
controls = summary.get("controls", [])
if controls:
    st.dataframe(controls, use_container_width=True)
else:
    st.info("Nenhum controle encontrado no resumo.")

st.subheader("Garantias de nao execucao")
guard = summary.get("execution_guard", {})
st.json(guard)

st.subheader("Operacoes bloqueadas")
for operation in summary.get("blocked_operations", []):
    st.write(f"- {operation}")

st.subheader("Evidencias por checkpoint")
evidence = summary.get("evidence", {}).get("checkpoints", {})
for checkpoint, item in evidence.items():
    with st.expander(f"Checkpoint {checkpoint} - {item.get('status')}"):
        st.write(f"Arquivos encontrados: {item.get('evidence_count', 0)}")
        files = item.get("files", [])
        if files:
            st.dataframe(files, use_container_width=True)
        else:
            st.info("Nenhuma evidencia localizada para este checkpoint.")

st.subheader("Closure")
if isinstance(closure, dict):
    st.json(closure)
else:
    st.info("Closure report ainda nao carregado.")

st.subheader("Relatorio Markdown")
markdown_content = read_text(SUMMARY_MD_PATH)
if markdown_content:
    st.markdown(markdown_content)
else:
    st.info("Arquivo markdown do resumo nao encontrado.")