from pathlib import Path
import json
from datetime import datetime, timezone

ROOT = Path.cwd()

def now():
    return datetime.now(timezone.utc).isoformat()

def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

policy = {
    "status": "ACTIVE",
    "phase": "38",
    "module": "K-OS Safe Executor Sandbox",
    "mode": "SANDBOX_ONLY",
    "goal": "executar apenas acoes seguras, auditaveis e reversiveis em ambiente local",
    "allowed_actions": {
        "git_status": True,
        "git_branch": True,
        "pytest_phase37": True,
        "pytest_workspace": True,
        "planner_bridge_dry_run": True
    },
    "blocked_actions": {
        "instagram_publish": True,
        "paid_ai_call": True,
        "secret_read": True,
        "codex_auto_execute": True,
        "arbitrary_shell": True,
        "production_publish": True,
        "delete_files": True
    },
    "hard_rules": {
        "sandbox_only": True,
        "no_paid_ai": True,
        "no_external_publish": True,
        "no_secret_exposure": True,
        "no_arbitrary_shell": True,
        "human_approval_required_for_real_actions": True,
        "parada_atlantida_locked": True,
        "hupmix_test_only": True
    },
    "created_at": now()
}

safe_executor_code = r'''
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
import subprocess
import sys
from typing import Iterable

ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = ROOT / "config" / "kos_safe_executor_policy.json"
LOG_DIR = ROOT / "logs" / "kaizen" / "safe_executor"

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

SAFE_ACTIONS = {
    "git_status": {
        "description": "Ler status Git sem alterar arquivos.",
        "cmd": ["git", "--no-pager", "status", "--short"],
        "timeout": 30,
    },
    "git_branch": {
        "description": "Ler branch atual.",
        "cmd": ["git", "branch", "--show-current"],
        "timeout": 30,
    },
    "pytest_phase37": {
        "description": "Rodar testes da Mission Queue.",
        "cmd": [sys.executable, "-m", "pytest", "tests/test_phase37_mission_queue.py", "-q"],
        "timeout": 120,
    },
    "pytest_workspace": {
        "description": "Rodar testes focados de workspace/gates.",
        "cmd": [
            sys.executable,
            "-m",
            "pytest",
            "tests/test_instagram_level4_adapter.py",
            "tests/test_kos_base_workspace.py",
            "-q",
        ],
        "timeout": 180,
    },
    "planner_bridge_dry_run": {
        "description": "Rodar Planner Bridge em modo dry-run local.",
        "cmd": [sys.executable, "scripts/run_phase36_planner_bridge.py"],
        "timeout": 180,
    },
}

BLOCKED_KEYWORDS = [
    "publish",
    "instagram_publish",
    "openai",
    "gemini",
    "token",
    "secret",
    "password",
    "remove-item",
    "del ",
    "rm ",
    "codex exec",
]

def _read_json(path: Path, default):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8-sig"))
    return default

def _save_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def is_allowed_action(action_name: str) -> bool:
    return action_name in SAFE_ACTIONS

def list_safe_actions() -> dict:
    return {
        name: {
            "description": data["description"],
            "cmd": data["cmd"],
            "timeout": data["timeout"],
        }
        for name, data in SAFE_ACTIONS.items()
    }

def _command_has_blocked_keyword(cmd: list[str]) -> bool:
    text = " ".join(cmd).lower()
    return any(keyword in text for keyword in BLOCKED_KEYWORDS)

def run_action(action_name: str, dry_run: bool = False) -> dict:
    if not is_allowed_action(action_name):
        return {
            "ok": False,
            "status": "ACTION_BLOCKED",
            "action": action_name,
            "reason": "acao nao esta na allowlist",
            "real_action_executed": False,
            "paid_ai_call_executed": False,
            "instagram_publish_executed": False,
        }

    action = SAFE_ACTIONS[action_name]
    cmd = action["cmd"]

    if _command_has_blocked_keyword(cmd):
        return {
            "ok": False,
            "status": "ACTION_BLOCKED",
            "action": action_name,
            "reason": "comando contem termo bloqueado",
            "cmd": cmd,
            "real_action_executed": False,
            "paid_ai_call_executed": False,
            "instagram_publish_executed": False,
        }

    if dry_run:
        return {
            "ok": True,
            "status": "DRY_RUN_ACTION_APPROVED",
            "action": action_name,
            "cmd": cmd,
            "executed": False,
            "real_action_executed": False,
            "paid_ai_call_executed": False,
            "instagram_publish_executed": False,
        }

    try:
        proc = subprocess.run(
            cmd,
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=action["timeout"],
        )

        return {
            "ok": proc.returncode == 0,
            "status": "SAFE_ACTION_COMPLETED" if proc.returncode == 0 else "SAFE_ACTION_FAILED",
            "action": action_name,
            "cmd": cmd,
            "returncode": proc.returncode,
            "stdout": (proc.stdout or "")[-6000:],
            "stderr": (proc.stderr or "")[-6000:],
            "safe_action_executed": True,
            "real_action_executed": False,
            "paid_ai_call_executed": False,
            "instagram_publish_executed": False,
        }

    except Exception as exc:
        return {
            "ok": False,
            "status": "SAFE_ACTION_ERROR",
            "action": action_name,
            "cmd": cmd,
            "error": str(exc),
            "safe_action_executed": False,
            "real_action_executed": False,
            "paid_ai_call_executed": False,
            "instagram_publish_executed": False,
        }

def run_safe_bundle(bundle_id: str, actions: Iterable[str], dry_run: bool = False) -> dict:
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    results = []
    for action_name in actions:
        results.append(run_action(action_name, dry_run=dry_run))

    report = {
        "status": "SAFE_EXECUTOR_BUNDLE_COMPLETED",
        "bundle_id": bundle_id,
        "mode": "DRY_RUN" if dry_run else "SANDBOX_ONLY",
        "actions": list(actions),
        "results": results,
        "ok": all(item.get("ok") for item in results),
        "safe_actions_executed": len([item for item in results if item.get("safe_action_executed") is True]),
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "created_at": now(),
    }

    path = LOG_DIR / f"{bundle_id}.json"
    _save_json(path, report)

    return report

def run_phase38_smoke() -> dict:
    return run_safe_bundle(
        bundle_id="phase38_smoke",
        actions=[
            "git_branch",
            "git_status",
            "pytest_phase37",
        ],
        dry_run=False,
    )

if __name__ == "__main__":
    print(json.dumps(run_phase38_smoke(), ensure_ascii=False, indent=2))
'''

runner_code = r'''
from k_atlas.kaizen.safe_executor import run_phase38_smoke, list_safe_actions
import json

if __name__ == "__main__":
    result = run_phase38_smoke()
    print(json.dumps({
        "status": "PHASE38_SAFE_EXECUTOR_DEMO_COMPLETED",
        "allowed_actions": list_safe_actions(),
        "result": result,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False
    }, ensure_ascii=False, indent=2))
'''

page_code = r'''
import streamlit as st
from k_atlas.kaizen.safe_executor import list_safe_actions, run_safe_bundle

st.set_page_config(page_title="KOS Safe Executor", layout="wide")

st.title("KOS Safe Executor Sandbox")
st.caption("Executa apenas acoes allowlist locais. Nao publica, nao usa IA paga, nao executa Codex automaticamente.")

actions = list_safe_actions()

st.subheader("Acoes permitidas")
st.json(actions)

selected = st.multiselect(
    "Selecionar acoes seguras",
    list(actions.keys()),
    default=["git_branch", "git_status"]
)

dry_run = st.checkbox("Dry-run apenas", value=True)

if st.button("Executar bundle seguro", use_container_width=True):
    result = run_safe_bundle("streamlit_safe_bundle", selected, dry_run=dry_run)
    st.json(result)

st.warning("Acoes reais continuam bloqueadas. Publicacao externa exige fase propria e confirmacao humana.")
'''

test_code = r'''
from k_atlas.kaizen.safe_executor import is_allowed_action, run_action, list_safe_actions

def test_allowlist_contains_expected_actions():
    actions = list_safe_actions()
    assert "git_status" in actions
    assert "git_branch" in actions
    assert "pytest_phase37" in actions

def test_unknown_action_is_blocked():
    result = run_action("instagram_publish")
    assert result["ok"] is False
    assert result["status"] == "ACTION_BLOCKED"
    assert result["real_action_executed"] is False

def test_dry_run_does_not_execute():
    result = run_action("git_status", dry_run=True)
    assert result["ok"] is True
    assert result["status"] == "DRY_RUN_ACTION_APPROVED"
    assert result["executed"] is False
    assert result["real_action_executed"] is False
'''

save_json(ROOT / "config" / "kos_safe_executor_policy.json", policy)
write(ROOT / "k_atlas" / "kaizen" / "safe_executor.py", safe_executor_code.strip() + "\n")
write(ROOT / "scripts" / "run_phase38_safe_executor_demo.py", runner_code.strip() + "\n")
write(ROOT / "pages" / "KOS_Safe_Executor.py", page_code.strip() + "\n")
write(ROOT / "tests" / "test_phase38_safe_executor.py", test_code.strip() + "\n")

report = {
    "status": "PHASE38_SAFE_EXECUTOR_BOOTSTRAPPED",
    "phase": "38",
    "created_files": [
        "config/kos_safe_executor_policy.json",
        "k_atlas/kaizen/safe_executor.py",
        "scripts/run_phase38_safe_executor_demo.py",
        "pages/KOS_Safe_Executor.py",
        "tests/test_phase38_safe_executor.py"
    ],
    "runtime_files": [
        "logs/kaizen/safe_executor/phase38_smoke.json"
    ],
    "real_action_executed": False,
    "paid_ai_call_executed": False,
    "instagram_publish_executed": False,
    "created_at": now()
}

save_json(ROOT / "reports" / "KOS_PHASE38_SAFE_EXECUTOR_BOOTSTRAP.json", report)

print(json.dumps(report, ensure_ascii=False, indent=2))