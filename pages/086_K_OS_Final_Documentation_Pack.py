# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from pathlib import Path

import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports" / "system" / "086_final_documentation_pack"
PACK_PATH = REPORT_DIR / "086_final_documentation_pack.json"
CLOSURE_PATH = REPORT_DIR / "086_closure_report.json"
PACK_MD_PATH = REPORT_DIR / "086_final_documentation_pack.md"


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
    page_title="086 - K-OS Final Documentation Pack",
    layout="wide",
)

st.title("086 - K-OS Final Documentation Pack Core")
st.caption("Pagina somente leitura. Pacote final de documentacao sem deploy, installer, release publish, rollback ou auto-fix.")

pack = read_json(PACK_PATH)
closure = read_json(CLOSURE_PATH)

if not isinstance(pack, dict):
    st.warning("Pacote final de documentacao ainda nao encontrado. Execute o checkpoint 086.")
    st.stop()

warnings = pack.get("warnings", [])
docs = pack.get("documentation_outputs", [])

col1, col2, col3, col4 = st.columns(4)
col1.metric("Checkpoint", pack.get("checkpoint", "086"))
col2.metric("Camada", pack.get("layer", "K-OS Core"))
col3.metric("Status", pack.get("status", "unknown"))
col4.metric("Documentos", len(docs))

st.subheader("Decisao operacional")
st.json(pack.get("operational_decision", {}))

st.subheader("Documentos gerados")
if docs:
    st.dataframe(docs, use_container_width=True)
else:
    st.info("Nenhum documento listado.")

st.subheader("Checkpoints documentados")
evidence = pack.get("evidence", {}).get("checkpoints", {})
if evidence:
    rows = []
    for checkpoint, item in evidence.items():
        rows.append({
            "checkpoint": checkpoint,
            "name": item.get("name"),
            "status": item.get("status"),
            "main_report_exists": item.get("main_report", {}).get("exists"),
            "closure_exists": item.get("closure_report", {}).get("exists"),
            "commercial_doc_exists": item.get("commercial_doc", {}).get("exists"),
            "evidence_file_count": item.get("evidence_file_count"),
        })
    st.dataframe(rows, use_container_width=True)

st.subheader("Superficie do projeto")
st.json(pack.get("project_surface", {}))

st.subheader("Warnings")
if warnings:
    for item in warnings:
        st.write(f"- {item}")
else:
    st.success("Nenhum warning registrado.")

st.subheader("Garantias de nao execucao")
st.json(pack.get("execution_guard", {}))

st.subheader("Operacoes bloqueadas")
for operation in pack.get("blocked_operations", []):
    st.write(f"- {operation}")

st.subheader("Closure report")
if isinstance(closure, dict):
    st.json(closure)
else:
    st.info("Closure report ainda nao carregado.")

st.subheader("Relatorio Markdown")
markdown_content = read_text(PACK_MD_PATH)
if markdown_content:
    st.markdown(markdown_content)
else:
    st.info("Arquivo markdown do pacote nao encontrado.")