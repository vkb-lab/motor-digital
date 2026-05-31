from __future__ import annotations

import json
import subprocess
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT_ROOT / "ops" / "k_os_external_api_sandbox.py"
REPORT_PATH = PROJECT_ROOT / "reports" / "external_sandbox" / "latest_external_api_sandbox_report.json"
POLICY_PATH = PROJECT_ROOT / "config" / "external_sandbox" / "k_os_external_api_sandbox_policy.json"

st.set_page_config(page_title="K-OS External API Sandbox", layout="wide")

st.title("K-OS External API Sandbox")
st.caption("Checkpoint 022 - simulação segura de APIs externas sem chamada real.")

st.warning(
    "Nenhuma chamada externa é feita. Este painel só monta payload, classifica risco, valida licença, estima custo e bloqueia execução real."
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


def run(args: list[str]) -> None:
    completed = subprocess.run(
        [python_exe(), str(SCRIPT), *args],
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


tab1, tab2, tab3 = st.tabs(["Simular", "Política", "Relatório"])

with tab1:
    provider = st.selectbox(
        "Provider",
        ["openai", "runway", "elevenlabs", "instagram", "whatsapp", "google", "luma", "sora", "comfyui"],
    )
    use_case = st.text_input("Use case", value="text_brief")
    agent = st.text_input("Agent", value="marketplace_ia_agent")
    prompt = st.text_area("Prompt", value="Simular payload seguro sem chamada externa.")
    customer_use = st.checkbox("Uso para cliente exige License Gate")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Simular payload", type="primary"):
            args = [
                "--mode", "simulate",
                "--provider", provider,
                "--use-case", use_case,
                "--prompt", prompt,
                "--agent", agent,
            ]
            if customer_use:
                args.append("--customer-use")
            run(args)

    with col2:
        if st.button("Smoke test"):
            run(["--mode", "smoke-test"])

with tab2:
    if POLICY_PATH.exists():
        st.json(json.loads(POLICY_PATH.read_text(encoding="utf-8-sig")))
    else:
        st.info("Política ainda não encontrada.")

with tab3:
    if REPORT_PATH.exists():
        report = json.loads(REPORT_PATH.read_text(encoding="utf-8-sig"))

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.metric("Status", report.get("status", "N/A"))

        with c2:
            st.metric("Chamada real", str(report.get("real_provider_call_performed", False)))

        with c3:
            st.metric("Envio externo", str(report.get("external_send_enabled", False)))

        with c4:
            st.metric("Publicação externa", str(report.get("external_publish_enabled", False)))

        st.json(report)
    else:
        st.info("Nenhum relatório ainda.")

st.caption("K-OS 022 - último escudo antes de qualquer integração externa real.")