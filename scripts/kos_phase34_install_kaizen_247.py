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
    "system": "K-OS",
    "module": "Kaizen Executor Orchestrator",
    "mode": "TIER_0_OBSERVE",
    "goal": "evoluir o K-OS continuamente com seguranca, memoria, logs e aprovacao humana para acoes reais",
    "autonomy_tiers": {
        "TIER_0_OBSERVE": {
            "description": "observa, audita, registra e recomenda",
            "can_modify_files": False,
            "can_commit": False,
            "can_publish": False,
            "can_call_paid_ai": False
        },
        "TIER_1_PLAN": {
            "description": "gera planos, patches e checklists sem aplicar automaticamente",
            "can_modify_files": False,
            "can_commit": False,
            "can_publish": False,
            "can_call_paid_ai": False
        },
        "TIER_2_SAFE_EXECUTE": {
            "description": "executa mudancas seguras com firewall e logs",
            "can_modify_files": True,
            "can_commit": True,
            "can_publish": False,
            "can_call_paid_ai": False
        },
        "TIER_3_APPROVED_REAL_ACTIONS": {
            "description": "executa acoes reais somente com confirmacao humana",
            "can_modify_files": True,
            "can_commit": True,
            "can_publish": True,
            "can_call_paid_ai": True
        }
    },
    "hard_rules": {
        "never_publish_without_human_confirmation": True,
        "never_expose_secrets": True,
        "never_use_browser_logged_accounts_as_backend": True,
        "always_log_events": True,
        "always_check_git_status": True,
        "always_run_firewall_before_commit": True,
        "always_keep_production_client_locked_for_tests": True,
        "production_clients_locked": ["parada_atlantida"],
        "test_clients_allowed": ["hupmix"]
    },
    "providers": {
        "default": "local_stub",
        "free_first": ["local_stub", "ollama_local"],
        "paid_guarded": ["openai", "gemini"],
        "paid_enabled": False
    },
    "created_at": now()
}

queue = {
    "status": "READY",
    "created_at": now(),
    "tasks": [
        {
            "id": "KOS-KAIZEN-001",
            "priority": "high",
            "type": "audit",
            "title": "Auditar estado operacional do K-OS",
            "status": "pending",
            "safe_mode": True
        },
        {
            "id": "KOS-KAIZEN-002",
            "priority": "high",
            "type": "architecture",
            "title": "Consolidar mapa de agentes, conectores e modulos ativos",
            "status": "pending",
            "safe_mode": True
        },
        {
            "id": "KOS-KAIZEN-003",
            "priority": "medium",
            "type": "cost_control",
            "title": "Monitorar uso de IA e evitar chamadas pagas sem budget",
            "status": "pending",
            "safe_mode": True
        }
    ]
}

state = {
    "status": "BOOTSTRAPPED",
    "mode": "TIER_0_OBSERVE",
    "last_cycle_at": None,
    "cycles": 0,
    "production_locked": True,
    "production_clients_locked": ["parada_atlantida"],
    "test_client": "hupmix",
    "created_at": now()
}

orchestrator = r'''
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
import os
import subprocess
import time

ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = ROOT / "config" / "kos_autonomy_policy.json"
STATE_PATH = ROOT / "memory" / "kaizen" / "state.json"
QUEUE_PATH = ROOT / "memory" / "kaizen" / "task_queue.json"
EVENTS_PATH = ROOT / "logs" / "kaizen" / "events.jsonl"
REPORT_PATH = ROOT / "reports" / "KOS_KAIZEN_LAST_CYCLE_REPORT.json"

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def read_json(path: Path, default):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8-sig"))
    return default

def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def append_event(event: dict):
    EVENTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    event["created_at"] = now()
    with EVENTS_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

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
            "stdout": (p.stdout or "")[-4000:],
            "stderr": (p.stderr or "")[-4000:],
        }
    except Exception as exc:
        return {
            "cmd": cmd,
            "returncode": -1,
            "stdout": "",
            "stderr": str(exc),
        }

def detect_codex() -> dict:
    return run_cmd("codex --version", timeout=10)

def detect_ollama() -> dict:
    return run_cmd("ollama --version", timeout=10)

def ai_local_plan(prompt: str) -> dict:
    # Primeira camada: sem custo. Usa provider_router_v2 se existir.
    try:
        from k_atlas.ai.provider_router_v2 import AIRequest, run_ai
        resp = run_ai(AIRequest(
            client_id="kos",
            task_id="kaizen_cycle",
            prompt=prompt,
            provider="local_stub",
            model="local_stub",
            estimated_usd=0.0
        ))
        return {
            "ok": resp.ok,
            "provider": resp.provider,
            "content": resp.content,
            "blocked": resp.blocked,
            "reason": resp.reason
        }
    except Exception as exc:
        return {
            "ok": True,
            "provider": "internal_stub",
            "content": "[KOS INTERNAL STUB] Plano local sem custo gerado.",
            "blocked": False,
            "reason": str(exc)
        }

def run_cycle() -> dict:
    policy = read_json(POLICY_PATH, {})
    state = read_json(STATE_PATH, {})
    queue = read_json(QUEUE_PATH, {"tasks": []})

    git_status = run_cmd("git --no-pager status --short", timeout=30)
    git_log = run_cmd("git --no-pager log --oneline -5", timeout=30)
    branch = run_cmd("git branch --show-current", timeout=30)

    codex = detect_codex()
    ollama = detect_ollama()

    pending_tasks = [t for t in queue.get("tasks", []) if t.get("status") == "pending"]

    prompt = (
        "Voce e o Kaizen Executor Orchestrator do K-OS. "
        "Gere um plano operacional curto, seguro e sem custo para o proximo ciclo. "
        "Nao publicar, nao chamar API paga, nao mexer em credenciais."
    )

    plan = ai_local_plan(prompt)

    recommendations = []

    if git_status.get("stdout", "").strip():
        recommendations.append("Workspace possui alteracoes locais. Revisar antes de qualquer execucao.")
    else:
        recommendations.append("Workspace limpo. Proximo passo pode ser planejamento ou execucao segura.")

    if "not recognized" in (codex.get("stderr", "") + codex.get("stdout", "")).lower():
        recommendations.append("Codex CLI nao detectado. Integracao deve ficar opcional.")
    else:
        recommendations.append("Codex CLI parece detectavel ou retornou resposta.")

    if "not recognized" in (ollama.get("stderr", "") + ollama.get("stdout", "")).lower():
        recommendations.append("Ollama nao detectado. Motor local gratuito ainda precisa instalacao.")
    else:
        recommendations.append("Ollama parece detectavel ou retornou resposta.")

    recommendations.append("Manter Parada Atlantida bloqueada para testes.")
    recommendations.append("Usar @hupmix somente para publicacoes de homologacao.")

    state["status"] = "RUNNING"
    state["last_cycle_at"] = now()
    state["cycles"] = int(state.get("cycles") or 0) + 1
    write_json(STATE_PATH, state)

    report = {
        "status": "KOS_KAIZEN_CYCLE_COMPLETED",
        "mode": policy.get("mode", "TIER_0_OBSERVE"),
        "cycle": state["cycles"],
        "branch": branch.get("stdout", "").strip(),
        "git_status": git_status,
        "last_commits": git_log.get("stdout", ""),
        "pending_tasks": pending_tasks,
        "codex_detection": codex,
        "ollama_detection": ollama,
        "ai_plan": plan,
        "recommendations": recommendations,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "created_at": now()
    }

    write_json(REPORT_PATH, report)
    append_event({
        "event": "kaizen_cycle_completed",
        "cycle": state["cycles"],
        "mode": report["mode"],
        "recommendations": recommendations
    })

    return report

def main():
    daemon = os.getenv("KOS_KAIZEN_DAEMON", "false").lower() == "true"
    interval = int(os.getenv("KOS_KAIZEN_INTERVAL_SECONDS", "900"))
    max_cycles = int(os.getenv("KOS_KAIZEN_MAX_CYCLES", "1"))

    cycles = 0
    while True:
        report = run_cycle()
        print(json.dumps({
            "status": report["status"],
            "cycle": report["cycle"],
            "mode": report["mode"],
            "real_action_executed": False,
            "paid_ai_call_executed": False,
            "instagram_publish_executed": False,
            "report": str(REPORT_PATH)
        }, ensure_ascii=False, indent=2))

        cycles += 1

        if not daemon:
            break

        if max_cycles > 0 and cycles >= max_cycles:
            break

        time.sleep(interval)

if __name__ == "__main__":
    main()
'''

runner = r'''
from k_atlas.kaizen.orchestrator import main

if __name__ == "__main__":
    main()
'''

start_ps1 = r'''
$ErrorActionPreference="Stop"
Set-Location "C:\Users\oi\Desktop\motor-digital"
$env:KOS_KAIZEN_DAEMON="true"
$env:KOS_KAIZEN_INTERVAL_SECONDS="900"
$env:KOS_KAIZEN_MAX_CYCLES="0"
python -m k_atlas.kaizen.orchestrator
'''

page = r'''
import json
from pathlib import Path
import streamlit as st

ROOT = Path.cwd()
STATE = ROOT / "memory" / "kaizen" / "state.json"
REPORT = ROOT / "reports" / "KOS_KAIZEN_LAST_CYCLE_REPORT.json"
QUEUE = ROOT / "memory" / "kaizen" / "task_queue.json"

st.set_page_config(page_title="KOS Kaizen 24/7", layout="wide")
st.title("KOS Kaizen 24/7 Orchestrator")
st.caption("Modo seguro: observa, planeja e registra. Nao publica e nao chama API paga.")

def load(path):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8-sig"))
    return {}

col1, col2, col3 = st.columns(3)

state = load(STATE)
report = load(REPORT)
queue = load(QUEUE)

col1.metric("Status", state.get("status", "N/A"))
col2.metric("Modo", state.get("mode", "N/A"))
col3.metric("Ciclos", state.get("cycles", 0))

st.subheader("Ultimo ciclo")
st.json(report)

st.subheader("Fila")
st.json(queue)
'''

write(ROOT / "k_atlas" / "kaizen" / "__init__.py", "")
write(ROOT / "k_atlas" / "kaizen" / "orchestrator.py", orchestrator.strip() + "\n")
write(ROOT / "scripts" / "run_kaizen_once.py", runner.strip() + "\n")
write(ROOT / "scripts" / "start_kaizen_247.ps1", start_ps1.strip() + "\n")
write(ROOT / "pages" / "KOS_Kaizen_247.py", page.strip() + "\n")

save_json(ROOT / "config" / "kos_autonomy_policy.json", policy)
save_json(ROOT / "memory" / "kaizen" / "task_queue.json", queue)
save_json(ROOT / "memory" / "kaizen" / "state.json", state)

report = {
    "status": "KOS_KAIZEN_247_BOOTSTRAPPED",
    "mode": "TIER_0_OBSERVE",
    "created_files": [
        "k_atlas/kaizen/orchestrator.py",
        "config/kos_autonomy_policy.json",
        "memory/kaizen/state.json",
        "memory/kaizen/task_queue.json",
        "scripts/start_kaizen_247.ps1",
        "scripts/run_kaizen_once.py",
        "pages/KOS_Kaizen_247.py"
    ],
    "real_action_executed": False,
    "paid_ai_call_executed": False,
    "instagram_publish_executed": False,
    "created_at": now()
}

save_json(ROOT / "reports" / "KOS_PHASE34_KAIZEN_247_BOOTSTRAP.json", report)
print(json.dumps(report, ensure_ascii=False, indent=2))