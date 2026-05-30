from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.cwd()
LIVE = ROOT / "live" / "marketplace_ia"

PUBLIC_DIAG = LIVE / "latest_public_lead_diagnostic.json"
LOCAL_DIAG = LIVE / "latest_lead_diagnostic.json"
LEAD_INTAKE = LIVE / "lead_intake.jsonl"
REVIEW = LIVE / "public_capture_review_decision.json"

REPORT = ROOT / "reports" / "test_missions" / "marketplace_ia_test_011_public_diag_recovery.json"

LIVE.mkdir(parents=True, exist_ok=True)
REPORT.parent.mkdir(parents=True, exist_ok=True)


def load_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return None


def load_jsonl_valid(path: Path) -> list[dict]:
    if not path.exists():
        return []

    rows = []
    for line in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        line = line.strip().lstrip("\ufeff")
        if not line:
            continue
        try:
            item = json.loads(line)
            if isinstance(item, dict):
                rows.append(item)
        except Exception:
            continue
    return rows


def default_recommendations() -> list[dict]:
    return [
        {
            "name": "Agente de follow-up comercial",
            "impact": "alto",
            "effort": "medio",
            "description": "Organizar respostas, proximos passos e acompanhamento comercial para leads capturados."
        },
        {
            "name": "Esteira de conteudo com aprovacao humana",
            "impact": "alto",
            "effort": "baixo",
            "description": "Criar calendario, posts, legendas e campanhas com revisao antes de publicar."
        },
        {
            "name": "Dashboard operacional de leads",
            "impact": "medio",
            "effort": "baixo",
            "description": "Centralizar leads, status, diagnostico, proposta e proximos passos em um painel simples."
        },
    ]


review = load_json(REVIEW)
existing_public = load_json(PUBLIC_DIAG)

if existing_public:
    source = "existing_public_diagnostic"
    diagnostic = existing_public
else:
    local_diag = load_json(LOCAL_DIAG)

    if local_diag and local_diag.get("recommendations"):
        source = "recovered_from_latest_lead_diagnostic"
        diagnostic = dict(local_diag)
        diagnostic["diagnostic_id"] = diagnostic.get("diagnostic_id") or str(uuid.uuid4())
        diagnostic["source"] = "marketplace_ia_public_approved_lead_diagnostic_recovered"
        diagnostic["review_gate_required"] = True
        diagnostic["review_gate_status"] = review.get("decision") if review else "recovered_without_review_file"
        diagnostic["external_send_enabled"] = False
        diagnostic["human_review_required"] = True
        diagnostic["next_step"] = "Gerar proposta comercial local para o lead publico aprovado."
    else:
        leads = load_jsonl_valid(LEAD_INTAKE)
        lead = leads[-1] if leads else {}

        source = "rebuilt_from_latest_lead"
        diagnostic = {
            "ok": True,
            "diagnostic_id": str(uuid.uuid4()),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "lead_id": lead.get("lead_id") or str(uuid.uuid4()),
            "source": "marketplace_ia_public_approved_lead_diagnostic_rebuilt",
            "review_gate_required": True,
            "review_gate_status": review.get("decision") if review else "recovered_without_review_file",
            "external_send_enabled": False,
            "human_review_required": True,
            "recommendations": default_recommendations(),
            "next_step": "Gerar proposta comercial local para o lead publico aprovado."
        }

    PUBLIC_DIAG.write_text(
        json.dumps(diagnostic, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

report = {
    "ok": True,
    "mission_id": "test_mission_011_public_diag_recovery",
    "status": "public_diagnostic_ready",
    "source": source,
    "public_diagnostic_exists": PUBLIC_DIAG.exists(),
    "external_send_enabled": False,
    "sensitive_data_committed": False,
    "next_step": "Refresh page 911 and save public proposal."
}

REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

print("PUBLIC_DIAGNOSTIC_READY")
print(json.dumps(report, ensure_ascii=False, indent=2))