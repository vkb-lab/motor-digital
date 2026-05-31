from __future__ import annotations

import json
import subprocess
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT_ROOT / "ops" / "k_os_mission_control_2.py"
REPORT_PATH = PROJECT_ROOT / "reports" / "mission_control" / "latest_mission_control_status.json"
MD_PATH = PROJECT_ROOT / "reports" / "mission_control" / "latest_mission_control_status.md"

st.set_page_config(page_title="K-OS Mission Control 2.0", layout="wide")

st.title("K-OS Mission Control 2.0")
st.caption("Checkpoint 020 - sala de controle da nave K-OS.")

st.warning(
    "Nenhuma ação externa é executada por este painel. "
    "Ele consolida status, risco, checkpoints, gates e próximos passos."
)


def python_exe() -> str:
    candidates = [
        PROJECT_ROOT / "venv" / "Scripts" / "python.exe",
        PROJECT_ROOT / ".venv" / "Scripts" / "python.exe",
    ]
    for item in candidates:
        if item.exists():
            return str(item)
    return "python"


def generate_status() -> None:
    completed = subprocess.run(
        [python_exe(), str(SCRIPT), "--mode", "generate"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    st.code(" ".join(completed.args), language="powershell")

    if completed.stdout:
        st.code(completed.stdout, language="json")

    if completed.stderr:
        st.code(completed.stderr, language="text")

    if completed.returncode == 0:
        st.success("Status atualizado.")
    else:
        st.error(f"Falhou: {completed.returncode}")


if st.button("Atualizar Mission Control", type="primary"):
    generate_status()

st.divider()

if REPORT_PATH.exists():
    status = json.loads(REPORT_PATH.read_text(encoding="utf-8-sig"))

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.metric("Status", status.get("status", "N/A"))

    with c2:
        st.metric("Readiness", str(status.get("readiness_score", 0)) + "%")

    with c3:
        st.metric("Checkpoints", f"{status.get('checkpoint_ok')}/{status.get('checkpoint_total')}")

    with c4:
        st.metric("Git clean", str(status.get("git", {}).get("clean")))

    with c5:
        st.metric("Blockers", len(status.get("blockers", [])))

    st.header("Checkpoints")

    for item in status.get("checkpoints", []):
        label = f"{item.get('id')} - {item.get('name')}"
        with st.expander(label, expanded=False):
            st.json(item)

    st.header("Security / Schema / Governance / Vault / Audit")

    tabs = st.tabs(["Security", "Schema", "Governance", "Vault", "Audit", "Git", "Blockers"])

    with tabs[0]:
        st.json(status.get("security", {}))

    with tabs[1]:
        st.json(status.get("schema", {}))

    with tabs[2]:
        st.json(status.get("governance", {}))

    with tabs[3]:
        st.json(status.get("vault", {}))

    with tabs[4]:
        st.json(status.get("audit", {}))

    with tabs[5]:
        st.json(status.get("git", {}))

    with tabs[6]:
        if status.get("blockers"):
            st.error("Existem blockers operacionais.")
            st.json(status.get("blockers", []))
        else:
            st.success("Nenhum blocker operacional encontrado.")

    st.divider()
    st.header("Próximo passo recomendado")
    st.success(status.get("recommended_next_step", "N/A"))

else:
    st.info("Nenhum status encontrado. Clique em Atualizar Mission Control.")

st.divider()

if MD_PATH.exists():
    st.header("Relatório Markdown")
    st.code(MD_PATH.read_text(encoding="utf-8-sig"), language="markdown")

st.caption("K-OS 020 - comando central antes de risco, sandbox externo e escala enterprise.")