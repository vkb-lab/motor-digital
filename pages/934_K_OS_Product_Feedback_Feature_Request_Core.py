from __future__ import annotations

import json
import subprocess
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT_ROOT / "ops" / "k_os_product_feedback_feature_request_core.py"
REPORT_PATH = PROJECT_ROOT / "reports" / "product_feedback" / "latest_product_feedback_report.json"
BACKLOG_PATH = PROJECT_ROOT / "reports" / "product_feedback" / "latest_product_backlog_snapshot.json"
ROADMAP_PATH = PROJECT_ROOT / "reports" / "product_feedback" / "latest_roadmap_candidate_snapshot.json"
POLICY_PATH = PROJECT_ROOT / "config" / "product_feedback" / "k_os_product_feedback_policy.json"

st.set_page_config(page_title="K-OS Product Feedback", layout="wide")

st.title("K-OS Product Feedback and Feature Request Core")
st.caption("Checkpoint 034 - feedback, features, backlog e candidatos de roadmap.")

st.warning(
    "Backlog local. Nenhum roadmap é publicado. Nenhuma promessa externa de feature é feita automaticamente."
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


tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Dashboard", "Feedback", "Feature", "Link", "Backlog", "Policy"])

with tab1:
    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("Inicializar Product Feedback", type="primary"):
            run(["--mode", "init"])

    with c2:
        if st.button("Criar demo"):
            run(["--mode", "create-demo"])

    with c3:
        if st.button("Auditar"):
            run(["--mode", "audit"])

    if REPORT_PATH.exists():
        report = json.loads(REPORT_PATH.read_text(encoding="utf-8-sig"))
        metrics = report.get("metrics", {})

        m1, m2, m3, m4 = st.columns(4)

        with m1:
            st.metric("Feedbacks", metrics.get("feedback_count", 0))

        with m2:
            st.metric("Features", metrics.get("feature_count", 0))

        with m3:
            st.metric("Críticos", metrics.get("critical_feedback_count", 0))

        with m4:
            st.metric("Roadmap candidates", metrics.get("roadmap_candidate_count", 0))

        st.subheader("Feedback")
        st.dataframe(report.get("feedback_items", []), use_container_width=True)

        st.subheader("Feature requests")
        st.dataframe(report.get("feature_requests", []), use_container_width=True)

        st.subheader("Links")
        st.dataframe(report.get("feature_feedback_links", []), use_container_width=True)

with tab2:
    customer_alias = st.text_input("Customer alias", value="demo_customer")
    feedback_type = st.selectbox("Tipo", ["bug", "improvement", "feature_request", "compliment", "complaint", "usability", "performance", "billing", "security", "integration", "automation"])
    category = st.selectbox("Categoria", ["cockpit", "agents", "memory", "automation", "campaigns", "crm", "billing", "license", "support", "security", "integrations", "analytics", "content", "marketplace"])
    summary = st.text_area("Resumo sanitizado", value="Cliente pediu melhoria operacional.")
    impact = st.selectbox("Impacto", ["low", "medium", "high", "critical"], index=1)
    urgency = st.selectbox("Urgência", ["low", "medium", "high", "critical"], index=1)
    sentiment = st.selectbox("Sentimento", ["positive", "neutral", "negative"], index=1)
    owner = st.text_input("Owner", value="k_os_operator")

    if st.button("Registrar feedback", type="primary"):
        run([
            "--mode", "create-feedback",
            "--customer-alias", customer_alias,
            "--feedback-type", feedback_type,
            "--category", category,
            "--summary", summary,
            "--impact", impact,
            "--urgency", urgency,
            "--sentiment", sentiment,
            "--owner", owner
        ])

with tab3:
    title = st.text_input("Título da feature", value="Melhoria no cockpit operacional")
    f_category = st.selectbox("Categoria da feature", ["cockpit", "agents", "memory", "automation", "campaigns", "crm", "billing", "license", "support", "security", "integrations", "analytics", "content", "marketplace"])
    f_impact = st.selectbox("Impacto feature", ["low", "medium", "high", "critical"], index=2)
    f_urgency = st.selectbox("Urgência feature", ["low", "medium", "high", "critical"], index=1)
    effort = st.selectbox("Esforço", ["small", "medium", "large", "unknown"], index=1)
    revenue_signal = st.selectbox("Sinal de receita", ["none", "low", "medium", "high", "strategic"], index=2)
    next_action = st.text_input("Próxima ação", value="revisar viabilidade e impacto")
    feature_owner = st.text_input("Product owner", value="k_os_operator")

    if st.button("Criar feature", type="primary"):
        run([
            "--mode", "create-feature",
            "--title", title,
            "--category", f_category,
            "--impact", f_impact,
            "--urgency", f_urgency,
            "--effort", effort,
            "--revenue-signal", revenue_signal,
            "--owner", feature_owner,
            "--next-action", next_action
        ])

    st.divider()

    feature_id_status = st.text_input("Feature ID")
    status = st.selectbox("Status", ["new", "triage", "backlog", "planned", "in_progress", "blocked", "shipped", "rejected", "archived"])
    reason = st.text_input("Motivo", value="manual_product_review")

    if st.button("Atualizar status"):
        run(["--mode", "set-feature-status", "--feature-id", feature_id_status, "--status", status, "--reason", reason])

    new_priority = st.selectbox("Prioridade manual", ["low", "medium", "high", "critical", "strategic"])

    if st.button("Atualizar prioridade"):
        run(["--mode", "set-feature-priority", "--feature-id", feature_id_status, "--priority", new_priority, "--reason", reason])

with tab4:
    feedback_id = st.text_input("Feedback ID")
    feature_id = st.text_input("Feature ID para link")
    link_reason = st.text_input("Razão do vínculo", value="manual_product_triage")

    if st.button("Vincular feedback à feature", type="primary"):
        run(["--mode", "link-feedback", "--feedback-id", feedback_id, "--feature-id", feature_id, "--reason", link_reason])

with tab5:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Backlog")
        if BACKLOG_PATH.exists():
            st.json(json.loads(BACKLOG_PATH.read_text(encoding="utf-8-sig")))
        else:
            st.info("Backlog ainda não gerado.")

    with col2:
        st.subheader("Roadmap candidates")
        if ROADMAP_PATH.exists():
            st.json(json.loads(ROADMAP_PATH.read_text(encoding="utf-8-sig")))
        else:
            st.info("Roadmap candidate snapshot ainda não gerado.")

with tab6:
    if POLICY_PATH.exists():
        st.json(json.loads(POLICY_PATH.read_text(encoding="utf-8-sig")))
    else:
        st.info("Policy ainda não encontrada.")