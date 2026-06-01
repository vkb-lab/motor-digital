from pathlib import Path
import json
from datetime import datetime, timezone
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[2]
DRY_RUN_DIR = ROOT / "reports" / "google_business_dry_runs"
DRY_RUN_DIR.mkdir(parents=True, exist_ok=True)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_id(value: str) -> str:
    return str(value or "item").lower().replace(" ", "_").replace("/", "_").replace("\\", "_")


def save_dry_run_receipt(kind: str, client_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    receipt = {
        "status": "PENDING_APPROVAL",
        "mode": "DRY_RUN",
        "provider": "google_business",
        "kind": kind,
        "client_id": client_id,
        "external_call_executed": False,
        "created_at": utc_now(),
        "payload": payload,
    }
    filename = f"{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}_{_safe_id(client_id)}_{_safe_id(kind)}.json"
    path = DRY_RUN_DIR / filename
    path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding="utf-8")
    receipt["receipt_path"] = str(path)
    return receipt


class GoogleBusinessDryRunGateway:
    def __init__(self, client_id: str = "parada_atlantida"):
        self.client_id = client_id

    def submit(self, kind: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return save_dry_run_receipt(kind, self.client_id, payload)

    def dry_run(self, kind: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self.submit(kind, payload)
