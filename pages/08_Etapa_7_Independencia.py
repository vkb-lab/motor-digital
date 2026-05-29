from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import streamlit as st


ROADMAP_PATH = Path("memory/roadmap/stage_7_independence.json")
VALIDATION_PATH = Path("reports/stage_7_render_validation.json")


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


st.set_page_config(
    page_title="Etapa 7 - Independencia",
    layout="wide",
)

st.title("Etapa 7/9 - Setembro: Independencia")
st.caption("K-Atlas OS online, governado e preparado para autonomia progressiva.")

roadmap = load_json(ROADMAP_PATH)
validation = load_json(VALIDATION_PATH)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Render", "Online")
    st.write("https://k-atlas-os.onrender.com")

with col2:
    st.metric("Auto Publish", "Bloqueado")

with col3:
    st.metric("APIs Externas", "Bloqueadas por padrao")

st.divider()

st.subheader("Checkpoint atual")

st.write({
    "stage": roadmap.get("stage", "7/9"),
    "name": roadmap.get("name", "independencia"),
    "checkpoint": roadmap.get("checkpoint", "Credential Vault + Test Page API Adapter"),
    "status": roadmap.get("status", "started"),
})

st.subheader("Governanca")

governance = roadmap.get("governance", {
    "auto_publish": False,
    "external_api_enabled_by_default": False,
    "official_publish_allowed": False,
    "mass_messaging_allowed": False,
    "browser_automation_allowed": False,
    "human_review_required": True,
    "credential_vault_required": True,
})

st.json(governance)

st.subheader("Proximos passos")

next_steps = roadmap.get("next", [
    "validar vault local",
    "configurar secrets no Render sem expor token",
    "criar test page endpoint controlado",
    "integrar creative media gateway",
    "liberar somente sandbox com logs",
])

for step in next_steps:
    st.checkbox(step, value=False)

st.divider()

st.subheader("Validacao Render")

if validation:
    st.success("Validacao Render registrada.")
    st.json(validation)
else:
    st.info("Validacao Render ainda nao registrada em reports/stage_7_render_validation.json.")

st.warning(
    "Publicacao real continua bloqueada. Esta etapa prepara independencia com seguranca, nao auto publish irrestrito."
)