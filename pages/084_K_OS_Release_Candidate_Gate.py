# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from pathlib import Path

import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports" / "system" / "084_release_candidate_gate"
GATE_PATH = REPORT_DIR / "084_release_candidate_gate.json"
CLOSURE_PATH = REPORT_DIR / "084_closure_report.json"
GATE_MD_PATH = REPORT_DIR / "084_release_candidate_gate.md"


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
    page_title="084 - K-OS Release Candidate Gate",
    layout="wide",
)

st.title("084 - K-OS Release Candidate Gate Core")
st.caption("Pagina somente leitura. Gate RC sem deploy, installer, release publish, recovery, rollback ou auto-fix.")

gate = read_json(GATE_PATH)
closure = read_json(CLOSURE_PATH)

if not isinstance(gate, dict):
    st.warning("Gate de Release Candidate ainda nao encontrado. Execute o checkpoint 084.")
    st.stop()

warnings = gate.get("warnings", [])
evidence = gate.get("evidence", {})

col1, col2, col3, col4 = st.columns(4)
col1.metric("Checkpoint", gate.get("checkpoint", "084"))
col2.metric("Camada", gate.get("layer", "K-OS Core"))
col3.metric("Status RC", gate.get("status", "unknown"))
col4.metric("Warnings", len(warnings))

st.subheader("Decisao do gate")
st.json(gate.get("gate_decision", {}))

st.subheader("Gate por dominio")
domain_gates = gate.get("domain_gates", [])
if domain_gates:
    st.dataframe(domain_gates, use_container_width=True)

st.subheader("Warnings")
if warnings:
    for item in warnings:
        st.write(f"- {item}")
else:
    st.success("Nenhum warning registrado.")

st.subheader("Evidencias consolidadas")
checkpoint_items = evidence.get("checkpoints", {})
if checkpoint_items:
    rows = []
    for checkpoint, item in checkpoint_items.items():
        rows.append({
            "checkpoint": checkpoint,
            "name": item.get("name"),
            "main_exists": item.get("main_exists"),
            "validate_status": item.get("validate_status"),
            "audit_status": item.get("audit_status"),
            "closure_status": item.get("closure_status"),
            "evidence_status": item.get("evidence_status"),
            "evidence_file_count": item.get("evidence_file_count"),
        })
    st.dataframe(rows, use_container_width=True)

    for checkpoint, item in checkpoint_items.items():
        with st.expander(f"Checkpoint {checkpoint} - {item.get('evidence_status')}"):
            st.json({
                "main_report": item.get("main_report"),
                "validate_report": item.get("validate_report"),
                "audit_report": item.get("audit_report"),
                "closure_report": item.get("closure_report"),
            })
            files = item.get("files", [])
            if files:
                st.dataframe(files, use_container_width=True)

st.subheader("Superficies")
st.json(gate.get("surfaces", {}))

st.subheader("Garantias de nao execucao")
st.json(gate.get("execution_guard", {}))

st.subheader("Operacoes bloqueadas")
for operation in gate.get("blocked_operations", []):
    st.write(f"- {operation}")

st.subheader("Closure report")
if isinstance(closure, dict):
    st.json(closure)
else:
    st.info("Closure report ainda nao carregado.")

st.subheader("Relatorio Markdown")
markdown_content = read_text(GATE_MD_PATH)
if markdown_content:
    st.markdown(markdown_content)
else:
    st.info("Arquivo markdown do gate nao encontrado.")