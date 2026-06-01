# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from pathlib import Path

import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports" / "system" / "081_agent_capability_registry"
REGISTRY_PATH = REPORT_DIR / "081_agent_capability_registry.json"
CLOSURE_PATH = REPORT_DIR / "081_closure_report.json"
REGISTRY_MD_PATH = REPORT_DIR / "081_agent_capability_registry.md"


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
    page_title="081 - K-OS Agent Capability Registry",
    layout="wide",
)

st.title("081 - K-OS Agent Capability Registry Core")
st.caption("Pagina somente leitura. Inventario de capacidades sem execucao de agentes, comandos, modulos ou auto-fix.")

registry = read_json(REGISTRY_PATH)
closure = read_json(CLOSURE_PATH)

if not isinstance(registry, dict):
    st.warning("Registry de capacidades ainda nao encontrado. Execute o checkpoint 081.")
    st.stop()

inventory = registry.get("inventory", {})

col1, col2, col3, col4 = st.columns(4)
col1.metric("Checkpoint", registry.get("checkpoint", "081"))
col2.metric("Camada", registry.get("layer", "K-OS Core"))
col3.metric("Status", registry.get("status", "unknown"))
col4.metric("Superficies", inventory.get("total_agent_surfaces", 0))

st.subheader("Decisao operacional")
st.json(registry.get("operational_decision", {}))

st.subheader("Contagem por capacidade")
by_capability = inventory.get("by_capability", {})
if by_capability:
    st.dataframe(
        [{"capability": key, "count": value} for key, value in by_capability.items()],
        use_container_width=True,
    )
else:
    st.info("Nenhuma capacidade encontrada.")

st.subheader("Contagem por tipo de superficie")
by_kind = inventory.get("by_kind", {})
if by_kind:
    st.dataframe(
        [{"agent_kind": key, "count": value} for key, value in by_kind.items()],
        use_container_width=True,
    )

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

st.subheader("Capacidades obrigatorias ausentes")
missing = registry.get("missing_required_capabilities", [])
if missing:
    for item in missing:
        st.write(f"- {item}")
else:
    st.success("Nenhuma capacidade obrigatoria ausente.")

st.subheader("Matriz capacidade-agente")
matrix = inventory.get("capability_matrix", [])
if matrix:
    st.dataframe(
        [{"capability": item.get("capability"), "agent_count": item.get("agent_count")} for item in matrix],
        use_container_width=True,
    )

st.subheader("Superficies registradas")
agents = inventory.get("agents", [])
if agents:
    selected_capability = st.selectbox(
        "Filtrar por capacidade",
        ["todas"] + sorted(set(cap for item in agents for cap in item.get("capabilities", []))),
    )

    filtered = agents
    if selected_capability != "todas":
        filtered = [item for item in agents if selected_capability in item.get("capabilities", [])]

    st.dataframe(filtered, use_container_width=True)
else:
    st.info("Nenhuma superficie de agente registrada.")

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