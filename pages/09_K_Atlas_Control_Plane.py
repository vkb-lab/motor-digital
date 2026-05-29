from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.control_plane.agent_registry import build_default_agent_registry
from k_atlas.core.control_plane.event_bus import EventBus
from k_atlas.core.control_plane.health_check import run_control_plane_health_check
from k_atlas.core.control_plane.supervisor_queue import SupervisorQueue
from k_atlas.core.control_plane.task_router import TaskRouter


EVENTS_PATH = Path("memory/control_plane/events.jsonl")
SUPERVISOR_QUEUE_PATH = Path("memory/control_plane/supervisor_queue.json")
SYSTEM_STATE_PATH = Path("memory/control_plane/system_state.json")


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def load_jsonl(path: Path, limit: int = 80) -> list[dict[str, Any]]:
    if not path.exists():
        return []

    rows: list[dict[str, Any]] = []

    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue

    return rows[-limit:]


st.set_page_config(
    page_title="K-Atlas Control Plane",
    layout="wide",
)

st.title("K-Atlas Control Plane")
st.caption("Centro operacional do K-Atlas OS: agentes, tarefas, permissoes, supervisao e eventos.")

registry = build_default_agent_registry()
event_bus = EventBus(EVENTS_PATH)
supervisor_queue = SupervisorQueue(SUPERVISOR_QUEUE_PATH)

agents = registry.list_agents()
events = load_jsonl(EVENTS_PATH)
approvals = supervisor_queue.load() if SUPERVISOR_QUEUE_PATH.exists() else []
pending_approvals = [item for item in approvals if item.get("status") == "pending_approval"]
system_state = load_json(SYSTEM_STATE_PATH)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Agentes", len(agents))

with col2:
    st.metric("Eventos", len(events))

with col3:
    st.metric("Aprovacoes pendentes", len(pending_approvals))

with col4:
    st.metric("Status", system_state.get("status", "online"))

st.divider()

tab_overview, tab_route, tab_supervisor, tab_events, tab_health = st.tabs([
    "Visao geral",
    "Roteador de tarefas",
    "Supervisor Queue",
    "Event Bus",
    "Health Check",
])

with tab_overview:
    st.subheader("K-Atlas OS")

    st.write({
        "papel": "sistema operacional modular de agentes IA",
        "cloud": "Render",
        "memoria": "GitHub + JSON",
        "cockpit": "Streamlit",
        "estado": "autonomia supervisionada em construcao",
    })

    st.subheader("Agentes registrados")

    for agent in agents:
        with st.expander(f"{agent.name} | {agent.domain} | autonomia {agent.autonomy_level}"):
            st.json(agent.to_dict())

with tab_route:
    st.subheader("Criar tarefa supervisionada")

    objective = st.text_input(
        "Objetivo",
        value="Criar pacote operacional supervisionado",
    )

    agent_options = {agent.agent_id: f"{agent.name} ({agent.domain})" for agent in agents}
    agent_id = st.selectbox(
        "Agente",
        options=list(agent_options.keys()),
        format_func=lambda item: agent_options[item],
    )

    action = st.selectbox(
        "Acao",
        options=[
            "create_campaign",
            "create_content_package",
            "enqueue_publish_payload",
            "dry_run",
            "test_page_publish",
            "create_product_structure",
            "generate_app_module",
            "run_smoke_test",
            "prepare_deploy",
            "create_brief",
            "create_prompt_pack",
            "generate_asset_plan",
            "prepare_media_package",
            "read_events",
            "summarize_state",
            "generate_report",
            "official_publish",
        ],
    )

    payload_text = st.text_area(
        "Payload JSON",
        value='{"module": "k_atlas", "risk": "controlled", "official_publish": false}',
        height=160,
    )

    if st.button("Enviar para Control Plane", type="primary"):
        try:
            payload = json.loads(payload_text)
        except json.JSONDecodeError as exc:
            st.error(f"Payload JSON invalido: {exc}")
        else:
            router = TaskRouter(
                registry=registry,
                event_bus=event_bus,
                supervisor_queue=supervisor_queue,
            )
            result = router.route(
                objective=objective,
                agent_id=agent_id,
                action=action,
                payload=payload,
                requested_by="streamlit_operator",
            )
            st.success(f"Resultado: {result.status}")
            st.json(result.to_dict())

with tab_supervisor:
    st.subheader("Fila de supervisao humana")

    approvals = supervisor_queue.load() if SUPERVISOR_QUEUE_PATH.exists() else []

    if not approvals:
        st.info("Nenhuma aprovacao registrada.")
    else:
        reviewer = st.text_input("Revisor", value="k_supervisor")

        for item in reversed(approvals[-50:]):
            label = f"{item.get('status')} | {item.get('approval_id')} | {item.get('task', {}).get('agent_name')}"
            with st.expander(label):
                st.json(item)

                if item.get("status") == "pending_approval":
                    if st.button("Aprovar", key=f"approve_{item.get('approval_id')}"):
                        approved = supervisor_queue.approve(
                            approval_id=item["approval_id"],
                            reviewer=reviewer,
                        )
                        event_bus.emit(
                            event_type="approval.granted",
                            source="control_plane.cockpit",
                            payload=approved,
                        )
                        st.success("Aprovado.")
                        st.json(approved)

with tab_events:
    st.subheader("Event Bus")

    events = load_jsonl(EVENTS_PATH)

    if not events:
        st.info("Nenhum evento registrado ainda.")
    else:
        for event in reversed(events[-80:]):
            with st.expander(f"{event.get('timestamp')} | {event.get('event_type')} | {event.get('severity')}"):
                st.json(event)

with tab_health:
    st.subheader("Health Check")

    if st.button("Rodar health check"):
        result = run_control_plane_health_check()
        event_bus.emit(
            event_type="health_check.executed",
            source="control_plane.cockpit",
            payload=result,
        )
        st.success("Health check executado.")
        st.json(result)

    st.subheader("System State")
    state = load_json(SYSTEM_STATE_PATH)

    if state:
        st.json(state)
    else:
        st.info("System state ainda nao criado. Rode o health check.")