from __future__ import annotations

import subprocess
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]

SAFE_PATHS = [
    ".github",
    "ops",
    "pages",
    "public_pages",
    "content_packs",
    "reports",
    "README.md",
    "K-ATLAS_CONTEXT.md",
    ".gitignore",
]

REPO_URL = "https://github.com/vkb-lab/motor-digital.git"


def run_git(args: list[str]) -> dict:
    completed = subprocess.run(
        ["git", *args],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    return {
        "code": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
        "cmd": "git " + " ".join(args),
    }


def render_result(title: str, result: dict) -> None:
    st.markdown(f"### {title}")
    st.code(result["cmd"], language="powershell")

    if result["stdout"]:
        st.code(result["stdout"], language="text")

    if result["stderr"]:
        st.code(result["stderr"], language="text")

    if result["code"] == 0:
        st.success("OK")
    else:
        st.error(f"Falhou com codigo {result['code']}")


def ensure_git_bridge() -> list[dict]:
    results = []

    if not (PROJECT_ROOT / ".git").exists():
        results.append(run_git(["init"]))

    remote = run_git(["remote"])
    if "origin" in remote["stdout"].splitlines():
        results.append(run_git(["remote", "set-url", "origin", REPO_URL]))
    else:
        results.append(run_git(["remote", "add", "origin", REPO_URL]))

    branch = run_git(["branch", "--show-current"])
    if not branch["stdout"].strip():
        results.append(run_git(["checkout", "-B", "main"]))
    elif branch["stdout"].strip() != "main":
        results.append(run_git(["checkout", "-B", "main"]))

    results.append(run_git(["config", "core.quotepath", "false"]))
    results.append(run_git(["config", "pull.rebase", "true"]))

    return results


def safe_add() -> list[dict]:
    results = []
    for item in SAFE_PATHS:
        if (PROJECT_ROOT / item).exists():
            results.append(run_git(["add", item]))
    return results


st.set_page_config(
    page_title="K-Uni Git Bridge",
    layout="wide",
)

st.title("K-Uni Git Bridge")
st.caption("Controle Git operacional dentro do cockpit K-Uni.")

st.warning(
    "Este painel usa o Git local do computador. Nenhum token fica salvo na pagina. "
    "Dados sensiveis em live/ devem permanecer fora do GitHub."
)

with st.sidebar:
    st.header("Acoes")
    commit_message = st.text_input(
        "Mensagem de commit",
        value="chore: sync k-uni cockpit changes",
    )

    do_connect = st.button("Conectar / reparar Git")
    do_status = st.button("Status Git")
    do_pull = st.button("Pull rebase")
    do_push = st.button("Commit + Push seguro")
    do_log = st.button("Ver ultimos commits")

st.header("Resumo")

col1, col2, col3 = st.columns(3)

branch = run_git(["branch", "--show-current"])
remote = run_git(["remote", "get-url", "origin"])
status = run_git(["status", "--short"])

with col1:
    st.metric("Branch", branch["stdout"] or "N/A")

with col2:
    st.metric("Origin", "OK" if remote["code"] == 0 else "PENDENTE")

with col3:
    changed_count = len([line for line in status["stdout"].splitlines() if line.strip()])
    st.metric("Alteracoes", changed_count)

st.divider()

if do_connect:
    st.header("Conectar / reparar Git")
    for index, result in enumerate(ensure_git_bridge(), start=1):
        render_result(f"Etapa {index}", result)

if do_status:
    st.header("Status Git")
    render_result("Remote", run_git(["remote", "-v"]))
    render_result("Branch", run_git(["branch", "--show-current"]))
    render_result("Status", run_git(["status", "--short"]))

if do_pull:
    st.header("Pull rebase")
    render_result("Pull", run_git(["pull", "--rebase", "origin", "main"]))

if do_push:
    st.header("Commit + Push seguro")

    for index, result in enumerate(safe_add(), start=1):
        render_result(f"Add seguro {index}", result)

    diff = run_git(["diff", "--cached", "--quiet"])

    if diff["code"] == 0:
        st.info("Sem alteracoes seguras para commit.")
    else:
        render_result("Commit", run_git(["commit", "-m", commit_message]))

    render_result("Push", run_git(["push", "origin", "main"]))

if do_log:
    st.header("Ultimos commits")
    render_result("Log", run_git(["log", "--oneline", "-10"]))

st.divider()
st.subheader("Estado atual")
render_result("Status atual", run_git(["status", "--short"]))

st.caption("K-Uni Git Bridge - GitHub como memoria persistente operacional.")