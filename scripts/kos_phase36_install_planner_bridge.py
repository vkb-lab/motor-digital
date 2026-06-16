from pathlib import Path
import json
from datetime import datetime, timezone
import subprocess
import shutil
import urllib.request
import urllib.error

ROOT = Path.cwd()

POLICY = ROOT / "config" / "kos_planner_bridge_policy.json"
BRIDGE = ROOT / "k_atlas" / "kaizen" / "planner_bridge.py"
RUNNER = ROOT / "scripts" / "run_phase36_planner_bridge.py"
REPORT = ROOT / "reports" / "KOS_PHASE36_PLANNER_BRIDGE_BOOTSTRAP.json"
LOG_DIR = ROOT / "logs" / "kaizen" / "planner_bridge"

def now():
    return datetime.now(timezone.utc).isoformat()

def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def cmd_version(cmd):
    exe = shutil.which(cmd)
    if not exe:
        return {
            "installed": False,
            "path": "",
            "version": ""
        }
    try:
        p = subprocess.run([cmd, "--version"], cwd=ROOT, capture_output=True, text=True, timeout=15)
        return {
            "installed": True,
            "path": exe,
            "version": ((p.stdout or "") + (p.stderr or "")).strip()
        }
    except Exception as exc:
        return {
            "installed": True,
            "path": exe,
            "version": f"version_error: {exc}"
        }

policy = {
    "status": "ACTIVE",
    "phase": "36",
    "module": "Codex/Ollama Planner Bridge",
    "mode": "DRY_RUN_ONLY",
    "goal": "transformar missoes em planos tecnicos auditaveis usando motor local gratuito e preparar tarefas para Codex sem executar automaticamente",
    "allowed_actions": {
        "read_project_state": True,
        "generate_plan": True,
        "write_local_runtime_logs": True,
        "write_codex_task_draft": True,
        "execute_codex": False,
        "modify_source_files": False,
        "commit": False,
        "push": False,
        "publish_instagram": False,
        "call_paid_ai": False
    },
    "providers": {
        "default": "ollama_or_local_stub",
        "ollama_enabled": True,
        "local_stub_enabled": True,
        "openai_enabled": False,
        "gemini_enabled": False
    },
    "hard_rules": {
        "no_paid_ai": True,
        "no_external_publish": True,
        "no_secret_exposure": True,
        "no_browser_logged_backend": True,
        "human_approval_required_for_execution": True,
        "codex_must_be_manual_until_next_tier": True,
        "parada_atlantida_locked": True,
        "hupmix_test_only": True
    },
    "created_at": now()
}

bridge_code = r'''
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
import shutil
import subprocess
import urllib.request
import urllib.error

ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = ROOT / "config" / "kos_planner_bridge_policy.json"
LOG_DIR = ROOT / "logs" / "kaizen" / "planner_bridge"

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def read_json(path: Path, default):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8-sig"))
    return default

def save_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def run_cmd(cmd: str, timeout: int = 30) -> dict:
    try:
        p = subprocess.run(
            cmd,
            cwd=ROOT,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "cmd": cmd,
            "returncode": p.returncode,
            "stdout": (p.stdout or "")[-5000:],
            "stderr": (p.stderr or "")[-5000:],
        }
    except Exception as exc:
        return {
            "cmd": cmd,
            "returncode": -1,
            "stdout": "",
            "stderr": str(exc),
        }

def detect_tool(cmd: str) -> dict:
    path = shutil.which(cmd)
    if not path:
        return {
            "installed": False,
            "path": "",
            "version": ""
        }

    version = run_cmd(f"{cmd} --version", timeout=15)
    return {
        "installed": True,
        "path": path,
        "version": ((version.get("stdout") or "") + (version.get("stderr") or "")).strip()
    }

def try_ollama(prompt: str, model: str = "llama3.2") -> dict:
    payload = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": False
    }).encode("utf-8")

    req = urllib.request.Request(
        "http://localhost:11434/api/generate",
        data=payload,
        method="POST",
        headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as res:
            data = json.loads(res.read().decode("utf-8", errors="replace"))
        return {
            "ok": True,
            "provider": "ollama_local",
            "model": model,
            "content": data.get("response", "")
        }
    except Exception as exc:
        return {
            "ok": False,
            "provider": "ollama_local",
            "model": model,
            "content": "",
            "error": str(exc)
        }

def local_stub_plan(mission: str) -> str:
    return f"""# K-OS Plano Seguro Gerado Localmente

## Missao
{mission}

## Modo
DRY_RUN_ONLY

## Plano
1. Ler estado atual do Git.
2. Confirmar que nao ha publicacao externa.
3. Confirmar que nao ha chamada de IA paga.
4. Gerar proposta tecnica.
5. Criar tarefa Codex em rascunho local.
6. Aguardar aprovacao humana antes de qualquer execucao.

## Regras
- Nao publicar Instagram.
- Nao alterar codigo automaticamente.
- Nao commitar sem firewall.
- Nao usar Gemini/OpenAI sem budget.
- Manter Parada Atlantida bloqueada.
- Usar Hupmix apenas como ambiente de teste.
"""

def build_codex_task(mission_id: str, mission: str, plan: str) -> dict:
    return {
        "task_id": mission_id,
        "status": "DRAFT_ONLY",
        "executor": "codex_cli_manual",
        "mission": mission,
        "plan": plan,
        "execution_allowed": False,
        "requires_human_approval": True,
        "constraints": {
            "no_paid_ai": True,
            "no_instagram_publish": True,
            "no_secret_exposure": True,
            "no_auto_commit": True,
            "run_tests_before_commit": True,
            "run_firewall_before_commit": True
        },
        "created_at": now()
    }

def run_planner_bridge(mission: str, mission_id: str = "KOS-MISSION-DRYRUN-001") -> dict:
    policy = read_json(POLICY_PATH, {})
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    git_status = run_cmd("git --no-pager status --short", timeout=30)
    branch = run_cmd("git branch --show-current", timeout=30)
    codex = detect_tool("codex")
    ollama = detect_tool("ollama")

    prompt = (
        "Voce e o K-OS Kaizen Planner. "
        "Gere um plano tecnico curto, seguro e auditavel. "
        "Nao executar nada. Nao publicar. Nao usar API paga. "
        f"Missao: {mission}"
    )

    ai_plan = None

    if ollama.get("installed"):
        ai_plan = try_ollama(prompt)

    if not ai_plan or not ai_plan.get("ok"):
        ai_plan = {
            "ok": True,
            "provider": "local_stub",
            "model": "local_stub",
            "content": local_stub_plan(mission),
            "fallback_reason": ai_plan.get("error") if ai_plan else "ollama_not_attempted"
        }

    codex_task = build_codex_task(
        mission_id=mission_id,
        mission=mission,
        plan=ai_plan.get("content", "")
    )

    safe_id = mission_id.replace("/", "_").replace("\\", "_")
    task_path = LOG_DIR / f"{safe_id}_codex_task_draft.json"
    plan_path = LOG_DIR / f"{safe_id}_plan.md"
    report_path = LOG_DIR / f"{safe_id}_planner_report.json"

    save_json(task_path, codex_task)
    plan_path.write_text(ai_plan.get("content", ""), encoding="utf-8")

    report = {
        "status": "PLANNER_BRIDGE_DRY_RUN_COMPLETED",
        "mission_id": mission_id,
        "mission": mission,
        "mode": policy.get("mode", "DRY_RUN_ONLY"),
        "branch": branch.get("stdout", "").strip(),
        "git_status": git_status.get("stdout", ""),
        "codex_detection": codex,
        "ollama_detection": ollama,
        "ai_plan_provider": ai_plan.get("provider"),
        "ai_plan_ok": ai_plan.get("ok"),
        "codex_task_draft": str(task_path.relative_to(ROOT)).replace("\\", "/"),
        "plan_file": str(plan_path.relative_to(ROOT)).replace("\\", "/"),
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "created_at": now()
    }

    save_json(report_path, report)
    return report

if __name__ == "__main__":
    result = run_planner_bridge(
        mission="Auditar e planejar proximo incremento seguro do K-OS sem executar alteracoes.",
        mission_id="KOS-PHASE36-SMOKE"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
'''

runner_code = r'''
from k_atlas.kaizen.planner_bridge import run_planner_bridge
import json

if __name__ == "__main__":
    result = run_planner_bridge(
        mission="Consolidar autonomia segura do K-OS com Codex/Ollama em modo dry-run.",
        mission_id="KOS-PHASE36-DEFAULT"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
'''

save_json(POLICY, policy)
write(BRIDGE, bridge_code.strip() + "\n")
write(RUNNER, runner_code.strip() + "\n")

codex = cmd_version("codex")
ollama = cmd_version("ollama")

report = {
    "status": "PHASE36_PLANNER_BRIDGE_INSTALLED",
    "phase": "36",
    "codex_detected": codex,
    "ollama_detected": ollama,
    "created_files": [
        "config/kos_planner_bridge_policy.json",
        "k_atlas/kaizen/planner_bridge.py",
        "scripts/run_phase36_planner_bridge.py"
    ],
    "real_action_executed": False,
    "paid_ai_call_executed": False,
    "instagram_publish_executed": False,
    "created_at": now()
}

save_json(REPORT, report)

print(json.dumps(report, ensure_ascii=False, indent=2))