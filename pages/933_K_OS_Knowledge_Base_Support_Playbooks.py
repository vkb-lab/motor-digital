from __future__ import annotations

import json
import subprocess
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT_ROOT / "ops" / "k_os_knowledge_base_support_playbooks.py"
REPORT_PATH = PROJECT_ROOT / "reports" / "knowledge_base" / "latest_knowledge_base_report.json"
PLAYBOOK_PATH = PROJECT_ROOT / "reports" / "knowledge_base" / "latest_support_playbook_snapshot.json"
DRAFT_PATH = PROJECT_ROOT / "reports" / "knowledge_base" / "latest_response_draft.json"
POLICY_PATH = PROJECT_ROOT / "config" / "knowledge_base" / "k_os_knowledge_base_playbooks_policy.json"

st.set_page_config(page_title="K-OS Knowledge Base", layout="wide")

st.title("K-OS Knowledge Base and Support Playbooks")
st.caption("Checkpoint 033 - base de conhecimento, playbooks, templates e vínculo com tickets.")

st.warning(
    "Base local. Nenhuma resposta externa é enviada. Artigos e playbooks não são publicados externamente."
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


tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Dashboard", "Artigo", "Playbook", "Template", "Draft", "Policy"])

with tab1:
    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("Inicializar KB", type="primary"):
            run(["--mode", "init"])

    with c2:
        if st.button("Criar demo KB"):
            run(["--mode", "create-demo"])

    with c3:
        if st.button("Auditar KB"):
            run(["--mode", "audit"])

    if REPORT_PATH.exists():
        report = json.loads(REPORT_PATH.read_text(encoding="utf-8-sig"))
        metrics = report.get("metrics", {})

        m1, m2, m3, m4 = st.columns(4)

        with m1:
            st.metric("Artigos", metrics.get("article_count", 0))

        with m2:
            st.metric("Playbooks", metrics.get("playbook_count", 0))

        with m3:
            st.metric("Templates", metrics.get("template_count", 0))

        with m4:
            st.metric("Links ticket", metrics.get("ticket_link_count", 0))

        st.subheader("Artigos")
        st.dataframe(report.get("articles", []), use_container_width=True)

        st.subheader("Playbooks")
        st.dataframe(report.get("playbooks", []), use_container_width=True)

        st.subheader("Templates")
        st.dataframe(report.get("response_templates", []), use_container_width=True)

    if PLAYBOOK_PATH.exists():
        st.subheader("Snapshot")
        st.json(json.loads(PLAYBOOK_PATH.read_text(encoding="utf-8-sig")))

with tab2:
    title = st.text_input("Título do artigo", value="Como resolver dúvida recorrente")
    category = st.selectbox("Categoria do artigo", ["onboarding", "delivery", "support", "billing", "license", "security", "incident", "technical", "commercial", "faq"])
    summary = st.text_area("Resumo sanitizado", value="Resumo interno do artigo.")
    content = st.text_area("Conteúdo interno", value="Passos internos, sem dados sensíveis de cliente.")
    owner = st.text_input("Owner", value="k_os_operator")

    if st.button("Criar artigo", type="primary"):
        run(["--mode", "create-article", "--title", title, "--category", category, "--summary", summary, "--content", content, "--owner", owner])

    st.divider()

    article_id = st.text_input("Article ID")
    article_status = st.selectbox("Status do artigo", ["draft", "internal_review", "approved_internal", "deprecated", "archived"])
    reason = st.text_input("Motivo", value="manual_update")

    if st.button("Atualizar artigo"):
        run(["--mode", "set-article-status", "--article-id", article_id, "--status", article_status, "--reason", reason])

with tab3:
    pb_title = st.text_input("Título do playbook", value="Playbook de triagem")
    pb_category = st.selectbox("Categoria do playbook", ["triage", "bug", "delivery", "billing", "license", "incident", "security", "customer_success", "commercial"])
    pb_steps = st.text_area("Steps separados por |", value="identificar contexto | revisar ticket | registrar nota | definir próxima ação | pedir aprovação")
    pb_owner = st.text_input("Owner do playbook", value="k_os_operator")

    if st.button("Criar playbook", type="primary"):
        run(["--mode", "create-playbook", "--title", pb_title, "--category", pb_category, "--steps", pb_steps, "--owner", pb_owner])

    st.divider()

    playbook_id = st.text_input("Playbook ID")
    pb_status = st.selectbox("Status do playbook", ["draft", "internal_review", "approved_internal", "deprecated", "archived"])

    if st.button("Atualizar playbook"):
        run(["--mode", "set-playbook-status", "--playbook-id", playbook_id, "--status", pb_status, "--reason", reason])

with tab4:
    tpl_title = st.text_input("Título do template", value="Resposta interna padrão")
    tpl_category = st.text_input("Categoria do template", value="support")
    tpl_body = st.text_area("Corpo do template", value="Rascunho interno. Envio externo exige aprovação humana.")
    tpl_owner = st.text_input("Owner do template", value="k_os_operator")

    if st.button("Criar template", type="primary"):
        run(["--mode", "add-template", "--title", tpl_title, "--category", tpl_category, "--content", tpl_body, "--owner", tpl_owner])

with tab5:
    ticket_id = st.text_input("Ticket ID")
    template_id = st.text_input("Template ID")

    if st.button("Gerar draft interno", type="primary"):
        run(["--mode", "generate-draft", "--ticket-id", ticket_id, "--template-id", template_id])

    if DRAFT_PATH.exists():
        st.json(json.loads(DRAFT_PATH.read_text(encoding="utf-8-sig")))

with tab6:
    if POLICY_PATH.exists():
        st.json(json.loads(POLICY_PATH.read_text(encoding="utf-8-sig")))
    else:
        st.info("Policy ainda não encontrada.")