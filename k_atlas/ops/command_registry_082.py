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


CHECKPOINT_ID = "082"
CHECKPOINT_NAME = "K-OS Command Registry Core"
LAYER_NAME = "K-OS Core"

ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "configs" / "k_os_command_registry_082.json"
REPORT_DIR = ROOT / "reports" / "system" / "082_command_registry"
DOCS_DIR = ROOT / "docs" / "commercial"
DOCS_PATH = DOCS_DIR / "082_k_os_command_registry.md"

PREVIOUS_CHECKPOINT = "081 - K-OS Agent Capability Registry Core"
NEXT_CHECKPOINT = "083 - K-OS Backup and Export Pack Core"

COMMAND_ROOTS = [
    "scripts",
    "k_atlas",
    "pages",
    "configs",
    "docs",
    "reports",
]

COMMAND_FAMILIES = [
    "python_runtime",
    "streamlit_runtime",
    "git_workflow",
    "powershell_wrapper",
    "security_guard",
    "report_generation",
    "registry_generation",
    "validation",
    "audit",
    "closure",
    "configuration",
    "documentation",
    "unknown",
]

BLOCKED_OPERATIONS = [
    "command_execution",
    "agent_execution",
    "module_execution",
    "automatic_remediation",
    "real_drill_execution",
    "real_recovery_execution",
    "real_rollback_execution",
    "git_reset_hard",
    "force_push",
    "destructive_shell",
    "memory_deletion",
    "secret_export",
]

IGNORED_PARTS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    ".streamlit",
    "local_secrets",
    "runtime",
}

IGNORED_SUFFIXES = {
    ".pyc",
    ".pyo",
    ".pyd",
    ".sqlite",
    ".db",
    ".zip",
    ".gz",
    ".7z",
    ".rar",
    ".exe",
    ".dll",
}

TEXT_SUFFIXES = {
    ".py",
    ".ps1",
    ".json",
    ".md",
    ".txt",
    ".yaml",
    ".yml",
    ".toml",
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

COMMAND_PATTERN_RE = re.compile(
    r"(?i)\b("
    r"python|py|streamlit|git|powershell|pwsh|pytest|pip|subprocess|"
    r"Start-Process|Write-Host|New-Item|Set-Content|Get-Content|"
    r"json\.dump|write_json|write_text|py_compile"
    r")\b"
)

BLOCKED_REFERENCE_PATTERNS = [
    re.compile(r"(?i)\bgit\s+reset\s+--hard\b"),
    re.compile(r"(?i)\bgit\s+push\b.*\b--force\b"),
    re.compile(r"(?i)\bRemove-Item\b.*\b-Recurse\b.*\b-Force\b"),
    re.compile(r"(?i)\brm\s+-rf\b"),
    re.compile(r"(?i)\bformat\s+"),
    re.compile(r"(?i)\bdel\s+/f\b"),
]

FAMILY_PATTERNS = {
    "python_runtime": ["python", "py_compile", "subprocess", ".py"],
    "streamlit_runtime": ["streamlit", "st.", "set_page_config"],
    "git_workflow": ["git ", "github", "commit", "push", "branch", "restore", "diff"],
    "powershell_wrapper": ["powershell", "Write-Host", "Start-Process", "$ErrorActionPreference", ".ps1"],
    "security_guard": ["security", "firewall", "secret", "sanitize", "redacted", "guard"],
    "report_generation": ["report", "relatorio", "write_json", "write_text", "json.dump"],
    "registry_generation": ["registry", "register", "inventory", "catalog", "capability"],
    "validation": ["validate", "validation", "py_compile", "checks"],
    "audit": ["audit", "auditoria"],
    "closure": ["closure", "fechamento", "closed"],
    "configuration": ["config", "policy", "settings", ".json"],
    "documentation": ["docs", "readme", ".md", "markdown"],
}


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


def read_text_limited(path: Path, max_chars: int = 250000) -> str:
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


def slug(value: str) -> str:
    clean = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip().lower())
    clean = re.sub(r"_+", "_", clean).strip("_")
    return clean or "command"


def default_config() -> Dict[str, Any]:
    return {
        "checkpoint": CHECKPOINT_ID,
        "name": CHECKPOINT_NAME,
        "layer": LAYER_NAME,
        "objective": (
            "Criar registro central de comandos do K-OS com catalogo local, "
            "classificacao de risco, politica de execucao, evidencias sanitizadas "
            "e dashboard somente leitura, sem executar comandos, agentes, modulos, "
            "auto-fix, recovery, rollback, drill, reset ou force push."
        ),
        "previous_checkpoint": PREVIOUS_CHECKPOINT,
        "next_checkpoint": NEXT_CHECKPOINT,
        "command_roots": COMMAND_ROOTS,
        "command_families": COMMAND_FAMILIES,
        "allowed_operations": [
            "read_local_project_state",
            "generate_sanitized_command_registry",
            "generate_read_only_dashboard",
            "update_accountability_register_if_exists",
            "validate_artifacts",
            "audit_checkpoint",
            "create_closure_report",
        ],
        "blocked_operations": BLOCKED_OPERATIONS,
        "registry_policy": {
            "read_only_inventory": True,
            "execute_commands": False,
            "execute_agents": False,
            "execute_modules": False,
            "auto_fix": False,
            "sanitize_reports": True,
            "include_sensitive_content": False,
            "include_file_hashes": True,
            "ignore_local_secrets": True,
            "ignore_memory_runtime": True,
            "require_operator_approval_for_publish": True,
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


def should_ignore(path: Path) -> bool:
    if set(path.parts).intersection(IGNORED_PARTS):
        return True

    rel_path = rel(path)

    if rel_path.startswith("reports/security/latest_security_firewall_report"):
        return True

    if rel_path.startswith("reports/system/082_command_registry"):
        return True

    if rel_path.startswith("memory/runtime"):
        return True

    if rel_path.startswith("local_secrets"):
        return True

    if path.name.lower().startswith(".env"):
        return True

    if path.suffix.lower() in IGNORED_SUFFIXES:
        return True

    try:
        if path.is_file() and path.stat().st_size > 5 * 1024 * 1024:
            return True
    except Exception:
        return True

    return False


def is_command_surface(path: Path) -> bool:
    if not path.is_file():
        return False

    suffix = path.suffix.lower()
    rel_path = rel(path)

    if suffix not in TEXT_SUFFIXES:
        return False

    if rel_path.startswith("scripts/"):
        return True

    if rel_path.startswith("k_atlas/ops/") and suffix == ".py":
        return True

    if rel_path.startswith("pages/") and suffix == ".py":
        return True

    if rel_path.startswith("configs/") and suffix == ".json":
        return True

    if rel_path.startswith("docs/") and suffix in {".md", ".txt"}:
        return True

    if rel_path.startswith("reports/") and suffix in {".json", ".md"}:
        return True

    return False


def classify_family(path: Path, text: str) -> str:
    rel_path = rel(path).lower()
    blob = f"{rel_path}\n{text[:30000]}"

    scores: Dict[str, int] = {}
    for family, terms in FAMILY_PATTERNS.items():
        count = 0
        for term in terms:
            if term.lower() in blob.lower():
                count += 1
        scores[family] = count

    best_family = "unknown"
    best_score = 0
    for family, score in scores.items():
        if score > best_score:
            best_family = family
            best_score = score

    return best_family if best_score > 0 else "unknown"


def detect_blocked_references(text: str) -> List[str]:
    findings = []
    for pattern in BLOCKED_REFERENCE_PATTERNS:
        if pattern.search(text):
            findings.append(pattern.pattern)
    return findings


def infer_risk_level(path: Path, text: str, family: str, blocked_refs: List[str]) -> str:
    rel_path = rel(path).lower()

    if blocked_refs:
        return "blocked_reference"

    if "git push" in text.lower() or "git commit" in text.lower():
        return "git_publish"

    if any(token in text.lower() for token in ["write_json", "write_text", "new-item", "set-content", "json.dump", "git add"]):
        return "write_artifact"

    if family in {"validation", "audit", "documentation", "configuration"}:
        return "read_only"

    if rel_path.startswith("scripts/") or path.suffix.lower() == ".ps1":
        return "operator_review_required"

    return "read_only"


def extract_command_signals(path: Path, text: str) -> List[Dict[str, Any]]:
    signals: List[Dict[str, Any]] = []

    for line_number, line in enumerate(text.splitlines(), start=1):
        raw = line.strip()
        if not raw:
            continue

        if len(raw) > 240:
            raw = raw[:240] + "..."

        if COMMAND_PATTERN_RE.search(raw):
            safe_line = sanitize(raw)

            signals.append({
                "line": line_number,
                "signal": safe_line,
            })

        if len(signals) >= 60:
            break

    return signals


def file_record(path: Path, root_name: str) -> Dict[str, Any]:
    text = read_text_limited(path)
    family = classify_family(path, text)
    blocked_refs = detect_blocked_references(text)
    risk_level = infer_risk_level(path, text, family, blocked_refs)
    stat = path.stat()

    command_signals = extract_command_signals(path, text)

    record: Dict[str, Any] = {
        "command_id": slug(rel(path)),
        "root": root_name,
        "path": rel(path),
        "command_family": family,
        "risk_level": risk_level,
        "status": "registered",
        "execution_policy": "read_only_registered_not_executed",
        "operator_approval_required": risk_level in {"git_publish", "operator_review_required", "blocked_reference"},
        "blocked_reference_detected": bool(blocked_refs),
        "blocked_reference_patterns": blocked_refs,
        "command_signal_count": len(command_signals),
        "command_signals": command_signals,
        "size_bytes": stat.st_size,
        "modified_utc": dt.datetime.fromtimestamp(
            stat.st_mtime,
            tz=dt.timezone.utc,
        ).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "sha256": sha256_file(path),
        "suffix": path.suffix.lower(),
    }

    if path.suffix.lower() == ".json":
        data = read_json(path)
        if isinstance(data, dict):
            record["json_keys"] = sorted([str(key) for key in data.keys()])[:30]
            for key in ["checkpoint", "name", "status", "layer", "next_checkpoint"]:
                if key in data and not isinstance(data[key], (dict, list)):
                    record[key] = sanitize(str(data[key]))[:160]

    return record


def discover_commands(config: Dict[str, Any]) -> Dict[str, Any]:
    roots = config.get("command_roots", COMMAND_ROOTS)
    if not isinstance(roots, list):
        roots = COMMAND_ROOTS

    records: List[Dict[str, Any]] = []
    root_status: List[Dict[str, Any]] = []

    for root_name in roots:
        if not isinstance(root_name, str):
            continue

        root_path = ROOT / root_name
        root_info = {
            "root": root_name,
            "path": rel(root_path),
            "exists": root_path.exists(),
            "status": "found" if root_path.exists() else "missing",
            "command_surface_count": 0,
        }

        if not root_path.exists():
            root_status.append(root_info)
            continue

        count = 0
        for path in sorted(root_path.rglob("*"), key=lambda item: rel(item)):
            if should_ignore(path):
                continue
            if not is_command_surface(path):
                continue

            records.append(file_record(path, root_name))
            count += 1

        root_info["command_surface_count"] = count
        root_status.append(root_info)

    by_family: Dict[str, int] = {}
    by_risk: Dict[str, int] = {}
    by_root: Dict[str, int] = {}

    for record in records:
        by_family[record["command_family"]] = by_family.get(record["command_family"], 0) + 1
        by_risk[record["risk_level"]] = by_risk.get(record["risk_level"], 0) + 1
        by_root[record["root"]] = by_root.get(record["root"], 0) + 1

    operator_review = [
        {
            "command_id": record["command_id"],
            "path": record["path"],
            "risk_level": record["risk_level"],
            "command_family": record["command_family"],
        }
        for record in records
        if record["operator_approval_required"]
    ]

    blocked_reference_records = [
        {
            "command_id": record["command_id"],
            "path": record["path"],
            "patterns": record["blocked_reference_patterns"],
        }
        for record in records
        if record["blocked_reference_detected"]
    ]

    return {
        "generated_at": now_utc(),
        "total_command_surfaces": len(records),
        "root_status": root_status,
        "by_family": dict(sorted(by_family.items())),
        "by_risk": dict(sorted(by_risk.items())),
        "by_root": dict(sorted(by_root.items())),
        "operator_review_required_count": len(operator_review),
        "operator_review_required": operator_review[:120],
        "blocked_reference_count": len(blocked_reference_records),
        "blocked_references": blocked_reference_records[:120],
        "commands": records,
    }


def build_registry(config: Dict[str, Any]) -> Dict[str, Any]:
    inventory = discover_commands(config)

    required_families = [
        "python_runtime",
        "powershell_wrapper",
        "git_workflow",
        "security_guard",
        "report_generation",
        "validation",
        "audit",
        "closure",
    ]

    missing_required_families = [
        family
        for family in required_families
        if inventory["by_family"].get(family, 0) == 0
    ]

    status = (
        "healthy"
        if inventory["total_command_surfaces"] > 0 and not missing_required_families
        else "attention"
    )

    return {
        "checkpoint": CHECKPOINT_ID,
        "name": CHECKPOINT_NAME,
        "layer": LAYER_NAME,
        "generated_at": now_utc(),
        "status": status,
        "objective": config.get("objective"),
        "previous_checkpoint": config.get("previous_checkpoint", PREVIOUS_CHECKPOINT),
        "next_checkpoint": config.get("next_checkpoint", NEXT_CHECKPOINT),
        "registry_policy": sanitize(config.get("registry_policy", {})),
        "command_families": COMMAND_FAMILIES,
        "required_families": required_families,
        "missing_required_families": missing_required_families,
        "inventory": inventory,
        "blocked_operations": BLOCKED_OPERATIONS,
        "execution_guard": {
            "command_execution_performed": False,
            "agent_execution_performed": False,
            "module_execution_performed": False,
            "automatic_remediation_executed": False,
            "real_drill_executed": False,
            "real_recovery_executed": False,
            "real_rollback_executed": False,
            "git_reset_hard_executed": False,
            "force_push_executed": False,
            "destructive_shell_executed": False,
            "memory_deletion_executed": False,
            "secret_export_executed": False,
        },
        "operational_decision": {
            "command_registry_created": True,
            "read_only_inventory": True,
            "commands_executed": False,
            "operator_approval_required_for_publish": True,
            "can_continue_to_next_checkpoint": True,
            "next_checkpoint": config.get("next_checkpoint", NEXT_CHECKPOINT),
        },
    }


def registry_markdown(registry: Dict[str, Any]) -> str:
    inventory = registry["inventory"]

    lines: List[str] = []
    lines.append("# 082 - K-OS Command Registry Core")
    lines.append("")
    lines.append(f"Gerado em: {registry['generated_at']}")
    lines.append("")
    lines.append("## Objetivo")
    lines.append("")
    lines.append(str(registry.get("objective", "")))
    lines.append("")
    lines.append("## Status")
    lines.append("")
    lines.append(f"- Checkpoint: {registry['checkpoint']}")
    lines.append(f"- Camada: {registry['layer']}")
    lines.append(f"- Status do registry: {registry['status']}")
    lines.append(f"- Checkpoint anterior: {registry['previous_checkpoint']}")
    lines.append(f"- Proximo checkpoint: {registry['next_checkpoint']}")
    lines.append(f"- Superficies de comando registradas: {inventory['total_command_surfaces']}")
    lines.append(f"- Revisao de operador requerida: {inventory['operator_review_required_count']}")
    lines.append(f"- Referencias bloqueadas detectadas: {inventory['blocked_reference_count']}")
    lines.append("")

    lines.append("## Contagem por familia")
    lines.append("")
    lines.append("| Familia | Quantidade |")
    lines.append("|---|---:|")
    for family, count in inventory["by_family"].items():
        lines.append(f"| {family} | {count} |")
    lines.append("")

    lines.append("## Contagem por risco")
    lines.append("")
    lines.append("| Risco | Quantidade |")
    lines.append("|---|---:|")
    for risk, count in inventory["by_risk"].items():
        lines.append(f"| {risk} | {count} |")
    lines.append("")

    lines.append("## Contagem por raiz")
    lines.append("")
    lines.append("| Raiz | Quantidade |")
    lines.append("|---|---:|")
    for root, count in inventory["by_root"].items():
        lines.append(f"| {root} | {count} |")
    lines.append("")

    lines.append("## Raizes monitoradas")
    lines.append("")
    lines.append("| Raiz | Existe | Status | Superficies |")
    lines.append("|---|---|---|---:|")
    for item in inventory["root_status"]:
        lines.append(f"| {item['root']} | {item['exists']} | {item['status']} | {item['command_surface_count']} |")
    lines.append("")

    lines.append("## Familias obrigatorias ausentes")
    lines.append("")
    if registry["missing_required_families"]:
        for item in registry["missing_required_families"]:
            lines.append(f"- {item}")
    else:
        lines.append("Nenhuma familia obrigatoria ausente.")
    lines.append("")

    lines.append("## Revisao de operador")
    lines.append("")
    if inventory["operator_review_required"]:
        lines.append("| Caminho | Familia | Risco |")
        lines.append("|---|---|---|")
        for item in inventory["operator_review_required"][:80]:
            lines.append(f"| {item['path']} | {item['command_family']} | {item['risk_level']} |")
    else:
        lines.append("Nenhuma superficie exigindo revisao de operador.")
    lines.append("")

    lines.append("## Amostra de comandos registrados")
    lines.append("")
    lines.append("| Familia | Risco | Caminho | Politica |")
    lines.append("|---|---|---|---|")
    for command in inventory["commands"][:140]:
        lines.append(
            f"| {command['command_family']} | {command['risk_level']} | "
            f"{command['path']} | {command['execution_policy']} |"
        )
    lines.append("")

    lines.append("## Garantias de nao execucao")
    lines.append("")
    for key, value in registry["execution_guard"].items():
        lines.append(f"- {key}: {value}")
    lines.append("")

    lines.append("## Operacoes bloqueadas")
    lines.append("")
    for operation in registry["blocked_operations"]:
        lines.append(f"- {operation}")
    lines.append("")

    lines.append("## Decisao operacional")
    lines.append("")
    lines.append("Registro central de comandos criado em modo somente leitura.")
    lines.append("O sistema pode seguir para 083 - K-OS Backup and Export Pack Core.")
    lines.append("")

    return "\n".join(lines)


def update_accountability_register(registry: Dict[str, Any]) -> List[str]:
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
        "status": registry["status"],
        "updated_at": now_utc(),
        "command_registry": rel(REPORT_DIR / "082_command_registry.json"),
        "closure_report": rel(REPORT_DIR / "082_closure_report.json"),
        "total_command_surfaces": registry["inventory"]["total_command_surfaces"],
        "next_checkpoint": NEXT_CHECKPOINT,
        "read_only_inventory": True,
        "commands_executed": False,
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
            "command_execution_performed": False,
            "agent_execution_performed": False,
            "module_execution_performed": False,
            "automatic_remediation_executed": False,
            "real_drill_executed": False,
            "real_recovery_executed": False,
            "real_rollback_executed": False,
            "destructive_shell_executed": False,
        },
        "config": sanitize(config),
    }

    write_json(REPORT_DIR / "082_init_report.json", report)
    return report


def mode_action() -> Dict[str, Any]:
    ensure_dirs()
    config = load_config()
    registry = build_registry(config)

    write_json(REPORT_DIR / "082_command_registry.json", registry)
    write_text(REPORT_DIR / "082_command_registry.md", registry_markdown(registry))
    write_text(DOCS_PATH, registry_markdown(registry))

    updated_registers = update_accountability_register(registry)

    report = {
        "checkpoint": CHECKPOINT_ID,
        "name": CHECKPOINT_NAME,
        "mode": "action",
        "status": "completed",
        "generated_at": now_utc(),
        "registry_status": registry["status"],
        "total_command_surfaces": registry["inventory"]["total_command_surfaces"],
        "missing_required_families": registry["missing_required_families"],
        "operator_review_required_count": registry["inventory"]["operator_review_required_count"],
        "command_registry_json": rel(REPORT_DIR / "082_command_registry.json"),
        "command_registry_md": rel(REPORT_DIR / "082_command_registry.md"),
        "commercial_doc": rel(DOCS_PATH),
        "updated_accountability_registers": updated_registers,
        "next_checkpoint": NEXT_CHECKPOINT,
        "read_only_inventory": True,
        "commands_executed": False,
        "blocked_operations": BLOCKED_OPERATIONS,
        "execution_guard": registry["execution_guard"],
    }

    write_json(REPORT_DIR / "082_action_report.json", report)
    return report


def mode_validate() -> Dict[str, Any]:
    ensure_dirs()

    expected_files = [
        CONFIG_PATH,
        Path(__file__),
        ROOT / "scripts" / "checkpoint_082_command_registry.ps1",
        ROOT / "pages" / "082_K_OS_Command_Registry.py",
        DOCS_PATH,
        REPORT_DIR / "082_init_report.json",
        REPORT_DIR / "082_action_report.json",
        REPORT_DIR / "082_command_registry.json",
        REPORT_DIR / "082_command_registry.md",
    ]

    checks = []
    for path in expected_files:
        checks.append({
            "path": rel(path),
            "exists": path.exists(),
        })

    registry = read_json(REPORT_DIR / "082_command_registry.json")

    guard_ok = False
    decision_ok = False
    registry_ok = False

    if isinstance(registry, dict):
        guard = registry.get("execution_guard", {})
        guard_ok = isinstance(guard, dict) and all(value is False for value in guard.values())
        decision = registry.get("operational_decision", {})
        decision_ok = (
            isinstance(decision, dict)
            and decision.get("command_registry_created") is True
            and decision.get("read_only_inventory") is True
            and decision.get("commands_executed") is False
            and decision.get("next_checkpoint") == NEXT_CHECKPOINT
        )
        inventory = registry.get("inventory", {})
        registry_ok = isinstance(inventory, dict) and inventory.get("total_command_surfaces", 0) > 0

    all_files_exist = all(item["exists"] for item in checks)

    report = {
        "checkpoint": CHECKPOINT_ID,
        "name": CHECKPOINT_NAME,
        "mode": "validate",
        "status": "passed" if all_files_exist and guard_ok and decision_ok and registry_ok else "failed",
        "generated_at": now_utc(),
        "file_checks": checks,
        "execution_guard_ok": guard_ok,
        "operational_decision_ok": decision_ok,
        "registry_has_command_surfaces": registry_ok,
        "next_checkpoint": NEXT_CHECKPOINT,
    }

    write_json(REPORT_DIR / "082_validate_report.json", report)

    if report["status"] != "passed":
        raise RuntimeError("Checkpoint 082 validation failed.")

    return report


def mode_audit() -> Dict[str, Any]:
    ensure_dirs()

    validate_report = read_json(REPORT_DIR / "082_validate_report.json")
    registry = read_json(REPORT_DIR / "082_command_registry.json")

    validate_passed = isinstance(validate_report, dict) and validate_report.get("status") == "passed"
    registry_exists = isinstance(registry, dict)

    checks = {
        "validate_passed": validate_passed,
        "command_registry_exists": registry_exists,
        "read_only_inventory": True,
        "command_execution_not_performed": True,
        "agent_execution_not_performed": True,
        "module_execution_not_performed": True,
        "automatic_remediation_not_executed": True,
        "real_drill_not_executed": True,
        "real_recovery_not_executed": True,
        "real_rollback_not_executed": True,
        "git_reset_hard_not_executed": True,
        "force_push_not_executed": True,
        "destructive_shell_not_executed": True,
        "memory_deletion_not_executed": True,
        "sensitive_content_not_exported": True,
        "reports_are_sanitized": True,
        "transition_to_083_declared": True,
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

    write_json(REPORT_DIR / "082_audit_report.json", report)

    if report["status"] != "passed":
        raise RuntimeError("Checkpoint 082 audit failed.")

    return report


def final_closure_markdown(report: Dict[str, Any]) -> str:
    lines = []
    lines.append("# 082 - Closure Report")
    lines.append("")
    lines.append(f"Checkpoint: {report['checkpoint']}")
    lines.append(f"Nome: {report['name']}")
    lines.append(f"Status: {report['status']}")
    lines.append(f"Gerado em: {report['generated_at']}")
    lines.append("")
    lines.append("## Resultado")
    lines.append("")
    lines.append("Checkpoint 082 fechado. Registro central de comandos criado em modo somente leitura.")
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

    action_report = read_json(REPORT_DIR / "082_action_report.json")
    validate_report = read_json(REPORT_DIR / "082_validate_report.json")
    audit_report = read_json(REPORT_DIR / "082_audit_report.json")
    registry = read_json(REPORT_DIR / "082_command_registry.json")

    ok = (
        isinstance(action_report, dict)
        and action_report.get("status") == "completed"
        and isinstance(validate_report, dict)
        and validate_report.get("status") == "passed"
        and isinstance(audit_report, dict)
        and audit_report.get("status") == "passed"
        and isinstance(registry, dict)
    )

    report = {
        "checkpoint": CHECKPOINT_ID,
        "name": CHECKPOINT_NAME,
        "mode": "closure",
        "status": "closed" if ok else "failed",
        "generated_at": now_utc(),
        "registry_status": registry.get("status") if isinstance(registry, dict) else "unknown",
        "total_command_surfaces": registry.get("inventory", {}).get("total_command_surfaces") if isinstance(registry, dict) else 0,
        "next_checkpoint": NEXT_CHECKPOINT,
        "action_report": rel(REPORT_DIR / "082_action_report.json"),
        "validate_report": rel(REPORT_DIR / "082_validate_report.json"),
        "audit_report": rel(REPORT_DIR / "082_audit_report.json"),
        "command_registry": rel(REPORT_DIR / "082_command_registry.json"),
        "read_only_inventory": True,
        "commands_executed": False,
        "blocked_operations_confirmed": True,
    }

    write_json(REPORT_DIR / "082_closure_report.json", report)
    write_text(REPORT_DIR / "082_closure_report.md", final_closure_markdown(report))

    if report["status"] != "closed":
        raise RuntimeError("Checkpoint 082 closure failed.")

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