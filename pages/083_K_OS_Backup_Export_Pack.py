# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from pathlib import Path

import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports" / "system" / "083_backup_export_pack"
MANIFEST_PATH = REPORT_DIR / "083_backup_export_manifest.json"
INDEX_PATH = REPORT_DIR / "083_export_pack_index.json"
CLOSURE_PATH = REPORT_DIR / "083_closure_report.json"
PACK_MD_PATH = REPORT_DIR / "083_backup_export_pack.md"


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
    page_title="083 - K-OS Backup Export Pack",
    layout="wide",
)

st.title("083 - K-OS Backup and Export Pack Core")
st.caption("Pagina somente leitura. Manifesto seguro sem copiar conteudo, sem compactar arquivos e sem exportar segredos.")

manifest = read_json(MANIFEST_PATH)
index = read_json(INDEX_PATH)
closure = read_json(CLOSURE_PATH)

if not isinstance(manifest, dict):
    st.warning("Manifesto de backup/export ainda nao encontrado. Execute o checkpoint 083.")
    st.stop()

inventory = manifest.get("inventory", {})

col1, col2, col3, col4 = st.columns(4)
col1.metric("Checkpoint", manifest.get("checkpoint", "083"))
col2.metric("Camada", manifest.get("layer", "K-OS Core"))
col3.metric("Status", manifest.get("status", "unknown"))
col4.metric("Arquivos no manifesto", inventory.get("total_included_files", 0))

st.subheader("Decisao operacional")
st.json(manifest.get("operational_decision", {}))

st.subheader("Politica de export")
st.json(manifest.get("export_policy", {}))

st.subheader("Resumo")
st.json({
    "manifest_only": inventory.get("manifest_only"),
    "files_copied": inventory.get("files_copied"),
    "archive_created": inventory.get("archive_created"),
    "total_included_files": inventory.get("total_included_files"),
    "total_excluded_files": inventory.get("total_excluded_files"),
    "sensitive_reference_count": inventory.get("sensitive_reference_count"),
})

st.subheader("Contagem por escopo")
by_scope = inventory.get("by_scope", {})
if by_scope:
    st.dataframe(
        [{"scope": key, "count": value} for key, value in by_scope.items()],
        use_container_width=True,
    )

st.subheader("Contagem por extensao")
by_suffix = inventory.get("by_suffix", {})
if by_suffix:
    st.dataframe(
        [{"suffix": key, "count": value} for key, value in by_suffix.items()],
        use_container_width=True,
    )

st.subheader("Raizes avaliadas")
root_status = inventory.get("root_status", [])
if root_status:
    st.dataframe(root_status, use_container_width=True)

st.subheader("Escopos obrigatorios ausentes")
missing = manifest.get("missing_required_scopes", [])
if missing:
    for item in missing:
        st.write(f"- {item}")
else:
    st.success("Nenhum escopo obrigatorio ausente.")

st.subheader("Arquivos manifestados")
included = inventory.get("included_files", [])
if included:
    selected_scope = st.selectbox(
        "Filtrar por escopo",
        ["todos"] + sorted(set(item.get("scope", "unknown") for item in included)),
    )

    filtered = included
    if selected_scope != "todos":
        filtered = [item for item in included if item.get("scope") == selected_scope]

    st.dataframe(filtered, use_container_width=True)
else:
    st.info("Nenhum arquivo manifestado.")

st.subheader("Arquivos excluidos")
excluded = inventory.get("excluded_files", [])
if excluded:
    st.dataframe(excluded, use_container_width=True)
else:
    st.success("Nenhum arquivo excluido listado.")

st.subheader("Garantias de nao exportacao sensivel")
st.json(manifest.get("execution_guard", {}))

st.subheader("Indice do export pack")
if isinstance(index, dict):
    st.json(index)
else:
    st.info("Indice ainda nao carregado.")

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
    st.info("Arquivo markdown do pack nao encontrado.")