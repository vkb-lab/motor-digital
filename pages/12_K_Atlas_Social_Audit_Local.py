from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.blackboard.blackboard_store import BlackboardStore
from k_atlas.social.social_audit.live_status import SocialAuditLiveStatus


MESSAGES_PATH = Path("memory/blackboard/messages.json")
COMMANDS_PATH = Path("memory/blackboard/command_queue.json")
RESULTS_PATH = Path("memory/blackboard/command_results.json")
REPORTS_ROOT = Path("reports/social_audit")


def load_json_list(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []

    if isinstance(data, list):
        return data

    return []


def list_report_dirs(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted([p for p in root.iterdir() if p.is_dir()], reverse=True)


st.set_page_config(page_title="K-Atlas Social Audit Local", layout="wide")

st.title("K-Atlas Social Audit Local")
st.caption("Auditoria visual supervisionada em rede social publica. Somente leitura. Sem publicacao.")

store = BlackboardStore(MESSAGES_PATH, COMMANDS_PATH, RESULTS_PATH)
live = SocialAuditLiveStatus()

commands = load_json_list(COMMANDS_PATH)
results = load_json_list(RESULTS_PATH)

social_commands = [
    item for item in commands
    if item.get("metadata", {}).get("kind") == "social_audit"
]

social_results = [
    item for item in results
    if item.get("result", {}).get("command", "").find("k_atlas.social.social_audit.profile_audit") >= 0
]

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Comandos social audit", len(social_commands))

with col2:
    st.metric("Resultados social audit", len(social_results))

with col3:
    st.metric("Relatorios salvos", len(list_report_dirs(REPORTS_ROOT)))

st.divider()

tab_new, tab_live, tab_queue, tab_reports = st.tabs([
    "Nova auditoria",
    "Live status",
    "Fila",
    "Relatorios",
])

with tab_new:
    st.subheader("Criar auditoria visual")

    url = st.text_input(
        "URL publica para auditar",
        value="https://www.instagram.com/openai/",
    )

    slow_mo = st.number_input("Velocidade visual (ms entre acoes)", min_value=100, max_value=2000, value=500, step=100)
    observe_seconds = st.number_input("Tempo de observacao final", min_value=1, max_value=60, value=5, step=1)

    if st.button("Enviar auditoria para fila local", type="primary"):
        command = (
            '.\\venv\\Scripts\\python.exe -m k_atlas.social.social_audit.profile_audit '
            f'--url "{url}" --output-root "reports/social_audit" --headed '
            f'--slow-mo {int(slow_mo)} --observe-seconds {int(observe_seconds)}'
        )

        item = store.queue_command(
            title="Auditoria social visual live",
            command=command,
            requested_by="streamlit_operator",
            metadata={
                "kind": "social_audit",
                "mode": "live_status",
                "target_url": url,
            },
        )

        st.success("Auditoria enviada para a fila local.")
        st.json(item)

with tab_live:
    st.subheader("Status ao vivo")

    if st.button("Atualizar status"):
        st.rerun()

    status = live.load()

    if not status:
        st.info("Nenhuma auditoria live em andamento ou registrada.")
    else:
        st.json(status)

        data = status.get("data", {})
        screenshot = data.get("screenshot") or data.get("screenshot_path")

        if screenshot and Path(screenshot).exists():
            st.image(screenshot, caption=screenshot, use_container_width=True)

    st.subheader("Eventos live recentes")

    events = live.load_events(limit=80)

    if not events:
        st.info("Nenhum evento live registrado.")
    else:
        for event in reversed(events[-40:]):
            with st.expander(f"{event.get('timestamp')} | {event.get('status')} | {event.get('step')}"):
                st.json(event)

with tab_queue:
    st.subheader("Fila de auditorias")

    rows = [
        item for item in reversed(load_json_list(COMMANDS_PATH))
        if item.get("metadata", {}).get("kind") == "social_audit"
    ]

    if not rows:
        st.info("Nenhuma auditoria social criada ainda.")
    else:
        for item in rows[:30]:
            with st.expander(f"{item.get('approval_status')} | {item.get('execution_status')} | {item.get('title')}"):
                st.code(item.get("command", ""), language="powershell")
                st.json(item)

with tab_reports:
    st.subheader("Relatorios gerados")

    dirs = list_report_dirs(REPORTS_ROOT)

    if not dirs:
        st.info("Nenhum relatorio gerado ainda.")
    else:
        for folder in dirs[:20]:
            with st.expander(folder.name):
                report_file = folder / "report.json"
                image_file = folder / "page.png"

                if report_file.exists():
                    try:
                        st.json(json.loads(report_file.read_text(encoding="utf-8")))
                    except Exception as exc:
                        st.error(f"Falha ao ler report.json: {exc}")

                if image_file.exists():
                    st.image(str(image_file), caption=str(image_file), use_container_width=True)