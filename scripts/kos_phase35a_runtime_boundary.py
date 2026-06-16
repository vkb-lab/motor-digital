from pathlib import Path
import json
import subprocess
from datetime import datetime, timezone
import shutil

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
Q = ROOT / "_local_quarantine" / f"phase35a_runtime_boundary_{STAMP}"

REPORT = ROOT / "reports" / "KOS_PHASE35A_RUNTIME_BOUNDARY_REPORT.json"
BOUNDARY = ROOT / "config" / "kos_runtime_boundary.json"
STATE = ROOT / "memory" / "kaizen" / "state.json"
STATE_EXAMPLE = ROOT / "memory" / "kaizen" / "state.example.json"

def now():
    return datetime.now(timezone.utc).isoformat()

def run(cmd):
    p = subprocess.run(cmd, cwd=ROOT, shell=True, capture_output=True, text=True)
    return {
        "cmd": cmd,
        "returncode": p.returncode,
        "stdout": (p.stdout or "")[-4000:],
        "stderr": (p.stderr or "")[-4000:]
    }

def backup(path: Path, items: list):
    if path.exists():
        dest = Q / path.relative_to(ROOT)
        dest.parent.mkdir(parents=True, exist_ok=True)
        if path.is_dir():
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(path, dest)
        else:
            shutil.copy2(path, dest)
        items.append({
            "original": str(path.relative_to(ROOT)).replace("\\", "/"),
            "backup": str(dest.relative_to(ROOT)).replace("\\", "/")
        })

Q.mkdir(parents=True, exist_ok=True)

runtime_files = [
    ROOT / "memory" / "kaizen" / "state.json",
    ROOT / "reports" / "KOS_KAIZEN_LAST_CYCLE_REPORT.json",
    ROOT / "reports" / "security" / "latest_security_firewall_report.json",
    ROOT / "reports" / "security" / "latest_security_firewall_report.md",
]

runtime_dirs = [
    ROOT / "local_runtime",
    ROOT / "logs",
    ROOT / "memory" / "security",
    ROOT / "memory" / "sandbox_api_adapter",
    ROOT / "ops" / "codex",
]

backups = []
for f in runtime_files:
    backup(f, backups)

for d in runtime_dirs:
    backup(d, backups)

boundary = {
    "status": "ACTIVE",
    "phase": "35A",
    "purpose": "separar codigo versionavel de runtime local para permitir ciclos Kaizen repetidos sem sujar o Git",
    "versioned": [
        "k_atlas/",
        "agents/",
        "pages/",
        "scripts/",
        "config/",
        "tests/",
        "docs/",
        "memory/kaizen/task_queue.json",
        "memory/kaizen/state.example.json"
    ],
    "local_runtime_ignored": [
        "local_runtime/",
        "logs/",
        "memory/security/",
        "memory/sandbox_api_adapter/",
        "memory/kaizen/state.json",
        "reports/security/latest_security_firewall_report.json",
        "reports/security/latest_security_firewall_report.md",
        "reports/KOS_KAIZEN_LAST_CYCLE_REPORT.json",
        "ops/codex/"
    ],
    "hard_rules": {
        "no_paid_ai_without_budget": True,
        "no_instagram_publish_without_human_confirmation": True,
        "no_secret_commit": True,
        "firewall_before_commit": True,
        "runtime_files_are_local": True
    },
    "created_at": now()
}

BOUNDARY.parent.mkdir(parents=True, exist_ok=True)
BOUNDARY.write_text(json.dumps(boundary, ensure_ascii=False, indent=2), encoding="utf-8")

if STATE.exists():
    try:
        state_data = json.loads(STATE.read_text(encoding="utf-8-sig"))
    except Exception:
        state_data = {}
else:
    state_data = {}

example = {
    "status": "BOOTSTRAPPED",
    "mode": state_data.get("mode", "TIER_0_OBSERVE"),
    "last_cycle_at": None,
    "cycles": 0,
    "production_locked": True,
    "production_clients_locked": ["parada_atlantida"],
    "test_client": "hupmix",
    "note": "Este arquivo e template versionavel. O state.json real e runtime local ignorado.",
    "created_at": now()
}

STATE_EXAMPLE.write_text(json.dumps(example, ensure_ascii=False, indent=2), encoding="utf-8")

gitignore = ROOT / ".gitignore"
if gitignore.exists():
    lines = gitignore.read_text(encoding="utf-8-sig").splitlines()
else:
    lines = []

entries = [
    "",
    "# K-OS runtime local",
    "local_runtime/",
    "logs/",
    "memory/security/",
    "memory/sandbox_api_adapter/",
    "memory/kaizen/state.json",
    "reports/security/latest_security_firewall_report.json",
    "reports/security/latest_security_firewall_report.md",
    "reports/KOS_KAIZEN_LAST_CYCLE_REPORT.json",
    "ops/codex/",
    "_local_quarantine/"
]

for e in entries:
    if e and e not in lines:
        lines.append(e)
    elif not e:
        if lines and lines[-1] != "":
            lines.append("")

gitignore.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

untrack_targets = [
    "memory/kaizen/state.json",
    "reports/KOS_KAIZEN_LAST_CYCLE_REPORT.json",
    "reports/security/latest_security_firewall_report.json",
    "reports/security/latest_security_firewall_report.md",
]

untrack_results = []
for target in untrack_targets:
    tracked = run(f'git ls-files --error-unmatch "{target}"')
    if tracked["returncode"] == 0:
        untrack_results.append(run(f'git rm --cached "{target}"'))

report = {
    "status": "RUNTIME_BOUNDARY_PREPARED",
    "phase": "35A",
    "backup_dir": str(Q.relative_to(ROOT)).replace("\\", "/"),
    "backups": backups,
    "runtime_boundary_file": str(BOUNDARY.relative_to(ROOT)).replace("\\", "/"),
    "state_example_file": str(STATE_EXAMPLE.relative_to(ROOT)).replace("\\", "/"),
    "untrack_results": untrack_results,
    "real_action_executed": False,
    "paid_ai_call_executed": False,
    "instagram_publish_executed": False,
    "created_at": now()
}

REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

print(json.dumps({
    "status": report["status"],
    "backup_dir": report["backup_dir"],
    "runtime_boundary_file": report["runtime_boundary_file"],
    "state_example_file": report["state_example_file"]
}, ensure_ascii=False, indent=2))