from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]

REPORTS = {
    "baseline_701": ROOT / "reports" / "KOS_PHASE701_CHATGPT_LOCAL_BRIDGE_BASELINE_CERTIFICATION.json",
    "hupmix_audit_69d": ROOT / "reports" / "KOS_PHASE69D_HUPMIX_INSTAGRAM_AUDIT_BOOTSTRAP.json",
    "publish_audit_69e": ROOT / "reports" / "KOS_PHASE69E_PUBLISH_AUDIT_GATE_BOOTSTRAP.json",
    "dry_run_69f": ROOT / "reports" / "KOS_PHASE69F_HUMAN_CONFIRMED_PUBLISH_DRY_RUN_GATE_BOOTSTRAP.json",
    "approval_ledger_69g": ROOT / "reports" / "KOS_PHASE69G_REAL_PUBLISH_APPROVAL_LEDGER_BOOTSTRAP.json",
    "real_executor_69h": ROOT / "reports" / "KOS_PHASE69H_HUPMIX_REAL_PUBLISH_EXECUTOR_BOOTSTRAP.json",
    "bridge_70e": ROOT / "reports" / "KOS_PHASE70E_CHATGPT_BRIDGE_RUNTIME_CONTROLLER_BOOTSTRAP.json",
}

STRATEGY_DIR = ROOT / "local_runtime" / "kos_social_ops" / "strategies"


def read_json(path: Path) -> dict:
    if not path.exists():
        return {"status": "MISSING", "path": str(path)}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        return {"status": "READ_ERROR", "path": str(path), "error": str(exc)}


def latest_strategy_files() -> list[Path]:
    if not STRATEGY_DIR.exists():
        return []
    return sorted(STRATEGY_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:10]


def bool_label(value: object) -> str:
    if value is True:
        return "sim"
    if value is False:
        return "nao"
    return "n/d"


st.set_page_config(page_title="K-OS Social Ops", layout="wide")

st.title("K-OS Social Ops Control Center")
st.caption("Auditoria, publicações em teste, estratégia e riscos. Não publica automaticamente.")

reports = {name: read_json(path) for name, path in REPORTS.items()}

tab_overview, tab_audit, tab_publish, tab_strategy, tab_risk = st.tabs(
    ["Resumo", "Auditoria", "Publicações", "Estratégia", "Riscos"]
)

with tab_overview:
    st.subheader("Estado operacional")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Conta teste", "Hupmix")
    c2.metric("Parada Atlântida", "bloqueada")
    c3.metric("Publicação real", "gateada")
    c4.metric("IA paga", "bloqueada")

    st.subheader("Relatórios principais")
    st.json({
        name: {
            "status": payload.get("status"),
            "phase": payload.get("phase"),
            "created_at": payload.get("created_at"),
        }
        for name, payload in reports.items()
    })

with tab_audit:
    st.subheader("Auditoria de redes")

    st.info("Esta área mostra o estado auditável. Ações reais devem continuar em scripts/gates próprios.")

    st.json({
        "hupmix_audit": reports["hupmix_audit_69d"],
        "publish_audit": reports["publish_audit_69e"],
        "dry_run": reports["dry_run_69f"],
    })

with tab_publish:
    st.subheader("Pipeline de publicação")

    st.warning("Nenhum botão aqui publica no Instagram. Esta tela é controle e revisão.")

    checklist = {
        "target_hupmix_only": True,
        "parada_atlantida_locked": True,
        "approval_ledger_required": True,
        "human_confirmation_required": True,
        "public_https_asset_required": True,
        "caption_required": True,
        "real_executor_installed": reports["real_executor_69h"].get("status") != "MISSING",
        "real_publish_executed": False,
    }

    st.json(checklist)

    st.subheader("Executor e ledger")
    st.json({
        "approval_ledger": reports["approval_ledger_69g"],
        "real_executor": reports["real_executor_69h"],
    })

with tab_strategy:
    st.subheader("Estratégias de campanha")

    st.caption("Estratégias ficam em local_runtime/kos_social_ops/strategies como JSON auditável.")

    files = latest_strategy_files()
    if not files:
        st.info("Nenhuma estratégia salva ainda.")
    else:
        selected = st.selectbox("Estratégias recentes", [p.name for p in files])
        st.json(read_json(STRATEGY_DIR / selected))

    st.subheader("Modelo de estratégia")
    st.json({
        "id": "strategy-hupmix-001",
        "target": "hupmix",
        "objective": "crescimento com teste controlado",
        "content_pillar": "produto, bastidor, prova social, chamada para acao",
        "risk_level": "low",
        "publish_mode": "draft_or_dry_run_first",
        "requires_human_approval": True,
    })

with tab_risk:
    st.subheader("Riscos e bloqueios")

    st.json({
        "parada_atlantida_locked": True,
        "browser_scraping_enabled": False,
        "browser_logged_account_automation_used": False,
        "paid_ai_locked": True,
        "auto_publish_enabled": False,
        "auto_execution_enabled": False,
        "operator_review_required": True,
        "real_action_executed": False,
        "instagram_publish_executed": False,
    })

    st.success("Sistema em modo seguro para testes, auditoria e estratégia.")
