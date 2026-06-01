# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from pathlib import Path

import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports" / "system" / "087_final_audit_pack"
PACK_PATH = REPORT_DIR / "087_final_audit_pack.json"
CLOSURE_PATH = REPORT_DIR / "087_closure_report.json"
PACK_MD_PATH = REPORT_DIR / "087_final_audit_pack.md"


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
    page_title="087 - K-OS Final Audit Pack",
    layout="wide",
)

st.title("087 - K-OS Final Audit Pack Core")
st.caption("Pagina somente leitura. Auditoria final sem deploy, installer, release publish, recovery, rollback ou auto-fix.")

pack = read_json(PACK_PATH)
closure = read_json(CLOSURE_PATH)

if not isinstance(pack, dict):
    st.warning("Pacote final de auditoria ainda nao encontrado. Execute o checkpoint 087.")
    st.stop()

warnings = pack.get("warnings", [])
checkpoint_audit = pack.get("checkpoint_audit", {})
surface_audit = pack.get("surface_audit", {})

col1, col2, col3, col4 = st.columns(4)
col1.metric("Checkpoint", pack.get("checkpoint", "087"))
col2.metric("Camada", pack.get("layer", "K-OS Core"))
col3.metric("Status", pack.get("status", "unknown"))
col4.metric("Warnings", len(warnings))

st.subheader("Decisao de auditoria")
st.json(pack.get("audit_decision", {}))

st.subheader("Resultado por dominio")
domain_results = pack.get("domain_results", [])
if domain_results:
    st.dataframe(domain_results, use_container_width=True)

st.subheader("Auditoria por checkpoint")
checkpoints = checkpoint_audit.get("checkpoints", {})
if checkpoints:
    rows = []
    for checkpoint, item in checkpoints.items():
        rows.append({
            "checkpoint": checkpoint,
            "name": item.get("name"),
            "status": item.get("status"),
            "validate": item.get("validate_status"),
            "audit": item.get("audit_status"),
            "closure": item.get("closure_status"),
            "guard_safe": item.get("execution_guard_safe"),
            "evidence_file_count": item.get("evidence_file_count"),
            "issues": ", ".join(item.get("issues", [])),
        })
    st.dataframe(rows, use_container_width=True)

    for checkpoint, item in checkpoints.items():
        with st.expander(f"Checkpoint {checkpoint} - {item.get('status')}"):
            st.json({
                "main_report": item.get("main_report"),
                "validate_report": item.get("validate_report"),
                "audit_report": item.get("audit_report"),
                "closure_report": item.get("closure_report"),
                "commercial_doc": item.get("commercial_doc"),
                "issues": item.get("issues"),
            })
            files = item.get("files", [])
            if files:
                st.dataframe(files, use_container_width=True)

st.subheader("Superficies finais")
if surface_audit:
    st.json(surface_audit)

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