from __future__ import annotations

import subprocess
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT_ROOT / "ops" / "k_os_github_admin_api_bridge.ps1"

st.set_page_config(page_title="K-OS GitHub Admin API Bridge", layout="wide")

st.title("K-OS GitHub Admin API Bridge")
st.caption("Acesso operacional do K-OS ao GitHub: repo, Pages e publicação controlada.")

st.warning(
    "Este módulo usa GitHub CLI autenticado localmente. "
    "Nenhum token é salvo no código. Mudança para público exige confirmação explícita."
)

def run_action(action: str, confirm_public: bool = False):
    cmd = [
        "powershell",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(SCRIPT),
        "-Action",
        action,
    ]

    if confirm_public:
        cmd.append("-ConfirmPublic")

    completed = subprocess.run(
        cmd,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    st.code(" ".join(cmd), language="powershell")

    if completed.stdout:
        st.code(completed.stdout, language="text")

    if completed.stderr:
        st.code(completed.stderr, language="text")

    if completed.returncode == 0:
        st.success("OK")
    else:
        st.error(f"Falhou: {completed.returncode}")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Diagnosticar GitHub"):
        run_action("Doctor")

with col2:
    if st.button("Ativar Pages em main /root"):
        run_action("EnablePagesRoot")

with col3:
    if st.button("Checar Pages"):
        run_action("CheckPages")

st.divider()

st.subheader("Ação sensível")

confirm = st.checkbox("Confirmo que quero tornar o repositório público e ativar Pages")

if st.button("Tornar público + ativar Pages", type="primary"):
    run_action("MakePublicAndEnablePages", confirm_public=confirm)

st.divider()

if st.button("Abrir GitHub Settings / Actions / URL pública"):
    run_action("OpenGitHub")

st.caption("K-OS Final: GitHub como memória persistente + API administrativa controlada.")