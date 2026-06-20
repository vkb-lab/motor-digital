from __future__ import annotations

import json
import subprocess
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "local_runtime" / "kos_unified_cockpit" / "latest_inventory.json"


def read_json(path: Path) -> dict:
    if not path.exists():
        return {"status": "MISSING", "path": str(path)}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        return {"status": "READ_ERROR", "path": str(path), "error": str(exc)}


def run_status(command: list[str]) -> dict:
    try:
        result = subprocess.run(
            command,
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=12,
            check=False,
        )
        text = result.stdout.strip()
        try:
            parsed = json.loads(text)
        except Exception:
            parsed = {"stdout": text[-4000:], "stderr": result.stderr[-2000:]}
        parsed["returncode"] = result.returncode
        return parsed
    except Exception as exc:
        return {"status": "STATUS_ERROR", "error": str(exc)}


def code_cmd(cmd: str):
    st.code(cmd, language="powershell")


def section_files(title: str, files: list[str], limit: int = 60):
    st.subheader(title)
    if not files:
        st.info("Nenhum item encontrado.")
        return
    for item in files[:limit]:
        st.write("- " + item)
    if len(files) > limit:
        st.caption(f"Mostrando {limit} de {len(files)} itens.")


st.set_page_config(page_title="K-OS Unified Cockpit", layout="wide")

st.title("K-OS Unified Command Cockpit")
st.caption("Cockpit principal do K-OS: agentes, orquestrador, SaaS, redes, auditoria, runtime e comandos seguros.")

inventory = read_json(INVENTORY)
if inventory.get("status") == "MISSING":
    st.warning("Inventario ainda nao gerado. Rode o comando abaixo.")
    code_cmd("python scripts\\run_phase72b_unified_command_cockpit_inventory.py")
    st.stop()

safe = inventory.get("safe_flags", {})
counts = inventory.get("counts", {})
categories = inventory.get("categories", {})

c1, c2, c3, c4 = st.columns(4)
c1.metric("Inventario", inventory.get("status", "n/d"))
c2.metric("Arquivos indexados", inventory.get("total_files_indexed", 0))
c3.metric("Conta teste", "Hupmix")
c4.metric("Parada Atlantida", "bloqueada")

st.success("Sistema centralizado. Este cockpit nao publica, nao aplica patch e nao executa acao perigosa automaticamente.")

tabs = st.tabs([
    "Home",
    "Runtime e Agentes",
    "Orquestrador",
    "SaaS e Produtos",
    "Redes e Publicacoes",
    "Ponte ChatGPT",
    "Patches",
    "Comandos",
    "Inventario",
])

with tabs[0]:
    st.subheader("Mapa operacional")
    st.json({
        "runtime": counts.get("runtime", 0),
        "agents": counts.get("agents", 0),
        "bridge": counts.get("bridge", 0),
        "products_saas": counts.get("products_saas", 0),
        "social_publish": counts.get("social_publish", 0),
        "patches": counts.get("patches", 0),
        "dashboards": counts.get("dashboards", 0),
    })

    st.subheader("Abertura rapida")
    code_cmd("C:\\Users\\oi\\Desktop\\KOS_Weekly_Operator_Workspace.cmd")
    code_cmd("C:\\Users\\oi\\Desktop\\KOS_Social_Ops_Control_Center.cmd")
    code_cmd("C:\\Users\\oi\\Desktop\\KOS_ChatGPT_Bridge_Status.cmd")

with tabs[1]:
    st.subheader("Status do runtime")
    if (ROOT / "scripts/kos_runtime_control.ps1").exists():
        st.json(run_status(["powershell", "-ExecutionPolicy", "Bypass", "-File", "scripts\\kos_runtime_control.ps1", "-Action", "status"]))
    else:
        st.warning("Runtime control nao encontrado.")

    section_files("Agentes, autonomia e runtime", categories.get("agents", []) + categories.get("runtime", []))

with tabs[2]:
    st.subheader("Orquestrador e filas")
    st.caption("Missões, filas, handoff, approvals, command bridge e scheduler.")
    section_files("Componentes de orquestracao", categories.get("agents", []) + categories.get("bridge", []))
    code_cmd("powershell -ExecutionPolicy Bypass -File scripts\\kos_runtime_control.ps1 -Action status")

with tabs[3]:
    st.subheader("Projetos SaaS e produtos")
    st.caption("Product factory, registry, scaffold, QA, export e runner gates.")
    section_files("Componentes SaaS/produtos", categories.get("products_saas", []))
    st.info("Use esta area para escolher um produto e transformar em MVP pequeno antes de expandir.")

with tabs[4]:
    st.subheader("Redes sociais, auditoria e publicacao")
    st.caption("Reutiliza o caminho existente 69D-69H. Nao cria novo publicador.")
    section_files("Social e publicacao", categories.get("social_publish", []))

    st.subheader("Comandos seguros")
    code_cmd("python scripts\\run_phase71b_social_strategy_generator.py --target hupmix --objective \"estrategia semanal Hupmix\" --campaign hupmix-weekly")
    code_cmd("python scripts\\run_phase71c_social_publish_readiness_auditor.py --target hupmix --asset-url https://example.com/imagem.png --caption \"legenda de teste sem publicar\"")

    st.warning("Publicacao real exige caminho 69F + 69G + 69H, confirmacao humana e imagem HTTPS publica.")

with tabs[5]:
    st.subheader("Ponte ChatGPT local")
    if (ROOT / "scripts/kos_chatgpt_bridge_runtime_control.ps1").exists():
        st.json(run_status(["powershell", "-ExecutionPolicy", "Bypass", "-File", "scripts\\kos_chatgpt_bridge_runtime_control.ps1", "-Action", "status"]))
    else:
        st.warning("Runtime controller da ponte nao encontrado.")

    code_cmd("powershell -ExecutionPolicy Bypass -File scripts\\kos_chatgpt_bridge_runtime_control.ps1 -Action start")
    code_cmd("powershell -ExecutionPolicy Bypass -File scripts\\kos_chatgpt_bridge_runtime_control.ps1 -Action status")
    code_cmd("powershell -ExecutionPolicy Bypass -File scripts\\kos_chatgpt_bridge_runtime_control.ps1 -Action stop")

with tabs[6]:
    st.subheader("Patch proposer e review")
    section_files("Patches", categories.get("patches", []))
    code_cmd("python scripts\\run_phase70a_safe_patch_proposer.py --objective \"melhoria pequena\" --files README.md")
    code_cmd("C:\\Users\\oi\\Desktop\\KOS_Safe_Patch_Review_Panel.cmd")
    st.warning("Patch automatico continua bloqueado. Aplicacao real exige gate futuro.")

with tabs[7]:
    st.subheader("Comandos principais")
    commands = [
        ("Git status", "git --no-pager status --short"),
        ("Runtime status", "powershell -ExecutionPolicy Bypass -File scripts\\kos_runtime_control.ps1 -Action status"),
        ("Social Ops", "C:\\Users\\oi\\Desktop\\KOS_Social_Ops_Control_Center.cmd"),
        ("Weekly Workspace", "C:\\Users\\oi\\Desktop\\KOS_Weekly_Operator_Workspace.cmd"),
        ("ChatGPT Bridge status", "powershell -ExecutionPolicy Bypass -File scripts\\kos_chatgpt_bridge_runtime_control.ps1 -Action status"),
        ("Gerar estrategia Hupmix", "python scripts\\run_phase71b_social_strategy_generator.py --target hupmix --objective \"estrategia semanal Hupmix\" --campaign hupmix-weekly"),
        ("Readiness Hupmix", "python scripts\\run_phase71c_social_publish_readiness_auditor.py --target hupmix --asset-url https://example.com/imagem.png --caption \"legenda de teste sem publicar\""),
    ]
    for label, cmd in commands:
        st.caption(label)
        code_cmd(cmd)

with tabs[8]:
    st.subheader("Inventario completo")
    st.json(inventory)
    st.subheader("Guardrails")
    st.json(safe)
