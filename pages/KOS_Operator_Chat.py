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
    from pathlib import Path
    from datetime import datetime, timezone
    import streamlit as st

    root = Path(__file__).resolve().parents[1]
    kit_path = root / "campaigns" / "hupmix_gp_recovery" / "GP_VIDEO_01_PRODUCTION_KIT.json"
    package_path = root / "campaigns" / "hupmix_gp_recovery" / "KOS_HUPMIX_GP_CONTINUITY_PACKAGE.json"
    preview_script = root / "scripts" / "run_kos_hupmix_gp_video_01_mp4_preview.py"
    preview_mp4 = root / "local_runtime" / "kos_video_previews" / "hupmix" / "GP_VIDEO_01_PREVIEW.mp4"
    decision_dir = root / "live" / "human_decision_center"
    decision_dir.mkdir(parents=True, exist_ok=True)

    if not kit_path.exists():
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
                timeout=120,
            )
    except Exception as exc:
        st.warning(f"Geracao do preview MP4 falhou: {exc}")

    checklist = kit.get("recording_checklist", []) or []
    calendar = package.get("calendar_7_days", []) or []

    st.markdown("## Lousa de aprovação visual")
    st.caption("Preview vertical do GP_VIDEO_01 gerado pelo K-OS. Isto é simulação para aprovação. Nada foi publicado.")

    st.markdown("### Vídeo preview MP4")

    if preview_mp4.exists():
        left, center, right = st.columns([1, 1.15, 1])
        with center:
            st.video(str(preview_mp4), format="video/mp4")
            st.caption("MP4 vertical de preview. Publicação real continua bloqueada.")
    else:
        st.warning("Preview MP4 ainda não encontrado.")

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

    if c1.button("Aprovar roteiro para gravação", key="kos_approve_gp_video_01_recording_v2"):
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

    if c2.button("Pedir ajuste antes de gravar", key="kos_request_gp_video_01_adjustment_v2"):
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


# KOS_READ_ONLY_DIAGNOSTIC_COMMANDS_BEGIN
def is_kos_read_only_diagnostic_request(text: str) -> bool:
    """Detecta comandos locais de diagnostico que nao devem acionar Router nem Safe Action."""
    import unicodedata

    value = str(text or "").strip().lower()
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))

    patterns = [
        "k-os diagnostic",
        "kos diagnostic",
        "operator flow",
        "diagnostico do fluxo",
        "diagnostico operator",
        "mostrar diagnostico",
        "painel de diagnostico",
        "diagnostico do operator",
        "diagnostico do operador",
    ]

    return any(pattern in value for pattern in patterns)
# KOS_READ_ONLY_DIAGNOSTIC_COMMANDS_END



# KOS_READ_ONLY_LOUSA_COMMANDS_BEGIN
def is_kos_read_only_lousa_request(text: str) -> bool:
    """Detecta comandos locais de lousa visual que nao devem acionar Router nem Safe Action."""
    import unicodedata

    value = str(text or "").strip().lower()
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))

    action_terms = [
        "mostrar lousa",
        "abrir lousa",
        "ver lousa",
        "visualizar video",
        "mostrar video",
        "ver video",
        "preview mp4",
        "mostrar preview",
    ]

    target_terms = [
        "gp_video_01",
        "gp video 01",
        "gp_video",
        "garoto oxy",
        "hupmix",
    ]

    return any(a in value for a in action_terms) and any(t in value for t in target_terms)
# KOS_READ_ONLY_LOUSA_COMMANDS_END


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

# KOS_READ_ONLY_DIAGNOSTIC_GATE_BEGIN
if send and is_kos_read_only_diagnostic_request(st.session_state.get("kos_operator_request_text", "")):
    st.session_state["kos_show_operator_flow_diagnostic"] = True
    st.session_state["kos_last_operator_request"] = st.session_state.get("kos_operator_request_text", "").strip()
    st.session_state["kos_diagnostic_read_only_message"] = "Diagnostico aberto em modo read-only. Nenhum Router, Safe Action, publicacao, deploy ou IA paga foi acionado."
    st.session_state["kos_last_operator_data"] = None
    st.session_state.pop("kos_last_safe_action_result", None)
    st.session_state.pop("kos_last_safe_action_packet_path", None)
    send = False
# KOS_READ_ONLY_DIAGNOSTIC_GATE_END

# KOS_READ_ONLY_LOUSA_GATE_BEGIN
if send and is_kos_read_only_lousa_request(st.session_state.get("kos_operator_request_text", "")):
    st.session_state["kos_show_gp_video_01_lousa"] = True
    st.session_state["kos_last_operator_request"] = st.session_state.get("kos_operator_request_text", "").strip()
    st.session_state["kos_lousa_read_only_message"] = "Lousa visual aberta em modo read-only. Nenhum Router, Safe Action, publicacao, deploy ou IA paga foi acionado."
    st.session_state["kos_last_operator_data"] = None
    st.session_state.pop("kos_last_safe_action_result", None)
    st.session_state.pop("kos_last_safe_action_packet_path", None)
    send = False
# KOS_READ_ONLY_LOUSA_GATE_END

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


# K-OS visual approval board persistent render hook
try:
    import json as _kos_json
    from pathlib import Path as _KosPath

    _kos_root = _KosPath(__file__).resolve().parents[1]
    _kos_gp_kit = _kos_root / "campaigns" / "hupmix_gp_recovery" / "GP_VIDEO_01_PRODUCTION_KIT.json"
    _kos_safe_dir = _kos_root / "local_runtime" / "kos_safe_actions"

    _kos_lousa_payload = st.session_state.get("kos_last_operator_data") or st.session_state.get("kos_last_safe_action_result") or {}
    _kos_lousa_request = str(st.session_state.get("kos_operator_request_text", "")) + " " + str(st.session_state.get("kos_last_operator_request", ""))

    _kos_latest_text = ""
    if _kos_safe_dir.exists():
        _kos_files = sorted(_kos_safe_dir.glob("kos_safe_action_*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
        if _kos_files:
            try:
                _kos_latest_text = _kos_files[0].read_text(encoding="utf-8", errors="replace")
            except Exception:
                _kos_latest_text = ""

    _kos_probe = (
        _kos_lousa_request
        + " "
        + _kos_json.dumps(_kos_lousa_payload, ensure_ascii=False, default=str)
        + " "
        + _kos_latest_text
    ).lower()

    _kos_should_show_lousa = (
        _kos_gp_kit.exists()
        and (
            "gp_video_01" in _kos_probe
            or "garoto oxy" in _kos_probe
            or "roteiro final de grava" in _kos_probe
            or "o heroi da limpeza chegou" in _kos_probe
            or "oxy power" in _kos_probe
        )
    )

    if _kos_should_show_lousa:
        render_hupmix_gp_lousa_preview(_kos_lousa_payload)

except Exception as _kos_lousa_exc:
    st.warning(f"Lousa visual GP_VIDEO_01 nao carregou: {_kos_lousa_exc}")


# KOS_OPERATOR_FLOW_DIAGNOSTIC_PANEL_BEGIN
def render_kos_operator_flow_diagnostic_panel():
    """Painel compacto de diagnostico do fluxo operador.
    Le apenas reports locais. Nao executa acao externa.
    """
    import json
    from pathlib import Path
    import streamlit as st

    root = Path.cwd()
    audit_path = root / "reports" / "KOS_OPERATOR_FLOW_AUDIT.json"
    digest_path = root / "reports" / "KOS_CODEBASE_STATIC_MAP_DIGEST.json"

    with st.expander("K-OS Diagnostic: Operator Flow", expanded=bool(st.session_state.get("kos_show_operator_flow_diagnostic", False))):
        st.caption("Leitura local. Sem IA, sem API, sem publicacao, sem deploy.")
        read_only_msg = st.session_state.get("kos_diagnostic_read_only_message")
        if read_only_msg:
            st.success(read_only_msg)

        if not audit_path.exists():
            st.warning("Relatorio Operator Flow ainda nao encontrado.")
            return

        try:
            audit = json.loads(audit_path.read_text(encoding="utf-8"))
        except Exception as exc:
            st.error(f"Falha ao ler Operator Flow Audit: {exc}")
            return

        summary = audit.get("summary", {})
        core_files = audit.get("core_flow_files", [])

        col1, col2, col3 = st.columns(3)
        col1.metric("Arquivos candidatos", summary.get("candidate_python_files", 0))
        col2.metric("Arquivos interessantes", summary.get("interesting_python_files", 0))
        col3.metric("Arquivos core", summary.get("core_files", 0))

        col4, col5, col6 = st.columns(3)
        col4.metric("Subprocess/browser", summary.get("files_with_subprocess_or_browser", 0))
        col5.metric("UI Streamlit", summary.get("files_with_ui_lines", 0))
        col6.metric("Runtime/reports", summary.get("files_with_runtime_or_reports", 0))

        st.markdown("### Top arquivos do fluxo")
        rows = []
        for item in core_files[:10]:
            rows.append({
                "arquivo": item.get("path", ""),
                "score": item.get("score", 0),
                "linhas": item.get("lines", 0),
                "riscos": ", ".join(item.get("risk_hits", [])[:8]),
                "ui_hits": len(item.get("ui_lines", [])),
                "subprocess_hits": len(item.get("subprocess_lines", [])),
                "runtime_hits": len(item.get("writes_runtime_or_reports", [])),
            })

        if rows:
            st.dataframe(rows, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum arquivo core encontrado no relatorio.")

        if digest_path.exists():
            try:
                digest = json.loads(digest_path.read_text(encoding="utf-8"))
                risks = digest.get("top_risk_keywords", [])[:10]
                if risks:
                    st.markdown("### Top riscos gerais")
                    st.dataframe(
                        [{"risco": r[0], "ocorrencias": r[1]} for r in risks],
                        use_container_width=True,
                        hide_index=True,
                    )
            except Exception as exc:
                st.warning(f"Digest encontrado, mas nao foi possivel ler: {exc}")

        st.info("Proximo alvo recomendado: separar UI, Router e Safe Action Executor em diagnostico permanente.")

try:
    render_kos_operator_flow_diagnostic_panel()
except Exception as exc:
    try:
        import streamlit as st
        st.warning(f"K-OS Diagnostic Panel indisponivel: {exc}")
    except Exception:
        pass
# KOS_OPERATOR_FLOW_DIAGNOSTIC_PANEL_END



# KOS_GP_VIDEO_01_LOUSA_READ_ONLY_RENDER_BEGIN
def render_kos_gp_video_01_lousa_read_only():
    """Renderiza a lousa visual do GP_VIDEO_01 usando MP4 local."""
    import json
    from pathlib import Path
    import streamlit as st

    if not st.session_state.get("kos_show_gp_video_01_lousa", False):
        return

    root = Path.cwd()
    mp4_path = root / "local_runtime" / "kos_video_previews" / "hupmix" / "GP_VIDEO_01_PREVIEW.mp4"
    storyboard_path = root / "local_runtime" / "kos_video_previews" / "hupmix" / "GP_VIDEO_01_STORYBOARD.png"
    job_path = root / "campaigns" / "hupmix_gp_recovery" / "GP_VIDEO_01_VIDEO_FACTORY_FREE_MODE_JOB.json"
    report_path = root / "reports" / "KOS_HUPMIX_GP_VIDEO_FACTORY_FREE_MODE_V1.json"

    st.markdown("## Lousa visual — GP_VIDEO_01 Hupmix")

    msg = st.session_state.get("kos_lousa_read_only_message")
    if msg:
        st.success(msg)

    st.caption("Preview local. Sem IA paga. Sem publicacao. Sem deploy. Gate humano obrigatorio.")

    st.markdown("### Preview MP4")
    if mp4_path.exists():
        st.video(str(mp4_path))
        st.caption("Fonte: local_runtime/kos_video_previews/hupmix/GP_VIDEO_01_PREVIEW.mp4")
    else:
        st.error("MP4 local nao encontrado. Rode o Video Factory Free Mode novamente.")

    c1, c2, c3 = st.columns(3)
    c1.metric("Modo", "Free/local")
    c2.metric("Publicacao", "Bloqueada")
    c3.metric("IA paga", "Nao usada")

    if storyboard_path.exists():
        with st.expander("Storyboard", expanded=False):
            st.image(str(storyboard_path), use_container_width=True)

    if report_path.exists():
        try:
            report = json.loads(report_path.read_text(encoding="utf-8"))
            outputs = report.get("outputs", {})
            with st.expander("Registro tecnico do video", expanded=False):
                st.json({
                    "status": report.get("status"),
                    "mp4": outputs.get("mp4"),
                    "mp4_size": outputs.get("mp4_size"),
                    "storyboard": outputs.get("storyboard"),
                    "storyboard_size": outputs.get("storyboard_size"),
                    "policy": report.get("policy"),
                })
        except Exception as exc:
            st.warning(f"Nao foi possivel ler o relatorio do video: {exc}")

    if job_path.exists():
        try:
            job = json.loads(job_path.read_text(encoding="utf-8"))
            scenes = job.get("scenes", [])
            with st.expander("Cenas do GP_VIDEO_01", expanded=False):
                for idx, scene in enumerate(scenes, start=1):
                    st.markdown(f"**Cena {idx}: {scene.get('title', '')}**")
                    st.write(scene.get("line", ""))
        except Exception as exc:
            st.warning(f"Nao foi possivel ler o job do video: {exc}")

try:
    render_kos_gp_video_01_lousa_read_only()
except Exception as exc:
    try:
        import streamlit as st
        st.warning(f"Lousa visual GP_VIDEO_01 indisponivel: {exc}")
    except Exception:
        pass
# KOS_GP_VIDEO_01_LOUSA_READ_ONLY_RENDER_END
