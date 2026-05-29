from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import streamlit as st

from k_atlas.social.publishing_gateway.audit_log import AuditLog
from k_atlas.social.publishing_gateway.dry_run_adapter import DryRunAdapter
from k_atlas.social.publishing_gateway.publish_queue import PublishQueue
from k_atlas.social.publishing_gateway.test_page_adapter import TestPageAdapter


QUEUE_PATH = Path("memory/social_publish_queue.json")
AUDIT_PATH = Path("reports/social_publishing_gateway_audit.jsonl")
TEST_PAGE_PATH = Path("reports/social_test_page_posts.jsonl")


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


def load_jsonl(path: Path) -> list[dict[str, Any]]:
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
    return rows


def save_json_list(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rows, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def render_social_publishing_gateway_panel() -> None:
    st.title("K-Social Publishing Gateway")
    st.caption("LEVEL 2 - sandbox/test page. Sem API real. Sem publicacao oficial.")

    audit = AuditLog(AUDIT_PATH)
    queue = PublishQueue(path=QUEUE_PATH, audit_log=audit)
    dry_run = DryRunAdapter(audit_log=audit)
    test_page = TestPageAdapter(output_path=TEST_PAGE_PATH, audit_log=audit)

    tab_create, tab_queue, tab_logs = st.tabs(["Criar payload", "Fila", "Logs"])

    with tab_create:
        st.subheader("Novo payload sandbox")

        campaign_id = st.text_input(
            "Campaign ID",
            value="parada-atlantida-ecobier-futebol-2026",
        )

        title = st.text_input(
            "Titulo",
            value="Parada Atlantida + Chopp Ecobier",
        )

        body = st.text_area(
            "Texto",
            value="Campanha de teste para validacao operacional no sandbox.",
            height=120,
        )

        cta = st.text_input(
            "CTA",
            value="Validar criativo",
        )

        reviewer = st.text_input(
            "Revisor humano",
            value="k_atlas_engineer",
        )

        approved = st.checkbox("Aprovado para test_page local", value=True)

        payload = {
            "campaign_id": campaign_id,
            "channel": "test_page",
            "autonomy_level": "level_2_sandbox_page",
            "content": {
                "title": title,
                "body": body,
                "cta": cta,
            },
            "human_approval": {
                "approved": approved,
                "reviewer": reviewer,
            },
            "external_api_used": False,
            "publish_real": False,
            "mass_messaging": False,
            "browser_automation": False,
            "metadata": {
                "source": "streamlit_publishing_gateway_panel",
                "mode": "sandbox",
            },
        }

        st.json(payload)

        if st.button("Adicionar na fila", type="primary"):
            item = queue.enqueue(payload, actor="streamlit_operator")
            st.success(f"Payload adicionado: {item.get('status')}")
            st.json(item)

    with tab_queue:
        st.subheader("Fila de publicacao")

        items = load_json_list(QUEUE_PATH)

        if not items:
            st.info("Fila vazia.")
        else:
            for index, item in enumerate(items):
                request_id = item.get("request_id", f"item_{index}")
                status = item.get("status", "unknown")
                campaign = item.get("campaign_id", "sem_campaign")

                with st.expander(f"{campaign} | {status} | {request_id}"):
                    st.json(item)

                    col1, col2 = st.columns(2)

                    with col1:
                        if st.button("Dry run", key=f"dry_{request_id}"):
                            result = dry_run.publish(item, actor="streamlit_operator")
                            st.json(result)

                    with col2:
                        can_publish_test = status == "approved_for_test_page"
                        if st.button("Publicar em test_page local", key=f"test_{request_id}", disabled=not can_publish_test):
                            result = test_page.publish(item, actor="streamlit_operator")
                            if result.get("ok"):
                                items[index]["status"] = "published_to_test_page"
                                save_json_list(QUEUE_PATH, items)
                                st.success("Publicado em test_page local.")
                            else:
                                st.warning("Publicacao bloqueada pela policy.")
                            st.json(result)

    with tab_logs:
        st.subheader("Audit log")
        events = load_jsonl(AUDIT_PATH)

        if not events:
            st.info("Nenhum evento registrado ainda.")
        else:
            st.write(f"Eventos: {len(events)}")
            for event in reversed(events[-30:]):
                with st.expander(f"{event.get('timestamp')} | {event.get('action')} | {event.get('status')}"):
                    st.json(event)

        st.subheader("Test page local")
        posts = load_jsonl(TEST_PAGE_PATH)

        if not posts:
            st.info("Nenhum post local em test_page.")
        else:
            st.write(f"Posts locais: {len(posts)}")
            for post in reversed(posts[-20:]):
                with st.expander(f"{post.get('timestamp')} | {post.get('campaign_id')}"):
                    st.json(post)


if __name__ == "__main__":
    render_social_publishing_gateway_panel()