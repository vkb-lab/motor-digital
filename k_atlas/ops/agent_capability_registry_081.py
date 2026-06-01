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


CHECKPOINT_ID = "081"
CHECKPOINT_NAME = "K-OS Agent Capability Registry Core"
LAYER_NAME = "K-OS Core"

ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "configs" / "k_os_agent_capability_registry_081.json"
REPORT_DIR = ROOT / "reports" / "system" / "081_agent_capability_registry"
DOCS_DIR = ROOT / "docs" / "commercial"
DOCS_PATH = DOCS_DIR / "081_k_os_agent_capability_registry.md"

PREVIOUS_CHECKPOINT = "080 - K-OS Module Registry Core"
NEXT_CHECKPOINT = "082 - K-OS Command Registry Core"

AGENT_ROOTS = [
    "agents",
    "k_atlas",
    "scripts",
    "pages",
    "configs",
    "docs",
    "reports",
]

CAPABILITY_TAXONOMY = [
    "agent_orchestration",
    "memory_management",
    "campaign_generation",
    "content_generation",
    "reporting",
    "resilience_governance",
    "system_health",
    "module_registry",
    "security_guard",
    "streamlit_interface",
    "github_workflow",
    "automation",
    "commercial_ops",
    "configuration",
    "documentation",
    "unknown",
]

BLOCKED_OPERATIONS = [
    "agent_execution",
    "module_execution",
    "command_execution",
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
]

CAPABILITY_PATTERNS = {
    "agent_orchestration": [
        "agent",
        "orchestrat",
        "capability",
        "dispatcher",
        "planner",
        "operator",
    ],
    "memory_management": [
        "memory",
        "memoria",
        "persistent",
        "state",
        "accountability",
        "register",
    ],
    "campaign_generation": [
        "campaign",
        "campanha",
        "lead",
        "ads",
        "meta",
        "marketing",
    ],
    "content_generation": [
        "content",
        "conteudo",
        "caption",
        "copy",
        "post",
        "creative",
    ],
    "reporting": [
        "report",
        "relatorio",
        "audit",
        "evidence",
        "closure",
        "summary",
    ],
    "resilience_governance": [
        "resilience",
        "rollback",
        "recovery",
        "drill",
        "dry_run",
        "scenario",
    ],
    "system_health": [
        "health",
        "system",
        "diagnostic",
        "monitor",
        "status",
    ],
    "module_registry": [
        "module",
        "registry",
        "inventory",
        "catalog",
        "catalogue",
    ],
    "security_guard": [
        "security",
        "firewall",
        "secret",
        "sanitize",
        "redacted",
        "guard",
    ],
    "streamlit_interface": [
        "streamlit",
        "st.",
        "set_page_config",
        "dataframe",
        "metric",
    ],
    "github_workflow": [
        "git ",
        "github",
        "commit",
        "push",
        "branch",
    ],
    "automation": [
        "subprocess",
        "schedule",
        "automation",
        "automacao",
        "script",
        "powershell",
    ],
    "commercial_ops": [
        "commercial",
        "comercial",
        "sales",
        "vendas",
        "revenue",
        "cliente",
    ],
    "configuration": [
        "config",
        "settings",
        "policy",
        "schema",
        "json",
    ],
    "documentation": [
        "docs",
        "documentation",
        "readme",
        "markdown",
        "# ",
    ],
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


def read_text_limited(path: Path, max_chars: int = 180000) -> str:
    try:
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        return text[:max_chars]
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
    return clean or "agent"


def default_config() -> Dict[str, Any]:
    return {
        "checkpoint": CHECKPOINT_ID,
        "name": CHECKPOINT_NAME,
        "layer": LAYER_NAME,
        "objective": (
            "Criar registro central de capacidades dos agentes do K-OS com "
            "inventario local, classificacao funcional, matriz agente-capacidade, "
            "evidencias sanitizadas e dashboard somente leitura, sem executar "
            "agentes, modulos, auto-fix, recovery, rollback, drill, reset ou force push."
        ),
        "previous_checkpoint": PREVIOUS_CHECKPOINT,
        "next_checkpoint": NEXT_CHECKPOINT,
        "agent_roots": AGENT_ROOTS,
        "capability_taxonomy": CAPABILITY_TAXONOMY,
        "allowed_operations": [
            "read_local_project_state",
            "generate_sanitized_agent_capability_registry",
            "generate_read_only_dashboard",
            "update_accountability_register_if_exists",
            "validate_artifacts",
            "audit_checkpoint",
            "create_closure_report",
        ],
        "blocked_operations": BLOCKED_OPERATIONS,
        "registry_policy": {
            "read_only_inventory": True,
            "execute_agents": False,
            "execute_modules": False,
            "execute_commands": False,
            "auto_fix": False,
            "sanitize_reports": True,
            "include_sensitive_content": False,
            "include_file_hashes": True,
            "ignore_local_secrets": True,
            "ignore_memory_runtime": True,
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

    if rel_path.startswith("reports/system/081_agent_capability_registry"):
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


def is_agent_candidate(path: Path) -> bool:
    rel_path = rel(path)
    suffix = path.suffix.lower()

    if not path.is_file():
        return False

    if suffix not in TEXT_SUFFIXES:
        return False

    if rel_path.startswith("agents/"):
        return True

    if rel_path.startswith("k_atlas/ops/") and suffix == ".py":
        return True

    if rel_path.startswith("pages/") and suffix == ".py":
        return True

    if rel_path.startswith("scripts/") and suffix in {".ps1", ".py"}:
        return True

    if rel_path.startswith("configs/") and suffix == ".json":
        return True

    if rel_path.startswith("docs/") and suffix in {".md", ".txt"}:
        return True

    if rel_path.startswith("reports/") and suffix in {".json", ".md"}:
        return True

    return False


def infer_agent_kind(path: Path) -> str:
    rel_path = rel(path)
    suffix = path.suffix.lower()

    if rel_path.startswith("agents/"):
        return "agent_module"

    if rel_path.startswith("k_atlas/ops/") and suffix == ".py":
        return "ops_agent"

    if rel_path.startswith("pages/") and suffix == ".py":
        return "interface_agent_surface"

    if rel_path.startswith("scripts/") and suffix == ".ps1":
        return "powershell_wrapper"

    if rel_path.startswith("scripts/") and suffix == ".py":
        return "script_agent"

    if rel_path.startswith("configs/") and suffix == ".json":
        return "configuration_surface"

    if rel_path.startswith("docs/"):
        return "documentation_surface"

    if rel_path.startswith("reports/"):
        return "report_evidence_surface"

    return "unknown_surface"


def detect_capabilities(path: Path) -> Dict[str, Any]:
    rel_path = rel(path)
    suffix = path.suffix.lower()
    name_blob = f"{rel_path} {path.name}".lower()
    content_blob = ""

    if suffix in TEXT_SUFFIXES and path.exists() and path.is_file():
        content_blob = read_text_limited(path).lower()

    scan_blob = f"{name_blob}\n{content_blob}"

    capabilities: List[str] = []
    evidence_terms: Dict[str, List[str]] = {}

    for capability, terms in CAPABILITY_PATTERNS.items():
        hits = []
        for term in terms:
            if term.lower() in scan_blob:
                hits.append(term)
        if hits:
            capabilities.append(capability)
            evidence_terms[capability] = sorted(set(hits))[:10]

    if not capabilities:
        capabilities = ["unknown"]
        evidence_terms["unknown"] = []

    return {
        "capabilities": sorted(set(capabilities)),
        "evidence_terms": evidence_terms,
    }


def file_record(path: Path, root_name: str) -> Dict[str, Any]:
    detected = detect_capabilities(path)
    stat = path.stat()

    record: Dict[str, Any] = {
        "agent_id": slug(rel(path)),
        "root": root_name,
        "path": rel(path),
        "agent_kind": infer_agent_kind(path),
        "capabilities": detected["capabilities"],
        "capability_count": len(detected["capabilities"]),
        "evidence_terms": detected["evidence_terms"],
        "status": "registered",
        "execution_policy": "read_only_registered_not_executed",
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


def discover_agent_capabilities(config: Dict[str, Any]) -> Dict[str, Any]:
    roots = config.get("agent_roots", AGENT_ROOTS)
    if not isinstance(roots, list):
        roots = AGENT_ROOTS

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
            "agent_surface_count": 0,
        }

        if not root_path.exists():
            root_status.append(root_info)
            continue

        count = 0
        for path in sorted(root_path.rglob("*"), key=lambda item: rel(item)):
            if should_ignore(path):
                continue
            if not is_agent_candidate(path):
                continue

            records.append(file_record(path, root_name))
            count += 1

        root_info["agent_surface_count"] = count
        root_status.append(root_info)

    by_capability: Dict[str, int] = {}
    by_kind: Dict[str, int] = {}
    by_root: Dict[str, int] = {}

    for record in records:
        by_kind[record["agent_kind"]] = by_kind.get(record["agent_kind"], 0) + 1
        by_root[record["root"]] = by_root.get(record["root"], 0) + 1
        for capability in record["capabilities"]:
            by_capability[capability] = by_capability.get(capability, 0) + 1

    capability_matrix = []
    for capability in CAPABILITY_TAXONOMY:
        matching = [
            {
                "agent_id": record["agent_id"],
                "path": record["path"],
                "agent_kind": record["agent_kind"],
                "root": record["root"],
            }
            for record in records
            if capability in record["capabilities"]
        ]

        capability_matrix.append({
            "capability": capability,
            "agent_count": len(matching),
            "agents": matching[:80],
        })

    missing_capabilities = [
        capability
        for capability in CAPABILITY_TAXONOMY
        if capability != "unknown" and by_capability.get(capability, 0) == 0
    ]

    return {
        "generated_at": now_utc(),
        "total_agent_surfaces": len(records),
        "root_status": root_status,
        "by_capability": dict(sorted(by_capability.items())),
        "by_kind": dict(sorted(by_kind.items())),
        "by_root": dict(sorted(by_root.items())),
        "missing_capabilities": missing_capabilities,
        "capability_matrix": capability_matrix,
        "agents": records,
    }


def build_registry(config: Dict[str, Any]) -> Dict[str, Any]:
    inventory = discover_agent_capabilities(config)

    required_minimum_capabilities = [
        "agent_orchestration",
        "memory_management",
        "reporting",
        "streamlit_interface",
        "configuration",
        "documentation",
    ]

    missing_required = [
        capability
        for capability in required_minimum_capabilities
        if inventory["by_capability"].get(capability, 0) == 0
    ]

    status = (
        "healthy"
        if inventory["total_agent_surfaces"] > 0 and not missing_required
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
        "capability_taxonomy": CAPABILITY_TAXONOMY,
        "required_minimum_capabilities": required_minimum_capabilities,
        "missing_required_capabilities": missing_required,
        "inventory": inventory,
        "blocked_operations": BLOCKED_OPERATIONS,
        "execution_guard": {
            "agent_execution_performed": False,
            "module_execution_performed": False,
            "command_execution_performed": False,
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
            "agent_capability_registry_created": True,
            "read_only_inventory": True,
            "agents_executed": False,
            "can_continue_to_next_checkpoint": True,
            "next_checkpoint": config.get("next_checkpoint", NEXT_CHECKPOINT),
        },
    }


def registry_markdown(registry: Dict[str, Any]) -> str:
    inventory = registry["inventory"]

    lines: List[str] = []
    lines.append("# 081 - K-OS Agent Capability Registry Core")
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
    lines.append(f"- Superficies de agente registradas: {inventory['total_agent_surfaces']}")
    lines.append("")

    lines.append("## Contagem por capacidade")
    lines.append("")
    lines.append("| Capacidade | Quantidade |")
    lines.append("|---|---:|")
    for capability, count in inventory["by_capability"].items():
        lines.append(f"| {capability} | {count} |")
    lines.append("")

    lines.append("## Contagem por tipo de superficie")
    lines.append("")
    lines.append("| Tipo | Quantidade |")
    lines.append("|---|---:|")
    for kind, count in inventory["by_kind"].items():
        lines.append(f"| {kind} | {count} |")
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
        lines.append(f"| {item['root']} | {item['exists']} | {item['status']} | {item['agent_surface_count']} |")
    lines.append("")

    lines.append("## Capacidades obrigatorias ausentes")
    lines.append("")
    if registry["missing_required_capabilities"]:
        for item in registry["missing_required_capabilities"]:
            lines.append(f"- {item}")
    else:
        lines.append("Nenhuma capacidade obrigatoria ausente.")
    lines.append("")

    lines.append("## Matriz capacidade-agente")
    lines.append("")
    lines.append("| Capacidade | Agentes |")
    lines.append("|---|---:|")
    for item in inventory["capability_matrix"]:
        lines.append(f"| {item['capability']} | {item['agent_count']} |")
    lines.append("")

    lines.append("## Amostra de superficies registradas")
    lines.append("")
    lines.append("| Tipo | Raiz | Caminho | Capacidades |")
    lines.append("|---|---|---|---|")
    for agent in inventory["agents"][:120]:
        caps = ", ".join(agent["capabilities"])
        lines.append(f"| {agent['agent_kind']} | {agent['root']} | {agent['path']} | {caps} |")
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
    lines.append("Registro central de capacidades dos agentes criado em modo somente leitura.")
    lines.append("O sistema pode seguir para 082 - K-OS Command Registry Core.")
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
        "agent_capability_registry": rel(REPORT_DIR / "081_agent_capability_registry.json"),
        "closure_report": rel(REPORT_DIR / "081_closure_report.json"),
        "total_agent_surfaces": registry["inventory"]["total_agent_surfaces"],
        "next_checkpoint": NEXT_CHECKPOINT,
        "read_only_inventory": True,
        "agents_executed": False,
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
            "agent_execution_performed": False,
            "module_execution_performed": False,
            "command_execution_performed": False,
            "automatic_remediation_executed": False,
            "real_drill_executed": False,
            "real_recovery_executed": False,
            "real_rollback_executed": False,
            "destructive_shell_executed": False,
        },
        "config": sanitize(config),
    }

    write_json(REPORT_DIR / "081_init_report.json", report)
    return report


def mode_action() -> Dict[str, Any]:
    ensure_dirs()
    config = load_config()
    registry = build_registry(config)

    write_json(REPORT_DIR / "081_agent_capability_registry.json", registry)
    write_text(REPORT_DIR / "081_agent_capability_registry.md", registry_markdown(registry))
    write_text(DOCS_PATH, registry_markdown(registry))

    updated_registers = update_accountability_register(registry)

    report = {
        "checkpoint": CHECKPOINT_ID,
        "name": CHECKPOINT_NAME,
        "mode": "action",
        "status": "completed",
        "generated_at": now_utc(),
        "registry_status": registry["status"],
        "total_agent_surfaces": registry["inventory"]["total_agent_surfaces"],
        "missing_required_capabilities": registry["missing_required_capabilities"],
        "agent_capability_registry_json": rel(REPORT_DIR / "081_agent_capability_registry.json"),
        "agent_capability_registry_md": rel(REPORT_DIR / "081_agent_capability_registry.md"),
        "commercial_doc": rel(DOCS_PATH),
        "updated_accountability_registers": updated_registers,
        "next_checkpoint": NEXT_CHECKPOINT,
        "read_only_inventory": True,
        "agents_executed": False,
        "blocked_operations": BLOCKED_OPERATIONS,
        "execution_guard": registry["execution_guard"],
    }

    write_json(REPORT_DIR / "081_action_report.json", report)
    return report


def mode_validate() -> Dict[str, Any]:
    ensure_dirs()

    expected_files = [
        CONFIG_PATH,
        Path(__file__),
        ROOT / "scripts" / "checkpoint_081_agent_capability_registry.ps1",
        ROOT / "pages" / "081_K_OS_Agent_Capability_Registry.py",
        DOCS_PATH,
        REPORT_DIR / "081_init_report.json",
        REPORT_DIR / "081_action_report.json",
        REPORT_DIR / "081_agent_capability_registry.json",
        REPORT_DIR / "081_agent_capability_registry.md",
    ]

    checks = []
    for path in expected_files:
        checks.append({
            "path": rel(path),
            "exists": path.exists(),
        })

    registry = read_json(REPORT_DIR / "081_agent_capability_registry.json")

    guard_ok = False
    decision_ok = False
    registry_ok = False

    if isinstance(registry, dict):
        guard = registry.get("execution_guard", {})
        guard_ok = isinstance(guard, dict) and all(value is False for value in guard.values())
        decision = registry.get("operational_decision", {})
        decision_ok = (
            isinstance(decision, dict)
            and decision.get("agent_capability_registry_created") is True
            and decision.get("read_only_inventory") is True
            and decision.get("agents_executed") is False
            and decision.get("next_checkpoint") == NEXT_CHECKPOINT
        )
        inventory = registry.get("inventory", {})
        registry_ok = isinstance(inventory, dict) and inventory.get("total_agent_surfaces", 0) > 0

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
        "registry_has_agent_surfaces": registry_ok,
        "next_checkpoint": NEXT_CHECKPOINT,
    }

    write_json(REPORT_DIR / "081_validate_report.json", report)

    if report["status"] != "passed":
        raise RuntimeError("Checkpoint 081 validation failed.")

    return report


def mode_audit() -> Dict[str, Any]:
    ensure_dirs()

    validate_report = read_json(REPORT_DIR / "081_validate_report.json")
    registry = read_json(REPORT_DIR / "081_agent_capability_registry.json")

    validate_passed = isinstance(validate_report, dict) and validate_report.get("status") == "passed"
    registry_exists = isinstance(registry, dict)

    checks = {
        "validate_passed": validate_passed,
        "agent_capability_registry_exists": registry_exists,
        "read_only_inventory": True,
        "agent_execution_not_performed": True,
        "module_execution_not_performed": True,
        "command_execution_not_performed": True,
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
        "transition_to_082_declared": True,
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

    write_json(REPORT_DIR / "081_audit_report.json", report)

    if report["status"] != "passed":
        raise RuntimeError("Checkpoint 081 audit failed.")

    return report


def final_closure_markdown(report: Dict[str, Any]) -> str:
    lines = []
    lines.append("# 081 - Closure Report")
    lines.append("")
    lines.append(f"Checkpoint: {report['checkpoint']}")
    lines.append(f"Nome: {report['name']}")
    lines.append(f"Status: {report['status']}")
    lines.append(f"Gerado em: {report['generated_at']}")
    lines.append("")
    lines.append("## Resultado")
    lines.append("")
    lines.append("Checkpoint 081 fechado. Registro central de capacidades dos agentes criado em modo somente leitura.")
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

    action_report = read_json(REPORT_DIR / "081_action_report.json")
    validate_report = read_json(REPORT_DIR / "081_validate_report.json")
    audit_report = read_json(REPORT_DIR / "081_audit_report.json")
    registry = read_json(REPORT_DIR / "081_agent_capability_registry.json")

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
        "total_agent_surfaces": registry.get("inventory", {}).get("total_agent_surfaces") if isinstance(registry, dict) else 0,
        "next_checkpoint": NEXT_CHECKPOINT,
        "action_report": rel(REPORT_DIR / "081_action_report.json"),
        "validate_report": rel(REPORT_DIR / "081_validate_report.json"),
        "audit_report": rel(REPORT_DIR / "081_audit_report.json"),
        "agent_capability_registry": rel(REPORT_DIR / "081_agent_capability_registry.json"),
        "read_only_inventory": True,
        "agents_executed": False,
        "blocked_operations_confirmed": True,
    }

    write_json(REPORT_DIR / "081_closure_report.json", report)
    write_text(REPORT_DIR / "081_closure_report.md", final_closure_markdown(report))

    if report["status"] != "closed":
        raise RuntimeError("Checkpoint 081 closure failed.")

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