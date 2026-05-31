from __future__ import annotations

import json
import subprocess
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT_ROOT / "ops" / "k_os_proposal_factory_quote_builder.py"
REPORT_PATH = PROJECT_ROOT / "reports" / "proposals" / "latest_proposal_factory_report.json"
APPROVAL_PATH = PROJECT_ROOT / "reports" / "proposals" / "latest_proposal_approval_dry_run.json"
POLICY_PATH = PROJECT_ROOT / "config" / "proposals" / "k_os_proposal_factory_policy.json"

st.set_page_config(page_title="K-OS Proposal Factory", layout="wide")

st.title("K-OS Proposal Factory and Quote Builder")
st.caption("Checkpoint 029 - propostas, orçamentos, approval gate e envio manual controlado.")

st.warning(
    "Propostas ficam locais. Nenhum envio externo é feito por este painel. "
    "Envio ao cliente exige aprovação humana e confirmação manual."
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


tab1, tab2, tab3, tab4, tab5 = st.tabs(["Dashboard", "Criar proposta", "Status", "Approval dry-run", "Policy"])

with tab1:
    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("Inicializar Proposal Factory", type="primary"):
            run(["--mode", "init"])

    with c2:
        if st.button("Criar proposta demo"):
            run(["--mode", "create-demo"])

    with c3:
        if st.button("Auditar propostas"):
            run(["--mode", "audit"])

    if REPORT_PATH.exists():
        report = json.loads(REPORT_PATH.read_text(encoding="utf-8-sig"))
        metrics = report.get("metrics", {})

        m1, m2, m3, m4 = st.columns(4)

        with m1:
            st.metric("Propostas", metrics.get("proposal_count", 0))

        with m2:
            st.metric("Setup BRL", metrics.get("setup_total_brl", 0))

        with m3:
            st.metric("Recorrente BRL", metrics.get("recurring_total_brl", 0))

        with m4:
            st.metric("Envio externo", str(report.get("external_send_enabled", False)))

        st.subheader("Propostas")
        st.dataframe(report.get("proposals", []), use_container_width=True)

        st.subheader("Atividades recentes")
        st.dataframe(report.get("recent_activities", []), use_container_width=True)

        st.subheader("Templates")
        st.dataframe(report.get("templates", []), use_container_width=True)

with tab2:
    deal_id = st.text_input("Deal ID")
    if st.button("Criar proposta a partir do deal", type="primary"):
        run(["--mode", "create-from-deal", "--deal-id", deal_id])

with tab3:
    proposal_id = st.text_input("Proposal ID")
    status = st.selectbox(
        "Novo status",
        [
            "draft",
            "internal_review",
            "commercial_review",
            "legal_review",
            "approved_for_manual_send",
            "sent_manually",
            "accepted",
            "rejected",
            "expired",
            "cancelled"
        ]
    )
    reason = st.text_input("Motivo", value="manual_status_update")

    if st.button("Atualizar status", type="primary"):
        run([
            "--mode", "set-status",
            "--proposal-id", proposal_id,
            "--status", status,
            "--reason", reason
        ])

with tab4:
    approval_proposal_id = st.text_input("Proposal ID para approval dry-run")

    if st.button("Rodar approval dry-run", type="primary"):
        run(["--mode", "approval-dry-run", "--proposal-id", approval_proposal_id])

    if APPROVAL_PATH.exists():
        st.json(json.loads(APPROVAL_PATH.read_text(encoding="utf-8-sig")))

with tab5:
    if POLICY_PATH.exists():
        st.json(json.loads(POLICY_PATH.read_text(encoding="utf-8-sig")))
    else:
        st.info("Policy ainda não encontrada.")