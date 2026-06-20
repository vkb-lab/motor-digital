from __future__ import annotations

import json
import subprocess
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
LATEST = ROOT / "local_runtime" / "kos_orchestrator_request_box" / "latest_orchestrator_response.json"


def read_json(path: Path) -> dict:
    if not path.exists():
        return {"status": "MISSING", "path": str(path)}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        return {"status": "READ_ERROR", "error": str(exc), "path": str(path)}


def run_orchestrator(request: str) -> dict:
    result = subprocess.run(
        ["python", "scripts\\run_phase72c_orchestrator_request_box.py", "--request", request],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
        check=False,
    )

    text = result.stdout.strip()
    try:
        data = json.loads(text)
    except Exception:
        data = {
            "status": "ORCHESTRATOR_OUTPUT_ERROR",
            "stdout": text[-4000:],
            "stderr": result.stderr[-4000:],
            "returncode": result.returncode,
        }

    data["returncode"] = result.returncode
    return data


def route_label(route: str) -> str:
    labels = {
        "social_publish": "Redes sociais / Hupmix / campanhas",
        "products_saas": "Produto SaaS / MVP / landing",
        "agents_orchestration": "Agentes / orquestrador / missões",
        "patches": "Código / correções / melhorias",
        "runtime_bridge": "Runtime / ponte ChatGPT / logs",
        "admin": "Administração / rotina / organização",
        "general": "Geral",
    }
    return labels.get(route, route or "Geral")


def simple_answer(data: dict) -> dict:
    plan = data.get("plan", {})
    decision = data.get("decision", {})

    return {
        "status": data.get("status"),
        "rota": route_label(data.get("route", "")),
        "entendimento": plan.get("summary", "Pedido recebido pelo K-OS."),
        "proximo_passo": decision.get("next_step", "Revisar o plano antes de executar."),
        "modulos_que_o_kos_vai_usar": plan.get("recommended_modules", []),
        "bloqueios_ativos": {
            "publicacao_automatica": data.get("auto_publish_enabled") is False,
            "execucao_automatica_perigosa": data.get("auto_execution_enabled") is False,
            "parada_atlantida": "bloqueada" if data.get("parada_atlantida_locked") else "verificar",
            "ia_paga": "bloqueada" if data.get("paid_ai_locked") else "verificar",
        },
    }


st.set_page_config(page_title="K-OS Operator Chat", layout="centered")

st.title("K-OS Operator Chat")
st.caption("Escreva o que você quer fazer. O K-OS decide a rota e usa os módulos certos.")

st.info("Use linguagem normal. Você não precisa procurar funcionalidades.")

examples = [
    "Criar uma campanha Hupmix para 7 dias sem publicar automaticamente",
    "Criar um projeto SaaS simples para testar esta semana",
    "Verificar status dos agentes e do runtime",
    "Preparar readiness de publicação Hupmix com imagem HTTPS e legenda",
    "Propor uma melhoria no código sem aplicar automaticamente",
]

with st.expander("Exemplos de pedidos"):
    for item in examples:
        st.write("- " + item)

request = st.text_area(
    "Pedido ao K-OS",
    placeholder="Exemplo: criar uma campanha Hupmix para 7 dias sem publicar automaticamente",
    height=160,
)

col1, col2 = st.columns(2)

if col1.button("Pedir ao Orquestrador", type="primary"):
    if not request.strip():
        st.warning("Escreva um pedido primeiro.")
    else:
        with st.spinner("K-OS analisando o pedido..."):
            data = run_orchestrator(request.strip())
        answer = simple_answer(data)

        st.success("Pedido analisado.")
        st.subheader("Resposta do K-OS")
        st.json(answer)

        commands = data.get("plan", {}).get("safe_commands", [])
        if commands:
            with st.expander("Comandos seguros sugeridos"):
                for cmd in commands:
                    st.code(cmd, language="powershell")

        with st.expander("Detalhes técnicos"):
            st.json(data)

if col2.button("Ver última resposta"):
    data = read_json(LATEST)
    if data.get("status") == "MISSING":
        st.warning("Ainda não existe resposta do orquestrador.")
    else:
        st.subheader("Última resposta")
        st.json(simple_answer(data))
        with st.expander("Detalhes técnicos"):
            st.json(data)

st.divider()
st.caption("Guardrails ativos: sem publicação automática, sem patch automático, sem IA paga, sem scraping, Parada Atlântida bloqueada.")
