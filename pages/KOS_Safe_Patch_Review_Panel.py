from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]

PROPOSALS_DIR = ROOT / "local_runtime" / "kos_safe_patch_proposals" / "proposals"
DIFFS_DIR = ROOT / "local_runtime" / "kos_safe_patch_proposals" / "diffs"
LATEST = ROOT / "local_runtime" / "kos_safe_patch_proposals" / "latest_safe_patch_proposal.json"


def read_json(path: Path) -> dict:
    if not path.exists():
        return {"status": "FILE_NOT_FOUND", "path": str(path)}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        return {"status": "READ_FAILED", "path": str(path), "error": str(exc)}


def read_text(path: Path) -> str:
    if not path.exists():
        return "FILE_NOT_FOUND"
    try:
        return path.read_text(encoding="utf-8-sig", errors="replace")
    except Exception as exc:
        return f"READ_FAILED: {exc}"


def list_proposals() -> list[Path]:
    if not PROPOSALS_DIR.exists():
        return []
    return sorted(PROPOSALS_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)


st.set_page_config(page_title="K-OS Safe Patch Review", layout="wide")

st.title("K-OS Safe Patch Review Panel")
st.caption("Painel de revisão. Não aplica patch. Não altera arquivos alvo. Não executa comandos.")

proposals = list_proposals()
latest = read_json(LATEST)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Propostas", len(proposals))
with col2:
    st.metric("Patch automático", "bloqueado")
with col3:
    st.metric("Revisão humana", "obrigatória")
with col4:
    st.metric("Aplicação", "fase futura")

st.warning("Este painel é somente leitura. Aplicar patch deve exigir gate futuro explícito.")

st.subheader("Última proposta")
st.json(latest)

proposal_names = [p.name for p in proposals]

if proposal_names:
    selected_name = st.selectbox("Selecionar proposta", proposal_names)
    selected_path = PROPOSALS_DIR / selected_name
    proposal = read_json(selected_path)

    st.subheader("Resumo da proposta")
    st.json({
        "status": proposal.get("status"),
        "proposal_id": proposal.get("proposal_id"),
        "objective": proposal.get("objective"),
        "diff_count": proposal.get("diff_count"),
        "patch_applied": proposal.get("patch_applied"),
        "target_file_modified": proposal.get("target_file_modified"),
        "operator_review_required": proposal.get("operator_review_required"),
        "apply_requires_future_gate": proposal.get("apply_requires_future_gate"),
    })

    st.subheader("Arquivos analisados")
    st.json(proposal.get("file_snapshots", []))

    diff_file = DIFFS_DIR / (selected_path.stem + ".diff")
    st.subheader("Diff proposto")
    st.code(read_text(diff_file), language="diff")

    st.subheader("Comando para gerar nova proposta")
    st.code(
        'python scripts\\run_phase70a_safe_patch_proposer.py --objective "descreva a melhoria" --files README.md pages\\KOS_User_Launcher.py',
        language="powershell",
    )
else:
    st.info("Nenhuma proposta encontrada ainda.")

st.subheader("Governança")
st.json({
    "mode": "review_only",
    "patch_application_enabled": False,
    "target_file_modified": False,
    "auto_execution_enabled": False,
    "operator_review_required": True,
    "apply_requires_future_gate": True,
    "production_publish_locked": True,
    "paid_ai_locked": True,
    "instagram_publish_executed": False,
    "browser_logged_account_automation_used": False,
})
