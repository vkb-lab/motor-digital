# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from pathlib import Path

import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports" / "resilience" / "078_resilience_layer_closure"
MANIFEST_PATH = REPORT_DIR / "078_layer_closure_manifest.json"
CLOSURE_PATH = REPORT_DIR / "078_closure_report.json"
MANIFEST_MD_PATH = REPORT_DIR / "078_layer_closure_manifest.md"


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
    page_title="078 - Resilience Layer Closure",
    layout="wide",
)

st.title("078 - K-Agent Resilience Layer Closure Core")
st.caption("Pagina somente leitura. Nao executa drill, recovery, rollback ou shell.")

manifest = read_json(MANIFEST_PATH)
closure = read_json(CLOSURE_PATH)

if not isinstance(manifest, dict):
    st.warning("Manifesto de fechamento ainda nao encontrado. Execute o checkpoint 078.")
    st.stop()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Checkpoint", manifest.get("checkpoint", "078"))
col2.metric("Camada", manifest.get("layer", "Resilience"))
col3.metric("Status", manifest.get("status", "unknown"))
col4.metric("Evidencias", manifest.get("evidence", {}).get("total_evidence_files", 0))

st.subheader("Fechamento oficial")
st.json({
    "official_layer_closure": manifest.get("official_layer_closure"),
    "next_checkpoint": manifest.get("layer_transition", {}).get("next_checkpoint"),
    "transition_allowed": manifest.get("layer_transition", {}).get("transition_allowed"),
})

st.subheader("Checkpoints consolidados")
controls = manifest.get("controls", [])
if controls:
    st.dataframe(controls, use_container_width=True)
else:
    st.info("Nenhum checkpoint consolidado encontrado.")

st.subheader("Garantias de nao execucao")
st.json(manifest.get("execution_guard", {}))

st.subheader("Operacoes bloqueadas")
for operation in manifest.get("blocked_operations", []):
    st.write(f"- {operation}")

st.subheader("Evidencias por checkpoint")
evidence = manifest.get("evidence", {}).get("checkpoints", {})
for checkpoint, item in evidence.items():
    with st.expander(f"Checkpoint {checkpoint} - {item.get('status')}"):
        st.write(f"Arquivos encontrados: {item.get('evidence_count', 0)}")
        files = item.get("files", [])
        if files:
            st.dataframe(files, use_container_width=True)
        else:
            st.info("Nenhuma evidencia local localizada para este checkpoint.")

st.subheader("Closure report")
if isinstance(closure, dict):
    st.json(closure)
else:
    st.info("Closure report ainda nao carregado.")

st.subheader("Manifesto Markdown")
markdown_content = read_text(MANIFEST_MD_PATH)
if markdown_content:
    st.markdown(markdown_content)
else:
    st.info("Arquivo markdown do manifesto nao encontrado.")