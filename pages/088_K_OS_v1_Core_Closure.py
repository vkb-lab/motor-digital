# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from pathlib import Path

import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports" / "system" / "088_v1_core_closure"
MANIFEST_PATH = REPORT_DIR / "088_v1_core_closure_manifest.json"
FINAL_STATUS_PATH = REPORT_DIR / "088_k_os_v1_final_status.json"
CLOSURE_PATH = REPORT_DIR / "088_closure_report.json"
MANIFEST_MD_PATH = REPORT_DIR / "088_v1_core_closure_manifest.md"


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
    page_title="088 - K-OS v1 Core Closure",
    layout="wide",
)

st.title("088 - K-OS v1 Core Closure")
st.caption("Pagina somente leitura. Fechamento oficial sem deploy, installer, release publish, recovery, rollback, git tag ou auto-fix.")

manifest = read_json(MANIFEST_PATH)
final_status = read_json(FINAL_STATUS_PATH)
closure = read_json(CLOSURE_PATH)

if not isinstance(manifest, dict):
    st.warning("Manifesto de fechamento v1 ainda nao encontrado. Execute o checkpoint 088.")
    st.stop()

warnings = manifest.get("warnings", [])
checkpoint_closure = manifest.get("checkpoint_closure", {})
final_surfaces = manifest.get("final_surfaces", {})

col1, col2, col3, col4 = st.columns(4)
col1.metric("Checkpoint", manifest.get("checkpoint", "088"))
col2.metric("Camada", manifest.get("layer", "K-OS Core"))
col3.metric("Status v1", manifest.get("status", "unknown"))
col4.metric("Warnings", len(warnings))

st.subheader("Decisao de fechamento")
st.json(manifest.get("closure_decision", {}))

st.subheader("Dominios de fechamento")
domains = manifest.get("closure_domains", [])
if domains:
    st.dataframe(domains, use_container_width=True)

st.subheader("Checkpoints consolidados")
checkpoints = checkpoint_closure.get("checkpoints", {})
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

st.subheader("Superficies finais")
if final_surfaces:
    st.json(final_surfaces)

st.subheader("Continuidade")
st.json(manifest.get("continuity", {}))

st.subheader("Status final")
if isinstance(final_status, dict):
    st.json(final_status)
else:
    st.info("Status final ainda nao carregado.")

st.subheader("Warnings")
if warnings:
    for item in warnings:
        st.write(f"- {item}")
else:
    st.success("Nenhum warning registrado.")

st.subheader("Garantias de nao execucao")
st.json(manifest.get("execution_guard", {}))

st.subheader("Operacoes bloqueadas")
for operation in manifest.get("blocked_operations", []):
    st.write(f"- {operation}")

st.subheader("Closure report")
if isinstance(closure, dict):
    st.json(closure)
else:
    st.info("Closure report ainda nao carregado.")

st.subheader("Relatorio Markdown")
markdown_content = read_text(MANIFEST_MD_PATH)
if markdown_content:
    st.markdown(markdown_content)
else:
    st.info("Arquivo markdown do manifesto nao encontrado.")