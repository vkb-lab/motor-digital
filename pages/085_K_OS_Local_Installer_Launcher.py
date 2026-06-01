# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from pathlib import Path

import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports" / "system" / "085_local_installer_launcher"
MANIFEST_PATH = REPORT_DIR / "085_local_installer_launcher_manifest.json"
CLOSURE_PATH = REPORT_DIR / "085_closure_report.json"
MANIFEST_MD_PATH = REPORT_DIR / "085_local_installer_launcher_manifest.md"


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
    page_title="085 - K-OS Local Installer Launcher",
    layout="wide",
)

st.title("085 - K-OS Local Installer / Launcher Core")
st.caption("Pagina somente leitura. Scripts gerados sem executar installer real, sem instalar dependencias e sem modificar sistema.")

manifest = read_json(MANIFEST_PATH)
closure = read_json(CLOSURE_PATH)

if not isinstance(manifest, dict):
    st.warning("Manifesto do launcher ainda nao encontrado. Execute o checkpoint 085.")
    st.stop()

warnings = manifest.get("warnings", [])

col1, col2, col3, col4 = st.columns(4)
col1.metric("Checkpoint", manifest.get("checkpoint", "085"))
col2.metric("Camada", manifest.get("layer", "K-OS Core"))
col3.metric("Status", manifest.get("status", "unknown"))
col4.metric("Warnings", len(warnings))

st.subheader("Decisao operacional")
st.json(manifest.get("operational_decision", {}))

st.subheader("Comandos manuais")
commands = manifest.get("operator_commands", {})
st.code(commands.get("check_only", ""), language="powershell")
st.code(commands.get("launch_cockpit", ""), language="powershell")

st.subheader("Entrypoint")
st.json(manifest.get("entrypoint", {}))

st.subheader("Runtime")
st.json(manifest.get("runtime", {}))

st.subheader("Gate anterior")
st.json(manifest.get("previous_release_candidate_gate", {}))

st.subheader("Scripts do launcher")
scripts = manifest.get("launcher_scripts", [])
if scripts:
    st.dataframe(scripts, use_container_width=True)
else:
    st.info("Nenhum script listado.")

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