import streamlit as st
import webbrowser
from pathlib import Path
from datetime import datetime

from k_atlas.core.intent_router import route_intent
from k_atlas.core.visual_logger import log_visual, get_timeline, log_debug, human_error


st.set_page_config(
    page_title="K-Atlas Local",
    page_icon="🧭",
    layout="wide"
)

BASE_DIR = Path.cwd()
WORKSPACE = Path.home() / "MotorDigital_Workspace"
WORKSPACE.mkdir(parents=True, exist_ok=True)


def open_url(url: str):
    webbrowser.open(url)
    log_visual(f"Abrindo navegador em: {url}")


def execute_safe_action(response):
    action = response.action
    metadata = response.metadata or {}

    try:
        if action in ["open_gmail", "open_instagram", "open_canva"]:
            url = metadata.get("url")
            if url:
                open_url(url)
                response.executed.append(f"Abri o navegador em: {url}")

        elif action == "list_windows":
            response.executed.append("Listagem de janelas ainda será reconectada ao módulo antigo.")

        elif action == "analyze_desktop":
            desktop = Path.home() / "Desktop"
            exports = BASE_DIR / "k_atlas" / "exports"
            exports.mkdir(parents=True, exist_ok=True)
            out = exports / "desktop_report.txt"

            lines = []
            lines.append(f"Relatório da Área de Trabalho - {datetime.now()}")
            lines.append("")
            for item in desktop.iterdir():
                lines.append(f"{item.name} | {'PASTA' if item.is_dir() else 'ARQUIVO'}")

            out.write_text("\n".join(lines), encoding="utf-8")
            response.executed.append(f"Relatório criado em: {out}")

        elif action == "create_project":
            projects_dir = BASE_DIR / "k_atlas" / "projects"
            projects_dir.mkdir(parents=True, exist_ok=True)

            project_name = "Projeto_K_Atlas_" + datetime.now().strftime("%Y%m%d_%H%M%S")
            project_path = projects_dir / project_name
            project_path.mkdir(parents=True, exist_ok=True)

            readme = project_path / "README.md"
            readme.write_text(
                f"# {project_name}\n\nProjeto criado pelo K-Atlas Local.\n",
                encoding="utf-8"
            )

            response.executed.append(f"Projeto criado em: {project_path}")

        elif action == "generate_app_plan":
            exports = BASE_DIR / "k_atlas" / "exports"
            exports.mkdir(parents=True, exist_ok=True)
            out = exports / f"app_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            out.write_text(response.to_markdown(), encoding="utf-8")
            response.executed.append(f"Plano inicial de app salvo em: {out}")

        else:
            response.executed.append("Nenhuma ação local automática foi executada.")

    except Exception as e:
        log_debug(e)
        response.blocked.append(human_error(e))

    return response


# Estado da sessão
if "last_response_md" not in st.session_state:
    st.session_state.last_response_md = "Aguardando seu primeiro comando."

if "last_command" not in st.session_state:
    st.session_state.last_command = ""


# Layout
st.title("🧭 K-Atlas Local — Cowork no seu Windows")
st.caption("Digite o que quer resolver. Eu interpreto, planejo, executo o que for seguro e explico limites quando precisar de API/permissão.")

left, right = st.columns([2, 1])

with left:
    st.subheader("💬 Prompt Bar")

    with st.form("command_form", clear_on_submit=False):
        command = st.text_input(
            "O que você quer que eu resolva agora?",
            value="",
            placeholder="Ex: verifique os emails de ontem no gmail"
        )
        submitted = st.form_submit_button("Executar")

    if submitted and command.strip():
        st.session_state.last_command = command.strip()
        log_visual(f"Pedido recebido: {command.strip()}")

        response = route_intent(command)
        log_visual(f"Intenção detectada: {response.intent}")

        response = execute_safe_action(response)

        if response.blocked:
            for block in response.blocked:
                log_visual(f"Bloqueio: {block}")

        for item in response.executed:
            log_visual(f"Executado: {item}")

        st.session_state.last_response_md = response.to_markdown()

    st.subheader("🧠 Lousa do Cowork")
    st.markdown(st.session_state.last_response_md)

    st.divider()

    st.subheader("⚡ Testes rápidos")
    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("Abrir Gmail"):
            response = route_intent("abra o gmail")
            response = execute_safe_action(response)
            st.session_state.last_response_md = response.to_markdown()
            st.rerun()

    with c2:
        if st.button("Abrir Instagram"):
            response = route_intent("abra o instagram")
            response = execute_safe_action(response)
            st.session_state.last_response_md = response.to_markdown()
            st.rerun()

    with c3:
        if st.button("Analisar Desktop"):
            response = route_intent("analise minha área de trabalho")
            response = execute_safe_action(response)
            st.session_state.last_response_md = response.to_markdown()
            st.rerun()

with right:
    st.subheader("📡 Linha do Tempo do Cowork")
    timeline = get_timeline(25)

    if timeline:
        for line in reversed(timeline):
            st.write(line)
    else:
        st.info("Nenhuma ação registrada ainda.")

    st.divider()

    st.subheader("🧩 Status")
    st.success("K-Atlas Local ativo")
    st.write(f"Workspace: `{WORKSPACE}`")
    st.write(f"Projeto: `{BASE_DIR}`")

    st.warning("Autoevolução direta está desativada nesta fase por segurança.")
