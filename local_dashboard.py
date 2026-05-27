import streamlit as st
from pathlib import Path
import subprocess
import webbrowser

from k_atlas.core.safe_executor import execute_plan
from k_atlas.scripts.approve_next import main as approve_next_main
from k_atlas.scripts.create_ai_evolution_plan import create_ai_evolution_plan


BASE = Path.cwd()
K = BASE / "k_atlas"
WORKSPACE = K / "workspace"
PLANS = K / "plans"
REPORTS = K / "reports"
PENDING = K / "execution" / "pending"
DONE = K / "execution" / "done"


st.set_page_config(
    page_title="K-Atlas Cockpit",
    page_icon="🧭",
    layout="wide"
)


def count(path: Path, pattern="*"):
    if not path.exists():
        return 0
    return len(list(path.glob(pattern)))


def latest_file(path: Path, pattern: str):
    if not path.exists():
        return None
    files = list(path.glob(pattern))
    if not files:
        return None
    return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)[0]


def latest_landing_index():
    if not WORKSPACE.exists():
        return None
    files = list(WORKSPACE.glob("**/index.html"))
    if not files:
        return None
    return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)[0]


def latest_landing_folder():
    index = latest_landing_index()
    return index.parent if index else None


def read_text_file(path: Path | None, limit=9000):
    if not path or not path.exists():
        return "Nada encontrado ainda."
    text = path.read_text(encoding="utf-8", errors="ignore")
    return text[:limit]


def run_git_save():
    subprocess.run(["git", "add", "."], cwd=BASE, check=False)
    commit = subprocess.run(
        ["git", "commit", "-m", "chore: salva estado pelo K-Atlas Cockpit"],
        cwd=BASE,
        check=False,
        capture_output=True,
        text=True
    )
    push = subprocess.run(
        ["git", "push", "origin", "main"],
        cwd=BASE,
        check=False,
        capture_output=True,
        text=True
    )
    return (commit.stdout or commit.stderr or "") + "\n" + (push.stdout or push.stderr or "")


def pending_files():
    if not PENDING.exists():
        return []
    return sorted(PENDING.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)


if "board" not in st.session_state:
    st.session_state.board = "K-Atlas pronto. Envie um pedido ou use as ações rápidas."

st.title("🧭 K-Atlas — Cockpit Operacional")
st.caption("Comando, IA, aprovação, landing e GitHub em um painel único.")

left, right = st.columns([2, 1])

with left:
    st.subheader("💬 Comando principal")

    with st.form("pedido_form", clear_on_submit=True):
        pedido = st.text_area(
            "Pedido",
            placeholder='Ex: use IA para criar uma campanha de Instagram para a promoção de chopp grátis da Parada Atlântida',
            height=120,
            label_visibility="collapsed"
        )
        enviar = st.form_submit_button("🚀 Enviar para o K-Atlas")

    if enviar and pedido.strip():
        plan, results = execute_plan(pedido.strip(), auto_confirm=False)

        lines = []
        lines.append("## Pedido recebido")
        lines.append(pedido.strip())
        lines.append("")
        lines.append("## Plano")
        lines.append(plan.to_markdown())
        lines.append("")
        lines.append("## Resultados")
        for r in results:
            lines.append(f"- {r}")

        st.session_state.board = "\n".join(lines)

    st.subheader("⚡ Ações rápidas")

    c1, c2 = st.columns(2)

    with c1:
        if st.button("🧠 Usar IA na última landing"):
            command = "use IA para evoluir a última landing da Parada Atlântida com foco em conversão, WhatsApp e impacto visual"
            plan, results = execute_plan(command, auto_confirm=False)
            st.session_state.board = "## IA acionada para última landing\n\n" + "\n".join(f"- {r}" for r in results)
            st.rerun()

    with c2:
        if st.button("📋 Criar plano IA aplicável"):
            try:
                create_ai_evolution_plan()
                st.session_state.board = "## Plano IA aplicável criado\n\nFoi criado AI_EVOLUTION_PLAN.md e uma aprovação pendente."
            except Exception as e:
                st.session_state.board = f"## Erro ao criar plano IA aplicável\n\n{e}"
            st.rerun()

    c3, c4 = st.columns(2)

    with c3:
        if st.button("✅ Aprovar próxima ação"):
            try:
                approve_next_main()
                st.session_state.board = "## Aprovação executada\n\nA próxima ação pendente foi aprovada e executada."
            except Exception as e:
                st.session_state.board = f"## Erro ao aprovar\n\n{e}"
            st.rerun()

    with c4:
        if st.button("🌐 Abrir última landing"):
            index = latest_landing_index()
            if index:
                webbrowser.open(index.as_uri())
                st.session_state.board = f"## Última landing aberta\n\n{index}"
            else:
                st.session_state.board = "## Nenhuma landing encontrada."
            st.rerun()

    st.divider()

    st.subheader("🧠 Lousa do Cowork")
    st.markdown(st.session_state.board)

    st.divider()

    st.subheader("📄 Último relatório IA")
    latest_ai = latest_file(REPORTS, "ai_brain_*.md")
    with st.expander("Ver último relatório IA", expanded=False):
        st.markdown(read_text_file(latest_ai))

    st.subheader("✅ Último plano aplicado")
    latest_applied = latest_file(WORKSPACE, "**/AI_APPLIED.md")
    with st.expander("Ver AI_APPLIED.md", expanded=False):
        st.markdown(read_text_file(latest_applied))

with right:
    st.subheader("📊 Status")
    st.metric("Projetos", count(WORKSPACE))
    st.metric("Planos", count(PLANS, "*.md"))
    st.metric("Relatórios", count(REPORTS, "*.md"))
    st.metric("Pendências", count(PENDING, "*.json"))
    st.metric("Concluídas", count(DONE, "*.json"))

    st.divider()

    st.subheader("⚠️ Pendências")
    pendings = pending_files()
    if pendings:
        st.warning(f"{len(pendings)} pendência(s)")
        st.code(str(pendings[0]))
    else:
        st.success("Sem pendências.")

    st.divider()

    st.subheader("📁 Última landing")
    index = latest_landing_index()
    if index:
        st.code(str(index))
    else:
        st.write("Nenhuma landing.")

    st.subheader("🧠 Último AI Brain")
    latest_ai = latest_file(REPORTS, "ai_brain_*.md")
    if latest_ai:
        st.code(latest_ai.name)
    else:
        st.write("Nenhum relatório IA.")

    st.divider()

    if st.button("💾 Salvar no GitHub"):
        output = run_git_save()
        st.code(output)

    st.divider()

    st.subheader("🧪 PowerShell")
    st.code('.\\scripts\\atlas.ps1 "seu pedido"')
    st.code('.\\scripts\\aprovar.ps1')
    st.code('python -m k_atlas.status')
