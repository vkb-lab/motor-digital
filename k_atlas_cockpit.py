# -*- coding: utf-8 -*-
"""
K-Atlas OS - Operational Cockpit

Cockpit operacional inicial do K-Atlas OS.

Objetivo:
- observabilidade
- status operacional
- auditoria
- visualizacao de agentes
- visualizacao de tarefas
- visualizacao de memoria
- visualizacao de learning
- visualizacao de eventos
- visualizacao de reports e logs

Execucao:
streamlit run k_atlas_cockpit.py
"""

from __future__ import annotations

from typing import Any, Dict, List

from cockpit.components.cards import render_command_health, render_metric_grid
from cockpit.services.kernel_service import collect_operational_snapshot
from cockpit.services.self_evolution_service import collect_self_evolution_snapshot
from cockpit.services.cowork_service import collect_cowork_snapshot
from cockpit.state.session_state import init_session_state
from cockpit.utils.formatting import to_display_rows


APP_TITLE = "K-Atlas OS Cockpit"
APP_VERSION = "0.1.0"


def get_learning_total(snapshot: Dict[str, Any]) -> int:
    totals = snapshot.get("health", {}).get("learning_totals", {})
    if not isinstance(totals, dict):
        return 0
    return sum(int(value) for value in totals.values())


def render_status_tab(st: Any, snapshot: Dict[str, Any]) -> None:
    health = snapshot.get("health", {})
    kernel_status = snapshot.get("kernel_status", {})

    st.subheader("Status operacional")

    render_metric_grid(
        st,
        [
            {"label": "Health", "value": health.get("status", "unknown")},
            {"label": "Risk", "value": health.get("risk_level", "unknown")},
            {"label": "Agents", "value": health.get("agents_total", 0)},
            {"label": "Pending Tasks", "value": health.get("pending_tasks", 0)},
            {"label": "Memories", "value": health.get("memories_total", 0)},
            {"label": "Learning Items", "value": get_learning_total(snapshot)},
            {"label": "Events", "value": health.get("events_total", 0)},
        ],
    )

    st.divider()

    left, right = st.columns(2)

    with left:
        st.markdown("#### Kernel")
        st.json(kernel_status)

    with right:
        st.markdown("#### Command Health")
        render_command_health(st, snapshot.get("commands", {}))


def render_agents_tab(st: Any, snapshot: Dict[str, Any]) -> None:
    st.subheader("Agents registrados")

    agents = snapshot.get("data", {}).get("agents", [])

    render_metric_grid(
        st,
        [
            {"label": "Total Agents", "value": len(agents)},
        ],
    )

    rows = to_display_rows(
        agents,
        [
            "agent_id",
            "name",
            "description",
            "version",
            "enabled",
            "capabilities",
            "permissions",
        ],
    )

    st.dataframe(rows, use_container_width=True)

    with st.expander("JSON bruto dos agents"):
        st.json(agents)


def render_tasks_tab(st: Any, snapshot: Dict[str, Any]) -> None:
    st.subheader("Tasks")

    tasks = snapshot.get("data", {}).get("tasks", [])

    pending = [item for item in tasks if isinstance(item, dict) and item.get("status") == "pending"]
    done = [item for item in tasks if isinstance(item, dict) and item.get("status") == "done"]

    render_metric_grid(
        st,
        [
            {"label": "Total Tasks", "value": len(tasks)},
            {"label": "Pending", "value": len(pending)},
            {"label": "Done", "value": len(done)},
        ],
    )

    rows = to_display_rows(
        tasks,
        [
            "task_id",
            "title",
            "status",
            "priority",
            "assigned_agent_id",
            "tags",
            "created_at",
            "updated_at",
        ],
    )

    st.dataframe(rows, use_container_width=True)

    with st.expander("JSON bruto das tasks"):
        st.json(tasks)


def render_memory_tab(st: Any, snapshot: Dict[str, Any]) -> None:
    st.subheader("Memory")

    memories = snapshot.get("data", {}).get("memories", [])

    render_metric_grid(
        st,
        [
            {"label": "Total Memories", "value": len(memories)},
        ],
    )

    rows = to_display_rows(
        memories,
        [
            "memory_id",
            "title",
            "type",
            "source",
            "visibility",
            "importance",
            "tags",
            "created_at",
        ],
    )

    st.dataframe(rows, use_container_width=True)

    with st.expander("JSON bruto da memoria"):
        st.json(memories)


def render_learning_tab(st: Any, snapshot: Dict[str, Any]) -> None:
    st.subheader("Learning")

    data = snapshot.get("data", {})
    learning_stats = data.get("learning_stats", {})
    lessons = data.get("learning_lessons", [])
    errors = data.get("learning_errors", [])
    playbooks = data.get("learning_playbooks", [])
    training = data.get("learning_training", [])

    totals = learning_stats.get("totals", {}) if isinstance(learning_stats, dict) else {}

    render_metric_grid(
        st,
        [
            {"label": "Lessons", "value": totals.get("lessons", len(lessons))},
            {"label": "Errors", "value": totals.get("errors", len(errors))},
            {"label": "Playbooks", "value": totals.get("playbooks", len(playbooks))},
            {"label": "Training Items", "value": totals.get("training_items", len(training))},
        ],
    )

    st.markdown("#### Playbooks")
    st.dataframe(
        to_display_rows(
            playbooks,
            [
                "playbook_id",
                "title",
                "objective",
                "tags",
                "version",
                "created_at",
            ],
        ),
        use_container_width=True,
    )

    st.markdown("#### Lessons")
    st.dataframe(
        to_display_rows(
            lessons,
            [
                "lesson_id",
                "title",
                "type",
                "source",
                "importance",
                "tags",
                "created_at",
            ],
        ),
        use_container_width=True,
    )

    st.markdown("#### Errors")
    st.dataframe(
        to_display_rows(
            errors,
            [
                "error_id",
                "title",
                "severity",
                "status",
                "tags",
                "created_at",
            ],
        ),
        use_container_width=True,
    )

    st.markdown("#### Training Items")
    st.dataframe(
        to_display_rows(
            training,
            [
                "training_id",
                "title",
                "type",
                "source",
                "importance",
                "tags",
                "created_at",
            ],
        ),
        use_container_width=True,
    )

    with st.expander("Learning stats JSON"):
        st.json(learning_stats)


def render_events_tab(st: Any, snapshot: Dict[str, Any]) -> None:
    st.subheader("Events, Reports e Logs")

    events = snapshot.get("data", {}).get("events", [])
    reports = snapshot.get("reports", [])
    logs = snapshot.get("logs", [])

    render_metric_grid(
        st,
        [
            {"label": "Events", "value": len(events)},
            {"label": "Reports", "value": len(reports)},
            {"label": "Logs", "value": len(logs)},
        ],
    )

    st.markdown("#### Ultimos eventos")
    st.dataframe(
        to_display_rows(
            events,
            [
                "event_id",
                "event_type",
                "source",
                "message",
                "level",
                "created_at",
            ],
        ),
        use_container_width=True,
    )

    st.markdown("#### Reports JSON")
    report_rows = [
        {
            "name": item.get("name"),
            "path": item.get("path"),
            "exists": item.get("exists"),
            "modified_at": item.get("modified_at"),
            "error": item.get("error"),
        }
        for item in reports
    ]
    st.dataframe(report_rows, use_container_width=True)

    if reports:
        selected_report = st.selectbox(
            "Abrir report",
            options=[item.get("name") for item in reports],
        )

        for item in reports:
            if item.get("name") == selected_report:
                st.json(item.get("data"))
                break

    st.markdown("#### Logs")
    if not logs:
        st.info("Nenhum arquivo .log encontrado.")
    else:
        for item in logs:
            with st.expander(item.get("name", "log")):
                if item.get("error"):
                    st.error(item.get("error"))
                st.code(item.get("tail", ""), language="text")



def render_self_evolution_tab(st: Any, snapshot: Dict[str, Any]) -> None:
    st.subheader("Self Evolution")

    self_snapshot = collect_self_evolution_snapshot(limit=50)
    totals = self_snapshot.get("totals", {})
    policy = self_snapshot.get("policy", {})

    render_metric_grid(
        st,
        [
            {"label": "Patch Requests", "value": totals.get("patch_requests", 0)},
            {"label": "Patch Inbox", "value": totals.get("patch_inbox", 0)},
            {"label": "Approved", "value": totals.get("patch_approved", 0)},
            {"label": "Rejected", "value": totals.get("patch_rejected", 0)},
            {"label": "Snapshots", "value": totals.get("snapshots", 0)},
            {"label": "Rollback Plans", "value": totals.get("rollback", 0)},
        ],
    )

    st.info("Modo read-only. O cockpit nao aplica patches, nao aprova e nao rejeita propostas.")

    st.markdown("#### Policy")
    st.json(policy)

    st.markdown("#### Risk Summary")
    st.dataframe(self_snapshot.get("risk_summary", []), use_container_width=True)

    data = self_snapshot.get("data", {})

    sections = [
        ("Patch Requests", "patch_requests"),
        ("Patch Inbox", "patch_inbox"),
        ("Patch Approved", "patch_approved"),
        ("Patch Rejected", "patch_rejected"),
        ("Snapshots", "snapshots"),
        ("Rollback", "rollback"),
    ]

    for title, key in sections:
        st.markdown("#### " + title)
        items = data.get(key, [])

        rows = []
        for item in items:
            payload = item.get("data", {})
            rows.append(
                {
                    "name": item.get("name"),
                    "status": payload.get("status"),
                    "title": payload.get("title"),
                    "risk_level": payload.get("risk", {}).get("risk_level") if isinstance(payload.get("risk"), dict) else None,
                    "risk_score": payload.get("risk", {}).get("risk_score") if isinstance(payload.get("risk"), dict) else None,
                    "modified_at": item.get("modified_at"),
                    "path": item.get("path"),
                }
            )

        st.dataframe(rows, use_container_width=True)

        for item in items:
            with st.expander(item.get("name", "item")):
                st.json(item.get("data"))
                if item.get("diff"):
                    st.markdown("Diff")
                    st.code(item.get("diff"), language="diff")



def render_cowork_tab(st: Any, snapshot: Dict[str, Any]) -> None:
    st.subheader("Cowork Mode")

    cowork_snapshot = collect_cowork_snapshot(limit=50)
    totals = cowork_snapshot.get("totals", {})
    policy = cowork_snapshot.get("policy", {})
    progress = cowork_snapshot.get("progress", {})
    latest_session = cowork_snapshot.get("latest_session", {})

    render_metric_grid(
        st,
        [
            {"label": "Sessions", "value": totals.get("sessions", 0)},
            {"label": "Steps", "value": totals.get("steps", 0)},
            {"label": "Reviews", "value": totals.get("reviews", 0)},
            {"label": "Current Step", "value": progress.get("current_step", 0)},
            {"label": "Max Steps", "value": progress.get("max_steps", 10)},
            {"label": "Progress", "value": str(progress.get("progress_percent", 0)) + "%"},
        ],
    )

    st.info("Modo read-only. O cockpit nao executa comandos, nao controla navegador e nao aplica patches.")

    st.markdown("#### Policy")
    st.json(policy)

    st.markdown("#### Sessao atual")
    if latest_session:
        st.json(latest_session)
    else:
        st.warning("Nenhuma sessao Cowork encontrada.")

    data = cowork_snapshot.get("data", {})

    st.markdown("#### Steps")
    step_rows = []
    for item in data.get("steps", []):
        payload = item.get("data", {})
        step_rows.append(
            {
                "step_number": payload.get("step_number"),
                "title": payload.get("title"),
                "status": payload.get("status"),
                "risk": payload.get("risk"),
                "created_at": payload.get("created_at"),
                "path": item.get("path"),
            }
        )
    st.dataframe(step_rows, use_container_width=True)

    st.markdown("#### Sessions")
    session_rows = []
    for item in data.get("sessions", []):
        payload = item.get("data", {})
        session_rows.append(
            {
                "session_id": payload.get("session_id"),
                "status": payload.get("status"),
                "goal": payload.get("goal"),
                "current_step": payload.get("current_step"),
                "max_steps": payload.get("max_steps"),
                "created_at": payload.get("created_at"),
                "path": item.get("path"),
            }
        )
    st.dataframe(session_rows, use_container_width=True)

    st.markdown("#### Reviews")
    review_rows = []
    for item in data.get("reviews", []):
        payload = item.get("data", {})
        review_rows.append(
            {
                "review_id": payload.get("review_id"),
                "goal": payload.get("goal"),
                "steps_total": payload.get("steps_total"),
                "score": payload.get("score"),
                "decision": payload.get("decision"),
                "created_at": payload.get("created_at"),
                "path": item.get("path"),
            }
        )
    st.dataframe(review_rows, use_container_width=True)


def main() -> None:
    import streamlit as st

    st.set_page_config(
        page_title=APP_TITLE,
        page_icon="K",
        layout="wide",
    )

    init_session_state(st)

    st.title(APP_TITLE)
    st.caption("Cockpit operacional read-only conectado ao kernel multiagente real.")

    with st.sidebar:
        st.markdown("### K-Atlas OS")
        st.write("Versao cockpit:", APP_VERSION)
        st.write("Modo:", "read-only")
        st.write("Foco:", "observabilidade")
        refresh = st.button("Recarregar snapshot")

        st.divider()
        st.markdown("### CLI equivalente")
        st.code(
            "python .\\k_atlas_cli.py status\n"
            "python .\\k_atlas_cli.py agents\n"
            "python .\\k_atlas_cli.py task-list\n"
            "python .\\k_atlas_cli.py memory-list\n"
            "python .\\k_atlas_cli.py learning-stats",
            language="powershell",
        )

    @st.cache_data(ttl=5)
    def load_snapshot() -> Dict[str, Any]:
        return collect_operational_snapshot(save_state=True)

    if refresh:
        st.cache_data.clear()

    with st.spinner("Carregando snapshot operacional do kernel..."):
        snapshot = load_snapshot()

    if not snapshot.get("success"):
        st.error("Falha ao carregar snapshot operacional.")
        st.json(snapshot)
        return

    tabs = st.tabs(
        [
            "Status",
            "Agents",
            "Tasks",
            "Memory",
            "Learning",
            "Events",
            "Self Evolution",
            "Cowork",
        ]
    )

    with tabs[0]:
        render_status_tab(st, snapshot)

    with tabs[1]:
        render_agents_tab(st, snapshot)

    with tabs[2]:
        render_tasks_tab(st, snapshot)

    with tabs[3]:
        render_memory_tab(st, snapshot)

    with tabs[4]:
        render_learning_tab(st, snapshot)

    with tabs[5]:
        render_events_tab(st, snapshot)

    with tabs[6]:
        render_self_evolution_tab(st, snapshot)

    with tabs[7]:
        render_cowork_tab(st, snapshot)


if __name__ == "__main__":
    main()
