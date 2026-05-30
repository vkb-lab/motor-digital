from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]

PUBLIC_QUEUE_PATH = PROJECT_ROOT / "live" / "marketplace_ia" / "public_capture_queue.jsonl"
LEAD_INTAKE_PATH = PROJECT_ROOT / "live" / "marketplace_ia" / "lead_intake.jsonl"
REVIEW_DECISION_PATH = PROJECT_ROOT / "live" / "marketplace_ia" / "public_capture_review_decision.json"


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []

    rows = []
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def lead_already_imported(lead_id: str) -> bool:
    if not LEAD_INTAKE_PATH.exists():
        return False

    for lead in load_jsonl(LEAD_INTAKE_PATH):
        if lead.get("lead_id") == lead_id:
            return True
    return False


def append_lead_to_intake(lead: dict) -> None:
    LEAD_INTAKE_PATH.parent.mkdir(parents=True, exist_ok=True)

    approved_lead = dict(lead)
    approved_lead["status"] = "approved_for_local_diagnostic"
    approved_lead["source"] = "public_capture_review_approved"
    approved_lead["approved_at"] = datetime.now(timezone.utc).isoformat()
    approved_lead["external_send_enabled"] = False
    approved_lead["human_review_required"] = True

    with LEAD_INTAKE_PATH.open("a", encoding="utf-8") as file:
        file.write(json.dumps(approved_lead, ensure_ascii=False) + "\n")


def save_decision(decision: dict) -> None:
    REVIEW_DECISION_PATH.parent.mkdir(parents=True, exist_ok=True)
    REVIEW_DECISION_PATH.write_text(
        json.dumps(decision, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


st.set_page_config(
    page_title="Marketplace IA - Review Gate Captura Publica",
    layout="wide",
)

st.title("Marketplace IA - Review Gate da Captura Publica")
st.caption("Test Mission 009 - revisão humana antes de mover lead para diagnóstico.")

captures = load_jsonl(PUBLIC_QUEUE_PATH)

if not captures:
    st.warning("Nenhuma captura publica encontrada em live/marketplace_ia/public_capture_queue.jsonl")
    st.stop()

latest = captures[-1]
lead_id = latest.get("lead_id", "")

st.header("Ultima captura publica")

safe_view = {
    "lead_id": latest.get("lead_id"),
    "created_at": latest.get("created_at"),
    "negocio": latest.get("negocio"),
    "segmento": latest.get("segmento"),
    "objetivo": latest.get("objetivo"),
    "desafio": latest.get("desafio"),
    "source": latest.get("source"),
    "status": latest.get("status"),
    "external_send_enabled": latest.get("external_send_enabled"),
    "human_review_required": latest.get("human_review_required"),
}

st.json(safe_view)

st.divider()

c1, c2, c3 = st.columns(3)

with c1:
    st.metric("Capturas publicas", len(captures))

with c2:
    st.metric("Ja importado", "SIM" if lead_already_imported(lead_id) else "NAO")

with c3:
    st.metric("Envio externo", "BLOQUEADO")

st.divider()

notes = st.text_area("Observacoes do operador")

left, right = st.columns(2)

with left:
    if st.button("Aprovar e mover para fila de diagnostico", type="primary"):
        if lead_already_imported(lead_id):
            st.info("Este lead ja foi movido para a fila de diagnostico.")
        else:
            append_lead_to_intake(latest)

        decision = {
            "ok": True,
            "decision": "approved_for_local_diagnostic",
            "lead_id": lead_id,
            "reviewed_at": datetime.now(timezone.utc).isoformat(),
            "notes": notes,
            "external_send_enabled": False,
            "human_review_recorded": True,
            "target_queue": "live/marketplace_ia/lead_intake.jsonl",
        }

        save_decision(decision)
        st.success("Lead aprovado e movido para a fila local de diagnostico.")
        st.json(decision)

with right:
    if st.button("Reprovar captura"):
        decision = {
            "ok": True,
            "decision": "rejected",
            "lead_id": lead_id,
            "reviewed_at": datetime.now(timezone.utc).isoformat(),
            "notes": notes,
            "external_send_enabled": False,
            "human_review_recorded": True,
        }

        save_decision(decision)
        st.error("Captura reprovada localmente.")
        st.json(decision)

if REVIEW_DECISION_PATH.exists():
    st.divider()
    st.subheader("Ultima decisao")
    st.json(json.loads(REVIEW_DECISION_PATH.read_text(encoding="utf-8-sig")))

st.caption("Nenhum envio externo. Dados sensiveis permanecem locais.")