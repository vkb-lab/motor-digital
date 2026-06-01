from pathlib import Path
import json

from k_atlas.safe_execution.human_greenlight import build_human_decision
from k_atlas.safe_execution.channel_queue import build_channel_queue
from k_atlas.safe_execution.channel_executor import execute_safe_channel_task
from k_atlas.safe_execution.receipt_store import save_safe_receipts
from k_atlas.safe_execution.final_review import build_safe_execution_review

ROOT = Path(__file__).resolve().parents[2]

def run_approved_safe_execution(client_id: str = "parada_atlantida", campaign_name: str = "campanha_lancamento_parada_atlantida", decision: str = "OK"):
    human_decision = build_human_decision(client_id, campaign_name, decision)

    if not human_decision["safe_execution_allowed"]:
        result = {
            "status": "BLOCKED_BY_HUMAN_DECISION",
            "client_id": client_id,
            "campaign_name": campaign_name,
            "decision": human_decision,
            "real_action_executed": False,
        }
    else:
        queue = build_channel_queue(client_id, campaign_name)
        receipts_list = [execute_safe_channel_task(task) for task in queue["items"]]
        receipts = save_safe_receipts(client_id, campaign_name, receipts_list)
        review = build_safe_execution_review(client_id, campaign_name, human_decision, queue, receipts)

        result = {
            "status": "SAFE_EXECUTION_COMPLETED",
            "client_id": client_id,
            "campaign_name": campaign_name,
            "decision": human_decision,
            "queue": queue,
            "receipts": receipts,
            "review": review,
            "real_action_executed": False,
            "external_call_executed": False,
        }

    out = ROOT / "reports" / "KOS_PHASE9_SAFE_EXECUTION_DEMO.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result
