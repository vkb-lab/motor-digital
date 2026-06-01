# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from pathlib import Path

import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports" / "system" / "080_module_registry"
REGISTRY_PATH = REPORT_DIR / "080_module_registry.json"
CLOSURE_PATH = REPORT_DIR / "080_closure_report.json"
REGISTRY_MD_PATH = REPORT_DIR / "080_module_registry.md"


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
    page_title="080 - K-OS Module Registry",
    layout="wide",
)

st.title("080 - K-OS Module Registry Core")
st.caption("Pagina somente leitura. Inventario local sem execucao de modulos, auto-fix, recovery, rollback ou shell.")

registry = read_json(REGISTRY_PATH)
closure = read_json(CLOSURE_PATH)

if not isinstance(registry, dict):
    st.warning("Registry de modulos ainda nao encontrado. Execute o checkpoint 080.")
    st.stop()

inventory = registry.get("inventory", {})

col1, col2, col3, col4 = st.columns(4)
col1.metric("Checkpoint", registry.get("checkpoint", "080"))
col2.metric("Camada", registry.get("layer", "K-OS Core"))
col3.metric("Status", registry.get("status", "unknown"))
col4.metric("Modulos", inventory.get("total_modules", 0))

st.subheader("Decisao operacional")
st.json(registry.get("operational_decision", {}))

st.subheader("Contagem por tipo")
by_type = inventory.get("by_type", {})
if by_type:
    st.dataframe(
        [{"module_type": key, "count": value} for key, value in by_type.items()],
        use_container_width=True,
    )
else:
    st.info("Nenhuma contagem por tipo encontrada.")

st.subheader("Contagem por raiz")
by_root = inventory.get("by_root", {})
if by_root:
    st.dataframe(
        [{"root": key, "count": value} for key, value in by_root.items()],
        use_container_width=True,
    )

st.subheader("Raizes monitoradas")
root_status = inventory.get("root_status", [])
if root_status:
    st.dataframe(root_status, use_container_width=True)

st.subheader("Tipos criticos ausentes")
missing = registry.get("missing_critical_module_types", [])
if missing:
    for item in missing:
        st.write(f"- {item}")
else:
    st.success("Nenhum tipo critico ausente.")

st.subheader("Modulos registrados")
modules = inventory.get("modules", [])
if modules:
    selected_type = st.selectbox(
        "Filtrar por tipo",
        ["todos"] + sorted(set(item.get("module_type", "unknown") for item in modules)),
    )

    filtered = modules
    if selected_type != "todos":
        filtered = [item for item in modules if item.get("module_type") == selected_type]

    st.dataframe(filtered, use_container_width=True)
else:
    st.info("Nenhum modulo registrado.")

st.subheader("Garantias de nao execucao")
st.json(registry.get("execution_guard", {}))

st.subheader("Operacoes bloqueadas")
for operation in registry.get("blocked_operations", []):
    st.write(f"- {operation}")

st.subheader("Closure report")
if isinstance(closure, dict):
    st.json(closure)
else:
    st.info("Closure report ainda nao carregado.")

st.subheader("Registry Markdown")
markdown_content = read_text(REGISTRY_MD_PATH)
if markdown_content:
    st.markdown(markdown_content)
else:
    st.info("Arquivo markdown do registry nao encontrado.")