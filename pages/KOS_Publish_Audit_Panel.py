from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]

FILES = {
    "Instagram Audit Hupmix": ROOT / "local_runtime" / "kos_instagram_audit" / "hupmix" / "latest_hupmix_instagram_audit.json",
    "Publish Audit": ROOT / "local_runtime" / "kos_publish_audit" / "hupmix" / "latest_publish_audit.json",
    "Publish Dry Run": ROOT / "local_runtime" / "kos_publish_dry_run" / "hupmix" / "latest_publish_dry_run.json",
    "Approval Ledger": ROOT / "local_runtime" / "kos_publish_approval_ledger" / "hupmix" / "latest_publish_approval_ledger.json",
    "Baseline 69Z": ROOT / "reports" / "KOS_PHASE69Z_REQUESTED_EXTERNAL_ACTION_GOVERNANCE_BASELINE_CERTIFICATION.json",
}


def read_json(path: Path) -> dict:
    if not path.exists():
        return {"status": "FILE_NOT_FOUND", "path": str(path)}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        return {"status": "READ_FAILED", "path": str(path), "error": str(exc)}


def status_badge(status: str) -> str:
    if "BLOCKED" in status:
        return "BLOQUEADO"
    if "READY" in status or "CREATED" in status or "CERTIFIED" in status or "CONNECTED" in status:
        return "OK"
    if "FAILED" in status or "ERROR" in status:
        return "ERRO"
    return "INFO"


st.set_page_config(page_title="K-OS Publish Audit Panel", layout="wide")

st.title("K-OS Publish Audit Panel")
st.caption("Painel visual de auditoria. Nao publica, nao usa POST, nao usa navegador logado.")

baseline = read_json(FILES["Baseline 69Z"])
ledger = read_json(FILES["Approval Ledger"])
dry_run = read_json(FILES["Publish Dry Run"])
audit = read_json(FILES["Publish Audit"])
ig_audit = read_json(FILES["Instagram Audit Hupmix"])

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Conta alvo", "hupmix")
with col2:
    st.metric("Parada Atlantida", "bloqueada")
with col3:
    st.metric("Publicacao real", "nao executada")
with col4:
    st.metric("Endpoint publish", "nao chamado")

st.subheader("Estado dos gates")

rows = [
    ("Instagram Audit", ig_audit.get("status", "UNKNOWN")),
    ("Publish Audit", audit.get("status", "UNKNOWN")),
    ("Dry Run", dry_run.get("status", "UNKNOWN")),
    ("Approval Ledger", ledger.get("status", "UNKNOWN")),
    ("Baseline 69Z", baseline.get("status", "UNKNOWN")),
]

for name, status in rows:
    st.write(f"{name}: {status_badge(str(status))} - {status}")

st.divider()

st.subheader("Comandos seguros")

st.caption("Estes comandos apenas geram auditoria/dry-run/ledger. Nao publicam.")

st.code(
    'python scripts\\run_phase69e_publish_audit_gate.py --target hupmix --campaign-id "painel-audit" --caption "rascunho seguro" --asset-ref "asset-local"',
    language="powershell",
)

st.code(
    'python scripts\\run_phase69f_human_confirmed_publish_dry_run_gate.py --target hupmix --campaign-id "painel-dry-run" --caption "rascunho seguro" --asset-ref "asset-local" --confirmation "YES_DRY_RUN_HUPMIX_PUBLISH_AUDIT_ONLY"',
    language="powershell",
)

st.code(
    'python scripts\\run_phase69g_real_publish_approval_ledger.py --target hupmix --campaign-id "painel-ledger" --caption "rascunho aprovado em ledger" --asset-ref "asset-local" --operator "operator" --approval-phrase "YES_CREATE_HUPMIX_REAL_PUBLISH_APPROVAL_LEDGER_ONLY"',
    language="powershell",
)

st.warning("69H sera o primeiro executor com POST real. Deve exigir confirmacao final explicita e Hupmix-only.")

st.subheader("Auditoria detalhada")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Instagram Audit",
    "Publish Audit",
    "Dry Run",
    "Approval Ledger",
    "Baseline",
])

with tab1:
    st.json(ig_audit)
with tab2:
    st.json(audit)
with tab3:
    st.json(dry_run)
with tab4:
    st.json(ledger)
with tab5:
    st.json(baseline)
