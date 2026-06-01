# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from pathlib import Path

import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports" / "system" / "082_command_registry"
REGISTRY_PATH = REPORT_DIR / "082_command_registry.json"
CLOSURE_PATH = REPORT_DIR / "082_closure_report.json"
REGISTRY_MD_PATH = REPORT_DIR / "082_command_registry.md"


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
    page_title="082 - K-OS Command Registry",
    layout="wide",
)

st.title("082 - K-OS Command Registry Core")
st.caption("Pagina somente leitura. Catalogo de comandos sem execucao, auto-fix, recovery, rollback, drill ou shell.")

registry = read_json(REGISTRY_PATH)
closure = read_json(CLOSURE_PATH)

if not isinstance(registry, dict):
    st.warning("Registry de comandos ainda nao encontrado. Execute o checkpoint 082.")
    st.stop()

inventory = registry.get("inventory", {})

col1, col2, col3, col4 = st.columns(4)
col1.metric("Checkpoint", registry.get("checkpoint", "082"))
col2.metric("Camada", registry.get("layer", "K-OS Core"))
col3.metric("Status", registry.get("status", "unknown"))
col4.metric("Comandos", inventory.get("total_command_surfaces", 0))

st.subheader("Decisao operacional")
st.json(registry.get("operational_decision", {}))

st.subheader("Contagem por familia")
by_family = inventory.get("by_family", {})
if by_family:
    st.dataframe(
        [{"family": key, "count": value} for key, value in by_family.items()],
        use_container_width=True,
    )
else:
    st.info("Nenhuma familia encontrada.")

st.subheader("Contagem por risco")
by_risk = inventory.get("by_risk", {})
if by_risk:
    st.dataframe(
        [{"risk_level": key, "count": value} for key, value in by_risk.items()],
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

st.subheader("Familias obrigatorias ausentes")
missing = registry.get("missing_required_families", [])
if missing:
    for item in missing:
        st.write(f"- {item}")
else:
    st.success("Nenhuma familia obrigatoria ausente.")

st.subheader("Revisao de operador")
review = inventory.get("operator_review_required", [])
if review:
    st.dataframe(review, use_container_width=True)
else:
    st.success("Nenhum item exigindo revisao de operador.")

st.subheader("Referencias bloqueadas")
blocked = inventory.get("blocked_references", [])
if blocked:
    st.dataframe(blocked, use_container_width=True)
else:
    st.success("Nenhuma referencia bloqueada detectada.")

st.subheader("Comandos registrados")
commands = inventory.get("commands", [])
if commands:
    selected_family = st.selectbox(
        "Filtrar por familia",
        ["todas"] + sorted(set(item.get("command_family", "unknown") for item in commands)),
    )

    selected_risk = st.selectbox(
        "Filtrar por risco",
        ["todos"] + sorted(set(item.get("risk_level", "unknown") for item in commands)),
    )

    filtered = commands
    if selected_family != "todas":
        filtered = [item for item in filtered if item.get("command_family") == selected_family]
    if selected_risk != "todos":
        filtered = [item for item in filtered if item.get("risk_level") == selected_risk]

    st.dataframe(filtered, use_container_width=True)
else:
    st.info("Nenhuma superficie de comando registrada.")

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