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

from .location_profile import build_profile_update_payload
from .posts import build_google_post_payload, build_offer_payload
from .reviews import build_review_reply_payload
from .media import build_media_payload


class GoogleBusinessClient:
    def __init__(self, client_id: str = "parada_atlantida", dry_run: bool = True):
        self.client_id = client_id
        self.dry_run = dry_run
        self.gateway = GoogleBusinessDryRunGateway(client_id)

    def profile_dry_run(self) -> Dict[str, Any]:
        return self.gateway.submit("profile_update", build_profile_update_payload(self.client_id))

    def update_profile(self, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
        return self.gateway.submit("profile_update", payload or build_profile_update_payload(self.client_id))

    def create_post(self, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
        return self.gateway.submit("post", payload or build_google_post_payload(self.client_id))

    def create_offer(self, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
        return self.gateway.submit("offer", payload or build_offer_payload(self.client_id))

    def reply_review(self, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
        return self.gateway.submit("review_reply", payload or build_review_reply_payload(self.client_id))

    def upload_media(self, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
        return self.gateway.submit("media", payload or build_media_payload(self.client_id))

    def dry_run_profile_update(self) -> Dict[str, Any]:
        return self.profile_dry_run()

    def dry_run_post(self) -> Dict[str, Any]:
        return self.create_post()

    def dry_run_offer(self) -> Dict[str, Any]:
        return self.create_offer()

    def dry_run_review_reply(self) -> Dict[str, Any]:
        return self.reply_review()


def create_google_business_dry_run(client_id: str = "parada_atlantida") -> Dict[str, Any]:
    client = GoogleBusinessClient(client_id=client_id, dry_run=True)
    return {
        "status": "PENDING_APPROVAL",
        "mode": "DRY_RUN",
        "client_id": client_id,
        "profile": client.profile_dry_run(),
        "post": client.create_post(),
        "offer": client.create_offer(),
        "review_reply": client.reply_review(),
    }
