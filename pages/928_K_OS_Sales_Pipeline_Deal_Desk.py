from __future__ import annotations

import json
import subprocess
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT_ROOT / "ops" / "k_os_sales_pipeline_deal_desk.py"
REPORT_PATH = PROJECT_ROOT / "reports" / "sales" / "latest_sales_pipeline_report.json"
APPROVAL_PATH = PROJECT_ROOT / "reports" / "sales" / "latest_deal_approval_dry_run.json"
POLICY_PATH = PROJECT_ROOT / "config" / "sales" / "k_os_sales_pipeline_deal_desk_policy.json"

st.set_page_config(page_title="K-OS Sales Pipeline Deal Desk", layout="wide")

st.title("K-OS Sales Pipeline and Deal Desk")
st.caption("Checkpoint 028 - oportunidades, propostas, valores, aprovacoes e proximas acoes comerciais.")

st.warning(
    "Deal Desk local. Nao fecha cliente automaticamente, nao envia proposta externa e nao ativa cliente sem gates."
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


tab1, tab2, tab3, tab4, tab5 = st.tabs(["Dashboard", "Novo deal", "Stage", "Approval dry-run", "Policy"])

with tab1:
    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("Inicializar Deal Desk", type="primary"):
            run(["--mode", "init"])

    with c2:
        if st.button("Criar demo local"):
            run(["--mode", "create-demo"])

    with c3:
        if st.button("Auditar pipeline"):
            run(["--mode", "audit"])

    if REPORT_PATH.exists():
        report = json.loads(REPORT_PATH.read_text(encoding="utf-8-sig"))
        pipeline = report.get("pipeline", {})

        m1, m2, m3, m4, m5 = st.columns(5)

        with m1:
            st.metric("Deals", pipeline.get("deal_count", 0))

        with m2:
            st.metric("Abertos", pipeline.get("open_deal_count", 0))

        with m3:
            st.metric("MRR aberto", pipeline.get("open_mrr_estimate_brl", 0))

        with m4:
            st.metric("MRR ponderado", pipeline.get("weighted_mrr_estimate_brl", 0))

        with m5:
            st.metric("ARR ponderado", pipeline.get("weighted_arr_estimate_brl", 0))

        st.subheader("Deals")
        st.dataframe(report.get("deals", []), use_container_width=True)

        st.subheader("Atividades recentes")
        st.dataframe(report.get("recent_activities", []), use_container_width=True)

with tab2:
    alias = st.text_input("Customer alias", value="cliente_pipeline_demo")
    agent_id = st.text_input("Agent ID", value="marketplace_ia_agent")
    mrr = st.number_input("MRR estimado BRL", min_value=0.0, value=997.0)
    setup = st.number_input("Setup estimado BRL", min_value=0.0, value=1500.0)
    priority = st.selectbox("Prioridade", ["low", "medium", "high", "strategic"])
    owner = st.text_input("Dono comercial", value="k_os_operator")
    next_action = st.text_input("Proxima acao", value="qualificar oportunidade")

    if st.button("Adicionar deal", type="primary"):
        run([
            "--mode", "add-deal",
            "--customer-alias", alias,
            "--agent-id", agent_id,
            "--mrr", str(mrr),
            "--setup", str(setup),
            "--priority", priority,
            "--owner", owner,
            "--next-action", next_action
        ])

with tab3:
    deal_id = st.text_input("Deal ID")
    stage = st.selectbox(
        "Novo stage",
        [
            "lead",
            "qualified",
            "discovery",
            "proposal_draft",
            "proposal_sent",
            "negotiation",
            "legal_review",
            "commercial_approval",
            "won_pending_activation",
            "active",
            "lost",
            "on_hold"
        ]
    )
    probability = st.slider("Probabilidade", 0, 100, 35)
    reason = st.text_input("Motivo", value="manual_stage_update")

    if st.button("Atualizar stage", type="primary"):
        run([
            "--mode", "update-stage",
            "--deal-id", deal_id,
            "--stage", stage,
            "--reason", reason,
            "--probability", str(probability)
        ])

with tab4:
    approval_deal_id = st.text_input("Deal ID para approval dry-run")

    if st.button("Rodar approval dry-run", type="primary"):
        run(["--mode", "approval-dry-run", "--deal-id", approval_deal_id])

    if APPROVAL_PATH.exists():
        st.json(json.loads(APPROVAL_PATH.read_text(encoding="utf-8-sig")))

with tab5:
    if POLICY_PATH.exists():
        st.json(json.loads(POLICY_PATH.read_text(encoding="utf-8-sig")))
    else:
        st.info("Policy ainda nao encontrada.")