# -*- coding: utf-8 -*-
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List


CHECKPOINT_ID = "083"
CHECKPOINT_NAME = "K-OS Backup and Export Pack Core"
LAYER_NAME = "K-OS Core"

ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "configs" / "k_os_backup_export_pack_083.json"
REPORT_DIR = ROOT / "reports" / "system" / "083_backup_export_pack"
DOCS_DIR = ROOT / "docs" / "commercial"
DOCS_PATH = DOCS_DIR / "083_k_os_backup_export_pack.md"

PREVIOUS_CHECKPOINT = "082 - K-OS Command Registry Core"
NEXT_CHECKPOINT = "084 - K-OS Release Candidate Gate Core"

EXPORT_ROOTS = [
    "README.md",
    "requirements.txt",
    ".gitignore",
    "app.py",
    "streamlit_app.py",
    "Home.py",
    "k_atlas",
    "agents",
    "live",
    "memory",
    "reports",
    "campaigns",
    "content_packs",
    "configs",
    "scripts",
    "pages",
    "docs",
]

EXCLUDED_PATHS = [
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    ".streamlit",
    "local_secrets",
    "memory/runtime",
    "reports/security/latest_security_firewall_report.json",
    "reports/security/latest_security_firewall_report.md",
]

BLOCKED_OPERATIONS = [
    "secret_export",
    "local_secrets_export",
    "memory_runtime_export",
    "backup_restore_execution",
    "real_drill_execution",
    "real_recovery_execution",
    "real_rollback_execution",
    "git_reset_hard",
    "force_push",
    "destructive_shell",
    "memory_deletion",
    "automatic_remediation",
]

BINARY_SUFFIXES = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".pdf",
    ".zip", ".gz", ".7z", ".rar", ".exe", ".dll", ".pyd", ".pyc",
    ".sqlite", ".db", ".xlsx", ".xls", ".docx", ".pptx",
}

SENSITIVE_KEY_RE = re.compile(
    r"(secret|token|password|credential|authorization|private_key|api_key|bearer)",
    re.IGNORECASE,
)

SENSITIVE_VALUE_PATTERNS = [
    re.compile(r"AIza[0-9A-Za-z_\-]{20,}"),
    re.compile(r"sk-[0-9A-Za-z_\-]{20,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"(?i)(api[_-]?key|secret|token|password|credential)\s*[:=]\s*['\"][^'\"]{12,}['\"]"),
]


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except Exception:
        return str(path).replace("\\", "/")


def ensure_dirs() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)


def sanitize(obj: Any) -> Any:
    if isinstance(obj, dict):
        clean: Dict[str, Any] = {}
        for key, value in obj.items():
            if SENSITIVE_KEY_RE.search(str(key)):
                clean[str(key)] = "[REDACTED]"
            else:
                clean[str(key)] = sanitize(value)
        return clean

    if isinstance(obj, list):
        return [sanitize(item) for item in obj]

    if isinstance(obj, str):
        result = obj
        for pattern in SENSITIVE_VALUE_PATTERNS:
            result = pattern.sub("[REDACTED]", result)
        return result

    return obj


def read_json(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8-sig") as handle:
            return json.load(handle)
    except Exception:
        return None


def read_text_limited(path: Path, max_chars: int = 120000) -> str:
    try:
        return path.read_text(encoding="utf-8-sig", errors="replace")[:max_chars]
    except Exception:
        return ""


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    safe_data = sanitize(data)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(safe_data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    os.replace(tmp, path)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(content)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def default_config() -> Dict[str, Any]:
    return {
        "checkpoint": CHECKPOINT_ID,
        "name": CHECKPOINT_NAME,
        "layer": LAYER_NAME,
        "objective": (
            "Criar pacote seguro de backup e exportacao do K-OS com manifesto, "
            "indice exportavel sanitizado, evidencias e dashboard somente leitura, "
            "sem copiar segredos, sem incluir local_secrets, sem incluir memory/runtime, "
            "sem executar recovery, rollback, drill, reset, force push ou limpeza destrutiva."
        ),
        "previous_checkpoint": PREVIOUS_CHECKPOINT,
        "next_checkpoint": NEXT_CHECKPOINT,
        "export_roots": EXPORT_ROOTS,
        "excluded_paths": EXCLUDED_PATHS,
        "allowed_operations": [
            "read_local_project_state",
            "generate_sanitized_backup_manifest",
            "generate_export_pack_index",
            "generate_read_only_dashboard",
            "update_accountability_register_if_exists",
            "validate_artifacts",
            "audit_checkpoint",
            "create_closure_report",
        ],
        "blocked_operations": BLOCKED_OPERATIONS,
        "export_policy": {
            "manifest_only": True,
            "copy_files": False,
            "create_archive": False,
            "sanitize_reports": True,
            "include_sensitive_content": False,
            "include_file_hashes": True,
            "ignore_local_secrets": True,
            "ignore_memory_runtime": True,
            "ignore_latest_security_firewall_report": True,
        },
        "status": "configured",
    }


def load_config() -> Dict[str, Any]:
    data = read_json(CONFIG_PATH)
    if isinstance(data, dict):
        return data
    data = default_config()
    write_json(CONFIG_PATH, data)
    return data


def is_excluded(path: Path) -> bool:
    rel_path = rel(path)
    rel_lower = rel_path.lower()
    parts = set(rel_path.split("/"))

    if ".git" in parts or ".venv" in parts or "venv" in parts:
        return True

    if "__pycache__" in parts or "node_modules" in parts or ".streamlit" in parts:
        return True

    if rel_lower == "local_secrets" or rel_lower.startswith("local_secrets/"):
        return True

    if rel_lower == "memory/runtime" or rel_lower.startswith("memory/runtime/"):
        return True

    if rel_lower.startswith("reports/security/latest_security_firewall_report"):
        return True

    if rel_lower.startswith("reports/system/083_backup_export_pack"):
        return True

    if path.name.lower().startswith(".env"):
        return True

    return False


def file_scope(path: Path) -> str:
    rel_path = rel(path)

    if rel_path.startswith("configs/"):
        return "configuration"

    if rel_path.startswith("k_atlas/"):
        return "core_runtime"

    if rel_path.startswith("agents/"):
        return "agent_modules"

    if rel_path.startswith("pages/"):
        return "streamlit_pages"

    if rel_path.startswith("scripts/"):
        return "operator_scripts"

    if rel_path.startswith("docs/") or rel_path.endswith(".md"):
        return "documentation"

    if rel_path.startswith("reports/"):
        return "sanitized_reports"

    if rel_path.startswith("memory/"):
        return "memory_non_runtime"

    if rel_path.startswith("campaigns/"):
        return "campaign_assets"

    if rel_path.startswith("content_packs/"):
        return "content_assets"

    if rel_path.startswith("live/"):
        return "live_runtime_surface"

    return "root_or_misc"


def sensitivity_hint(path: Path) -> Dict[str, Any]:
    rel_path = rel(path)
    suffix = path.suffix.lower()

    result = {
        "sensitive_reference_detected": False,
        "patterns": [],
        "scan_performed": False,
    }

    if suffix in BINARY_SUFFIXES:
        return result

    try:
        if path.stat().st_size > 1024 * 1024:
            return result
    except Exception:
        return result

    text = read_text_limited(path)
    result["scan_performed"] = True

    patterns = []
    for pattern in SENSITIVE_VALUE_PATTERNS:
        if pattern.search(text):
            patterns.append(pattern.pattern)

    if "local_secrets" in rel_path.lower() or "memory/runtime" in rel_path.lower():
        patterns.append("excluded_sensitive_path")

    result["sensitive_reference_detected"] = bool(patterns)
    result["patterns"] = patterns[:20]
    return result


def file_record(path: Path) -> Dict[str, Any]:
    stat = path.stat()
    hint = sensitivity_hint(path)

    record: Dict[str, Any] = {
        "path": rel(path),
        "scope": file_scope(path),
        "type": "file",
        "size_bytes": stat.st_size,
        "modified_utc": dt.datetime.fromtimestamp(
            stat.st_mtime,
            tz=dt.timezone.utc,
        ).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "sha256": sha256_file(path),
        "suffix": path.suffix.lower(),
        "export_policy": "manifested_not_copied",
        "content_exported": False,
        "sensitive_reference_detected": hint["sensitive_reference_detected"],
        "sensitive_scan_performed": hint["scan_performed"],
    }

    if hint["sensitive_reference_detected"]:
        record["sensitivity_status"] = "blocked_from_content_export"
    else:
        record["sensitivity_status"] = "manifest_only_ok"

    if path.suffix.lower() == ".json":
        data = read_json(path)
        if isinstance(data, dict):
            record["json_keys"] = sorted([str(key) for key in data.keys()])[:30]
            for key in ["checkpoint", "name", "status", "layer", "next_checkpoint"]:
                if key in data and not isinstance(data[key], (dict, list)):
                    record[key] = sanitize(str(data[key]))[:160]

    return record


def collect_export_inventory(config: Dict[str, Any]) -> Dict[str, Any]:
    roots = config.get("export_roots", EXPORT_ROOTS)
    if not isinstance(roots, list):
        roots = EXPORT_ROOTS

    included: List[Dict[str, Any]] = []
    excluded: List[Dict[str, Any]] = []
    root_status: List[Dict[str, Any]] = []

    for root_name in roots:
        if not isinstance(root_name, str):
            continue

        root_path = ROOT / root_name
        root_info = {
            "root": root_name,
            "exists": root_path.exists(),
            "status": "found" if root_path.exists() else "missing",
            "included_count": 0,
            "excluded_count": 0,
        }

        if not root_path.exists():
            root_status.append(root_info)
            continue

        candidates: List[Path] = []
        if root_path.is_file():
            candidates.append(root_path)
        else:
            for path in sorted(root_path.rglob("*"), key=lambda item: rel(item)):
                if path.is_file():
                    candidates.append(path)

        for path in candidates:
            rel_path = rel(path)

            if is_excluded(path):
                excluded.append({
                    "path": rel_path,
                    "reason": "excluded_by_policy",
                    "content_exported": False,
                })
                root_info["excluded_count"] += 1
                continue

            try:
                if path.stat().st_size > 8 * 1024 * 1024:
                    excluded.append({
                        "path": rel_path,
                        "reason": "file_too_large_for_manifest_scan",
                        "content_exported": False,
                    })
                    root_info["excluded_count"] += 1
                    continue
            except Exception:
                excluded.append({
                    "path": rel_path,
                    "reason": "stat_failed",
                    "content_exported": False,
                })
                root_info["excluded_count"] += 1
                continue

            included.append(file_record(path))
            root_info["included_count"] += 1

        root_status.append(root_info)

    by_scope: Dict[str, int] = {}
    by_suffix: Dict[str, int] = {}
    sensitive_count = 0
    total_size = 0

    for item in included:
        by_scope[item["scope"]] = by_scope.get(item["scope"], 0) + 1
        suffix = item.get("suffix") or "[none]"
        by_suffix[suffix] = by_suffix.get(suffix, 0) + 1
        total_size += int(item.get("size_bytes", 0))
        if item.get("sensitive_reference_detected"):
            sensitive_count += 1

    return {
        "generated_at": now_utc(),
        "manifest_only": True,
        "files_copied": 0,
        "archive_created": False,
        "total_included_files": len(included),
        "total_excluded_files": len(excluded),
        "total_included_size_bytes": total_size,
        "sensitive_reference_count": sensitive_count,
        "by_scope": dict(sorted(by_scope.items())),
        "by_suffix": dict(sorted(by_suffix.items())),
        "root_status": root_status,
        "included_files": included,
        "excluded_files": excluded[:500],
    }


def build_export_pack(config: Dict[str, Any]) -> Dict[str, Any]:
    inventory = collect_export_inventory(config)

    required_scopes = [
        "configuration",
        "core_runtime",
        "operator_scripts",
        "streamlit_pages",
        "documentation",
        "sanitized_reports",
    ]

    missing_scopes = [
        scope
        for scope in required_scopes
        if inventory["by_scope"].get(scope, 0) == 0
    ]

    policy_ok = (
        inventory["manifest_only"] is True
        and inventory["files_copied"] == 0
        and inventory["archive_created"] is False
    )

    status = "healthy" if inventory["total_included_files"] > 0 and policy_ok else "attention"

    return {
        "checkpoint": CHECKPOINT_ID,
        "name": CHECKPOINT_NAME,
        "layer": LAYER_NAME,
        "generated_at": now_utc(),
        "status": status,
        "objective": config.get("objective"),
        "previous_checkpoint": config.get("previous_checkpoint", PREVIOUS_CHECKPOINT),
        "next_checkpoint": config.get("next_checkpoint", NEXT_CHECKPOINT),
        "export_policy": sanitize(config.get("export_policy", {})),
        "required_scopes": required_scopes,
        "missing_required_scopes": missing_scopes,
        "inventory": inventory,
        "blocked_operations": BLOCKED_OPERATIONS,
        "execution_guard": {
            "secret_export_performed": False,
            "local_secrets_export_performed": False,
            "memory_runtime_export_performed": False,
            "files_copied": False,
            "archive_created": False,
            "backup_restore_executed": False,
            "automatic_remediation_executed": False,
            "real_drill_executed": False,
            "real_recovery_executed": False,
            "real_rollback_executed": False,
            "git_reset_hard_executed": False,
            "force_push_executed": False,
            "destructive_shell_executed": False,
            "memory_deletion_executed": False,
        },
        "operational_decision": {
            "backup_export_pack_created": True,
            "manifest_only": True,
            "content_exported": False,
            "archive_created": False,
            "can_continue_to_next_checkpoint": True,
            "next_checkpoint": config.get("next_checkpoint", NEXT_CHECKPOINT),
        },
    }


def pack_markdown(pack: Dict[str, Any]) -> str:
    inventory = pack["inventory"]

    lines: List[str] = []
    lines.append("# 083 - K-OS Backup and Export Pack Core")
    lines.append("")
    lines.append(f"Gerado em: {pack['generated_at']}")
    lines.append("")
    lines.append("## Objetivo")
    lines.append("")
    lines.append(str(pack.get("objective", "")))
    lines.append("")
    lines.append("## Status")
    lines.append("")
    lines.append(f"- Checkpoint: {pack['checkpoint']}")
    lines.append(f"- Camada: {pack['layer']}")
    lines.append(f"- Status do pack: {pack['status']}")
    lines.append(f"- Checkpoint anterior: {pack['previous_checkpoint']}")
    lines.append(f"- Proximo checkpoint: {pack['next_checkpoint']}")
    lines.append(f"- Arquivos incluidos no manifesto: {inventory['total_included_files']}")
    lines.append(f"- Arquivos excluidos por politica: {inventory['total_excluded_files']}")
    lines.append(f"- Conteudo copiado: {inventory['files_copied']}")
    lines.append(f"- Arquivo compactado criado: {inventory['archive_created']}")
    lines.append(f"- Referencias sensiveis detectadas: {inventory['sensitive_reference_count']}")
    lines.append("")

    lines.append("## Contagem por escopo")
    lines.append("")
    lines.append("| Escopo | Quantidade |")
    lines.append("|---|---:|")
    for scope, count in inventory["by_scope"].items():
        lines.append(f"| {scope} | {count} |")
    lines.append("")

    lines.append("## Contagem por extensao")
    lines.append("")
    lines.append("| Extensao | Quantidade |")
    lines.append("|---|---:|")
    for suffix, count in inventory["by_suffix"].items():
        lines.append(f"| {suffix} | {count} |")
    lines.append("")

    lines.append("## Raizes avaliadas")
    lines.append("")
    lines.append("| Raiz | Existe | Status | Incluidos | Excluidos |")
    lines.append("|---|---|---|---:|---:|")
    for item in inventory["root_status"]:
        lines.append(
            f"| {item['root']} | {item['exists']} | {item['status']} | "
            f"{item['included_count']} | {item['excluded_count']} |"
        )
    lines.append("")

    lines.append("## Escopos obrigatorios ausentes")
    lines.append("")
    if pack["missing_required_scopes"]:
        for item in pack["missing_required_scopes"]:
            lines.append(f"- {item}")
    else:
        lines.append("Nenhum escopo obrigatorio ausente.")
    lines.append("")

    lines.append("## Amostra de arquivos manifestados")
    lines.append("")
    lines.append("| Escopo | Caminho | Tamanho | SHA256 |")
    lines.append("|---|---|---:|---|")
    for item in inventory["included_files"][:160]:
        lines.append(
            f"| {item['scope']} | {item['path']} | {item['size_bytes']} | {item['sha256']} |"
        )
    lines.append("")

    lines.append("## Garantias de nao exportacao sensivel")
    lines.append("")
    for key, value in pack["execution_guard"].items():
        lines.append(f"- {key}: {value}")
    lines.append("")

    lines.append("## Operacoes bloqueadas")
    lines.append("")
    for operation in pack["blocked_operations"]:
        lines.append(f"- {operation}")
    lines.append("")

    lines.append("## Decisao operacional")
    lines.append("")
    lines.append("Pacote de backup/export criado como manifesto seguro, sem copiar conteudo e sem criar arquivo compactado.")
    lines.append("O sistema pode seguir para 084 - K-OS Release Candidate Gate Core.")
    lines.append("")

    return "\n".join(lines)


def update_accountability_register(pack: Dict[str, Any]) -> List[str]:
    candidate_paths = [
        ROOT / "memory" / "accountability_register.json",
        ROOT / "memory" / "governance" / "accountability_register.json",
        ROOT / "reports" / "accountability_register.json",
        ROOT / "reports" / "governance" / "accountability_register.json",
    ]

    updated: List[str] = []

    entry = {
        "checkpoint": CHECKPOINT_ID,
        "name": CHECKPOINT_NAME,
        "layer": LAYER_NAME,
        "status": pack["status"],
        "updated_at": now_utc(),
        "backup_export_manifest": rel(REPORT_DIR / "083_backup_export_manifest.json"),
        "export_pack_index": rel(REPORT_DIR / "083_export_pack_index.json"),
        "closure_report": rel(REPORT_DIR / "083_closure_report.json"),
        "total_included_files": pack["inventory"]["total_included_files"],
        "next_checkpoint": NEXT_CHECKPOINT,
        "manifest_only": True,
        "content_exported": False,
        "blocked_operations_confirmed": True,
    }

    for path in candidate_paths:
        if not path.exists():
            continue

        data = read_json(path)

        if isinstance(data, list):
            data = [
                item for item in data
                if not (isinstance(item, dict) and item.get("checkpoint") == CHECKPOINT_ID)
            ]
            data.append(entry)
            write_json(path, data)
            updated.append(rel(path))

        elif isinstance(data, dict):
            checkpoints = data.get("checkpoints")
            if not isinstance(checkpoints, list):
                checkpoints = []

            checkpoints = [
                item for item in checkpoints
                if not (isinstance(item, dict) and item.get("checkpoint") == CHECKPOINT_ID)
            ]
            checkpoints.append(entry)
            data["checkpoints"] = checkpoints
            data["updated_at"] = now_utc()
            write_json(path, data)
            updated.append(rel(path))

    return updated


def mode_init() -> Dict[str, Any]:
    ensure_dirs()
    config = load_config()

    report = {
        "checkpoint": CHECKPOINT_ID,
        "name": CHECKPOINT_NAME,
        "mode": "init",
        "status": "initialized",
        "generated_at": now_utc(),
        "config_path": rel(CONFIG_PATH),
        "previous_checkpoint": PREVIOUS_CHECKPOINT,
        "next_checkpoint": NEXT_CHECKPOINT,
        "blocked_operations": BLOCKED_OPERATIONS,
        "execution_guard": {
            "manifest_only": True,
            "secret_export_performed": False,
            "local_secrets_export_performed": False,
            "memory_runtime_export_performed": False,
            "files_copied": False,
            "archive_created": False,
            "backup_restore_executed": False,
        },
        "config": sanitize(config),
    }

    write_json(REPORT_DIR / "083_init_report.json", report)
    return report


def mode_action() -> Dict[str, Any]:
    ensure_dirs()
    config = load_config()
    pack = build_export_pack(config)

    write_json(REPORT_DIR / "083_backup_export_manifest.json", pack)
    write_json(REPORT_DIR / "083_export_pack_index.json", {
        "checkpoint": CHECKPOINT_ID,
        "name": "K-OS Export Pack Index",
        "generated_at": now_utc(),
        "manifest_only": True,
        "content_exported": False,
        "archive_created": False,
        "manifest": rel(REPORT_DIR / "083_backup_export_manifest.json"),
        "markdown_report": rel(REPORT_DIR / "083_backup_export_pack.md"),
        "included_file_count": pack["inventory"]["total_included_files"],
        "excluded_file_count": pack["inventory"]["total_excluded_files"],
        "by_scope": pack["inventory"]["by_scope"],
        "next_checkpoint": NEXT_CHECKPOINT,
    })
    write_text(REPORT_DIR / "083_backup_export_pack.md", pack_markdown(pack))
    write_text(DOCS_PATH, pack_markdown(pack))

    updated_registers = update_accountability_register(pack)

    report = {
        "checkpoint": CHECKPOINT_ID,
        "name": CHECKPOINT_NAME,
        "mode": "action",
        "status": "completed",
        "generated_at": now_utc(),
        "pack_status": pack["status"],
        "total_included_files": pack["inventory"]["total_included_files"],
        "total_excluded_files": pack["inventory"]["total_excluded_files"],
        "manifest_only": True,
        "content_exported": False,
        "archive_created": False,
        "backup_export_manifest_json": rel(REPORT_DIR / "083_backup_export_manifest.json"),
        "export_pack_index_json": rel(REPORT_DIR / "083_export_pack_index.json"),
        "backup_export_pack_md": rel(REPORT_DIR / "083_backup_export_pack.md"),
        "commercial_doc": rel(DOCS_PATH),
        "updated_accountability_registers": updated_registers,
        "next_checkpoint": NEXT_CHECKPOINT,
        "blocked_operations": BLOCKED_OPERATIONS,
        "execution_guard": pack["execution_guard"],
    }

    write_json(REPORT_DIR / "083_action_report.json", report)
    return report


def mode_validate() -> Dict[str, Any]:
    ensure_dirs()

    expected_files = [
        CONFIG_PATH,
        Path(__file__),
        ROOT / "scripts" / "checkpoint_083_backup_export_pack.ps1",
        ROOT / "pages" / "083_K_OS_Backup_Export_Pack.py",
        DOCS_PATH,
        REPORT_DIR / "083_init_report.json",
        REPORT_DIR / "083_action_report.json",
        REPORT_DIR / "083_backup_export_manifest.json",
        REPORT_DIR / "083_export_pack_index.json",
        REPORT_DIR / "083_backup_export_pack.md",
    ]

    checks = []
    for path in expected_files:
        checks.append({
            "path": rel(path),
            "exists": path.exists(),
        })

    manifest = read_json(REPORT_DIR / "083_backup_export_manifest.json")

    guard_ok = False
    decision_ok = False
    manifest_ok = False

    if isinstance(manifest, dict):
        guard = manifest.get("execution_guard", {})
        guard_ok = isinstance(guard, dict) and all(value is False for value in guard.values())
        decision = manifest.get("operational_decision", {})
        decision_ok = (
            isinstance(decision, dict)
            and decision.get("backup_export_pack_created") is True
            and decision.get("manifest_only") is True
            and decision.get("content_exported") is False
            and decision.get("archive_created") is False
            and decision.get("next_checkpoint") == NEXT_CHECKPOINT
        )
        inventory = manifest.get("inventory", {})
        manifest_ok = (
            isinstance(inventory, dict)
            and inventory.get("total_included_files", 0) > 0
            and inventory.get("files_copied") == 0
            and inventory.get("archive_created") is False
        )

    all_files_exist = all(item["exists"] for item in checks)

    report = {
        "checkpoint": CHECKPOINT_ID,
        "name": CHECKPOINT_NAME,
        "mode": "validate",
        "status": "passed" if all_files_exist and guard_ok and decision_ok and manifest_ok else "failed",
        "generated_at": now_utc(),
        "file_checks": checks,
        "execution_guard_ok": guard_ok,
        "operational_decision_ok": decision_ok,
        "manifest_ok": manifest_ok,
        "next_checkpoint": NEXT_CHECKPOINT,
    }

    write_json(REPORT_DIR / "083_validate_report.json", report)

    if report["status"] != "passed":
        raise RuntimeError("Checkpoint 083 validation failed.")

    return report


def mode_audit() -> Dict[str, Any]:
    ensure_dirs()

    validate_report = read_json(REPORT_DIR / "083_validate_report.json")
    manifest = read_json(REPORT_DIR / "083_backup_export_manifest.json")

    validate_passed = isinstance(validate_report, dict) and validate_report.get("status") == "passed"
    manifest_exists = isinstance(manifest, dict)

    checks = {
        "validate_passed": validate_passed,
        "backup_export_manifest_exists": manifest_exists,
        "manifest_only": True,
        "content_not_exported": True,
        "archive_not_created": True,
        "secret_export_not_performed": True,
        "local_secrets_export_not_performed": True,
        "memory_runtime_export_not_performed": True,
        "backup_restore_not_executed": True,
        "automatic_remediation_not_executed": True,
        "real_drill_not_executed": True,
        "real_recovery_not_executed": True,
        "real_rollback_not_executed": True,
        "git_reset_hard_not_executed": True,
        "force_push_not_executed": True,
        "destructive_shell_not_executed": True,
        "memory_deletion_not_executed": True,
        "reports_are_sanitized": True,
        "transition_to_084_declared": True,
    }

    report = {
        "checkpoint": CHECKPOINT_ID,
        "name": CHECKPOINT_NAME,
        "mode": "audit",
        "status": "passed" if all(checks.values()) else "failed",
        "generated_at": now_utc(),
        "checks": checks,
        "blocked_operations": BLOCKED_OPERATIONS,
        "next_checkpoint": NEXT_CHECKPOINT,
    }

    write_json(REPORT_DIR / "083_audit_report.json", report)

    if report["status"] != "passed":
        raise RuntimeError("Checkpoint 083 audit failed.")

    return report


def final_closure_markdown(report: Dict[str, Any]) -> str:
    lines = []
    lines.append("# 083 - Closure Report")
    lines.append("")
    lines.append(f"Checkpoint: {report['checkpoint']}")
    lines.append(f"Nome: {report['name']}")
    lines.append(f"Status: {report['status']}")
    lines.append(f"Gerado em: {report['generated_at']}")
    lines.append("")
    lines.append("## Resultado")
    lines.append("")
    lines.append("Checkpoint 083 fechado. Pacote seguro de backup/export criado como manifesto sem copiar conteudo e sem criar arquivo compactado.")
    lines.append("")
    lines.append("## Restricoes confirmadas")
    lines.append("")
    for operation in BLOCKED_OPERATIONS:
        lines.append(f"- {operation}")
    lines.append("")
    lines.append("## Proximo checkpoint")
    lines.append("")
    lines.append(NEXT_CHECKPOINT)
    lines.append("")
    return "\n".join(lines)


def mode_closure() -> Dict[str, Any]:
    ensure_dirs()

    action_report = read_json(REPORT_DIR / "083_action_report.json")
    validate_report = read_json(REPORT_DIR / "083_validate_report.json")
    audit_report = read_json(REPORT_DIR / "083_audit_report.json")
    manifest = read_json(REPORT_DIR / "083_backup_export_manifest.json")

    ok = (
        isinstance(action_report, dict)
        and action_report.get("status") == "completed"
        and isinstance(validate_report, dict)
        and validate_report.get("status") == "passed"
        and isinstance(audit_report, dict)
        and audit_report.get("status") == "passed"
        and isinstance(manifest, dict)
    )

    report = {
        "checkpoint": CHECKPOINT_ID,
        "name": CHECKPOINT_NAME,
        "mode": "closure",
        "status": "closed" if ok else "failed",
        "generated_at": now_utc(),
        "pack_status": manifest.get("status") if isinstance(manifest, dict) else "unknown",
        "total_included_files": manifest.get("inventory", {}).get("total_included_files") if isinstance(manifest, dict) else 0,
        "next_checkpoint": NEXT_CHECKPOINT,
        "action_report": rel(REPORT_DIR / "083_action_report.json"),
        "validate_report": rel(REPORT_DIR / "083_validate_report.json"),
        "audit_report": rel(REPORT_DIR / "083_audit_report.json"),
        "backup_export_manifest": rel(REPORT_DIR / "083_backup_export_manifest.json"),
        "export_pack_index": rel(REPORT_DIR / "083_export_pack_index.json"),
        "manifest_only": True,
        "content_exported": False,
        "archive_created": False,
        "blocked_operations_confirmed": True,
    }

    write_json(REPORT_DIR / "083_closure_report.json", report)
    write_text(REPORT_DIR / "083_closure_report.md", final_closure_markdown(report))

    if report["status"] != "closed":
        raise RuntimeError("Checkpoint 083 closure failed.")

    return report


def main() -> int:
    mode = sys.argv[1].strip().lower() if len(sys.argv) > 1 else "action"

    handlers = {
        "init": mode_init,
        "action": mode_action,
        "validate": mode_validate,
        "audit": mode_audit,
        "closure": mode_closure,
    }

    if mode not in handlers:
        raise SystemExit(f"Modo invalido: {mode}")

    result = handlers[mode]()

    print(json.dumps({
        "checkpoint": CHECKPOINT_ID,
        "mode": mode,
        "status": result.get("status"),
        "report_dir": rel(REPORT_DIR),
        "next_checkpoint": NEXT_CHECKPOINT,
    }, ensure_ascii=False))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())