from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
LATEST_PACKET = ROOT / "local_runtime" / "kos_action_router" / "latest_action_packet.json"
SAFE_ACTIONS_DIR = ROOT / "local_runtime" / "kos_safe_actions"

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


def subprocess_env() -> dict:
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    return env


def run_action_router(request: str) -> dict:
    result = subprocess.run(
        ["python", "scripts\\run_phase72f_orchestrator_action_router.py", "--request", request],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=90,
        check=False,
        env=subprocess_env(),
    )

    text = (result.stdout or "").strip()
    try:
        data = json.loads(text)
    except Exception:
        data = {
            "status": "ACTION_ROUTER_OUTPUT_ERROR",
            "stdout": text[-1000:],
            "stderr": (result.stderr or "")[-1000:],
            "returncode": result.returncode,
        }

    data["returncode"] = result.returncode
    return data


def run_safe_action(packet_path: str) -> dict:
    result = subprocess.run(
        ["python", "scripts\\run_phase72g_safe_action_executor.py", "--packet-path", packet_path],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=90,
        check=False,
        env=subprocess_env(),
    )

    text = (result.stdout or "").strip()
    try:
        data = json.loads(text)
    except Exception:
        data = {
            "status": "SAFE_ACTION_OUTPUT_ERROR",
            "stdout": text[-1000:],
            "stderr": (result.stderr or "")[-1000:],
            "returncode": result.returncode,
        }

    data["returncode"] = result.returncode
    return data


def list_safe_actions(limit: int = 5) -> list[dict]:
    if not SAFE_ACTIONS_DIR.exists():
        return []

    items = []
    for path in sorted(SAFE_ACTIONS_DIR.glob("kos_safe_action_*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        data = read_json(path)
        if data.get("status") == "KOS_SAFE_ACTION_READY":
            data["_json_path"] = str(path)
            items.append(data)
        if len(items) >= limit:
            break
    return items


def show_safe_action_result(result: dict) -> None:
    if result.get("status") != "KOS_SAFE_ACTION_READY":
        st.error("A acao segura nao foi gerada.")
        st.write(result.get("status", "erro desconhecido"))
        return

    st.subheader("Resultado seguro gerado")
    st.success(result.get("summary", "Acao segura criada."))

    sections = result.get("sections", [])
    for section in sections:
        st.markdown("#### " + str(section.get("title", "Secao")))
        for item in section.get("items", []):
            st.write("- " + str(item))

    files = result.get("files", {})
    st.info("Arquivo local gerado: " + str(files.get("markdown", "nao registrado")))
    st.caption("Nada foi publicado, implantado ou aplicado automaticamente.")


def show_safe_action_history() -> None:
    actions = list_safe_actions(limit=5)

    with st.expander("Historico de acoes seguras", expanded=False):
        if not actions:
            st.write("Nenhuma acao segura gerada ainda.")
            return

        st.caption("Ultimos rascunhos gerados localmente. Sem comandos e sem JSON bruto.")

        for action in actions:
            title = action.get("title", "Acao segura")
            created_at = action.get("created_at", "")
            route_label = action.get("route_label", action.get("route", ""))
            summary = action.get("summary", "")
            files = action.get("files", {})

            with st.container(border=True):
                st.markdown("#### " + str(title))
                if summary:
                    st.write(summary)
                if route_label:
                    st.caption("Rota: " + str(route_label))
                if created_at:
                    st.caption("Criado em: " + str(created_at))
                markdown_path = str(files.get("markdown", ""))
                if markdown_path:
                    st.info("Arquivo local: " + markdown_path)

                    open_key = "open_safe_action_" + str(action.get("action_id", markdown_path))
                    if st.button("Abrir rascunho", key=open_key, use_container_width=True):
                        md_file = Path(markdown_path)
                        if md_file.exists():
                            try:
                                content = md_file.read_text(encoding="utf-8-sig")
                                st.markdown("##### Rascunho aberto")
                                st.markdown(content)
                            except Exception as exc:
                                st.error("Nao foi possivel abrir o rascunho.")
                                st.caption(str(exc))
                        else:
                            st.warning("Arquivo local nao encontrado.")

                with st.expander("Ver resumo deste rascunho"):
                    for section in action.get("sections", []):
                        st.markdown("##### " + str(section.get("title", "Secao")))
                        for item in section.get("items", []):
                            st.write("- " + str(item))



def render_hupmix_gp_lousa_preview(data=None):
    import json
    import html as _kos_html
    from pathlib import Path
    from datetime import datetime, timezone
    import streamlit as st
    import streamlit.components.v1 as components

    root = Path(__file__).resolve().parents[1]
    kit_path = root / "campaigns" / "hupmix_gp_recovery" / "GP_VIDEO_01_PRODUCTION_KIT.json"
    package_path = root / "campaigns" / "hupmix_gp_recovery" / "KOS_HUPMIX_GP_CONTINUITY_PACKAGE.json"
    decision_dir = root / "live" / "human_decision_center"
    decision_dir.mkdir(parents=True, exist_ok=True)

    request_text = ""
    try:
        request_text += " " + str(st.session_state.get("kos_operator_request_text", ""))
        request_text += " " + str(st.session_state.get("kos_last_operator_request", ""))
    except Exception:
        pass

    try:
        request_text += " " + json.dumps(data or {}, ensure_ascii=False)
    except Exception:
        request_text += " " + str(data or "")

    request_text = request_text.lower()

    should_show = (
        kit_path.exists()
        and (
            "gp_video_01" in request_text
            or "garoto oxy" in request_text
            or "roteiro cena" in request_text
            or "production kit" in request_text
            or "gravação" in request_text
            or "gravacao" in request_text
        )
    )

    if not should_show:
        return

    try:
        kit = json.loads(kit_path.read_text(encoding="utf-8"))
    except Exception as exc:
        st.warning(f"Lousa visual GP_VIDEO_01 indisponivel: {exc}")
        return

    try:
        package = json.loads(package_path.read_text(encoding="utf-8")) if package_path.exists() else {}
    except Exception:
        package = {}

    scenes = kit.get("scenes", []) or []
    checklist = kit.get("recording_checklist", []) or []
    caption = kit.get("final_caption", "")
    calendar = package.get("calendar_7_days", []) or []

    def esc(value):
        return _kos_html.escape(str(value or ""))

    scene_cards = ""
    for scene in scenes:
        scene_cards += f"""
        <div class="scene-card">
          <div class="scene-title">{esc(scene.get("scene"))}</div>
          <div class="scene-time">{esc(scene.get("duration"))}</div>
          <div class="scene-speech">"{esc(scene.get("speech"))}"</div>
          <div class="scene-take">{esc(scene.get("take"))}</div>
        </div>
        """

    html = f"""
    <style>
      .kos-wrap {{
        width: 100%;
        display: flex;
        justify-content: center;
        padding: 10px 0 25px 0;
        font-family: Arial, sans-serif;
      }}
      .phone {{
        width: 360px;
        height: 720px;
        border-radius: 38px;
        background: #111;
        padding: 14px;
        box-shadow: 0 20px 55px rgba(0,0,0,0.25);
        border: 6px solid #222;
      }}
      .screen {{
        width: 100%;
        height: 100%;
        border-radius: 28px;
        overflow: hidden;
        background: #f8fafc;
      }}
      .ig-top {{
        height: 48px;
        background: #fff;
        border-bottom: 1px solid #e5e7eb;
        display: flex;
        align-items: center;
        padding: 0 14px;
        font-weight: 700;
        font-size: 14px;
      }}
      .avatar {{
        width: 28px;
        height: 28px;
        border-radius: 50%;
        background: #16a34a;
        margin-right: 10px;
      }}
      .video-area {{
        height: 430px;
        background: linear-gradient(160deg, #0f172a 0%, #1e293b 45%, #14532d 100%);
        color: white;
        padding: 18px;
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
      }}
      .badge {{
        background: rgba(255,255,255,0.14);
        border: 1px solid rgba(255,255,255,0.28);
        padding: 6px 9px;
        border-radius: 999px;
        font-size: 12px;
        width: fit-content;
      }}
      .big-title {{
        font-size: 26px;
        font-weight: 800;
        line-height: 1.05;
        margin-top: 20px;
      }}
      .product {{
        background: rgba(255,255,255,0.16);
        border-radius: 18px;
        padding: 14px;
        margin-top: 18px;
      }}
      .price {{
        font-size: 24px;
        font-weight: 900;
        margin-top: 8px;
      }}
      .cta {{
        font-size: 13px;
        opacity: 0.95;
        margin-top: 10px;
      }}
      .bottom {{
        background: #fff;
        padding: 12px 14px;
        height: 242px;
        overflow: auto;
      }}
      .actions {{
        font-size: 20px;
        letter-spacing: 9px;
        margin-bottom: 8px;
      }}
      .caption {{
        font-size: 12px;
        line-height: 1.35;
        color: #111827;
      }}
      .scenes {{
        margin-top: 8px;
        font-size: 11px;
      }}
      .scene-card {{
        background: #f3f4f6;
        border-radius: 10px;
        padding: 8px;
        margin-top: 7px;
      }}
      .scene-title {{
        font-weight: 800;
      }}
      .scene-time {{
        color: #64748b;
        font-size: 10px;
      }}
      .scene-speech {{
        margin-top: 4px;
      }}
      .scene-take {{
        margin-top: 4px;
        color: #475569;
      }}
    </style>

    <div class="kos-wrap">
      <div class="phone">
        <div class="screen">
          <div class="ig-top">
            <div class="avatar"></div>
            @hupmix
          </div>
          <div class="video-area">
            <div>
              <div class="badge">PREVIEW REEL - GP_VIDEO_01</div>
              <div class="big-title">A solução que faltava!</div>
              <div class="product">
                <div>Oxy Power 5L</div>
                <div>Oxigênio Ativo · sem cloro · não tóxico</div>
                <div class="price">R$ 49,90</div>
                <div class="cta">Passe na HupMix ou chame no WhatsApp</div>
              </div>
            </div>
            <div class="badge">Publicação bloqueada até aprovação humana</div>
          </div>
          <div class="bottom">
            <div class="actions">♡ 💬 ↗</div>
            <div class="caption"><b>hupmix</b> {esc(caption)}</div>
            <div class="scenes">
              {scene_cards}
            </div>
          </div>
        </div>
      </div>
    </div>
    """

    st.markdown("## Lousa de aprovação visual")
    st.caption("Preview visual do GP_VIDEO_01. Isto é uma simulação para aprovação. Nada foi publicado.")

    
    preview_script = root / "scripts" / "run_kos_hupmix_gp_video_01_animatic.py"
    preview_gif = root / "local_runtime" / "kos_video_previews" / "hupmix" / "GP_VIDEO_01_PREVIEW.gif"
    preview_png = root / "local_runtime" / "kos_video_previews" / "hupmix" / "GP_VIDEO_01_STORYBOARD.png"

    try:
        if preview_script.exists():
            subprocess = __import__("subprocess")
            sysmod = __import__("sys")
            subprocess.run(
                [sysmod.executable, str(preview_script)],
                cwd=str(root),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=60,
            )

        if preview_gif.exists():
            st.markdown("### Preview animado do Reel")
            st.image(str(preview_gif), caption="Animatic visual do GP_VIDEO_01. Isto simula o vídeo para aprovação. Nada foi publicado.")
        elif preview_png.exists():
            st.markdown("### Storyboard visual")
            st.image(str(preview_png), caption="Storyboard do GP_VIDEO_01. Nada foi publicado.")
        else:
            st.info("Preview visual ainda nao foi gerado. O roteiro permanece aprovado apenas para gravacao.")
    except Exception as exc:
        st.warning(f"Preview visual nao carregou: {exc}")


    components.html(html, height=790, scrolling=False)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Programação semanal")
        if calendar:
            for item in calendar:
                st.write("- " + str(item))
        else:
            st.write("Calendário semanal ainda não encontrado.")

    with col2:
        st.markdown("### Checklist antes de gravar")
        for item in checklist:
            st.write("- " + str(item))

    c1, c2 = st.columns(2)

    if c1.button("Aprovar roteiro para gravação", key="kos_approve_gp_video_01_recording"):
        decision = {
            "status": "APPROVED_FOR_RECORDING",
            "scope": "GP_VIDEO_01",
            "brand": "Hupmix",
            "campaign": "GP / Garoto Oxy Power / Oxy Power",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "instagram_publish_executed": False,
            "approval_type": "recording_only",
            "note": "Aprovado apenas para gravacao. Publicacao real continua bloqueada."
        }
        out = decision_dir / "hupmix_gp_video_01_recording_approval.json"
        out.write_text(json.dumps(decision, ensure_ascii=False, indent=2), encoding="utf-8")
        st.success("Roteiro aprovado para gravação. Publicação real continua bloqueada.")

    if c2.button("Pedir ajuste antes de gravar", key="kos_request_gp_video_01_adjustment"):
        decision = {
            "status": "ADJUSTMENT_REQUESTED",
            "scope": "GP_VIDEO_01",
            "brand": "Hupmix",
            "campaign": "GP / Garoto Oxy Power / Oxy Power",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "instagram_publish_executed": False,
            "approval_type": "adjustment_before_recording",
            "note": "Operador pediu ajuste antes da gravacao."
        }
        out = decision_dir / "hupmix_gp_video_01_adjustment_requested.json"
        out.write_text(json.dumps(decision, ensure_ascii=False, indent=2), encoding="utf-8")
        st.warning("Pedido de ajuste registrado. Nada foi publicado.")


def show_operator_response(data: dict) -> None:
    response = data.get("operator_response", {})
    locks = data.get("locks", {})
    packet_path = data.get("packet_path", "")

    st.subheader("Resposta do K-OS")

    st.markdown("### Entendi")
    st.write(response.get("entendi", "Pedido recebido pelo K-OS."))

    st.markdown("### Vou usar estes modulos")
    modules = response.get("vou_usar_estes_modulos", [])
    if modules:
        for module in modules:
            st.write("- " + str(module))
    else:
        st.write("- K-OS Orchestrator")

    st.markdown("### Proximo passo")
    st.success(response.get("proximo_passo", "Revisar o plano antes de executar."))

    st.markdown("### Risco / bloqueio")
    st.warning(response.get("risco_bloqueio", "Acoes reais exigem gate humano."))

    st.markdown("### Acao segura disponivel")
    st.info(response.get("acao_segura_disponivel", "Gerar plano em rascunho."))

    if packet_path:
        button_key = "safe_action_" + str(data.get("packet_id", "latest"))
        if st.button("Gerar acao segura agora", type="primary", use_container_width=True, key=button_key):
            with st.spinner("Gerando rascunho seguro..."):
                safe_result = run_safe_action(packet_path)
            st.session_state["kos_last_safe_action_result"] = safe_result
            st.session_state["kos_last_safe_action_packet_path"] = str(packet_path)
        
        last_safe_result = st.session_state.get("kos_last_safe_action_result")
        if last_safe_result:
            st.markdown("### Rascunho gerado")
            show_safe_action_result(last_safe_result)

    st.caption(
        "Guardrails ativos: sem publicacao automatica, sem patch automatico, sem IA paga, sem scraping, Parada Atlantida bloqueada."
    )

    with st.expander("Registro tecnico seguro"):
        st.write("Rota interna:", data.get("route_label", data.get("route", "geral")))
        st.write("Action Packet:", data.get("packet_id", "sem id"))
        st.write("Arquivo local:", data.get("packet_path", "nao registrado"))

        active_blocks = []
        if locks.get("auto_publish_enabled") is False:
            active_blocks.append("publicacao automatica bloqueada")
        if locks.get("auto_execution_enabled") is False:
            active_blocks.append("execucao automatica perigosa bloqueada")
        if locks.get("paid_ai_enabled") is False:
            active_blocks.append("IA paga bloqueada")
        if locks.get("parada_atlantida_locked") is True:
            active_blocks.append("Parada Atlantida bloqueada")
        if locks.get("browser_logged_automation_blocked") is True:
            active_blocks.append("automacao de navegador logado bloqueada")
        if locks.get("human_gate_required") is True:
            active_blocks.append("gate humano obrigatorio")

        if active_blocks:
            st.write("Bloqueios ativos:")
            for item in active_blocks:
                st.write("- " + item)

        st.info(
            "Comandos internos e JSON bruto foram ocultados para evitar execucao acidental no PowerShell."
        )
        st.caption(
            "Para executar algo, faca um novo pedido ao K-OS. Acoes reais continuam exigindo confirmacao humana."
        )


st.title("K-OS Operator Chat")
st.caption("Uma caixa. Um pedido. O K-OS escolhe a rota e mantem acoes reais gateadas.")
st.info("Use esta tela como entrada principal. Nao cole a resposta do K-OS no PowerShell.")

if "kos_operator_request_text" not in st.session_state:
    st.session_state["kos_operator_request_text"] = ""

request = st.text_area(
    "Pedido ao K-OS",
    placeholder="Exemplo: Criar uma campanha Hupmix para 7 dias sem publicar automaticamente",
    height=140,
    key="kos_operator_request_text",
)

col1, col2 = st.columns([2, 1])

with col1:
    send = st.button("Enviar pedido ao K-OS", type="primary", use_container_width=True)

with col2:
    advanced = st.button("Modo avancado", use_container_width=True)

if advanced:
    st.info(
        "Modo avancado nao abre cockpits automaticamente. Para evitar erro humano, comandos tecnicos continuam ocultos."
    )
    st.write("Peca ao K-OS a acao desejada em linguagem normal.")

if send:
    st.session_state.pop("kos_last_safe_action_result", None)
    st.session_state.pop("kos_last_safe_action_packet_path", None)
    clean_request = st.session_state.get("kos_operator_request_text", "").strip()
    if not clean_request:
        st.error("Escreva um pedido simples para o K-OS.")
    else:
        with st.spinner("K-OS entendendo o pedido e montando Action Packet seguro..."):
            data = run_action_router(clean_request)
        st.session_state["kos_last_operator_data"] = data
        st.session_state["kos_last_operator_request"] = clean_request

last_operator_data = st.session_state.get("kos_last_operator_data")

if last_operator_data and last_operator_data.get("status") == "KOS_ACTION_PACKET_READY":
    show_operator_response(last_operator_data)
else:
    st.markdown("### Comece por aqui")
    st.write("Digite um pedido ao K-OS na caixa acima. O K-OS escolhe a rota e mostra a proxima acao segura.")

    col_home_1, col_home_2 = st.columns(2)

    with col_home_1:
        show_last = st.button("Ver ultimo pedido", use_container_width=True)

    with col_home_2:
        show_history = st.button("Ver historico seguro", use_container_width=True)

    if show_last:
        latest = read_json(LATEST_PACKET)
        if latest.get("status") == "KOS_ACTION_PACKET_READY":
            st.session_state["kos_last_operator_data"] = latest
            show_operator_response(latest)
        else:
            st.info("Nenhum pedido anterior encontrado.")

    if show_history:
        show_safe_action_history()
    else:
        st.caption("Ultimo pedido e historico ficam ocultos por padrao para manter a tela limpa.")


# K-OS visual approval board render hook
try:
    import json as _kos_json
    _kos_lousa_payload = st.session_state.get("kos_last_operator_data") or st.session_state.get("kos_last_safe_action_result") or {}
    _kos_lousa_request = str(st.session_state.get("kos_operator_request_text", "")) + " " + str(st.session_state.get("kos_last_operator_request", ""))
    _kos_lousa_probe = (_kos_lousa_request + " " + _kos_json.dumps(_kos_lousa_payload, ensure_ascii=False)).lower()
    if "gp_video_01" in _kos_lousa_probe or "garoto oxy" in _kos_lousa_probe or "roteiro cena" in _kos_lousa_probe or "gravacao" in _kos_lousa_probe or "gravação" in _kos_lousa_probe:
        render_hupmix_gp_lousa_preview(_kos_lousa_payload)
except Exception as _kos_lousa_exc:
    st.warning(f"Lousa visual GP_VIDEO_01 nao carregou: {_kos_lousa_exc}")

