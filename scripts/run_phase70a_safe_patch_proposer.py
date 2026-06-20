from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

BLOCKED_PATH_PARTS = {
    ".git",
    "local_runtime/kos_secrets",
    "local_runtime/secrets",
    "memory/security",
    ".env",
    "credentials",
    "tokens",
    "secrets",
}

BLOCKED_OBJECTIVE_TERMS = {
    "access_token",
    "password",
    "secret",
    "api_key",
    "paradaatlantida",
    "17841480166187766",
    "--execute-real-publish",
    "KOS_REAL_HUPMIX_PUBLISH_ENABLED",
    "YES_EXECUTE_REAL_HUPMIX_INSTAGRAM_PUBLISH_NOW",
}

DEFAULT_FILES = [
    "README.md",
    "docs/KOS_ENGINEER_PACKET_GOVERNANCE_BASELINE_V0691.md",
    "pages/KOS_User_Launcher.py",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def slug(value: str) -> str:
    value = value.strip() or "safe-patch-proposal"
    value = re.sub(r"[^A-Za-z0-9_\-]+", "-", value)
    return value[:120]


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()


def normalize_relpath(value: str) -> str:
    return value.replace("\\", "/").strip().lstrip("/")


def is_blocked_path(relpath: str) -> bool:
    rel = normalize_relpath(relpath).lower()
    return any(part.lower() in rel for part in BLOCKED_PATH_PARTS)


def blocked_terms_in_text(value: str) -> list[str]:
    low = value.lower()
    return sorted([term for term in BLOCKED_OBJECTIVE_TERMS if term.lower() in low])


def read_file_snapshot(relpath: str) -> dict[str, Any]:
    rel = normalize_relpath(relpath)

    if is_blocked_path(rel):
        return {
            "path": rel,
            "status": "BLOCKED_PATH",
            "exists": False,
            "reason": "path_blocked_by_policy",
        }

    path = (ROOT / rel).resolve()

    if not str(path).startswith(str(ROOT.resolve())):
        return {
            "path": rel,
            "status": "BLOCKED_PATH",
            "exists": False,
            "reason": "path_outside_repo",
        }

    if not path.exists():
        return {
            "path": rel,
            "status": "FILE_NOT_FOUND",
            "exists": False,
        }

    if path.is_dir():
        return {
            "path": rel,
            "status": "DIRECTORY_SKIPPED",
            "exists": True,
        }

    try:
        text = path.read_text(encoding="utf-8-sig", errors="replace")
    except Exception as exc:
        return {
            "path": rel,
            "status": "READ_FAILED",
            "exists": True,
            "error": str(exc),
        }

    lines = text.splitlines()

    return {
        "path": rel,
        "status": "SNAPSHOT_READY",
        "exists": True,
        "sha256": sha256_text(text),
        "size_chars": len(text),
        "line_count": len(lines),
        "preview_lines": lines[:25],
    }


def proposed_append_block(objective: str, relpath: str) -> list[str]:
    if relpath.lower().endswith(".md"):
        return [
            "",
            "## K-OS Safe Patch Proposal",
            "",
            f"Objective: {objective}",
            "",
            "Status: proposal only. Human review required before applying.",
        ]

    if relpath.lower().endswith(".py"):
        return [
            "",
            "# KOS_SAFE_PATCH_PROPOSAL_START",
            f"# Objective: {objective}",
            "# Proposal only. Do not apply automatically.",
            "# KOS_SAFE_PATCH_PROPOSAL_END",
        ]

    return [
        "",
        f"# KOS safe patch proposal: {objective}",
        "# Proposal only. Human review required.",
    ]


def build_unified_diff(snapshot: dict[str, Any], objective: str) -> str:
    relpath = snapshot["path"]

    if snapshot.get("status") != "SNAPSHOT_READY":
        return ""

    original = snapshot.get("preview_lines", [])
    proposed = list(original) + proposed_append_block(objective, relpath)

    diff = difflib.unified_diff(
        original,
        proposed,
        fromfile=f"a/{relpath}",
        tofile=f"b/{relpath}",
        lineterm="",
    )

    return "\n".join(diff)


def build_patch_proposal(objective: str, files: list[str], proposal_id: str = "") -> dict[str, Any]:
    proposal_id = slug(proposal_id or ("70A-" + datetime.now().strftime("%Y%m%d-%H%M%S")))

    objective_hits = blocked_terms_in_text(objective)
    path_hits = [f for f in files if is_blocked_path(f)]

    if objective_hits or path_hits:
        return {
            "status": "KOS_SAFE_PATCH_PROPOSAL_BLOCKED",
            "phase": "70A",
            "proposal_id": proposal_id,
            "objective": objective,
            "reason": "blocked_terms_or_paths_detected",
            "blocked_objective_terms": objective_hits,
            "blocked_paths": path_hits,
            "target_file_modified": False,
            "patch_applied": False,
            "auto_execution_enabled": False,
            "created_at": now_iso(),
        }

    snapshots = [read_file_snapshot(f) for f in files]
    diffs = []

    for snap in snapshots:
        diff = build_unified_diff(snap, objective)
        if diff:
            diffs.append({
                "path": snap["path"],
                "diff": diff,
            })

    patch_text_parts = [
        "# K-OS SAFE PATCH PROPOSAL",
        "# DO_NOT_APPLY_AUTOMATICALLY",
        f"# proposal_id: {proposal_id}",
        f"# objective: {objective}",
        "",
    ]

    for item in diffs:
        patch_text_parts.append(item["diff"])
        patch_text_parts.append("")

    patch_text = "\n".join(patch_text_parts)

    proposal = {
        "status": "KOS_SAFE_PATCH_PROPOSAL_READY",
        "phase": "70A",
        "proposal_id": proposal_id,
        "objective": objective,
        "files_requested": files,
        "file_snapshots": snapshots,
        "diff_count": len(diffs),
        "diffs": diffs,
        "patch_text_sha256": sha256_text(patch_text),
        "operator_review_required": True,
        "apply_requires_future_gate": True,
        "target_file_modified": False,
        "patch_applied": False,
        "auto_execution_enabled": False,
        "production_publish_locked": True,
        "paid_ai_locked": True,
        "instagram_publish_executed": False,
        "browser_logged_account_automation_used": False,
        "real_action_executed": False,
        "created_at": now_iso(),
    }

    proposal_dir = ROOT / "local_runtime" / "kos_safe_patch_proposals" / "proposals"
    diff_dir = ROOT / "local_runtime" / "kos_safe_patch_proposals" / "diffs"

    proposal_dir.mkdir(parents=True, exist_ok=True)
    diff_dir.mkdir(parents=True, exist_ok=True)

    (proposal_dir / f"{proposal_id}.json").write_text(
        json.dumps(proposal, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    (diff_dir / f"{proposal_id}.diff").write_text(patch_text, encoding="utf-8")

    latest = ROOT / "local_runtime" / "kos_safe_patch_proposals" / "latest_safe_patch_proposal.json"
    latest.write_text(json.dumps(proposal, indent=2, ensure_ascii=False), encoding="utf-8")

    return proposal


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--objective", default="melhorar clareza operacional do K-OS sem aplicar patch automaticamente")
    parser.add_argument("--files", nargs="*", default=DEFAULT_FILES)
    parser.add_argument("--proposal-id", default="")
    args = parser.parse_args()

    result = build_patch_proposal(
        objective=args.objective,
        files=args.files,
        proposal_id=args.proposal_id,
    )

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
