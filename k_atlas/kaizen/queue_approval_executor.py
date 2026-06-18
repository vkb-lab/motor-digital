from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import time
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path.cwd()
BASE = ROOT / "local_runtime" / "kos_engineer_handoff"
APPROVALS_DIR = BASE / "approvals"
APPROVALS_CONSUMED_DIR = BASE / "approvals_consumed"
STAGED_DIR = BASE / "staged_commands"
EXECUTED_DIR = BASE / "executed"
FAILED_DIR = BASE / "failed"
LOG_DIR = BASE / "logs"
STATUS_PATH = BASE / "latest_queue_approval_executor_status.json"
EVENTS_PATH = LOG_DIR / "queue_approval_executor_events.jsonl"
POLICY_PATH = ROOT / "config" / "kos_queue_approval_executor_policy.json"

REQUIRED_CONFIRMATION = "YES_EXECUTE_K_ATLAS_ENGINEER_COMMAND_LOCAL_ONLY"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_dirs() -> None:
    for path in [APPROVALS_DIR, APPROVALS_CONSUMED_DIR, STAGED_DIR, EXECUTED_DIR, FAILED_DIR, LOG_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def safe_read_approval_json(path: Path, attempts: int = 8, delay_seconds: float = 0.5) -> tuple[dict[str, Any] | None, str]:
    last_error = ""
    for _ in range(attempts):
        try:
            return read_json(path), ""
        except Exception as exc:
            last_error = str(exc)
            time.sleep(delay_seconds)
    return None, last_error


def write_event(stage: str, message: str, data: dict[str, Any] | None = None) -> None:
    ensure_dirs()
    payload = {
        "stage": stage,
        "message": message,
        "data": data or {},
        "created_at": now_iso(),
    }
    with EVENTS_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
    print(f"[KOS][{stage}] {message}", flush=True)


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "yes", "sim"}
    return False


def resolve_under_root(path_value: str | None) -> Path | None:
    if not path_value:
        return None
    candidate = Path(path_value)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    try:
        resolved = candidate.resolve()
        root_resolved = ROOT.resolve()
        if root_resolved not in [resolved, *resolved.parents]:
            return None
        return resolved
    except Exception:
        return None


def list_staged_jsons() -> list[Path]:
    ensure_dirs()
    return sorted(STAGED_DIR.glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True)


def find_staged_json(approval: dict[str, Any], approval_path: Path) -> Path | None:
    direct = approval.get("staged_json_path") or approval.get("staged_json")
    direct_path = resolve_under_root(str(direct)) if direct else None
    if direct_path and direct_path.exists() and direct_path.suffix.lower() == ".json":
        return direct_path

    staged_id = str(approval.get("staged_id") or approval.get("command_id") or "").strip()
    command_hash = str(approval.get("command_hash") or "").strip()

    for staged in list_staged_jsons():
        try:
            data = read_json(staged)
        except Exception:
            continue

        if staged_id and staged.stem == staged_id:
            return staged

        if staged_id and staged.name == staged_id:
            return staged

        if command_hash and str(data.get("command_hash") or "").strip() == command_hash:
            return staged

    approval_stem = approval_path.stem
    for staged in list_staged_jsons():
        if staged.stem == approval_stem:
            return staged

    return None


def execution_marker_paths(command_key: str) -> tuple[Path, Path]:
    return EXECUTED_DIR / f"{command_key}.json", FAILED_DIR / f"{command_key}.json"


def command_key_for(staged_json: Path, staged_payload: dict[str, Any], ps1_path: Path) -> str:
    command_hash = str(staged_payload.get("command_hash") or "").strip()
    if command_hash:
        return command_hash[:24].upper()

    try:
        return file_hash(ps1_path)[:24].upper()
    except Exception:
        return staged_json.stem


def validate_approval(approval: dict[str, Any]) -> tuple[bool, str]:
    confirmation = str(approval.get("confirmation") or "").strip()
    approved_by = str(approval.get("approved_by") or "").strip()

    if confirmation != REQUIRED_CONFIRMATION:
        return False, "invalid_confirmation"

    if not approved_by:
        return False, "missing_approved_by"

    return True, "approval_valid"


def validate_staged(staged_payload: dict[str, Any], ps1_path: Path) -> tuple[bool, str]:
    safe = normalize_bool(staged_payload.get("safe_for_confirmed_execution"))
    if not safe:
        safe = normalize_bool(staged_payload.get("safe"))

    if not safe:
        return False, "staged_command_not_marked_safe"

    if not ps1_path.exists():
        return False, "ps1_path_missing"

    try:
        resolved = ps1_path.resolve()
        staged_resolved = STAGED_DIR.resolve()
        if staged_resolved not in [resolved, *resolved.parents]:
            return False, "ps1_path_outside_staged_dir"
    except Exception:
        return False, "ps1_path_resolution_failed"

    return True, "staged_valid"


def move_approval(path: Path, target_dir: Path, suffix: str) -> Path:
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / f"{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{suffix}_{path.name}"
    shutil.move(str(path), str(target))
    return target


def execute_one_approval(approval_path: Path) -> dict[str, Any]:
    write_event("APPROVAL_FOUND", "Approval encontrado", {"approval": str(approval_path)})

    approval, approval_error = safe_read_approval_json(approval_path)
    if approval is None:
        failed = {
            "status": "KOS_QUEUE_APPROVAL_EXECUTOR_APPROVAL_INVALID_JSON",
            "approval_path": str(approval_path),
            "error": approval_error,
            "guard": "safe_read_approval_json_retry_exhausted",
            "created_at": now_iso(),
        }
        write_json(FAILED_DIR / f"{approval_path.stem}_invalid_approval.json", failed)
        move_approval(approval_path, FAILED_DIR, "invalid_approval")
        return failed

    approval_valid, approval_reason = validate_approval(approval)
    if not approval_valid:
        failed = {
            "status": "KOS_QUEUE_APPROVAL_EXECUTOR_APPROVAL_REJECTED",
            "approval_path": str(approval_path),
            "reason": approval_reason,
            "created_at": now_iso(),
        }
        write_json(FAILED_DIR / f"{approval_path.stem}_rejected.json", failed)
        move_approval(approval_path, FAILED_DIR, "rejected")
        write_event("APPROVAL_REJECTED", "Approval rejeitado", failed)
        return failed

    staged_json = find_staged_json(approval, approval_path)
    if not staged_json:
        failed = {
            "status": "KOS_QUEUE_APPROVAL_EXECUTOR_STAGED_NOT_FOUND",
            "approval_path": str(approval_path),
            "created_at": now_iso(),
        }
        write_json(FAILED_DIR / f"{approval_path.stem}_staged_missing.json", failed)
        move_approval(approval_path, FAILED_DIR, "staged_missing")
        write_event("STAGED_NOT_FOUND", "Staged command nao encontrado", failed)
        return failed

    staged_payload = read_json(staged_json)

    ps1_raw = staged_payload.get("ps1_path")
    ps1_path = resolve_under_root(str(ps1_raw)) if ps1_raw else staged_json.with_suffix(".ps1")

    if ps1_path is None:
        ps1_path = staged_json.with_suffix(".ps1")

    staged_valid, staged_reason = validate_staged(staged_payload, ps1_path)
    if not staged_valid:
        failed = {
            "status": "KOS_QUEUE_APPROVAL_EXECUTOR_STAGED_REJECTED",
            "approval_path": str(approval_path),
            "staged_json": str(staged_json),
            "ps1_path": str(ps1_path),
            "reason": staged_reason,
            "created_at": now_iso(),
        }
        write_json(FAILED_DIR / f"{approval_path.stem}_staged_rejected.json", failed)
        move_approval(approval_path, FAILED_DIR, "staged_rejected")
        write_event("STAGED_REJECTED", "Staged command rejeitado", failed)
        return failed

    command_key = command_key_for(staged_json, staged_payload, ps1_path)
    executed_marker, failed_marker = execution_marker_paths(command_key)

    if executed_marker.exists():
        duplicate = {
            "status": "KOS_QUEUE_APPROVAL_EXECUTOR_DUPLICATE_SKIPPED",
            "approval_path": str(approval_path),
            "staged_json": str(staged_json),
            "command_key": command_key,
            "existing_execution": str(executed_marker),
            "created_at": now_iso(),
        }
        move_approval(approval_path, APPROVALS_CONSUMED_DIR, "duplicate")
        write_event("DUPLICATE_SKIPPED", "Comando ja executado anteriormente", duplicate)
        return duplicate

    command = [
        "powershell",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        "scripts\\run_phase66_engineer_command_confirmed.ps1",
        "-CommandFile",
        str(ps1_path),
        "-Confirmation",
        REQUIRED_CONFIRMATION,
    ]

    write_event("EXECUTION_STARTED", "Executando staged command aprovado", {
        "approval": str(approval_path),
        "staged_json": str(staged_json),
        "ps1_path": str(ps1_path),
        "command_key": command_key,
    })

    completed = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=600,
        check=False,
    )

    result = {
        "status": "KOS_QUEUE_APPROVAL_EXECUTOR_EXECUTED" if completed.returncode == 0 else "KOS_QUEUE_APPROVAL_EXECUTOR_FAILED",
        "returncode": completed.returncode,
        "approval_path": str(approval_path),
        "staged_json": str(staged_json),
        "ps1_path": str(ps1_path),
        "command_key": command_key,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "approved_by": approval.get("approved_by"),
        "confirmation": approval.get("confirmation"),
        "real_action_executed": True,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "browser_logged_account_automation_used": False,
        "created_at": now_iso(),
    }

    if completed.returncode == 0:
        write_json(executed_marker, result)
        move_approval(approval_path, APPROVALS_CONSUMED_DIR, "executed")
        write_event("EXECUTION_COMPLETED", "Comando aprovado executado com sucesso", {
            "command_key": command_key,
            "marker": str(executed_marker),
        })
    else:
        write_json(failed_marker, result)
        move_approval(approval_path, FAILED_DIR, "execution_failed")
        write_event("EXECUTION_FAILED", "Comando aprovado falhou", {
            "command_key": command_key,
            "marker": str(failed_marker),
            "returncode": completed.returncode,
        })

    return result


def process_approvals(limit: int = 5) -> dict[str, Any]:
    ensure_dirs()

    approval_files = sorted(
        [item for item in APPROVALS_DIR.glob("*.json") if not item.name.endswith(".tmp.json")],
        key=lambda item: item.stat().st_mtime,
    )

    processed: list[dict[str, Any]] = []
    for approval in approval_files[:limit]:
        processed.append(execute_one_approval(approval))

    status = {
        "status": "KOS_QUEUE_APPROVAL_EXECUTOR_STATUS",
        "pending_approval_count": len(list(APPROVALS_DIR.glob("*.json"))),
        "processed_count": len(processed),
        "processed": processed,
        "executed_count_total": len(list(EXECUTED_DIR.glob("*.json"))),
        "failed_count_total": len(list(FAILED_DIR.glob("*.json"))),
        "real_action_executed": any(item.get("status") == "KOS_QUEUE_APPROVAL_EXECUTOR_EXECUTED" for item in processed),
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "browser_logged_account_automation_used": False,
        "created_at": now_iso(),
    }

    write_json(STATUS_PATH, status)
    return status


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()

    status = process_approvals(limit=args.limit)
    print(json.dumps(status, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
