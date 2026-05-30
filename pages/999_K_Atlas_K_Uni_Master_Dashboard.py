from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def run_cmd(args: list[str]) -> str:
    try:
        result = subprocess.run(
            args,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=8,
            shell=False,
        )
        return (result.stdout + result.stderr).strip()
    except Exception as exc:
        return f"erro: {exc}"


def count_files(pattern: str) -> int:
    return len(list(PROJECT_ROOT.glob(pattern)))


def latest_pages(limit: int = 12) -> list[str]:
    pages = sorted(
        PROJECT_ROOT.glob("pages/*.py"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return [p.name for p in pages[:limit]]


def latest_commits(limit: int = 8) -> str:
    return run_cmd(["git", "log", "--oneline", f"-{limit}"])


def git_status() -> str:
    status = run_cmd(["git", "status", "--short"])
    return status if status else "limpo"


def build_report() -> dict:
    return {
        "ok": True,
        "name": "K-Uni Master Dashboard",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "operational",
        "counts": {
            "core_modules": count_files("k_atlas/core/*"),
            "pages": count_files("pages/*.py"),
            "ops_scripts": count_files("ops/*.ps1"),
            "readmes": count_files("README*.md"),
        },
        "commands": {
            "open_kuni": 'powershell -ExecutionPolicy Bypass -File ".\\ops\\kuni.ps1"',
            "batch_factory": 'powershell -ExecutionPolicy Bypass -File ".\\ops\\k_batch_factory.ps1"',
        },
        "guardrails": [
            "execucao automatica externa bloqueada por padrao",
            "acoes sensiveis exigem aprovacao humana",
            "GitHub usado como memoria persistente",
            "Streamlit usado como cockpit operacional",
            "PowerShell/Python usados como executor local",
        ],
    }


st.set_page_config(page_title="K-Uni Master Dashboard", layout="wide")

report = build_report()

st.title("K-Uni Master Dashboard")
st.caption("Console consolidado do K-Atlas Local OS / Unicorn Factory.")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Core modules", report["counts"]["core_modules"])

with col2:
    st.metric("Pages", report["counts"]["pages"])

with col3:
    st.metric("Ops scripts", report["counts"]["ops_scripts"])

with col4:
    st.metric("Status", report["status"])

st.divider()

tab_home, tab_commands, tab_git, tab_pages, tab_report = st.tabs([
    "Home",
    "Comandos",
    "Git",
    "Páginas recentes",
    "Relatório",
])

with tab_home:
    st.subheader("Estado do K-Uni")
    st.success("K-Uni Local OS operacional.")
    st.write("Use este painel como ponto inicial para operação, navegação e validação.")
    st.json(report["guardrails"])

with tab_commands:
    st.subheader("Comandos principais")
    st.code(report["commands"]["open_kuni"], language="powershell")
    st.code(report["commands"]["batch_factory"], language="powershell")

with tab_git:
    st.subheader("Git status")
    st.code(git_status(), language="text")
    st.subheader("Últimos commits")
    st.code(latest_commits(), language="text")

with tab_pages:
    st.subheader("Páginas recentes")
    for page in latest_pages():
        st.write("- " + page)

with tab_report:
    st.json(report)

report_path = PROJECT_ROOT / "reports" / "k_uni_master" / "latest_master_dashboard.json"
report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
