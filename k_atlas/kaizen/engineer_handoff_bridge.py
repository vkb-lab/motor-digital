
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
import uuid
import hashlib

ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ROOT / "local_runtime" / "kos_engineer_handoff"
STAGED = RUNTIME / "staged_commands"
LOGS = RUNTIME / "logs"
LATEST = RUNTIME / "latest_engineer_handoff_status.json"
EVENTS = LOGS / "events.jsonl"
REVIEW = ROOT / "local_runtime" / "kos_local_review_inbox" / "latest_review_inbox.json"

CONFIRMATION_PHRASE = "YES_EXECUTE_K_ATLAS_ENGINEER_COMMAND_LOCAL_ONLY"

BLOCKED_TERMS = [
    "invoke" + "-webrequest",
    "invoke" + "-restmethod",
    "curl.exe",
    "wget.exe",
    "graph.facebook.com",
    "paid_ai_allowed=$" + "true",
    "instagram_publish_allowed=$" + "true",
    "deploy_allowed=$" + "true",
    "format-volume",
    "clear-disk",
    "restart-computer",
    "stop-computer",
]

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        return {"status": "JSON_READ_ERROR", "error": str(exc), "path": str(path)}

def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def append_event(data: dict) -> None:
    EVENTS.parent.mkdir(parents=True, exist_ok=True)
    with EVENTS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")

def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT.resolve())).replace("\\", "/")
    except Exception:
        return path.as_posix().replace("\\", "/")


def compute_engineer_command_hash(command_text: str) -> str:
    normalized = "\n".join([line.rstrip() for line in (command_text or "").strip().splitlines()])
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

def find_existing_staged_command_by_hash(command_hash: str) -> dict | None:
    if not STAGED.exists():
        return None
    for path in sorted(STAGED.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        data = read_json(path)
        if data.get("command_hash") == command_hash:
            return data
    return None

def extract_powershell_command(response_text: str) -> str:
    text = response_text or ""
    marker = "$ErrorActionPreference"
    if marker in text:
        return text[text.index(marker):].strip()
    if "Set-Location" in text or "Write-Host" in text:
        return text.strip()
    return ""

def scan_engineer_command(command_text: str) -> dict:
    command = command_text or ""
    lower = command.lower()
    findings = []

    if not command.strip():
        findings.append({"type": "empty_command"})

    for term in BLOCKED_TERMS:
        if term.lower() in lower:
            findings.append({"type": "blocked_term", "value": term})

    return {
        "status": "ENGINEER_COMMAND_SCAN_SAFE" if not findings else "ENGINEER_COMMAND_SCAN_BLOCKED",
        "safe": len(findings) == 0,
        "findings": findings,
        "lines_count": len([x for x in command.splitlines() if x.strip()]),
        "chars_count": len(command),
        "confirmation_required": CONFIRMATION_PHRASE,
        "created_at": now(),
    }

def build_engineer_prompt_from_review() -> dict:
    review = read_json(REVIEW)
    bundle = (review.get("review_bundle") or {}).get("bundle_text") or ""

    prompt = "\n".join([
        "K-Atlas Engineer, receba este bundle do K-OS Local Coworker.",
        "",
        "Gere um comando PowerShell completo, seguro e pronto para copiar.",
        "",
        "Regras:",
        "- Windows PowerShell",
        "- UTF-8",
        "- bloco unico",
        "- sem IA paga",
        "- sem Instagram",
        "- sem deploy",
        "- sem navegador logado",
        "- com testes, firewall, commit e push quando aplicavel",
        "",
        "Bundle:",
        "",
        bundle or "Nenhum bundle disponivel."
    ])

    return {
        "status": "KOS_ENGINEER_PROMPT_READY",
        "prompt_text": prompt,
        "has_review_bundle": bool(bundle),
        "real_action_executed": False,
        "created_at": now(),
    }

def stage_engineer_response(response_text: str, title: str = "K-Atlas Engineer Command") -> dict:
    command = extract_powershell_command(response_text)
    scan = scan_engineer_command(command)
    command_hash = compute_engineer_command_hash(command)
    existing = find_existing_staged_command_by_hash(command_hash)
    if existing:
        existing["status"] = "KOS_ENGINEER_COMMAND_DUPLICATE_SKIPPED"
        existing["duplicate_skipped"] = True
        existing["execution_allowed_now"] = False
        existing["created_at"] = now()
        write_json(LATEST, existing)
        append_event(existing)
        return existing

    draft_id = "KOS-ENGINEER-CMD-" + uuid.uuid4().hex[:12].upper()
    ps1_path = STAGED / f"{draft_id}.ps1"
    json_path = STAGED / f"{draft_id}.json"

    write_text(ps1_path, command)

    confirmed_command = (
        "powershell -ExecutionPolicy Bypass -File scripts\\run_phase66_engineer_command_confirmed.ps1 "
        f"-CommandFile \"{rel(ps1_path)}\" "
        f"-Confirmation \"{CONFIRMATION_PHRASE}\""
    )

    payload = {
        "status": "KOS_ENGINEER_COMMAND_STAGED",
        "draft_id": draft_id,
        "title": title,
        "command_hash": command_hash,
        "ps1_path": rel(ps1_path),
        "scan": scan,
        "safe_for_confirmed_execution": scan.get("safe") is True,
        "execution_allowed_now": False,
        "confirmed_execution_command": confirmed_command,
        "confirmation_required": CONFIRMATION_PHRASE,
        "gates": {
            "execute_without_confirmation": False,
            "human_confirmation_required": True,
            "safety_scan_required": True,
            "paid_ai_allowed": False,
            "instagram_publish_allowed": False,
            "external_publish_allowed": False,
        },
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "created_at": now(),
    }

    write_json(json_path, payload)
    write_json(LATEST, payload)
    append_event(payload)
    return payload

def validate_engineer_command_file(command_file: str) -> dict:
    raw = Path(command_file)
    path = raw if raw.is_absolute() else ROOT / raw

    if not path.exists():
        return {"status": "ENGINEER_COMMAND_FILE_INVALID", "valid": False, "reason": "not_found", "path": str(path)}

    if path.suffix.lower() != ".ps1":
        return {"status": "ENGINEER_COMMAND_FILE_INVALID", "valid": False, "reason": "not_ps1", "path": str(path)}

    try:
        resolved = path.resolve()
        staged_root = STAGED.resolve()
        inside = str(resolved).lower().startswith(str(staged_root).lower())
    except Exception:
        inside = False

    if not inside:
        return {"status": "ENGINEER_COMMAND_FILE_INVALID", "valid": False, "reason": "outside_staged_dir", "path": str(path)}

    command = path.read_text(encoding="utf-8-sig")
    scan = scan_engineer_command(command)

    return {
        "status": "ENGINEER_COMMAND_FILE_VALID" if scan.get("safe") else "ENGINEER_COMMAND_FILE_BLOCKED",
        "valid": scan.get("safe") is True,
        "path": rel(path),
        "scan": scan,
        "confirmation_required": CONFIRMATION_PHRASE,
        "created_at": now(),
    }

def list_staged_engineer_commands(limit: int = 20) -> list[dict]:
    if not STAGED.exists():
        return []
    paths = sorted(STAGED.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]
    return [read_json(path) for path in paths]

def get_engineer_handoff_status() -> dict:
    prompt = build_engineer_prompt_from_review()
    staged = list_staged_engineer_commands()

    payload = {
        "status": "KOS_ENGINEER_HANDOFF_BRIDGE_READY",
        "has_review_bundle": prompt.get("has_review_bundle"),
        "staged_commands_count": len(staged),
        "latest_staged_command": staged[0] if staged else None,
        "confirmation_required": CONFIRMATION_PHRASE,
        "gates": {
            "execute_without_confirmation": False,
            "human_confirmation_required": True,
            "safety_scan_required": True,
            "paid_ai_allowed": False,
            "instagram_publish_allowed": False,
            "external_publish_allowed": False,
        },
        "real_action_executed": False,
        "created_at": now(),
    }

    write_json(LATEST, payload)
    return payload
