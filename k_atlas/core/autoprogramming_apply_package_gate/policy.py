from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Mapping


ALLOWED_PREFIXES = (
    "k_atlas/",
    "agents/",
    "pages/",
    "ops/",
    "README_",
    "tests/",
    "reports/autoprog_generated/",
)

BLOCKED_FLAGS = [
    "execution_enabled",
    "real_execution_enabled",
    "external_api_enabled",
    "auto_publish",
    "auto_send",
    "auto_deploy",
    "browser_automation",
    "mouse_automation",
    "apply_now",
]

BLOCKED_MARKERS = [
    "token=",
    "api_key=",
    "password=",
    "senha=",
    "secret=",
    "access_token=",
    "refresh_token=",
    "Invoke-Expression",
    "iex ",
    "os.system",
    "subprocess.Popen",
]


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def normalize_path(value: str) -> str:
    return value.replace("\\", "/").strip()


def validate_file_plan(plan: Mapping[str, Any]) -> dict[str, Any]:
    data = dict(plan or {})
    reasons: list[str] = []

    path = normalize_path(str(data.get("path", "")))
    content = str(data.get("content", ""))
    expected_hash = str(data.get("content_sha256", "")).strip()
    actual_hash = sha256_text(content)

    if not path:
        reasons.append("path_required")

    if Path(path).is_absolute():
        reasons.append("absolute_path_blocked")

    if ".." in Path(path).parts:
        reasons.append("parent_path_blocked")

    if not path.startswith(ALLOWED_PREFIXES):
        reasons.append(f"path_prefix_not_allowed:{path}")

    if expected_hash and expected_hash != actual_hash:
        reasons.append("content_hash_mismatch")

    lowered = content.lower()

    for marker in BLOCKED_MARKERS:
        if marker.lower() in lowered:
            reasons.append(f"blocked_marker:{marker}")

    return {
        "ok": len(reasons) == 0,
        "status": "file_plan_gate_passed" if not reasons else "file_plan_gate_blocked",
        "path": path,
        "content_sha256": actual_hash,
        "reasons": reasons or ["file_plan_gate_passed"],
    }


def validate_apply_package(package: Mapping[str, Any]) -> dict[str, Any]:
    data = dict(package or {})
    reasons: list[str] = []

    for flag in BLOCKED_FLAGS:
        if data.get(flag) is True:
            reasons.append(f"{flag}_blocked")

    if data.get("status") != "waiting_execution_gate_validation":
        reasons.append(f"invalid_package_status:{data.get('status')}")

    file_plans = data.get("file_plans", [])

    if not isinstance(file_plans, list) or not file_plans:
        reasons.append("file_plans_required")

    file_results = []
    for plan in file_plans if isinstance(file_plans, list) else []:
        result = validate_file_plan(plan)
        file_results.append(result)
        if not result["ok"]:
            reasons.append("invalid_file_plan_detected")

    package_hash = str(data.get("package_hash", "")).strip()
    if not package_hash:
        reasons.append("package_hash_required")

    return {
        "ok": len(reasons) == 0,
        "status": "apply_package_gate_passed" if not reasons else "apply_package_gate_blocked",
        "package_id": data.get("apply_package_id"),
        "source_review_id": data.get("source_review_id"),
        "checkpoint": data.get("checkpoint"),
        "reasons": reasons or ["apply_package_gate_passed"],
        "file_results": file_results,
        "execution_enabled": False,
        "real_execution_enabled": False,
        "human_approval_required": True,
    }
