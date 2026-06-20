from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

STAGED_DIR = ROOT / "local_runtime" / "kos_engineer_command_intake" / "staged"
PROMOTED_DIR = ROOT / "local_runtime" / "kos_engineer_command_intake" / "promoted"
HANDOFF_INBOX = ROOT / "local_runtime" / "kos_engineer_handoff" / "inbox"

BLOCKED_TERMS = [
    "access_token",
    "secret",
    "password",
    "api_key",
    "paradaatlantida",
    "17841480166187766",
    "KOS_REAL_HUPMIX_PUBLISH_ENABLED",
    "YES_EXECUTE_REAL_HUPMIX_INSTAGRAM_PUBLISH_NOW",
    "--execute-real-publish",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def slug(value: str) -> str:
    value = value.strip() or "engineer-packet"
    value = re.sub(r"[^A-Za-z0-9_\-]+", "-", value)
    return value[:120]


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def find_latest_staged() -> Path | None:
    files = sorted(STAGED_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None


def blocked_hits(payload: dict[str, Any]) -> list[str]:
    blob = json.dumps(payload, ensure_ascii=False).lower()
    return [term for term in BLOCKED_TERMS if term.lower() in blob]


def promote_packet(packet_path: Path | None = None) -> dict[str, Any]:
    if packet_path is None:
        packet_path = find_latest_staged()

    if packet_path is None or not packet_path.exists():
        return {
            "status": "KOS_ENGINEER_PACKET_PROMOTION_BLOCKED",
            "phase": "69J",
            "reason": "no_staged_packet_found",
            "created_at": now_iso(),
        }

    packet = read_json(packet_path)
    packet_id = slug(str(packet.get("packet_id") or packet_path.stem))
    command = str(packet.get("command", "")).strip()

    if packet.get("status") != "KOS_ENGINEER_COMMAND_INTAKE_STAGED":
        return {
            "status": "KOS_ENGINEER_PACKET_PROMOTION_BLOCKED",
            "phase": "69J",
            "reason": "packet_not_staged",
            "packet_id": packet_id,
            "source": str(packet_path),
            "created_at": now_iso(),
        }

    hits = blocked_hits(packet)
    if hits:
        return {
            "status": "KOS_ENGINEER_PACKET_PROMOTION_BLOCKED",
            "phase": "69J",
            "reason": "blocked_pattern_detected",
            "blocked_patterns": hits,
            "packet_id": packet_id,
            "source": str(packet_path),
            "created_at": now_iso(),
        }

    if not command:
        return {
            "status": "KOS_ENGINEER_PACKET_PROMOTION_BLOCKED",
            "phase": "69J",
            "reason": "missing_command",
            "packet_id": packet_id,
            "source": str(packet_path),
            "created_at": now_iso(),
        }

    command_hash = sha256_text(command)

    handoff_payload = {
        "status": "KOS_ENGINEER_HANDOFF_INBOX_REQUEST",
        "source_phase": "69J",
        "packet_id": packet_id,
        "title": packet.get("title"),
        "objective": packet.get("objective"),
        "command": command,
        "command_hash": command_hash,
        "mode": "stage_for_existing_handoff_pipeline",
        "operator_review_required": True,
        "safe_for_auto_execution": False,
        "execution_requires_approval_pipeline": True,
        "production_publish_locked": True,
        "paid_ai_locked": True,
        "instagram_publish_executed": False,
        "browser_logged_account_automation_used": False,
        "real_action_executed": False,
        "created_at": now_iso(),
    }

    out = HANDOFF_INBOX / f"engineer_packet_{packet_id}_{command_hash[:12]}.json"
    write_json(out, handoff_payload)

    promotion = {
        "status": "KOS_ENGINEER_PACKET_PROMOTED_TO_HANDOFF_INBOX",
        "phase": "69J",
        "packet_id": packet_id,
        "source": str(packet_path),
        "handoff_inbox_file": str(out),
        "command_hash": command_hash,
        "auto_execution_enabled": False,
        "operator_review_required": True,
        "created_at": now_iso(),
    }

    write_json(PROMOTED_DIR / f"{packet_id}.json", promotion)
    write_json(ROOT / "local_runtime" / "kos_engineer_command_intake" / "latest_promotion_result.json", promotion)

    return promotion


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet-file", default="")
    args = parser.parse_args()

    packet_path = Path(args.packet_file) if args.packet_file else None
    result = promote_packet(packet_path)

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["status"] in {
        "KOS_ENGINEER_PACKET_PROMOTED_TO_HANDOFF_INBOX",
        "KOS_ENGINEER_PACKET_PROMOTION_BLOCKED",
    } else 1


if __name__ == "__main__":
    raise SystemExit(main())
