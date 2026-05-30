from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.cwd()
LIVE = ROOT / "live" / "marketplace_ia"
PUBLIC_QUEUE = LIVE / "public_capture_queue.jsonl"
LEAD_INTAKE = LIVE / "lead_intake.jsonl"
REPORT = ROOT / "reports" / "test_missions" / "marketplace_ia_test_009_queue_recovery.json"

LIVE.mkdir(parents=True, exist_ok=True)
REPORT.parent.mkdir(parents=True, exist_ok=True)


def read_jsonl_valid(path: Path) -> list[dict]:
    if not path.exists():
        return []

    rows: list[dict] = []

    text = path.read_text(encoding="utf-8-sig", errors="replace")

    for line in text.splitlines():
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


public_rows = read_jsonl_valid(PUBLIC_QUEUE)

if public_rows:
    source = "existing_public_queue"
    created = False
    recovered = public_rows[-1]
else:
    lead_rows = read_jsonl_valid(LEAD_INTAKE)

    if lead_rows:
        base = lead_rows[-1]
        source = "recovered_from_lead_intake"
        recovered = {
            "lead_id": base.get("lead_id") or str(uuid.uuid4()),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "nome": base.get("nome", ""),
            "contato": base.get("contato", ""),
            "negocio": base.get("negocio", ""),
            "segmento": base.get("segmento", "Outro"),
            "objetivo": base.get("objetivo", "Organizar operacao"),
            "desafio": base.get("desafio", "Captura publica recuperada para validar o review gate."),
            "source": "public_capture_recovered_from_local_lead_intake",
            "status": "captured_public_local_only_recovered",
            "external_send_enabled": False,
            "human_review_required": True,
        }
    else:
        source = "synthetic_safe_local_capture"
        recovered = {
            "lead_id": str(uuid.uuid4()),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "nome": "Teste Local",
            "contato": "teste-local",
            "negocio": "Marketplace IA Teste",
            "segmento": "Outro",
            "objetivo": "Organizar operacao",
            "desafio": "Captura publica recriada localmente para validar o review gate 009.",
            "source": "public_capture_synthetic_safe_local",
            "status": "captured_public_local_only_recovered",
            "external_send_enabled": False,
            "human_review_required": True,
        }

    PUBLIC_QUEUE.write_text(
        json.dumps(recovered, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    created = True

report = {
    "ok": True,
    "mission_id": "test_mission_009_queue_recovery",
    "status": "public_capture_queue_ready",
    "source": source,
    "created_queue": created,
    "public_queue_exists": PUBLIC_QUEUE.exists(),
    "public_queue_valid_rows": len(read_jsonl_valid(PUBLIC_QUEUE)),
    "lead_intake_valid_rows": len(read_jsonl_valid(LEAD_INTAKE)),
    "sensitive_data_committed": False,
    "external_send_enabled": False,
    "next_step": "Refresh page 009 and approve public capture.",
}

REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

print("QUEUE_009_READY")
print(json.dumps(report, ensure_ascii=False, indent=2))