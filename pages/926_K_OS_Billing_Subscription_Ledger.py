from __future__ import annotations

import json
import subprocess
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT_ROOT / "ops" / "k_os_billing_subscription_ledger.py"
REPORT_PATH = PROJECT_ROOT / "reports" / "billing" / "latest_billing_subscription_report.json"
RECONCILE_PATH = PROJECT_ROOT / "reports" / "billing" / "latest_billing_reconciliation_dry_run.json"
POLICY_PATH = PROJECT_ROOT / "config" / "billing" / "k_os_billing_subscription_policy.json"

st.set_page_config(page_title="K-OS Billing Subscription Ledger", layout="wide")

st.title("K-OS Billing and Subscription Ledger")
st.caption("Checkpoint 026 - clientes, planos, assinaturas, status de pagamento e vinculo com License Gate.")

st.warning(
    "Este modulo nao cobra dinheiro, nao gera nota fiscal e nao chama processador externo. "
    "Ele e um ledger operacional local com status manual e auditoria."
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


tab1, tab2, tab3, tab4 = st.tabs(["Ledger", "Reconciliation", "Status manual", "Policy"])

with tab1:
    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("Inicializar ledger", type="primary"):
            run(["--mode", "init"])

    with c2:
        if st.button("Criar demo local"):
            run(["--mode", "create-demo"])

    with c3:
        if st.button("Auditar ledger"):
            run(["--mode", "audit"])

    if REPORT_PATH.exists():
        report = json.loads(REPORT_PATH.read_text(encoding="utf-8-sig"))
        metrics = report.get("metrics", {})

        m1, m2, m3, m4, m5 = st.columns(5)

        with m1:
            st.metric("Assinaturas", metrics.get("subscription_count", 0))

        with m2:
            st.metric("Ativas", metrics.get("active_count", 0))

        with m3:
            st.metric("Trials", metrics.get("trial_count", 0))

        with m4:
            st.metric("MRR BRL", metrics.get("mrr_estimate_brl", 0))

        with m5:
            st.metric("ARR BRL", metrics.get("arr_estimate_brl", 0))

        st.subheader("Assinaturas")
        st.dataframe(report.get("subscriptions", []), use_container_width=True)

        st.subheader("Clientes")
        st.dataframe(report.get("customers", []), use_container_width=True)

        st.subheader("Gates antes de ativacao paga")
        for gate in report.get("required_gates_before_paid_activation", []):
            st.write("- " + gate)

with tab2:
    if st.button("Rodar reconciliation dry-run", type="primary"):
        run(["--mode", "reconcile-dry-run"])

    if RECONCILE_PATH.exists():
        st.json(json.loads(RECONCILE_PATH.read_text(encoding="utf-8-sig")))
    else:
        st.info("Nenhuma reconciliacao dry-run encontrada.")

with tab3:
    subscription_id = st.text_input("Subscription ID")
    status = st.selectbox(
        "Novo status",
        [
            "draft",
            "trial",
            "active",
            "past_due",
            "suspended",
            "cancelled",
            "expired",
            "pending_legal_review",
            "pending_payment_confirmation"
        ]
    )
    reason = st.text_input("Motivo", value="manual_update_by_operator")

    if st.button("Atualizar status manual", type="primary"):
        run([
            "--mode", "set-status",
            "--subscription-id", subscription_id,
            "--status", status,
            "--reason", reason
        ])

with tab4:
    if POLICY_PATH.exists():
        st.json(json.loads(POLICY_PATH.read_text(encoding="utf-8-sig")))
    else:
        st.info("Policy ainda nao encontrada.")