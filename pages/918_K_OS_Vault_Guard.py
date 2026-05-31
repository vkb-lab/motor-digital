from __future__ import annotations

import json
import subprocess
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT_ROOT / "ops" / "k_os_vault_guard.ps1"
REPORT_PATH = PROJECT_ROOT / "reports" / "vault" / "latest_vault_guard_report.json"
POLICY_PATH = PROJECT_ROOT / "config" / "security" / "k_os_vault_policy.json"

st.set_page_config(page_title="K-OS Vault Guard", layout="wide")

st.title("K-OS Vault Guard")
st.caption("Checkpoint 018 - cofre local de chaves com DPAPI, auditoria e acesso controlado.")

st.warning(
    "Nenhum valor bruto de chave é exibido nesta tela. "
    "O cofre é local, ignorado pelo Git e protegido por approval gate."
)


def run_action(action: str) -> None:
    completed = subprocess.run(
        [
            "powershell",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(SCRIPT),
            "-Action",
            action,
        ],
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
        st.success("OK")
    else:
        st.error(f"Falhou: {completed.returncode}")


col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Inicializar cofre"):
        run_action("Init")

with col2:
    if st.button("Auditar cofre"):
        run_action("Audit")

with col3:
    if st.button("Smoke test"):
        run_action("SmokeTest")

st.divider()

st.header("Política")

if POLICY_PATH.exists():
    st.json(json.loads(POLICY_PATH.read_text(encoding="utf-8-sig")))
else:
    st.info("Política ainda não encontrada.")

st.divider()

st.header("Último relatório")

if REPORT_PATH.exists():
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8-sig"))

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("Status", report.get("status", "N/A"))

    with c2:
        st.metric("Itens", report.get("item_count", 0))

    with c3:
        st.metric("Raw exposto", str(report.get("raw_values_exposed", False)))

    with c4:
        st.metric("API externa", str(report.get("external_api_enabled", False)))

    st.json(report)
else:
    st.info("Nenhum relatório encontrado ainda.")

st.divider()

st.header("Adicionar chave no cofre")

st.code(
    'powershell -ExecutionPolicy Bypass -File ".\\ops\\k_os_vault_guard.ps1" -Action SetItem -Provider "openai" -Name "primary"',
    language="powershell",
)

st.caption("K-OS 018 - credenciais reais ficam somente em local_secrets/, fora do GitHub.")