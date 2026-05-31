from __future__ import annotations

import json
import subprocess
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT_ROOT / "ops" / "k_os_customer_registry_crm_core.py"
REPORT_PATH = PROJECT_ROOT / "reports" / "crm" / "latest_customer_registry_report.json"
PIPELINE_PATH = PROJECT_ROOT / "reports" / "crm" / "latest_crm_pipeline_snapshot.json"
POLICY_PATH = PROJECT_ROOT / "config" / "crm" / "k_os_customer_registry_crm_policy.json"

st.set_page_config(page_title="K-OS Customer Registry CRM", layout="wide")

st.title("K-OS Customer Registry and CRM Core")
st.caption("Checkpoint 027 - clientes, contatos, leads, status comercial, licencas, assinaturas e historico.")

st.warning(
    "CRM local. Dados brutos ficam em local_secrets/k_os_crm e nao vao para GitHub. "
    "Envio externo e mensagens automaticas continuam bloqueados."
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


tab1, tab2, tab3, tab4, tab5 = st.tabs(["Dashboard", "Adicionar cliente", "Status", "Vinculos", "Policy"])

with tab1:
    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("Inicializar CRM", type="primary"):
            run(["--mode", "init"])

    with c2:
        if st.button("Criar demo local"):
            run(["--mode", "create-demo"])

    with c3:
        if st.button("Auditar CRM"):
            run(["--mode", "audit"])

    if REPORT_PATH.exists():
        report = json.loads(REPORT_PATH.read_text(encoding="utf-8-sig"))
        pipeline = report.get("pipeline", {})

        m1, m2, m3, m4, m5 = st.columns(5)

        with m1:
            st.metric("Clientes", pipeline.get("customer_count", 0))

        with m2:
            st.metric("Pipeline aberto", pipeline.get("open_pipeline_count", 0))

        with m3:
            st.metric("Trials", pipeline.get("trial_count", 0))

        with m4:
            st.metric("Ativos", pipeline.get("active_customer_count", 0))

        with m5:
            st.metric("Suspensos", pipeline.get("suspended_count", 0))

        st.subheader("Clientes")
        st.dataframe(report.get("customers", []), use_container_width=True)

        st.subheader("Atividades recentes")
        st.dataframe(report.get("recent_activities", []), use_container_width=True)

        st.subheader("Contatos sanitizados")
        st.dataframe(report.get("contacts_sanitized", []), use_container_width=True)

with tab2:
    alias = st.text_input("Alias do cliente", value="cliente_demo_novo")
    source = st.selectbox("Origem", ["manual", "marketplace_ia", "instagram_manual", "whatsapp_manual", "referral", "website", "event", "internal_demo"])
    owner = st.text_input("Dono comercial", value="k_os_operator")
    next_action = st.text_input("Proxima acao", value="qualificar lead")
    agent_id = st.text_input("Agent ID", value="marketplace_ia_agent")

    if st.button("Adicionar cliente", type="primary"):
        run([
            "--mode", "add-customer",
            "--alias", alias,
            "--source", source,
            "--owner", owner,
            "--next-action", next_action,
            "--agent-id", agent_id
        ])

with tab3:
    customer_id = st.text_input("Customer ID")
    status = st.selectbox(
        "Novo status",
        [
            "lead",
            "qualified",
            "proposal_sent",
            "negotiation",
            "trial",
            "active_customer",
            "past_due",
            "suspended",
            "cancelled",
            "lost",
            "archived"
        ]
    )
    reason = st.text_input("Motivo", value="manual_update_by_operator")

    if st.button("Atualizar status", type="primary"):
        run([
            "--mode", "set-status",
            "--customer-id", customer_id,
            "--status", status,
            "--reason", reason
        ])

with tab4:
    link_customer_id = st.text_input("Customer ID para vinculo")
    link_type = st.selectbox("Tipo de vinculo", ["billing_subscription", "license_gate", "proposal", "incident", "audit", "commercial_order", "manual_note"])
    target = st.text_input("Target", value="reports/billing/latest_billing_subscription_report.json")

    if st.button("Criar vinculo", type="primary"):
        run([
            "--mode", "link-record",
            "--customer-id", link_customer_id,
            "--link-type", link_type,
            "--target", target
        ])

    if PIPELINE_PATH.exists():
        st.subheader("Pipeline snapshot")
        st.json(json.loads(PIPELINE_PATH.read_text(encoding="utf-8-sig")))

with tab5:
    if POLICY_PATH.exists():
        st.json(json.loads(POLICY_PATH.read_text(encoding="utf-8-sig")))
    else:
        st.info("Policy ainda nao encontrada.")