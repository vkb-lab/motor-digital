# -*- coding: utf-8 -*-
"""
K-OS Security Firewall
Checkpoint 015

Objetivo:
- impedir commit acidental de tokens, chaves, credenciais, leads e dados sensíveis
- gerar evidência de auditoria
- funcionar como pre-commit guard
- manter live/ e runtime fora do GitHub
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

ROOT = Path.cwd()
REPORT_DIR = ROOT / "reports" / "security"
MEMORY_DIR = ROOT / "memory" / "security"
LATEST_JSON = REPORT_DIR / "latest_security_firewall_report.json"
LATEST_MD = REPORT_DIR / "latest_security_firewall_report.md"
EVENTS_JSONL = MEMORY_DIR / "security_firewall_events.jsonl"

BLOCKED_PATH_PREFIXES = [
    "live/",
    "secrets/",
    "credentials/",
    "private/",
    "local_secrets/",
    "memory/k_uni_runtime/",
    "reports/k_uni_hygiene/",
    "reports/k_uni_master/",
]

BLOCKED_PATH_FRAGMENTS = [
    "lead_intake",
    "manual_send_pack",
    "approval_decision",
    "latest_public_commercial_proposal",
    "latest_public_lead_diagnostic",
    "latest_commercial_proposal",
    "latest_lead_diagnostic",
    "public_capture_queue",
    "credential",
    "credentials",
    "secret",
    "token",
    "api_key",
    "apikey",
    "password",
    "senha",
]

BLOCKED_EXTENSIONS = [
    ".pem",
    ".key",
    ".p12",
    ".pfx",
    ".db",
    ".sqlite",
    ".sqlite3",
]

HIGH_CONFIDENCE_PATTERNS = [
    {
        "name": "github_token",
        "pattern": r"(gh[pousr]_[A-Za-z0-9_]{30,}|github_pat_[A-Za-z0-9_]{40,})",
        "severity": "critical",
    },
    {
        "name": "openai_like_secret",
        "pattern": r"\bsk-[A-Za-z0-9_\-]{30,}\b",
        "severity": "critical",
    },
    {
        "name": "aws_access_key",
        "pattern": r"\bAKIA[0-9A-Z]{16}\b",
        "severity": "critical",
    },
    {
        "name": "google_api_key",
        "pattern": r"\bAIza[0-9A-Za-z_\-]{30,}\b",
        "severity": "critical",
    },
    {
        "name": "slack_token",
        "pattern": r"\bxox[baprs]-[A-Za-z0-9\-]{20,}\b",
        "severity": "critical",
    },
    {
        "name": "private_key_block",
        "pattern": r"-----BEGIN (RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----",
        "severity": "critical",
    },
    {
        "name": "long_secret_assignment",
        "pattern": r"(?i)\b(api[_-]?key|secret|token|password|senha|client_secret)\b\s*[:=]\s*[\"']?[A-Za-z0-9_\-./+=]{24,}",
        "severity": "high",
    },
]

SAFE_TEXT_EXTENSIONS = {
    ".py",
    ".ps1",
    ".md",
    ".txt",
    ".json",
    ".jsonl",
    ".yaml",
    ".yml",
    ".toml",
    ".html",
    ".css",
    ".js",
    ".ts",
    ".csv",
    ".gitignore",
}

MAX_SCAN_BYTES = 2_000_000


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize(path: str | Path) -> str:
    return str(path).replace("\\", "/").lstrip("./")


def run_git(args: list[str]) -> tuple[int, str, str]:
    completed = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return completed.returncode, completed.stdout.strip(), completed.stderr.strip()


def get_staged_files() -> list[str]:
    code, stdout, stderr = run_git(["diff", "--cached", "--name-only", "--diff-filter=ACMRT"])
    if code != 0:
        raise RuntimeError(f"Falha ao listar arquivos staged: {stderr}")
    return [line.strip() for line in stdout.splitlines() if line.strip()]


def get_working_files() -> list[str]:
    code, stdout, stderr = run_git(["ls-files", "--others", "--cached", "--modified", "--exclude-standard"])
    if code != 0:
        raise RuntimeError(f"Falha ao listar arquivos working tree: {stderr}")
    return sorted(set(line.strip() for line in stdout.splitlines() if line.strip()))


def path_is_blocked(path: str) -> list[dict]:
    normalized = normalize(path)
    lower = normalized.lower()
    findings = []

    for prefix in BLOCKED_PATH_PREFIXES:
        if lower.startswith(prefix.lower()):
            findings.append({
                "type": "blocked_path_prefix",
                "severity": "critical",
                "path": normalized,
                "reason": f"path starts with {prefix}",
            })

    for fragment in BLOCKED_PATH_FRAGMENTS:
        if fragment.lower() in lower:
            findings.append({
                "type": "blocked_path_fragment",
                "severity": "high",
                "path": normalized,
                "reason": f"path contains {fragment}",
            })

    suffix = Path(lower).suffix
    if suffix in BLOCKED_EXTENSIONS:
        findings.append({
            "type": "blocked_extension",
            "severity": "critical",
            "path": normalized,
            "reason": f"extension {suffix} is blocked",
        })

    return findings


def should_scan_content(path: Path) -> bool:
    if not path.exists() or not path.is_file():
        return False

    if path.stat().st_size > MAX_SCAN_BYTES:
        return False

    suffix = path.suffix.lower()

    if path.name == ".gitignore":
        return True

    if suffix in SAFE_TEXT_EXTENSIONS:
        return True

    return False


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def scan_content(path: Path) -> list[dict]:
    findings = []

    if not should_scan_content(path):
        return findings

    try:
        text = path.read_text(encoding="utf-8-sig", errors="replace")
    except Exception:
        return findings

    normalized = normalize(path.relative_to(ROOT) if path.is_absolute() else path)

    for item in HIGH_CONFIDENCE_PATTERNS:
        pattern = re.compile(item["pattern"])
        for match in pattern.finditer(text):
            start = max(0, match.start() - 12)
            end = min(len(text), match.end() + 12)
            context = text[start:end].replace("\n", " ").replace("\r", " ")

            findings.append({
                "type": "secret_pattern",
                "name": item["name"],
                "severity": item["severity"],
                "path": normalized,
                "hash": sha256_text(match.group(0)),
                "context_preview": context[:160],
                "reason": "high confidence secret-like pattern detected",
            })

    return findings


def scan_files(files: Iterable[str]) -> dict:
    findings = []

    for file_item in files:
        normalized = normalize(file_item)
        findings.extend(path_is_blocked(normalized))

        path = ROOT / normalized
        findings.extend(scan_content(path))

    blocking = [item for item in findings if item.get("severity") in {"critical", "high"}]

    return {
        "ok": len(blocking) == 0,
        "status": "passed" if len(blocking) == 0 else "blocked",
        "generated_at": utc_now(),
        "repo": str(ROOT),
        "files_scanned": list(files),
        "findings_count": len(findings),
        "blocking_findings_count": len(blocking),
        "findings": findings,
        "policy": {
            "external_send_enabled": False,
            "external_publish_enabled": False,
            "manual_approval_required": True,
            "sensitive_paths_blocked": BLOCKED_PATH_PREFIXES,
        },
    }


def write_report(report: dict) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)

    LATEST_JSON.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    lines = [
        "# K-OS Security Firewall Report",
        "",
        f"- Status: {report.get('status')}",
        f"- OK: {report.get('ok')}",
        f"- Generated at: {report.get('generated_at')}",
        f"- Files scanned: {len(report.get('files_scanned', []))}",
        f"- Findings: {report.get('findings_count')}",
        f"- Blocking findings: {report.get('blocking_findings_count')}",
        "",
        "## Findings",
        "",
    ]

    for finding in report.get("findings", []):
        lines.append(f"- {finding.get('severity')} | {finding.get('type')} | {finding.get('path')} | {finding.get('reason')}")

    if not report.get("findings"):
        lines.append("- Nenhum risco bloqueante encontrado.")

    LATEST_MD.write_text("\n".join(lines), encoding="utf-8")

    event = {
        "event": "security_firewall.scan",
        "created_at": utc_now(),
        "status": report.get("status"),
        "ok": report.get("ok"),
        "blocking_findings_count": report.get("blocking_findings_count"),
    }

    with EVENTS_JSONL.open("a", encoding="utf-8") as file:
        file.write(json.dumps(event, ensure_ascii=False) + "\n")


def install_hook() -> dict:
    git_dir = ROOT / ".git"
    hook_dir = git_dir / "hooks"
    hook_dir.mkdir(parents=True, exist_ok=True)

    hook_path = hook_dir / "pre-commit"
    hook_content = """#!/bin/sh
python ops/k_os_security_firewall.py --mode scan-staged --no-write-report
RESULT=$?
if [ $RESULT -ne 0 ]; then
  echo ""
  echo "K-OS Security Firewall bloqueou este commit."
  echo "Rode: python ops/k_os_security_firewall.py --mode scan-staged"
  exit $RESULT
fi
exit 0
"""

    hook_path.write_text(hook_content, encoding="utf-8")
    try:
        os.chmod(hook_path, 0o755)
    except Exception:
        pass

    return {
        "ok": True,
        "status": "hook_installed",
        "hook_path": normalize(hook_path),
        "generated_at": utc_now(),
    }


def smoke_test() -> dict:
    safe_file = ROOT / "reports" / "security" / "_smoke_safe.txt"
    risky_file = ROOT / "reports" / "security" / "_smoke_risky.txt"

    safe_file.parent.mkdir(parents=True, exist_ok=True)

    safe_file.write_text(
        "K-OS smoke safe file. Sem token real. Sem credencial.",
        encoding="utf-8",
    )

    fake_github = "ghp_" + ("A" * 40)
    fake_openai = "sk-" + ("B" * 40)

    risky_file.write_text(
        f"fake_token={fake_github}\nfake_openai={fake_openai}\n",
        encoding="utf-8",
    )

    safe_report = scan_files([normalize(safe_file.relative_to(ROOT))])
    risky_report = scan_files([normalize(risky_file.relative_to(ROOT))])

    try:
        safe_file.unlink(missing_ok=True)
        risky_file.unlink(missing_ok=True)
    except Exception:
        pass

    ok = safe_report["ok"] is True and risky_report["ok"] is False

    report = {
        "ok": ok,
        "status": "smoke_passed" if ok else "smoke_failed",
        "generated_at": utc_now(),
        "safe_report_status": safe_report["status"],
        "risky_report_status": risky_report["status"],
        "risky_findings_count": risky_report["findings_count"],
    }

    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["scan-staged", "scan-working", "install-hook", "smoke-test"], required=True)
    parser.add_argument("--no-write-report", action="store_true")
    args = parser.parse_args()

    if args.mode == "scan-staged":
        files = get_staged_files()
        report = scan_files(files)
        if not args.no_write_report:
            write_report(report)

        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report["ok"] else 2

    if args.mode == "scan-working":
        files = get_working_files()
        report = scan_files(files)
        if not args.no_write_report:
            write_report(report)

        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report["ok"] else 2

    if args.mode == "install-hook":
        report = install_hook()
        if not args.no_write_report:
            write_report(report)

        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    if args.mode == "smoke-test":
        report = smoke_test()
        if not args.no_write_report:
            write_report(report)

        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report["ok"] else 3

    return 1


if __name__ == "__main__":
    raise SystemExit(main())