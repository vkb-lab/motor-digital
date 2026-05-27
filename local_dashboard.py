import streamlit as st
from pathlib import Path
from datetime import datetime
import subprocess
import sys

from k_atlas.core.safe_executor import execute_plan
from k_atlas.scripts.approve_next import main as approve_next_main


BASE = Path.cwd()
K = BASE / "k_atlas"
PENDING = K / "execution" / "pending"
DONE = K / "execution" / "done"
REPORTS = K / "reports"
PLANS = K / "plans"
WORKSPACE = K / "workspace"


st.set_page_config(
    page_title="K-Atlas Cowork",
    page_icon="🧭",
    layout="wide"
)


def count(path: Path, pattern="*"):
    if not path.exists():
        return 0
    return len(list(path.glob(pattern)))


def latest_file(path: Path, pattern="*"):
    if not path.exists():
        return None
    files = list(path.glob(pattern))
    if not files:
        return None
    return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)[0]


def read_latest(path: Path, pattern="*.md"):
    f = latest_file(path, pattern)
    if not f:
        return "Nada ainda."
    try:
        return f.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        return f"Não consegui ler {f}: {e}"


def run_git_save(message: str):
    try:
        subprocess.run(["git", "add", "."], cwd=BASE, check=False)
        subprocess.run(["git", "commit", "-m", message], cwd=BASE, check=False)
        subprocess.run(["git", "push", "origin", "main"], cwd=BASE, check=False)
        return "Alterações salvas no GitHub."
    except Exception as e:
        return f"Não consegui salvar no GitHub: {e}"


def pending_files():
    if not PENDING.exists():
        return []
    return sorted(PENDING.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)


if "last_board" not in st.session_state:
    st.session_state.last_board = "K-Atlas pronto. Diga o que você quer construir, analisar ou executar."

if "last_results" not in st.session_state:
    st.session_state.last_results = []


st.title("🧭 K-Atlas — Cowork Operacional")
st.caption("Agente local com planejamento, execução segura e aprovação antes de ações sensíveis.")

left, right = st.columns([2, 1])

with left:
    st.subheader("💬 O que você quer que eu resolva agora?")

    with st.form("pedido_form", clear_on_submit=True):
        pedido = st.text_area(
            "Pedido",
            placeholder="Ex: crie uma landing page para Parada Atlântida vender chopp grátis",
            height=120,
            label_visibility="collapsed"
        )
        executar = st.form_submit_button("🚀 Enviar para o K-Atlas")

    if executar and pedido.strip():
        plan, results = execute_plan(pedido.strip(), auto_confirm=False)

        board = []
        board.append("## Pedido recebido")
        board.append(pedido.strip())
        board.append("")
        board.append("## Plano")
        board.append(plan.to_markdown())
        board.append("")
        board.append("## Resultados")
        for item in results:
            board.append(f"- {item}")

        st.session_state.last_board = "\n".join(board)
        st.session_state.last_results = results

    st.subheader("🧠 Lousa do Cowork")
    st.markdown(st.session_state.last_board)

    st.divider()

    st.subheader("✅ Aprovação")
    pendings = pending_files()

    if pendings:
        st.warning(f"Existe {len(pendings)} aprovação pendente.")
        st.code(str(pendings[0]))

        if st.button("✅ Aprovar próxima ação"):
            approve_next_main()
            st.session_state.last_board += "\n\n## Aprovação executada\nA próxima ação pendente foi aprovada e executada."
            st.rerun()
    else:
        st.success("Sem aprovações pendentes.")

    st.divider()

    st.subheader("💾 GitHub")
    if st.button("Salvar estado no GitHub"):
        msg = run_git_save("chore: salva estado pelo painel K-Atlas Cowork")
        st.info(msg)

with right:
    st.subheader("📊 Status")

    st.metric("Projetos", count(WORKSPACE))
    st.metric("Planos", count(PLANS, "*.md"))
    st.metric("Relatórios", count(REPORTS, "*.md"))
    st.metric("Pendências", count(PENDING, "*.json"))
    st.metric("Concluídas", count(DONE, "*.json"))

    st.divider()

    st.subheader("📁 Último plano")
    last_plan = latest_file(PLANS, "*.md")
    if last_plan:
        st.write(last_plan.name)
    else:
        st.write("Nenhum plano.")

    st.subheader("📄 Último relatório")
    last_report = latest_file(REPORTS, "*.md")
    if last_report:
        st.write(last_report.name)
    else:
        st.write("Nenhum relatório.")

    st.divider()

    st.subheader("🧪 Comandos locais")
    st.code('.\\scripts\\atlas.ps1 "seu pedido"')
    st.code('.\\scripts\\aprovar.ps1')
    st.code('python -m k_atlas.status')
