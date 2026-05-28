import streamlit as st
from pathlib import Path
import subprocess
import json
from datetime import datetime

BASE = Path.cwd()
K = BASE / "k_atlas"
MEMORY = K / "memory"
CONTENT = K / "content_packs"
REPORTS = K / "reports"
APPROVED = K / "approved_campaigns"

APPROVED.mkdir(parents=True, exist_ok=True)

st.set_page_config(
    page_title="K-Atlas Cockpit",
    page_icon="🧭",
    layout="wide"
)

def count_files(path, pattern="*"):
    if not path.exists():
        return 0
    return len(list(path.glob(pattern)))

def latest_file(path, pattern="*"):
    if not path.exists():
        return None
    files = list(path.glob(pattern))
    if not files:
        return None
    return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)[0]

def read_json(path):
    if not path or not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return {}

def run_k_atlas(command):
    result = subprocess.run(
        [
            "python",
            "-m",
            "k_atlas.live.live_commander_once",
            "--command",
            command
        ],
        cwd=BASE,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    output = ""

    if result.stdout:
        output += result.stdout

    if result.stderr:
        output += "\n" + result.stderr

    return output.strip()

def git_save():
    subprocess.run(["git", "add", "."], cwd=BASE, check=False)
    commit = subprocess.run(
        ["git", "commit", "-m", "chore: salva estado pelo cockpit K-Atlas"],
        cwd=BASE,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )
    push = subprocess.run(
        ["git", "push", "origin", "main"],
        cwd=BASE,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )
    return (commit.stdout or commit.stderr or "") + "\n" + (push.stdout or push.stderr or "")

def approve_last_pack():
    pack = latest_file(CONTENT, "instagram_pack_*.json")

    if not pack:
        return "Nenhum pacote Instagram para aprovar."

    data = read_json(pack)

    approved_file = APPROVED / f"approved_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    approved_file.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    return f"Campanha aprovada e salva em: {approved_file}"

if "board" not in st.session_state:
    st.session_state.board = "K-Atlas pronto para receber comandos."

st.title("🧭 K-Atlas — Cockpit Operacional")
st.caption("Comando central, memoria, campanhas, aprovacao e execucao em um painel unico.")

left, right = st.columns([2, 1])

with left:
    st.subheader("💬 Comando principal")

    with st.form("command_form", clear_on_submit=True):
        command = st.text_area(
            "Comando",
            placeholder="Ex: cliente desesperado piscina verde filhos vao usar hoje criar campanha instagram",
            height=120,
            label_visibility="collapsed"
        )
        send = st.form_submit_button("🚀 Enviar para o K-Atlas")

    if send and command.strip():
        st.session_state.board = run_k_atlas(command.strip())

    st.subheader("🧠 Resposta do K-Atlas")
    st.code(st.session_state.board)

    st.divider()

    st.subheader("📦 Ultimo pacote Instagram")
    pack = latest_file(CONTENT, "instagram_pack_*.json")

    if pack:
        data = read_json(pack)
        full_post = data.get("full_post", "Pacote encontrado, mas sem full_post.")

        st.text_area(
            "Post pronto",
            value=full_post,
            height=260
        )

        b1, b2 = st.columns(2)

        with b1:
            if st.button("✅ Aprovar campanha"):
                st.session_state.board = approve_last_pack()
                st.rerun()

        with b2:
            if st.button("💾 Salvar no GitHub"):
                st.session_state.board = git_save()
                st.rerun()

        with st.expander("Ver JSON completo"):
            st.json(data)
    else:
        st.info("Nenhum pacote Instagram encontrado.")

with right:
    st.subheader("📊 Status")
    st.metric("Memorias", count_files(MEMORY, "*.json"))
    st.metric("Pacotes Instagram", count_files(CONTENT, "*.json"))
    st.metric("Aprovadas", count_files(APPROVED, "*.json"))
    st.metric("Relatorios", count_files(REPORTS, "*"))

    st.divider()

    st.subheader("🧠 Ultima memoria")
    mem = latest_file(MEMORY, "*.json")
    if mem:
        st.code(mem.name)
        st.json(read_json(mem))
    else:
        st.info("Nenhuma memoria encontrada.")

    st.divider()

    st.subheader("✅ Ultima campanha aprovada")
    approved = latest_file(APPROVED, "*.json")
    if approved:
        st.code(approved.name)
        st.json(read_json(approved))
    else:
        st.info("Nenhuma campanha aprovada ainda.")

    st.divider()

    st.subheader("⚡ Atalho")
    st.code("Tanque-K-Atlas.bat")
