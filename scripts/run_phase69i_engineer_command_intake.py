from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

PACKET_START = "KOS_ENGINEER_PACKET_START"
PACKET_END = "KOS_ENGINEER_PACKET_END"

ALLOWED_ACTIONS = {
    "stage_command",
    "audit_request",
    "mission_request",
    "command_packet",
}

ALLOWED_MODES = {
    "stage_only",
    "audit_only",
    "prepare_only",
}

BLOCKED_PATTERNS = [
    "access_token",
    "meta_access_token",
    "facebook_access_token",
    "password",
    "secret",
    "api_key",
    "KOS_REAL_HUPMIX_PUBLISH_ENABLED",
    "YES_EXECUTE_REAL_HUPMIX_INSTAGRAM_PUBLISH_NOW",
    "--execute-real-publish",
    "paradaatlantida",
    "17841480166187766",
    "Remove-Item -Recurse -Force C:\\",
    "format c:",
    "Set-ExecutionPolicy Unrestricted",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def slug(value: str) -> str:
    value = value.strip() or "engineer-packet"
    value = re.sub(r"[^A-Za-z0-9_\-]+", "-", value)
    return value[:120]


def extract_packet_text(raw: str) -> str:
    text = raw.strip()

    if PACKET_START in text and PACKET_END in text:
        start = text.index(PACKET_START) + len(PACKET_START)
        end = text.index(PACKET_END)
        return text[start:end].strip()

    return text


def parse_packet(raw: str) -> dict[str, Any]:
    packet_text = extract_packet_text(raw)
    return json.loads(packet_text)


def find_blocked_patterns(value: str) -> list[str]:
    value_lower = value.lower()
    hits = []
    for pattern in BLOCKED_PATTERNS:
        if pattern.lower() in value_lower:
            hits.append(pattern)
    return hits


def validate_packet(packet: dict[str, Any]) -> dict[str, Any]:
    packet_id = slug(str(packet.get("id") or ("packet-" + datetime.now().strftime("%Y%m%d-%H%M%S"))))
    action = str(packet.get("action", "")).strip()
    mode = str(packet.get("mode", "stage_only")).strip()
    title = str(packet.get("title", "")).strip()
    command = str(packet.get("command", "")).strip()
    objective = str(packet.get("objective", "")).strip()

    raw_blob = json.dumps(packet, ensure_ascii=False)
    blocked_hits = find_blocked_patterns(raw_blob)

    base = {
        "status": "KOS_ENGINEER_COMMAND_INTAKE_PENDING",
        "phase": "69I",
        "packet_id": packet_id,
        "title": title,
        "objective": objective,
        "action": action,
        "mode": mode,
        "created_at": now_iso(),
    }

    if action not in ALLOWED_ACTIONS:
        return {
            **base,
            "status": "KOS_ENGINEER_COMMAND_INTAKE_BLOCKED",
            "reason": "action_not_allowed",
            "allowed_actions": sorted(ALLOWED_ACTIONS),
            "safe_for_auto_execution": False,
        }

    if mode not in ALLOWED_MODES:
        return {
            **base,
            "status": "KOS_ENGINEER_COMMAND_INTAKE_BLOCKED",
            "reason": "mode_not_allowed",
            "allowed_modes": sorted(ALLOWED_MODES),
            "safe_for_auto_execution": False,
        }

    if not title:
        return {
            **base,
            "status": "KOS_ENGINEER_COMMAND_INTAKE_BLOCKED",
            "reason": "missing_title",
            "safe_for_auto_execution": False,
        }

    if not command:
        return {
            **base,
            "status": "KOS_ENGINEER_COMMAND_INTAKE_BLOCKED",
            "reason": "missing_command",
            "safe_for_auto_execution": False,
        }

    if len(command) > 25000:
        return {
            **base,
            "status": "KOS_ENGINEER_COMMAND_INTAKE_BLOCKED",
            "reason": "command_too_large",
            "safe_for_auto_execution": False,
        }

    if blocked_hits:
        return {
            **base,
            "status": "KOS_ENGINEER_COMMAND_INTAKE_BLOCKED",
            "reason": "blocked_pattern_detected",
            "blocked_patterns": blocked_hits,
            "safe_for_auto_execution": False,
        }

    return {
        **base,
        "status": "KOS_ENGINEER_COMMAND_INTAKE_STAGED",
        "reason": "packet_validated_and_staged",
        "command": command,
        "operator_review_required": True,
        "safe_for_auto_execution": False,
        "execution_requires_existing_approval_pipeline": True,
        "production_publish_locked": True,
        "paid_ai_locked": True,
        "instagram_publish_executed": False,
        "browser_logged_account_automation_used": False,
        "real_action_executed": False,
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def process_raw_packet(raw: str) -> dict[str, Any]:
    try:
        packet = parse_packet(raw)
    except Exception as exc:
        result = {
            "status": "KOS_ENGINEER_COMMAND_INTAKE_BLOCKED",
            "phase": "69I",
            "reason": "packet_parse_failed",
            "error": str(exc),
            "safe_for_auto_execution": False,
            "created_at": now_iso(),
        }
        write_json(ROOT / "local_runtime" / "kos_engineer_command_intake" / "blocked" / ("parse_failed_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".json"), result)
        write_json(ROOT / "local_runtime" / "kos_engineer_command_intake" / "latest_intake_result.json", result)
        return result

    result = validate_packet(packet)

    folder = "staged" if result["status"] == "KOS_ENGINEER_COMMAND_INTAKE_STAGED" else "blocked"
    out = ROOT / "local_runtime" / "kos_engineer_command_intake" / folder / (result.get("packet_id", "packet") + ".json")

    write_json(out, result)
    write_json(ROOT / "local_runtime" / "kos_engineer_command_intake" / "latest_intake_result.json", result)

    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--text-file", required=True)
    args = parser.parse_args()

    raw = Path(args.text_file).read_text(encoding="utf-8-sig")
    result = process_raw_packet(raw)

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["status"] in {
        "KOS_ENGINEER_COMMAND_INTAKE_STAGED",
        "KOS_ENGINEER_COMMAND_INTAKE_BLOCKED",
    } else 1


if __name__ == "__main__":
    raise SystemExit(main())
