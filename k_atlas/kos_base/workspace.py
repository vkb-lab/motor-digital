from __future__ import annotations

import json
import subprocess
from html import escape
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

import streamlit as st

from k_atlas.kaizen.orchestrator import run_cycle
from k_atlas.ig_real_gate.readiness import inspect_ig_real_readiness
from k_atlas.social.publishing_gateway.audit_log import AuditLog
from k_atlas.social.publishing_gateway.instagram_level4_adapter import InstagramLevel4Adapter
from k_atlas.whiteboard.board_store import load_board, save_board


ROOT = Path(__file__).resolve().parents[2]
KAIZEN_REPORT = ROOT / "reports" / "KOS_KAIZEN_LAST_CYCLE_REPORT.json"
KAIZEN_QUEUE = ROOT / "memory" / "kaizen" / "task_queue.json"
META_REVIEW = ROOT / "reports" / "KOS_META_CONNECTION_REVIEW_20260616.md"
META_ADMIN_SETUP = ROOT / "reports" / "KOS_META_ADMIN_SETUP_20260616.md"
VIKHING_LAUNCH_DIR = ROOT / "reports" / "vikhing_launch"
AUDIT_PATH = ROOT / "reports" / "social_publishing_gateway_audit.jsonl"
SOCIAL_QUEUE_PATH = ROOT / "memory" / "social_publish_queue.json"
CLIENTS_DIR = ROOT / "clients"
LOCAL_IG_RUNTIME = ROOT / "local_runtime" / "ig_runtime.env"

PROTECTED_CLIENTS = {"parada_atlantida", "parada-atlantida"}
TEST_CLIENTS = {"vikhing", "hupmix", "kos_viking", "viking"}

LANES = {
    "observe": "Observar",
    "plan": "Planejar",
    "build": "Construir",
    "review": "Revisar",
    "done": "Feito",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path, default: Any) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return default
    return default


def run_git(args: list[str], timeout: int = 10) -> dict[str, Any]:
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "returncode": proc.returncode,
            "stdout": (proc.stdout or "").strip(),
            "stderr": (proc.stderr or "").strip(),
        }
    except Exception as exc:
        return {"returncode": -1, "stdout": "", "stderr": str(exc)}


def ensure_base_board() -> dict[str, Any]:
    board = load_board()
    if board.get("status") != "EMPTY":
        board.setdefault("cards", [])
        board.setdefault("lanes", LANES)
        return board

    board = {
        "status": "ACTIVE",
        "system": "K-OS BASE",
        "created_at": utc_now(),
        "updated_at": utc_now(),
        "lanes": LANES,
        "cards": [
            {
                "id": "base-kaizen-cycle",
                "lane": "observe",
                "title": "Rodar ciclo Kaizen seguro",
                "agent": "kaizen_orchestrator",
                "status": "ready",
                "approval_required": True,
                "note": "Executa um ciclo unico em modo seguro, sem daemon 24/7.",
            },
            {
                "id": "base-meta-gate",
                "lane": "review",
                "title": "Revisar gate Meta Level 4",
                "agent": "social_publishing_gateway",
                "status": "locked",
                "approval_required": True,
                "note": "Publicacao real segue bloqueada ate confirmacao final e variaveis Meta.",
            },
            {
                "id": "base-workspace",
                "lane": "build",
                "title": "Evoluir layout BASE",
                "agent": "k_os_base_workspace",
                "status": "in_progress",
                "approval_required": False,
                "note": "Area de trabalho local com lousa, status e orquestrador.",
            },
        ],
    }
    return save_board(board)


def add_board_card(title: str, lane: str, note: str, agent: str = "operator") -> dict[str, Any]:
    board = ensure_base_board()
    card = {
        "id": f"card-{uuid4().hex[:10]}",
        "lane": lane if lane in LANES else "observe",
        "title": title.strip() or "Novo card K-OS",
        "agent": agent.strip() or "operator",
        "status": "new",
        "approval_required": True,
        "note": note.strip(),
        "created_at": utc_now(),
    }
    board["cards"].append(card)
    board["updated_at"] = utc_now()
    save_board(board)
    return card


def move_card(card_id: str, lane: str) -> dict[str, Any]:
    board = ensure_base_board()
    for card in board.get("cards", []):
        if card.get("id") == card_id:
            card["lane"] = lane if lane in LANES else card.get("lane", "observe")
            card["updated_at"] = utc_now()
            break
    board["updated_at"] = utc_now()
    return save_board(board)


def load_audit_events(limit: int = 12) -> list[dict[str, Any]]:
    return AuditLog(AUDIT_PATH).read_events()[-limit:]


def load_publish_queue() -> list[dict[str, Any]]:
    data = read_json(SOCIAL_QUEUE_PATH, [])
    return data if isinstance(data, list) else []


def read_runtime_presence(path: Path = LOCAL_IG_RUNTIME) -> dict[str, Any]:
    if not path.exists():
        return {
            "path": str(path),
            "exists": False,
            "keys": {},
            "secret_values_exposed": False,
        }

    keys: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        keys[key.strip()] = "present" if value.strip() else "empty"

    return {
        "path": str(path),
        "exists": True,
        "keys": keys,
        "secret_values_exposed": False,
    }


def build_client_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    discovered = sorted(path.name for path in CLIENTS_DIR.iterdir() if path.is_dir()) if CLIENTS_DIR.exists() else []
    for client_id in sorted(set(discovered) | {"vikhing", "hupmix"}):
        client_path = CLIENTS_DIR / client_id
        is_protected = client_id in PROTECTED_CLIENTS
        is_test = client_id in TEST_CLIENTS
        connector_dirs = []
        if client_path.exists():
            connector_dirs = [path.name for path in client_path.iterdir() if path.is_dir() and path.name in {"connectors", "instagram", "google_business"}]

        if client_id == "hupmix":
            connector_status = "meta_app_base_connected"
            publish_gate = "level4_preview_only"
        elif client_id == "vikhing":
            connector_status = "launch_test_client"
            publish_gate = "test_page_ready_meta_l4_preview"
        elif is_protected:
            connector_status = "production_protected"
            publish_gate = "real_publish_blocked_by_policy"
        else:
            connector_status = "client_scaffold"
            publish_gate = "requires_connector_review"

        rows.append({
            "client_id": client_id,
            "role": "protected_production" if is_protected else "test_launch" if is_test else "future_client",
            "workspace": "present" if client_path.exists() else "virtual_from_meta_setup",
            "connectors": ", ".join(connector_dirs) if connector_dirs else "pending",
            "connector_status": connector_status,
            "publish_gate": publish_gate,
            "real_publish_allowed_now": False,
        })
    return rows


def build_connector_rows(meta_readiness: dict[str, Any], runtime: dict[str, Any]) -> list[dict[str, Any]]:
    runtime_keys = runtime.get("keys", {})
    return [
        {
            "connector": "Meta Business Apps",
            "scope": "hupmix base / Business Meta",
            "status": "configured_locally" if runtime.get("exists") else "missing_runtime_file",
            "side_effects": "none",
            "detail": "IDs locais presentes" if runtime_keys else "runtime local ausente",
        },
        {
            "connector": "Instagram Graph Level 4",
            "scope": "Vikhing/HupMix teste governado",
            "status": "armed" if meta_readiness.get("can_run_real") else "locked",
            "side_effects": "none_until_final_confirmation",
            "detail": "usa ig_real_gate + Fase 14, nao navegador",
        },
        {
            "connector": "Parada Atlantida",
            "scope": "producao protegida",
            "status": "blocked_by_local_policy",
            "side_effects": "none",
            "detail": "cliente bloqueado no adapter Level 4",
        },
        {
            "connector": "Test Page Local",
            "scope": "sandbox operacional",
            "status": "ready",
            "side_effects": "local_jsonl_only",
            "detail": "fila e relatorios locais sem API externa",
        },
    ]


def build_report_rows() -> list[dict[str, Any]]:
    candidates = [META_ADMIN_SETUP, META_REVIEW, *sorted(VIKHING_LAUNCH_DIR.glob("*"))] if VIKHING_LAUNCH_DIR.exists() else [META_ADMIN_SETUP, META_REVIEW]
    rows = []
    for path in candidates:
        rows.append({
            "report": path.name,
            "path": str(path),
            "exists": path.exists(),
            "bytes": path.stat().st_size if path.exists() else 0,
        })
    return rows


def build_workspace_snapshot() -> dict[str, Any]:
    branch = run_git(["branch", "--show-current"])
    status = run_git(["--no-pager", "status", "--short"])
    kaizen = read_json(KAIZEN_REPORT, {})
    queue = read_json(KAIZEN_QUEUE, {"tasks": []})
    board = ensure_base_board()
    publish_queue = load_publish_queue()
    meta_report_exists = META_REVIEW.exists()
    meta_readiness = inspect_ig_real_readiness()
    runtime = read_runtime_presence()
    client_rows = build_client_rows()

    return {
        "generated_at": utc_now(),
        "branch": branch.get("stdout") or "unknown",
        "git_dirty": bool(status.get("stdout")),
        "git_status": status.get("stdout", ""),
        "kaizen": kaizen,
        "queue_size": len(queue.get("tasks", [])) if isinstance(queue, dict) else 0,
        "mission_queue_size": len(publish_queue),
        "publish_queue": publish_queue,
        "board": board,
        "clients": client_rows,
        "connectors": build_connector_rows(meta_readiness, runtime),
        "reports": build_report_rows(),
        "runtime_presence": runtime,
        "meta_review_exists": meta_report_exists,
        "meta_level4_preview_status": "locked" if not meta_readiness.get("can_run_real") else "armed",
        "meta_level4_side_effects": "none",
        "meta_readiness": meta_readiness,
        "audit_events": load_audit_events(),
    }


def render_status_pill(label: str, value: str, tone: str = "neutral") -> None:
    colors = {
        "good": ("#063f2d", "#7dffbf"),
        "warn": ("#423705", "#ffe08a"),
        "bad": ("#4a1212", "#ff9a9a"),
        "neutral": ("#17212b", "#d7e3ee"),
    }
    bg, fg = colors.get(tone, colors["neutral"])
    st.markdown(
        f"<div class='kos-pill' style='background:{bg};color:{fg}'><span>{label}</span><strong>{value}</strong></div>",
        unsafe_allow_html=True,
    )


def inject_base_css() -> None:
    st.markdown(
        """
<style>
.kos-base-hero {
  padding: 22px 24px;
  border: 1px solid rgba(120, 255, 190, .20);
  background: linear-gradient(135deg, #07110e 0%, #10221d 48%, #182126 100%);
  color: #f2fff8;
  border-radius: 8px;
  margin-bottom: 18px;
}
.kos-base-hero h1 {
  font-size: 34px;
  line-height: 1.12;
  margin: 0 0 8px 0;
  letter-spacing: 0;
}
.kos-base-hero p {
  margin: 0;
  color: #b8d8cb;
  font-size: 15px;
}
.kos-pill {
  min-height: 74px;
  border-radius: 8px;
  padding: 14px 16px;
  border: 1px solid rgba(255,255,255,.10);
}
.kos-pill span {
  display: block;
  font-size: 12px;
  opacity: .8;
  margin-bottom: 7px;
}
.kos-pill strong {
  display: block;
  font-size: 20px;
  line-height: 1.1;
  letter-spacing: 0;
}
.kos-card {
  border: 1px solid rgba(255,255,255,.12);
  background: rgba(255,255,255,.035);
  border-radius: 8px;
  padding: 12px;
  min-height: 134px;
  margin-bottom: 10px;
}
.kos-card-title {
  font-weight: 700;
  color: #f4fff9;
  margin-bottom: 6px;
}
.kos-card-meta {
  color: #a7c2b8;
  font-size: 12px;
  margin-bottom: 8px;
}
.kos-card-note {
  color: #d9eee6;
  font-size: 13px;
  line-height: 1.35;
}
.kos-section-label {
  color: #92c9b6;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0;
  margin: 2px 0 8px 0;
}
</style>
        """,
        unsafe_allow_html=True,
    )


def render_board(board: dict[str, Any]) -> None:
    cards = board.get("cards", [])
    lanes = board.get("lanes", LANES)
    columns = st.columns(len(LANES))
    for col, lane_id in zip(columns, LANES):
        lane_cards = [card for card in cards if card.get("lane") == lane_id]
        with col:
            st.markdown(f"**{lanes.get(lane_id, lane_id)}**")
            st.caption(f"{len(lane_cards)} cards")
            for card in lane_cards:
                title = escape(str(card.get("title", "Sem titulo")))
                agent = escape(str(card.get("agent", "agent")))
                status = escape(str(card.get("status", "status")))
                note = escape(str(card.get("note", "")))
                st.markdown(
                    f"""
<div class="kos-card">
  <div class="kos-card-title">{title}</div>
  <div class="kos-card-meta">{agent} | {status}</div>
  <div class="kos-card-note">{note}</div>
</div>
                    """,
                    unsafe_allow_html=True,
                )


def render_kos_base_workspace_panel() -> None:
    inject_base_css()
    snapshot = build_workspace_snapshot()
    kaizen = snapshot.get("kaizen", {})

    st.markdown(
        """
<div class="kos-base-hero">
  <h1>K-OS BASE</h1>
  <p>Area de trabalho operacional multi-cliente para lousa, orquestrador, conectores, fila de missoes, gates Meta e auditoria segura.</p>
</div>
        """,
        unsafe_allow_html=True,
    )

    top = st.columns(5)
    with top[0]:
        render_status_pill("Branch", snapshot["branch"], "neutral")
    with top[1]:
        render_status_pill("Git", "sujo" if snapshot["git_dirty"] else "limpo", "warn" if snapshot["git_dirty"] else "good")
    with top[2]:
        render_status_pill("Kaizen", str(kaizen.get("status", "sem ciclo")), "good" if kaizen else "neutral")
    with top[3]:
        render_status_pill("Missoes", str(snapshot["mission_queue_size"]), "neutral")
    with top[4]:
        render_status_pill("Meta L4", str(snapshot["meta_level4_preview_status"]), "good")

    tab_clients, tab_board, tab_orchestrator, tab_meta, tab_reports, tab_logs = st.tabs([
        "Clientes",
        "Lousa BASE",
        "Orquestrador",
        "Meta/Gates",
        "Relatorios",
        "Evidencias",
    ])

    with tab_clients:
        st.subheader("Dashboard multi-cliente")
        st.caption("Operacao sob demanda por cliente. Publicacao real segue sempre por gates/API do K-OS.")
        st.dataframe(snapshot["clients"], use_container_width=True, hide_index=True)

        st.subheader("Status de contas e conectores")
        st.dataframe(snapshot["connectors"], use_container_width=True, hide_index=True)

        runtime = snapshot["runtime_presence"]
        st.markdown("<div class='kos-section-label'>Runtime local IG/Meta</div>", unsafe_allow_html=True)
        st.write({
            "arquivo_existe": runtime["exists"],
            "caminho": runtime["path"],
            "valores_secretos_expostos": runtime["secret_values_exposed"],
        })
        st.json(runtime.get("keys", {}))

    with tab_board:
        st.subheader("Lousa operacional")
        render_board(snapshot["board"])

        with st.expander("Adicionar card"):
            with st.form("kos_base_new_card"):
                title = st.text_input("Titulo", value="Nova tarefa K-OS")
                lane = st.selectbox("Raia", list(LANES.keys()), format_func=lambda item: LANES[item])
                agent = st.text_input("Agente", value="operator")
                note = st.text_area("Nota", value="Descrever proximo passo operacional.")
                submitted = st.form_submit_button("Adicionar na lousa")
            if submitted:
                add_board_card(title=title, lane=lane, note=note, agent=agent)
                st.success("Card adicionado na lousa local.")
                st.rerun()

        with st.expander("Mover card"):
            cards = snapshot["board"].get("cards", [])
            if cards:
                labels = {card["id"]: f"{card.get('title')} ({card.get('lane')})" for card in cards if card.get("id")}
                card_id = st.selectbox("Card", list(labels.keys()), format_func=lambda item: labels[item])
                target_lane = st.selectbox("Nova raia", list(LANES.keys()), format_func=lambda item: LANES[item], key="target_lane")
                if st.button("Mover card selecionado"):
                    move_card(card_id, target_lane)
                    st.success("Card movido.")
                    st.rerun()
            else:
                st.info("Nenhum card para mover.")

    with tab_orchestrator:
        st.subheader("Executor e orquestrador integrado")
        st.caption("Executa somente um ciclo local seguro. Nao inicia daemon 24/7.")

        col_a, col_b = st.columns([1, 2])
        with col_a:
            if st.button("Rodar 1 ciclo seguro", type="primary", use_container_width=True):
                result = run_cycle()
                st.success("Ciclo Kaizen concluido.")
                st.json(result)
        with col_b:
            st.json(kaizen or {"status": "sem relatorio"})

        if snapshot["git_status"]:
            st.code(snapshot["git_status"], language="text")

        st.subheader("Fila de missoes")
        if snapshot["publish_queue"]:
            st.dataframe(snapshot["publish_queue"], use_container_width=True)
        else:
            st.info("Fila de missoes sem itens de publicacao.")

    with tab_meta:
        st.subheader("Gates de publicacao")
        st.caption("Preview governado. A chamada real continua presa no gate final e nao usa navegador.")
        st.write({
            "adapter": "instagram_level4_adapter",
            "preview_status": snapshot["meta_level4_preview_status"],
            "side_effects": snapshot["meta_level4_side_effects"],
            "review_report": str(META_REVIEW) if snapshot["meta_review_exists"] else "missing",
        })
        st.json(snapshot.get("meta_readiness", {}))
        if st.button("Gerar preview auditavel do adapter L4", use_container_width=True):
            adapter = InstagramLevel4Adapter(audit_log=AuditLog(AUDIT_PATH))
            preview = adapter.prepare(
                {
                    "client_id": "kos_viking",
                    "account_alias": "kos_viking",
                    "channel": "instagram_official",
                    "autonomy_level": "level_4_limited_real_publish",
                    "campaign_name": "kos_base_workspace_preview",
                    "image_url": "https://placehold.co/1080x1080/png",
                    "caption": "K-OS BASE preview.",
                    "publish_real": False,
                    "browser_automation": False,
                    "mass_messaging": False,
                },
                actor="kos_base_workspace",
            )
            st.json(preview)
        st.info("Conta de teste allowlist: kos_viking / viking. Cliente de producao parada_atlantida segue bloqueado.")

    with tab_reports:
        st.subheader("Auditoria e relatorios")
        st.dataframe(snapshot["reports"], use_container_width=True, hide_index=True)
        for row in snapshot["reports"]:
            path = Path(row["path"])
            if not path.exists() or path.suffix.lower() not in {".md", ".json"}:
                continue
            with st.expander(row["report"]):
                if path.suffix.lower() == ".json":
                    st.json(read_json(path, {}))
                else:
                    st.markdown(path.read_text(encoding="utf-8-sig"))

    with tab_logs:
        st.subheader("Auditoria recente")
        events = snapshot.get("audit_events", [])
        if events:
            for event in reversed(events):
                with st.expander(f"{event.get('timestamp')} | {event.get('action')} | {event.get('status')}"):
                    st.json(event)
        else:
            st.info("Sem eventos recentes do gateway.")
