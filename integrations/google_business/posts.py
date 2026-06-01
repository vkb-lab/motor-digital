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


def build_google_post_payload(client_id: str = "parada_atlantida", title: str = "Experiencia Parada Atlantida") -> Dict[str, Any]:
    return {
        "action": "google_business_post",
        "client_id": client_id,
        "title": title,
        "summary": "Conheca experiencias locais, cupons e roteiros selecionados pela Parada Atlantida.",
        "cta": "Saiba mais",
        "status": "PENDING_APPROVAL",
        "manual_approval_required": True,
    }


def build_offer_payload(client_id: str = "parada_atlantida", title: str = "Oferta Parada Atlantida") -> Dict[str, Any]:
    return {
        "action": "google_business_offer",
        "client_id": client_id,
        "title": title,
        "description": "Oferta promocional em modo rascunho para aprovacao manual.",
        "coupon_code": "PARADA10",
        "status": "PENDING_APPROVAL",
        "manual_approval_required": True,
    }


def create_post_dry_run(client_id: str = "parada_atlantida") -> Dict[str, Any]:
    return save_dry_run_receipt("post", client_id, build_google_post_payload(client_id))


def create_offer_dry_run(client_id: str = "parada_atlantida") -> Dict[str, Any]:
    return save_dry_run_receipt("offer", client_id, build_offer_payload(client_id))
