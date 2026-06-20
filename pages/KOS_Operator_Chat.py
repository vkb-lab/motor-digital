from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
LATEST_PACKET = ROOT / "local_runtime" / "kos_action_router" / "latest_action_packet.json"


st.set_page_config(
    page_title="K-OS Operator Chat",
    page_icon="K",
    layout="centered",
    initial_sidebar_state="collapsed",
)


def read_json(path: Path) -> dict:
    if not path.exists():
        return {"status": "MISSING", "path": str(path)}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        return {"status": "READ_ERROR", "error": str(exc), "path": str(path)}


def run_action_router(request: str) -> dict:
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"

    result = subprocess.run(
        ["python", "scripts\\run_phase72f_orchestrator_action_router.py", "--request", request],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=90,
        check=False,
        env=env,
    )

    text = (result.stdout or "").strip()
    try:
        data = json.loads(text)
    except Exception:
        data = {
            "status": "ACTION_ROUTER_OUTPUT_ERROR",
            "stdout": text[-4000:],
            "stderr": (result.stderr or "")[-4000:],
            "returncode": result.returncode,
        }

    data["returncode"] = result.returncode
    return data


def show_operator_response(data: dict) -> None:
    response = data.get("operator_response", {})
    locks = data.get("locks", {})
    action_packet = data.get("action_packet", {})

    st.subheader("Resposta do K-OS")

    st.markdown("### Entendi")
    st.write(response.get("entendi", "Pedido recebido pelo K-OS."))

    st.markdown("### Vou usar estes módulos")
    modules = response.get("vou_usar_estes_modulos", [])
    if modules:
        for module in modules:
            st.write("- " + str(module))
    else:
        st.write("K-OS Orchestrator")

    st.markdown("### Próximo passo")
    st.success(response.get("proximo_passo", "Revisar o plano antes de executar."))

    st.markdown("### Risco / bloqueio")
    st.warning(response.get("risco_bloqueio", "Ações reais exigem gate humano."))

    st.markdown("### Ação segura disponível")
    st.info(response.get("acao_segura_disponivel", "Gerar plano em rascunho."))

    st.caption(
        "Guardrails ativos: sem publicação automática, sem patch automático, sem IA paga, sem scraping, Parada Atlântida bloqueada."
    )

    with st.expander("Detalhes técnicos"):
        st.write("Rota interna:", data.get("route_label", data.get("route", "geral")))
        st.write("Action Packet:", data.get("packet_id", "sem id"))
        st.write("Arquivo:", data.get("packet_path", "nao registrado"))
        st.write("Bloqueios:", locks)
        st.write("Comandos internos ocultos:")
        commands = action_packet.get("internal_commands_hidden_by_default", [])
        if commands:
            for command in commands:
                st.code(command, language="powershell")
        else:
            st.write("Nenhum comando interno sugerido.")
        st.json(data)


st.title("K-OS Operator Chat")
st.caption("Uma caixa. Um pedido. O K-OS escolhe a rota e mantém ações reais gateadas.")

request = st.text_area(
    "Pedido ao K-OS",
    placeholder="Exemplo: Criar uma campanha Hupmix para 7 dias sem publicar automaticamente",
    height=140,
)

col1, col2 = st.columns([2, 1])

with col1:
    send = st.button("Enviar pedido ao K-OS", type="primary", use_container_width=True)

with col2:
    advanced = st.button("Modo avançado", use_container_width=True)

if advanced:
    st.info("Modo avançado permanece manual. O K-OS não abre cockpits técnicos automaticamente.")
    st.write("Use o modo avançado só quando precisar revisar módulos específicos.")

if send:
    clean_request = request.strip()
    if not clean_request:
        st.error("Escreva um pedido simples para o K-OS.")
    else:
        with st.spinner("K-OS entendendo o pedido e montando Action Packet seguro..."):
            data = run_action_router(clean_request)
        show_operator_response(data)
else:
    latest = read_json(LATEST_PACKET)
    if latest.get("status") == "KOS_ACTION_PACKET_READY":
        with st.expander("Último pedido processado"):
            show_operator_response(latest)