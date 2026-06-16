from pathlib import Path
import sys
import json

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from k_atlas.kaizen.evidence_ledger import append_evidence, summarize_evidence

if __name__ == "__main__":
    entry = append_evidence(
        source="phase48_runner",
        note="Registro manual da Fase 48.",
        extra={"phase": "48"}
    )

    summary = summarize_evidence(limit=10)

    print(json.dumps({
        "status": "PHASE48_EVIDENCE_LEDGER_RECORDED",
        "evidence_id": entry.get("evidence_id"),
        "summary": summary,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False
    }, ensure_ascii=False, indent=2))
