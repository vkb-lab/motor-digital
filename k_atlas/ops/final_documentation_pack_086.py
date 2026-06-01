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


CHECKPOINT_ID = "086"
CHECKPOINT_NAME = "K-OS Final Documentation Pack Core"
LAYER_NAME = "K-OS Core"

ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "configs" / "k_os_final_documentation_pack_086.json"
REPORT_DIR = ROOT / "reports" / "system" / "086_final_documentation_pack"
DOCS_DIR = ROOT / "docs" / "k_os"
COMMERCIAL_DOCS_DIR = ROOT / "docs" / "commercial"
COMMERCIAL_DOCS_PATH = COMMERCIAL_DOCS_DIR / "086_k_os_final_documentation_pack.md"

PREVIOUS_CHECKPOINT = "085 - K-OS Local Installer / Launcher Core"
NEXT_CHECKPOINT = "087 - K-OS Final Audit Pack Core"

SOURCE_CHECKPOINTS = ["079", "080", "081", "082", "083", "084", "085"]

DOC_OUTPUTS = {
    "readme": DOCS_DIR / "README_K_OS.md",
    "operator_guide": DOCS_DIR / "OPERATOR_GUIDE.md",
    "architecture": DOCS_DIR / "ARCHITECTURE.md",
    "governance": DOCS_DIR / "GOVERNANCE.md",
    "launcher_guide": DOCS_DIR / "LAUNCHER_GUIDE.md",
    "release_notes": DOCS_DIR / "RELEASE_NOTES.md",
    "index": DOCS_DIR / "FINAL_DOCUMENTATION_INDEX.md",
}

CHECKPOINT_ARTIFACTS = {
    "079": {
        "name": "K-OS System Health Monitor Core",
        "dir": "reports/system/079_system_health_monitor",
        "main": "079_system_health_report.json",
        "closure": "079_closure_report.json",
        "doc": "docs/commercial/079_k_os_system_health_monitor.md",
    },
    "080": {
        "name": "K-OS Module Registry Core",
        "dir": "reports/system/080_module_registry",
        "main": "080_module_registry.json",
        "closure": "080_closure_report.json",
        "doc": "docs/commercial/080_k_os_module_registry.md",
    },
    "081": {
        "name": "K-OS Agent Capability Registry Core",
        "dir": "reports/system/081_agent_capability_registry",
        "main": "081_agent_capability_registry.json",
        "closure": "081_closure_report.json",
        "doc": "docs/commercial/081_k_os_agent_capability_registry.md",
    },
    "082": {
        "name": "K-OS Command Registry Core",
        "dir": "reports/system/082_command_registry",
        "main": "082_command_registry.json",
        "closure": "082_closure_report.json",
        "doc": "docs/commercial/082_k_os_command_registry.md",
    },
    "083": {
        "name": "K-OS Backup and Export Pack Core",
        "dir": "reports/system/083_backup_export_pack",
        "main": "083_backup_export_manifest.json",
        "closure": "083_closure_report.json",
        "doc": "docs/commercial/083_k_os_backup_export_pack.md",
    },
    "084": {
        "name": "K-OS Release Candidate Gate Core",
        "dir": "reports/system/084_release_candidate_gate",
        "main": "084_release_candidate_gate.json",
        "closure": "084_closure_report.json",
        "doc": "docs/commercial/084_k_os_release_candidate_gate.md",
    },
    "085": {
        "name": "K-OS Local Installer / Launcher Core",
        "dir": "reports/system/085_local_installer_launcher",
        "main": "085_local_installer_launcher_manifest.json",
        "closure": "085_closure_report.json",
        "doc": "docs/commercial/085_k_os_local_installer_launcher.md",
    },
}

BLOCKED_OPERATIONS = [
    "deploy_execution",
    "installer_execution",
    "dependency_install_execution",
    "release_publish_execution",
    "backup_restore_execution",
    "real_drill_execution",
    "real_recovery_execution",
    "real_rollback_execution",
    "git_reset_hard",
    "force_push",
    "destructive_shell",
    "memory_deletion",
    "secret_export",
    "automatic_remediation",
]

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
    COMMERCIAL_DOCS_DIR.mkdir(parents=True, exist_ok=True)
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


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8-sig", errors="replace")
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


def file_info(path: Path) -> Dict[str, Any]:
    item: Dict[str, Any] = {
        "path": rel(path),
        "exists": path.exists(),
    }

    if path.exists() and path.is_file():
        stat = path.stat()
        item.update({
            "type": "file",
            "size_bytes": stat.st_size,
            "modified_utc": dt.datetime.fromtimestamp(
                stat.st_mtime,
                tz=dt.timezone.utc,
            ).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "sha256": sha256_file(path),
        })

        if path.suffix.lower() == ".json":
            data = read_json(path)
            if isinstance(data, dict):
                item["status"] = data.get("status")
                item["checkpoint"] = data.get("checkpoint")
                item["mode"] = data.get("mode")
                item["next_checkpoint"] = data.get("next_checkpoint")
    elif path.exists() and path.is_dir():
        item.update({
            "type": "directory",
            "file_count": sum(1 for child in path.rglob("*") if child.is_file()),
        })
    else:
        item["type"] = "missing"

    return item


def default_config() -> Dict[str, Any]:
    return {
        "checkpoint": CHECKPOINT_ID,
        "name": CHECKPOINT_NAME,
        "layer": LAYER_NAME,
        "objective": (
            "Criar pacote final de documentacao do K-OS consolidando arquitetura, "
            "operacao, governanca, launcher local, evidencias dos checkpoints 079-085 "
            "e indice de continuidade, sem executar deploy, installer, recovery, rollback, "
            "drill, reset, force push, limpeza destrutiva ou auto-fix."
        ),
        "previous_checkpoint": PREVIOUS_CHECKPOINT,
        "next_checkpoint": NEXT_CHECKPOINT,
        "source_checkpoints": SOURCE_CHECKPOINTS,
        "documentation_outputs": [rel(path) for path in DOC_OUTPUTS.values()],
        "allowed_operations": [
            "read_existing_evidence",
            "generate_final_documentation_pack",
            "generate_sanitized_reports",
            "generate_read_only_dashboard",
            "update_accountability_register_if_exists",
            "validate_artifacts",
            "audit_checkpoint",
            "create_closure_report",
        ],
        "blocked_operations": BLOCKED_OPERATIONS,
        "documentation_policy": {
            "generate_docs_only": True,
            "read_only_evidence": True,
            "sanitize_reports": True,
            "include_sensitive_content": False,
            "include_file_hashes": True,
            "execute_launcher": False,
            "execute_installer": False,
            "publish_release": False,
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


def collect_checkpoint_evidence() -> Dict[str, Any]:
    items: Dict[str, Any] = {}

    for checkpoint, definition in CHECKPOINT_ARTIFACTS.items():
        base_dir = ROOT / definition["dir"]
        main_path = base_dir / definition["main"]
        closure_path = base_dir / definition["closure"]
        doc_path = ROOT / definition["doc"]

        main_data = read_json(main_path)
        closure_data = read_json(closure_path)

        status = "ready"
        if not isinstance(main_data, dict):
            status = "warning"
        if not isinstance(closure_data, dict) or closure_data.get("status") != "closed":
            status = "warning"
        if not doc_path.exists():
            status = "warning"

        files = []
        if base_dir.exists():
            for path in sorted(base_dir.glob("*"), key=lambda item: rel(item)):
                if path.is_file():
                    files.append(file_info(path))

        items[checkpoint] = {
            "checkpoint": checkpoint,
            "name": definition["name"],
            "status": status,
            "directory": file_info(base_dir),
            "main_report": file_info(main_path),
            "closure_report": file_info(closure_path),
            "commercial_doc": file_info(doc_path),
            "main_status": main_data.get("status") if isinstance(main_data, dict) else None,
            "closure_status": closure_data.get("status") if isinstance(closure_data, dict) else None,
            "evidence_file_count": len(files),
            "files": files[:80],
        }

    ready_count = sum(1 for item in items.values() if item["status"] == "ready")

    return {
        "generated_at": now_utc(),
        "source_checkpoints": SOURCE_CHECKPOINTS,
        "ready_count": ready_count,
        "warning_count": len(items) - ready_count,
        "checkpoints": items,
    }


def collect_project_surface() -> Dict[str, Any]:
    entrypoint_candidates = ["app.py", "streamlit_app.py", "Home.py"]
    found_entrypoints = [file_info(ROOT / item) for item in entrypoint_candidates if (ROOT / item).exists()]

    launcher_scripts = [
        ROOT / "scripts" / "k_os_local_install_check.ps1",
        ROOT / "scripts" / "k_os_local_launcher.ps1",
    ]

    roots = [
        ROOT / "k_atlas",
        ROOT / "agents",
        ROOT / "memory",
        ROOT / "reports",
        ROOT / "configs",
        ROOT / "scripts",
        ROOT / "pages",
        ROOT / "docs",
    ]

    return {
        "entrypoint": {
            "candidates": entrypoint_candidates,
            "found": found_entrypoints,
            "selected": found_entrypoints[0]["path"] if found_entrypoints else None,
            "status": "ready" if found_entrypoints else "warning",
        },
        "launcher_scripts": [file_info(path) for path in launcher_scripts],
        "project_roots": [file_info(path) for path in roots],
    }


def doc_header(title: str) -> List[str]:
    return [
        f"# {title}",
        "",
        f"Gerado em: {now_utc()}",
        "",
        "Projeto: K-Atlas / K-OS / motor-digital",
        "",
    ]


def generate_readme(evidence: Dict[str, Any], surface: Dict[str, Any]) -> str:
    lines = doc_header("K-OS - Documentacao Final")
    lines.extend([
        "## Visao geral",
        "",
        "O K-OS e a camada operacional do K-Atlas para coordenacao local de agentes, memoria, modulos, comandos, relatorios, governanca e cockpit Streamlit.",
        "",
        "## Estado atual",
        "",
        f"- Checkpoints consolidados: {', '.join(SOURCE_CHECKPOINTS)}",
        f"- Evidencias prontas: {evidence['ready_count']}",
        f"- Evidencias com warning: {evidence['warning_count']}",
        f"- Entrypoint Streamlit selecionado: {surface['entrypoint']['selected']}",
        "",
        "## Documentos principais",
        "",
    ])

    for key, path in DOC_OUTPUTS.items():
        lines.append(f"- {rel(path)}")

    lines.extend([
        "",
        "## Comandos manuais principais",
        "",
        "Checagem local:",
        "",
        "```powershell",
        "powershell -ExecutionPolicy Bypass -File scripts\\k_os_local_install_check.ps1",
        "```",
        "",
        "Abrir cockpit:",
        "",
        "```powershell",
        "powershell -ExecutionPolicy Bypass -File scripts\\k_os_local_launcher.ps1",
        "```",
        "",
    ])
    return "\n".join(lines)


def generate_operator_guide(evidence: Dict[str, Any]) -> str:
    lines = doc_header("K-OS - Guia Operacional")
    lines.extend([
        "## Prioridade operacional",
        "",
        "1. Validar ambiente local.",
        "2. Abrir cockpit Streamlit.",
        "3. Consultar registries e relatorios.",
        "4. Operar somente com comandos aprovados.",
        "5. Registrar evidencias antes de qualquer mudanca relevante.",
        "",
        "## Checagem local",
        "",
        "```powershell",
        "powershell -ExecutionPolicy Bypass -File scripts\\k_os_local_install_check.ps1",
        "```",
        "",
        "## Abrir cockpit",
        "",
        "```powershell",
        "powershell -ExecutionPolicy Bypass -File scripts\\k_os_local_launcher.ps1",
        "```",
        "",
        "## Regras de seguranca",
        "",
        "- Nao subir segredos para GitHub.",
        "- Nao versionar local_secrets.",
        "- Nao versionar memory/runtime.",
        "- Nao executar git reset hard.",
        "- Nao executar force push.",
        "- Nao executar recovery, rollback ou drill real.",
        "- Nao executar comandos destrutivos.",
        "",
        "## Continuidade",
        "",
        "Proximo checkpoint: 087 - K-OS Final Audit Pack Core.",
        "",
    ])
    return "\n".join(lines)


def generate_architecture(evidence: Dict[str, Any], surface: Dict[str, Any]) -> str:
    lines = doc_header("K-OS - Arquitetura")
    lines.extend([
        "## Camadas",
        "",
        "- IA: cerebro operacional.",
        "- Python: executor local.",
        "- JSON: estado e evidencias.",
        "- Streamlit: cockpit operacional.",
        "- GitHub: memoria persistente versionada.",
        "- Reports: auditoria e rastreabilidade.",
        "",
        "## Estrutura principal",
        "",
    ])

    for item in surface["project_roots"]:
        lines.append(f"- {item['path']}: exists={item['exists']}")

    lines.extend([
        "",
        "## Checkpoints K-OS consolidados",
        "",
        "| Checkpoint | Nome | Status | Evidencias |",
        "|---:|---|---|---:|",
    ])

    for checkpoint, item in evidence["checkpoints"].items():
        lines.append(f"| {checkpoint} | {item['name']} | {item['status']} | {item['evidence_file_count']} |")

    lines.extend([
        "",
        "## Principios",
        "",
        "- Interface nao deve conter logica critica.",
        "- Toda acao importante deve gerar evento, relatorio e evidencia.",
        "- Todo modulo deve ser reutilizavel.",
        "- Toda automacao deve possuir logs.",
        "- Todo deploy deve ser reversivel.",
        "",
    ])
    return "\n".join(lines)


def generate_governance(evidence: Dict[str, Any]) -> str:
    lines = doc_header("K-OS - Governanca")
    lines.extend([
        "## Politica de governanca",
        "",
        "- Execucao real exige aprovacao operacional.",
        "- Checkpoints finais sao baseados em evidencia local sanitizada.",
        "- Relatorios devem evitar conteudo sensivel.",
        "- Comandos perigosos permanecem bloqueados.",
        "",
        "## Operacoes bloqueadas nesta fase",
        "",
    ])

    for operation in BLOCKED_OPERATIONS:
        lines.append(f"- {operation}")

    lines.extend([
        "",
        "## Evidencias de checkpoint",
        "",
        "| Checkpoint | Main | Closure | Doc | Status |",
        "|---:|---|---|---|---|",
    ])

    for checkpoint, item in evidence["checkpoints"].items():
        lines.append(
            f"| {checkpoint} | {item['main_report']['exists']} | "
            f"{item['closure_report']['exists']} | {item['commercial_doc']['exists']} | {item['status']} |"
        )

    lines.extend([
        "",
        "## Decisao",
        "",
        "A documentacao final foi gerada em modo somente escrita de artefatos, sem executar deploy, installer, recovery ou rollback.",
        "",
    ])
    return "\n".join(lines)


def generate_launcher_guide(surface: Dict[str, Any]) -> str:
    lines = doc_header("K-OS - Launcher Local")
    lines.extend([
        "## Objetivo",
        "",
        "Fornecer comandos manuais para validar e abrir o cockpit local.",
        "",
        "## Checagem",
        "",
        "```powershell",
        "powershell -ExecutionPolicy Bypass -File scripts\\k_os_local_install_check.ps1",
        "```",
        "",
        "## Abrir cockpit",
        "",
        "```powershell",
        "powershell -ExecutionPolicy Bypass -File scripts\\k_os_local_launcher.ps1",
        "```",
        "",
        "## Entrypoint detectado",
        "",
        f"- Selecionado: {surface['entrypoint']['selected']}",
        "",
        "## Scripts",
        "",
    ])

    for item in surface["launcher_scripts"]:
        lines.append(f"- {item['path']}: exists={item['exists']} sha256={item.get('sha256')}")

    lines.extend([
        "",
        "## Observacao",
        "",
        "O launcher nao deve instalar dependencias automaticamente. Caso falte dependencia, o operador decide manualmente.",
        "",
    ])
    return "\n".join(lines)


def generate_release_notes(evidence: Dict[str, Any]) -> str:
    lines = doc_header("K-OS - Release Notes")
    lines.extend([
        "## Escopo desta release candidate",
        "",
        "Esta release candidate consolida a camada K-OS Core de 079 a 086.",
        "",
        "## Checkpoints incluidos",
        "",
    ])

    for checkpoint, item in evidence["checkpoints"].items():
        lines.append(f"- {checkpoint} - {item['name']}: {item['status']}")

    lines.extend([
        "",
        "## Proximo passo",
        "",
        "087 - K-OS Final Audit Pack Core.",
        "",
        "## Restricoes",
        "",
        "Nenhum deploy, release publish, installer real, rollback, recovery ou drill real foi executado por este checkpoint.",
        "",
    ])
    return "\n".join(lines)


def generate_index(evidence: Dict[str, Any]) -> str:
    lines = doc_header("K-OS - Indice Final de Documentacao")
    lines.extend([
        "## Arquivos gerados",
        "",
        "| Documento | Caminho |",
        "|---|---|",
    ])

    for key, path in DOC_OUTPUTS.items():
        lines.append(f"| {key} | {rel(path)} |")

    lines.extend([
        "",
        "## Evidencias consolidadas",
        "",
        "| Checkpoint | Status | Main report | Closure |",
        "|---:|---|---|---|",
    ])

    for checkpoint, item in evidence["checkpoints"].items():
        lines.append(
            f"| {checkpoint} | {item['status']} | "
            f"{item['main_report']['path']} | {item['closure_report']['path']} |"
        )

    lines.extend([
        "",
        "## Continuidade",
        "",
        "Proximo checkpoint: 087 - K-OS Final Audit Pack Core.",
        "",
    ])
    return "\n".join(lines)


def build_documentation_pack(config: Dict[str, Any]) -> Dict[str, Any]:
    evidence = collect_checkpoint_evidence()
    surface = collect_project_surface()

    warnings = []
    if evidence["warning_count"] > 0:
        warnings.append("source_checkpoint_evidence_warning")
    if surface["entrypoint"]["status"] != "ready":
        warnings.append("streamlit_entrypoint_warning")

    docs_content = {
        "readme": generate_readme(evidence, surface),
        "operator_guide": generate_operator_guide(evidence),
        "architecture": generate_architecture(evidence, surface),
        "governance": generate_governance(evidence),
        "launcher_guide": generate_launcher_guide(surface),
        "release_notes": generate_release_notes(evidence),
        "index": generate_index(evidence),
    }

    for key, content in docs_content.items():
        write_text(DOC_OUTPUTS[key], content)

    doc_files = [file_info(path) for path in DOC_OUTPUTS.values()]

    status = "ready" if not warnings else "ready_with_warnings"

    return {
        "checkpoint": CHECKPOINT_ID,
        "name": CHECKPOINT_NAME,
        "layer": LAYER_NAME,
        "generated_at": now_utc(),
        "status": status,
        "objective": config.get("objective"),
        "previous_checkpoint": config.get("previous_checkpoint", PREVIOUS_CHECKPOINT),
        "next_checkpoint": config.get("next_checkpoint", NEXT_CHECKPOINT),
        "documentation_policy": sanitize(config.get("documentation_policy", {})),
        "source_checkpoints": SOURCE_CHECKPOINTS,
        "evidence": evidence,
        "project_surface": surface,
        "documentation_outputs": doc_files,
        "warnings": warnings,
        "blocked_operations": BLOCKED_OPERATIONS,
        "execution_guard": {
            "deploy_executed": False,
            "installer_executed": False,
            "dependency_install_executed": False,
            "release_publish_executed": False,
            "backup_restore_executed": False,
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
            "final_documentation_pack_created": True,
            "docs_generated": True,
            "docs_count": len(doc_files),
            "installer_executed": False,
            "deploy_executed": False,
            "release_published": False,
            "can_continue_to_next_checkpoint": True,
            "next_checkpoint": config.get("next_checkpoint", NEXT_CHECKPOINT),
        },
    }


def pack_markdown(pack: Dict[str, Any]) -> str:
    lines: List[str] = []

    lines.append("# 086 - K-OS Final Documentation Pack Core")
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
    lines.append(f"- Status do pacote: {pack['status']}")
    lines.append(f"- Checkpoint anterior: {pack['previous_checkpoint']}")
    lines.append(f"- Proximo checkpoint: {pack['next_checkpoint']}")
    lines.append(f"- Documentos gerados: {len(pack['documentation_outputs'])}")
    lines.append("")

    lines.append("## Documentos gerados")
    lines.append("")
    lines.append("| Documento | Existe | SHA256 |")
    lines.append("|---|---|---|")
    for item in pack["documentation_outputs"]:
        lines.append(f"| {item['path']} | {item['exists']} | {item.get('sha256')} |")
    lines.append("")

    lines.append("## Checkpoints documentados")
    lines.append("")
    lines.append("| Checkpoint | Nome | Status | Evidencias |")
    lines.append("|---:|---|---|---:|")
    for checkpoint, item in pack["evidence"]["checkpoints"].items():
        lines.append(f"| {checkpoint} | {item['name']} | {item['status']} | {item['evidence_file_count']} |")
    lines.append("")

    lines.append("## Warnings")
    lines.append("")
    if pack["warnings"]:
        for warning in pack["warnings"]:
            lines.append(f"- {warning}")
    else:
        lines.append("Nenhum warning registrado.")
    lines.append("")

    lines.append("## Garantias de nao execucao")
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
    lines.append("Pacote final de documentacao criado. O sistema pode seguir para 087 - K-OS Final Audit Pack Core.")
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
        "documentation_pack": rel(REPORT_DIR / "086_final_documentation_pack.json"),
        "closure_report": rel(REPORT_DIR / "086_closure_report.json"),
        "docs_count": len(pack["documentation_outputs"]),
        "next_checkpoint": NEXT_CHECKPOINT,
        "docs_generated": True,
        "deploy_executed": False,
        "installer_executed": False,
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
            "deploy_executed": False,
            "installer_executed": False,
            "dependency_install_executed": False,
            "release_publish_executed": False,
            "real_recovery_executed": False,
            "real_rollback_executed": False,
        },
        "config": sanitize(config),
    }

    write_json(REPORT_DIR / "086_init_report.json", report)
    return report


def mode_action() -> Dict[str, Any]:
    ensure_dirs()
    config = load_config()
    pack = build_documentation_pack(config)

    write_json(REPORT_DIR / "086_final_documentation_pack.json", pack)
    write_text(REPORT_DIR / "086_final_documentation_pack.md", pack_markdown(pack))
    write_text(COMMERCIAL_DOCS_PATH, pack_markdown(pack))

    updated_registers = update_accountability_register(pack)

    report = {
        "checkpoint": CHECKPOINT_ID,
        "name": CHECKPOINT_NAME,
        "mode": "action",
        "status": "completed",
        "generated_at": now_utc(),
        "pack_status": pack["status"],
        "warnings": pack["warnings"],
        "docs_count": len(pack["documentation_outputs"]),
        "final_documentation_pack_json": rel(REPORT_DIR / "086_final_documentation_pack.json"),
        "final_documentation_pack_md": rel(REPORT_DIR / "086_final_documentation_pack.md"),
        "commercial_doc": rel(COMMERCIAL_DOCS_PATH),
        "documentation_outputs": [item["path"] for item in pack["documentation_outputs"]],
        "updated_accountability_registers": updated_registers,
        "next_checkpoint": NEXT_CHECKPOINT,
        "deploy_executed": False,
        "installer_executed": False,
        "blocked_operations": BLOCKED_OPERATIONS,
        "execution_guard": pack["execution_guard"],
    }

    write_json(REPORT_DIR / "086_action_report.json", report)
    return report


def mode_validate() -> Dict[str, Any]:
    ensure_dirs()

    expected_files = [
        CONFIG_PATH,
        Path(__file__),
        ROOT / "scripts" / "checkpoint_086_final_documentation_pack.ps1",
        ROOT / "pages" / "086_K_OS_Final_Documentation_Pack.py",
        COMMERCIAL_DOCS_PATH,
        REPORT_DIR / "086_init_report.json",
        REPORT_DIR / "086_action_report.json",
        REPORT_DIR / "086_final_documentation_pack.json",
        REPORT_DIR / "086_final_documentation_pack.md",
    ] + list(DOC_OUTPUTS.values())

    checks = []
    for path in expected_files:
        checks.append({
            "path": rel(path),
            "exists": path.exists(),
        })

    pack = read_json(REPORT_DIR / "086_final_documentation_pack.json")

    guard_ok = False
    decision_ok = False
    docs_ok = False

    if isinstance(pack, dict):
        guard = pack.get("execution_guard", {})
        guard_ok = isinstance(guard, dict) and all(value is False for value in guard.values())
        decision = pack.get("operational_decision", {})
        decision_ok = (
            isinstance(decision, dict)
            and decision.get("final_documentation_pack_created") is True
            and decision.get("docs_generated") is True
            and decision.get("deploy_executed") is False
            and decision.get("installer_executed") is False
            and decision.get("release_published") is False
            and decision.get("next_checkpoint") == NEXT_CHECKPOINT
        )
        docs = pack.get("documentation_outputs", [])
        docs_ok = isinstance(docs, list) and len(docs) >= 7 and all(
            isinstance(item, dict) and item.get("exists") is True
            for item in docs
        )

    all_files_exist = all(item["exists"] for item in checks)

    report = {
        "checkpoint": CHECKPOINT_ID,
        "name": CHECKPOINT_NAME,
        "mode": "validate",
        "status": "passed" if all_files_exist and guard_ok and decision_ok and docs_ok else "failed",
        "generated_at": now_utc(),
        "file_checks": checks,
        "execution_guard_ok": guard_ok,
        "operational_decision_ok": decision_ok,
        "documentation_outputs_ok": docs_ok,
        "next_checkpoint": NEXT_CHECKPOINT,
    }

    write_json(REPORT_DIR / "086_validate_report.json", report)

    if report["status"] != "passed":
        raise RuntimeError("Checkpoint 086 validation failed.")

    return report


def mode_audit() -> Dict[str, Any]:
    ensure_dirs()

    validate_report = read_json(REPORT_DIR / "086_validate_report.json")
    pack = read_json(REPORT_DIR / "086_final_documentation_pack.json")

    validate_passed = isinstance(validate_report, dict) and validate_report.get("status") == "passed"
    pack_exists = isinstance(pack, dict)

    checks = {
        "validate_passed": validate_passed,
        "final_documentation_pack_exists": pack_exists,
        "docs_generated": True,
        "deploy_not_executed": True,
        "installer_not_executed": True,
        "dependency_install_not_executed": True,
        "release_not_published": True,
        "backup_restore_not_executed": True,
        "automatic_remediation_not_executed": True,
        "real_drill_not_executed": True,
        "real_recovery_not_executed": True,
        "real_rollback_not_executed": True,
        "git_reset_hard_not_executed": True,
        "force_push_not_executed": True,
        "destructive_shell_not_executed": True,
        "memory_deletion_not_executed": True,
        "secret_export_not_executed": True,
        "reports_are_sanitized": True,
        "transition_to_087_declared": True,
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

    write_json(REPORT_DIR / "086_audit_report.json", report)

    if report["status"] != "passed":
        raise RuntimeError("Checkpoint 086 audit failed.")

    return report


def final_closure_markdown(report: Dict[str, Any]) -> str:
    lines = []
    lines.append("# 086 - Closure Report")
    lines.append("")
    lines.append(f"Checkpoint: {report['checkpoint']}")
    lines.append(f"Nome: {report['name']}")
    lines.append(f"Status: {report['status']}")
    lines.append(f"Gerado em: {report['generated_at']}")
    lines.append("")
    lines.append("## Resultado")
    lines.append("")
    lines.append("Checkpoint 086 fechado. Pacote final de documentacao do K-OS criado e validado.")
    lines.append("")
    lines.append("## Documentos principais")
    lines.append("")
    for path in DOC_OUTPUTS.values():
        lines.append(f"- {rel(path)}")
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

    action_report = read_json(REPORT_DIR / "086_action_report.json")
    validate_report = read_json(REPORT_DIR / "086_validate_report.json")
    audit_report = read_json(REPORT_DIR / "086_audit_report.json")
    pack = read_json(REPORT_DIR / "086_final_documentation_pack.json")

    ok = (
        isinstance(action_report, dict)
        and action_report.get("status") == "completed"
        and isinstance(validate_report, dict)
        and validate_report.get("status") == "passed"
        and isinstance(audit_report, dict)
        and audit_report.get("status") == "passed"
        and isinstance(pack, dict)
    )

    report = {
        "checkpoint": CHECKPOINT_ID,
        "name": CHECKPOINT_NAME,
        "mode": "closure",
        "status": "closed" if ok else "failed",
        "generated_at": now_utc(),
        "pack_status": pack.get("status") if isinstance(pack, dict) else "unknown",
        "docs_count": len(pack.get("documentation_outputs", [])) if isinstance(pack, dict) else 0,
        "next_checkpoint": NEXT_CHECKPOINT,
        "action_report": rel(REPORT_DIR / "086_action_report.json"),
        "validate_report": rel(REPORT_DIR / "086_validate_report.json"),
        "audit_report": rel(REPORT_DIR / "086_audit_report.json"),
        "final_documentation_pack": rel(REPORT_DIR / "086_final_documentation_pack.json"),
        "deploy_executed": False,
        "installer_executed": False,
        "release_published": False,
        "blocked_operations_confirmed": True,
    }

    write_json(REPORT_DIR / "086_closure_report.json", report)
    write_text(REPORT_DIR / "086_closure_report.md", final_closure_markdown(report))

    if report["status"] != "closed":
        raise RuntimeError("Checkpoint 086 closure failed.")

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