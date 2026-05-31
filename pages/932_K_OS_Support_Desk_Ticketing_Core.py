from __future__ import annotations

import json
import subprocess
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT_ROOT / "ops" / "k_os_support_desk_ticketing_core.py"
REPORT_PATH = PROJECT_ROOT / "reports" / "support" / "latest_support_desk_report.json"
SLA_PATH = PROJECT_ROOT / "reports" / "support" / "latest_support_sla_snapshot.json"
POLICY_PATH = PROJECT_ROOT / "config" / "support" / "k_os_support_desk_ticketing_policy.json"

st.set_page_config(page_title="K-OS Support Desk", layout="wide")

st.title("K-OS Support Desk and Ticketing Core")
st.caption("Checkpoint 032 - tickets, prioridade, SLA operacional, triagem e escalonamento.")

st.warning(
    "Suporte local. Nenhuma resposta externa é enviada. Dados brutos ficam fora do GitHub."
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


tab1, tab2, tab3, tab4, tab5 = st.tabs(["Dashboard", "Novo ticket", "Status", "Nota", "Policy"])

with tab1:
    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("Inicializar Support Desk", type="primary"):
            run(["--mode", "init"])

    with c2:
        if st.button("Criar ticket demo"):
            run(["--mode", "create-demo"])

    with c3:
        if st.button("Auditar suporte"):
            run(["--mode", "audit"])

    if REPORT_PATH.exists():
        report = json.loads(REPORT_PATH.read_text(encoding="utf-8-sig"))
        metrics = report.get("metrics", {})

        m1, m2, m3, m4, m5 = st.columns(5)

        with m1:
            st.metric("Tickets", metrics.get("ticket_count", 0))

        with m2:
            st.metric("Abertos", metrics.get("open_ticket_count", 0))

        with m3:
            st.metric("Críticos", metrics.get("critical_ticket_count", 0))

        with m4:
            st.metric("SLA risco", metrics.get("sla_at_risk_count", 0))

        with m5:
            st.metric("SLA vencido", metrics.get("sla_breached_count", 0))

        st.subheader("Tickets")
        st.dataframe(report.get("tickets", []), use_container_width=True)

        st.subheader("Notas recentes")
        st.dataframe(report.get("recent_notes", []), use_container_width=True)

        st.subheader("Atividades recentes")
        st.dataframe(report.get("recent_activities", []), use_container_width=True)

    if SLA_PATH.exists():
        st.subheader("SLA Snapshot")
        st.json(json.loads(SLA_PATH.read_text(encoding="utf-8-sig")))

with tab2:
    customer_alias = st.text_input("Customer alias", value="demo_customer")
    category = st.selectbox("Categoria", ["question", "bug", "delivery", "billing", "license", "onboarding", "access", "incident", "feature_request", "legal", "security"])
    priority = st.selectbox("Prioridade", ["low", "medium", "high", "critical"])
    subject = st.text_input("Assunto", value="Validar suporte recorrente")
    summary = st.text_area("Resumo sanitizado", value="Ticket criado para validar fluxo de suporte local.")
    owner = st.text_input("Support owner", value="k_os_operator")

    if st.button("Criar ticket", type="primary"):
        run([
            "--mode", "create-ticket",
            "--customer-alias", customer_alias,
            "--category", category,
            "--priority", priority,
            "--subject", subject,
            "--summary", summary,
            "--owner", owner
        ])

with tab3:
    ticket_id = st.text_input("Ticket ID")
    status = st.selectbox("Status", ["new", "triage", "in_progress", "waiting_customer", "waiting_internal", "escalated", "resolved_pending_review", "closed", "cancelled"])
    reason = st.text_input("Motivo", value="manual_update")

    if st.button("Atualizar status", type="primary"):
        run(["--mode", "set-status", "--ticket-id", ticket_id, "--status", status, "--reason", reason])

    st.divider()

    priority_ticket_id = st.text_input("Ticket ID para prioridade")
    new_priority = st.selectbox("Nova prioridade", ["low", "medium", "high", "critical"])

    if st.button("Atualizar prioridade"):
        run(["--mode", "set-priority", "--ticket-id", priority_ticket_id, "--priority", new_priority, "--reason", reason])

with tab4:
    note_ticket_id = st.text_input("Ticket ID da nota")
    note_type = st.selectbox("Tipo da nota", ["internal", "customer_summary", "technical", "commercial", "incident_link"])
    note_summary = st.text_area("Resumo da nota", value="Nota interna sanitizada.")
    note_owner = st.text_input("Autor", value="k_os_operator")

    if st.button("Adicionar nota", type="primary"):
        run([
            "--mode", "add-note",
            "--ticket-id", note_ticket_id,
            "--summary", note_summary,
            "--note-type", note_type,
            "--owner", note_owner
        ])

with tab5:
    if POLICY_PATH.exists():
        st.json(json.loads(POLICY_PATH.read_text(encoding="utf-8-sig")))
    else:
        st.info("Policy ainda não encontrada.")