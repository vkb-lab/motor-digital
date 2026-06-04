from pathlib import Path
import json
import os
import re
import shutil
import subprocess
from datetime import datetime, timezone

ROOT = Path.cwd()

REPORT = ROOT / "reports" / "KOS_PHASE29_AI_TRACE_FREE_TOOLS_RESULT.json"
CATALOG = ROOT / "config" / "free_ai_tools_catalog.json"
BUDGET = ROOT / "config" / "ai_budget_policy.json"
RUNTIME = ROOT / "local_runtime" / "ai_runtime.env"
LEDGER = ROOT / "logs" / "ai_cost" / "ledger.jsonl"

AI_DIR = ROOT / "k_atlas" / "ai"
REGISTRY = AI_DIR / "free_tools_registry.py"
COST_GUARD = AI_DIR / "cost_guard.py"
ROUTER = AI_DIR / "provider_router_v2.py"
INIT = AI_DIR / "__init__.py"

SCAN_EXTS = {
    ".py", ".md", ".txt", ".json", ".yaml", ".yml", ".toml",
    ".ps1", ".bat", ".sh", ".html", ".js", ".ts", ".env"
}

EXCLUDE_DIRS = {
    ".git", ".venv", "venv", "node_modules", "__pycache__",
    ".pytest_cache", ".mypy_cache", "local_runtime", "logs"
}

PROVIDER_PATTERNS = {
    "gemini": [
        "gemini", "google.generativeai", "google-genai", "genai",
        "GEMINI_API_KEY", "GOOGLE_API_KEY", "models/gemini"
    ],
    "openai": [
        "openai", "OPENAI_API_KEY", "chat.completions",
        "responses.create", "gpt-", "GPT_MODEL"
    ],
    "anthropic": [
        "anthropic", "ANTHROPIC_API_KEY", "claude"
    ],
    "ollama": [
        "ollama", "OLLAMA_HOST", "localhost:11434"
    ],
    "cost_risk": [
        "generate_content", "stream_generate_content", "media.generate",
        "grounding", "google_search", "web_search", "image_generation",
        "video", "veo", "batch"
    ],
    "secret_like": [
        "API_KEY", "ACCESS_TOKEN", "SECRET", "TOKEN"
    ]
}

def now():
    return datetime.now(timezone.utc).isoformat()

def rel(path):
    return str(path.relative_to(ROOT)).replace("\\", "/")

def should_scan(path):
    if path.is_dir():
        return False
    if any(part in EXCLUDE_DIRS for part in path.parts):
        return False
    if path.suffix.lower() in SCAN_EXTS:
        return True
    if path.name.lower().endswith(".env"):
        return True
    return False

def safe_read(path):
    try:
        return path.read_text(encoding="utf-8-sig", errors="replace")
    except Exception:
        return ""

def mask_line(line):
    line = re.sub(r"([A-Z0-9_]*(?:API_KEY|TOKEN|SECRET|ACCESS_KEY)[A-Z0-9_]*\s*=\s*)[^ \n\r]+", r"\1***MASKED***", line)
    return line.strip()[:500]

def cmd_version(cmd):
    exe = shutil.which(cmd)
    if not exe:
        return {"installed": False, "path": ""}
    try:
        p = subprocess.run([cmd, "--version"], capture_output=True, text=True, timeout=8)
        return {
            "installed": True,
            "path": exe,
            "version_output": ((p.stdout or "") + (p.stderr or "")).strip()[:400]
        }
    except Exception as exc:
        return {"installed": True, "path": exe, "version_output": str(exc)}

summary = {
    "files_scanned": 0,
    "gemini_files": 0,
    "openai_files": 0,
    "anthropic_files": 0,
    "ollama_files": 0,
    "cost_risk_files": 0,
    "secret_like_files": 0
}

findings = []

for path in ROOT.rglob("*"):
    if not should_scan(path):
        continue

    summary["files_scanned"] += 1
    text = safe_read(path)
    if not text:
        continue

    lower = text.lower()
    item = {
        "file": rel(path),
        "hits": {
            "gemini": [],
            "openai": [],
            "anthropic": [],
            "ollama": [],
            "cost_risk": [],
            "secret_like": []
        }
    }

    lines = text.splitlines()
    for group, terms in PROVIDER_PATTERNS.items():
        for term in terms:
            term_l = term.lower()
            if term_l in lower:
                for idx, line in enumerate(lines, start=1):
                    if term_l in line.lower():
                        item["hits"][group].append({
                            "line": idx,
                            "term": term,
                            "snippet": mask_line(line)
                        })

    if any(item["hits"][k] for k in item["hits"]):
        findings.append(item)
        if item["hits"]["gemini"]:
            summary["gemini_files"] += 1
        if item["hits"]["openai"]:
            summary["openai_files"] += 1
        if item["hits"]["anthropic"]:
            summary["anthropic_files"] += 1
        if item["hits"]["ollama"]:
            summary["ollama_files"] += 1
        if item["hits"]["cost_risk"]:
            summary["cost_risk_files"] += 1
        if item["hits"]["secret_like"]:
            summary["secret_like_files"] += 1

local_tools = {
    "python": cmd_version("python"),
    "git": cmd_version("git"),
    "node": cmd_version("node"),
    "npm": cmd_version("npm"),
    "ollama": cmd_version("ollama"),
    "docker": cmd_version("docker")
}

catalog = {
    "status": "ACTIVE",
    "default_order": [
        "local_stub",
        "ollama_local",
        "gemini_free_guarded",
        "cloudflare_workers_ai_guarded",
        "openai_paid_guarded"
    ],
    "tools": {
        "local_stub": {
            "type": "internal",
            "cost": "zero",
            "enabled_by_default": True,
            "use_for": [
                "testes de fluxo",
                "orquestracao",
                "mock de agentes",
                "validacao de prompts sem custo"
            ],
            "risk": "low"
        },
        "ollama_local": {
            "type": "local_model_runtime",
            "cost": "sem custo de API; usa hardware local",
            "enabled_by_default": bool(local_tools["ollama"]["installed"]),
            "detected": local_tools["ollama"],
            "use_for": [
                "rascunhos",
                "classificacao simples",
                "sumarios internos",
                "agentes locais",
                "memoria operacional"
            ],
            "risk": "medium_quality_variation"
        },
        "gemini_free_guarded": {
            "type": "external_api",
            "cost": "free tier possivel, mas pago se exceder regras/tier",
            "enabled_by_default": False,
            "requires": [
                "GEMINI_API_KEY",
                "KOS_AI_GEMINI_ENABLED=true",
                "budget policy ativa"
            ],
            "use_for": [
                "tarefas com free tier controlado",
                "testes pequenos"
            ],
            "risk": "unexpected_cost_if_uncontrolled"
        },
        "cloudflare_workers_ai_guarded": {
            "type": "external_serverless_ai",
            "cost": "free allocation e depois pago por uso",
            "enabled_by_default": False,
            "requires": [
                "CLOUDFLARE_ACCOUNT_ID",
                "CLOUDFLARE_API_TOKEN",
                "budget policy ativa"
            ],
            "use_for": [
                "futuro SaaS",
                "modelos abertos serverless",
                "ambiente comercial com custo rastreavel"
            ],
            "risk": "usage_based_cost"
        },
        "openai_paid_guarded": {
            "type": "external_api",
            "cost": "pago por token",
            "enabled_by_default": False,
            "requires": [
                "OPENAI_API_KEY",
                "KOS_AI_OPENAI_ENABLED=true",
                "budget policy ativa"
            ],
            "use_for": [
                "tarefas premium",
                "alta qualidade",
                "clientes pagantes"
            ],
            "risk": "paid_api_cost"
        },
        "browser_logged_accounts": {
            "type": "browser_session",
            "cost": "nao permitido como backend",
            "enabled_by_default": False,
            "allowed_as_backend": False,
            "reason": "fragil, nao escalavel, risco operacional e de compliance"
        }
    },
    "created_at": now()
}

budget = {
    "status": "ACTIVE",
    "mode": "DEV_SAFE",
    "currency": "USD",
    "default_provider": "local_stub",
    "daily_budget_usd": 1.00,
    "monthly_budget_usd": 5.00,
    "per_request_max_usd": 0.05,
    "hard_blocks": {
        "gemini": True,
        "openai": True,
        "anthropic": True,
        "browser_logged_accounts": True
    },
    "allow": {
        "local_stub": True,
        "ollama_local": bool(local_tools["ollama"]["installed"]),
        "gemini_free_guarded": False,
        "cloudflare_workers_ai_guarded": False,
        "openai_paid_guarded": False
    },
    "rules": {
        "require_client_id": True,
        "require_task_id": True,
        "require_cost_estimate": True,
        "require_ledger_log": True,
        "require_human_approval_for_paid_provider": True,
        "disable_ai_calls_when_budget_unknown": True
    },
    "created_at": now()
}

runtime = [
    "# K-OS AI runtime - nao versionar",
    "KOS_AI_MODE=DEV_SAFE",
    "KOS_AI_DEFAULT_PROVIDER=local_stub",
    "KOS_AI_LOCAL_STUB_ENABLED=true",
    f"KOS_AI_OLLAMA_ENABLED={'true' if local_tools['ollama']['installed'] else 'false'}",
    "KOS_AI_GEMINI_ENABLED=false",
    "KOS_AI_OPENAI_ENABLED=false",
    "KOS_AI_CLOUDFLARE_WORKERS_AI_ENABLED=false",
    "KOS_AI_BROWSER_LOGIN_BACKEND_ALLOWED=false",
    "KOS_AI_DAILY_BUDGET_USD=1.00",
    "KOS_AI_MONTHLY_BUDGET_USD=5.00",
    "KOS_AI_PER_REQUEST_MAX_USD=0.05",
    "KOS_AI_REQUIRE_LEDGER=true"
]

cost_guard_code = r'''
from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
import json
import os
import uuid

ROOT = Path(__file__).resolve().parents[2]
BUDGET_PATH = ROOT / "config" / "ai_budget_policy.json"
LEDGER_PATH = ROOT / "logs" / "ai_cost" / "ledger.jsonl"

@dataclass
class CostDecision:
    allowed: bool
    blocked: bool
    reason: str
    provider: str
    estimated_usd: float
    request_id: str

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

def load_budget() -> dict:
    if BUDGET_PATH.exists():
        return json.loads(BUDGET_PATH.read_text(encoding="utf-8-sig"))
    return {
        "mode": "DEV_SAFE",
        "default_provider": "local_stub",
        "per_request_max_usd": 0.05,
        "hard_blocks": {
            "gemini": True,
            "openai": True,
            "anthropic": True,
            "browser_logged_accounts": True
        },
        "allow": {
            "local_stub": True
        },
        "rules": {
            "require_client_id": True,
            "require_task_id": True,
            "require_cost_estimate": True,
            "require_ledger_log": True
        }
    }

def log_ledger(event: dict) -> None:
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

def check_cost_gate(
    provider: str,
    client_id: str,
    task_id: str,
    estimated_usd: float = 0.0,
    model: str = ""
) -> CostDecision:
    budget = load_budget()
    request_id = str(uuid.uuid4())

    provider_key = (provider or budget.get("default_provider") or "local_stub").strip()
    hard_blocks = budget.get("hard_blocks", {})
    allow = budget.get("allow", {})
    rules = budget.get("rules", {})

    allowed = True
    reason = "allowed"

    if rules.get("require_client_id", True) and not client_id:
        allowed = False
        reason = "client_id obrigatorio"

    if rules.get("require_task_id", True) and not task_id:
        allowed = False
        reason = "task_id obrigatorio"

    if hard_blocks.get(provider_key, False):
        allowed = False
        reason = f"provider bloqueado por politica: {provider_key}"

    if not allow.get(provider_key, False):
        allowed = False
        reason = f"provider nao habilitado: {provider_key}"

    per_request_max = float(budget.get("per_request_max_usd", 0.05))
    if float(estimated_usd or 0.0) > per_request_max:
        allowed = False
        reason = f"estimativa acima do limite por requisicao: {estimated_usd} > {per_request_max}"

    decision = CostDecision(
        allowed=allowed,
        blocked=not allowed,
        reason=reason,
        provider=provider_key,
        estimated_usd=float(estimated_usd or 0.0),
        request_id=request_id
    )

    log_ledger({
        "request_id": request_id,
        "created_at": _now(),
        "event": "cost_gate_check",
        "provider": provider_key,
        "model": model,
        "client_id": client_id,
        "task_id": task_id,
        "estimated_usd": float(estimated_usd or 0.0),
        "decision": asdict(decision)
    })

    return decision
'''

registry_code = r'''
from __future__ import annotations

from pathlib import Path
import json
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = ROOT / "config" / "free_ai_tools_catalog.json"

def _cmd_version(cmd: str) -> dict:
    exe = shutil.which(cmd)
    if not exe:
        return {"installed": False, "path": ""}
    try:
        p = subprocess.run([cmd, "--version"], capture_output=True, text=True, timeout=8)
        return {
            "installed": True,
            "path": exe,
            "version_output": ((p.stdout or "") + (p.stderr or "")).strip()[:400]
        }
    except Exception as exc:
        return {"installed": True, "path": exe, "version_output": str(exc)}

def load_catalog() -> dict:
    if CATALOG_PATH.exists():
        return json.loads(CATALOG_PATH.read_text(encoding="utf-8-sig"))
    return {"tools": {}}

def detect_free_tools() -> dict:
    return {
        "ollama": _cmd_version("ollama"),
        "python": _cmd_version("python"),
        "git": _cmd_version("git"),
        "node": _cmd_version("node"),
        "npm": _cmd_version("npm"),
        "docker": _cmd_version("docker")
    }

if __name__ == "__main__":
    print(json.dumps({
        "catalog": load_catalog(),
        "detected": detect_free_tools()
    }, ensure_ascii=False, indent=2))
'''

router_code = r'''
from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import json
import subprocess
import urllib.request
import urllib.error

from .cost_guard import check_cost_gate

ROOT = Path(__file__).resolve().parents[2]

@dataclass
class AIRequest:
    client_id: str
    task_id: str
    prompt: str
    provider: str = "local_stub"
    model: str = "local_stub"
    estimated_usd: float = 0.0

@dataclass
class AIResponse:
    ok: bool
    provider: str
    model: str
    content: str
    blocked: bool
    reason: str
    request_id: str

def run_ai(req: AIRequest) -> AIResponse:
    decision = check_cost_gate(
        provider=req.provider,
        client_id=req.client_id,
        task_id=req.task_id,
        estimated_usd=req.estimated_usd,
        model=req.model
    )

    if decision.blocked:
        return AIResponse(
            ok=False,
            provider=decision.provider,
            model=req.model,
            content="",
            blocked=True,
            reason=decision.reason,
            request_id=decision.request_id
        )

    if decision.provider == "local_stub":
        return AIResponse(
            ok=True,
            provider="local_stub",
            model="local_stub",
            content="[KOS LOCAL STUB] chamada simulada sem custo.",
            blocked=False,
            reason="no_cost_stub",
            request_id=decision.request_id
        )

    if decision.provider == "ollama_local":
        return _run_ollama(req, decision.request_id)

    return AIResponse(
        ok=False,
        provider=decision.provider,
        model=req.model,
        content="",
        blocked=True,
        reason="provider sem executor implementado nesta fase",
        request_id=decision.request_id
    )

def _run_ollama(req: AIRequest, request_id: str) -> AIResponse:
    # Execucao local opcional. So funciona se Ollama estiver rodando.
    model = req.model if req.model and req.model != "local_stub" else "llama3.2"
    payload = json.dumps({
        "model": model,
        "prompt": req.prompt,
        "stream": False
    }).encode("utf-8")

    http_req = urllib.request.Request(
        "http://localhost:11434/api/generate",
        data=payload,
        method="POST",
        headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(http_req, timeout=120) as res:
            data = json.loads(res.read().decode("utf-8", errors="replace"))
        return AIResponse(
            ok=True,
            provider="ollama_local",
            model=model,
            content=data.get("response", ""),
            blocked=False,
            reason="local_ollama",
            request_id=request_id
        )
    except Exception as exc:
        return AIResponse(
            ok=False,
            provider="ollama_local",
            model=model,
            content="",
            blocked=True,
            reason=f"ollama indisponivel: {exc}",
            request_id=request_id
        )

if __name__ == "__main__":
    demo = AIRequest(
        client_id="system",
        task_id="phase29_smoke_test",
        prompt="Responda OK.",
        provider="local_stub",
        model="local_stub",
        estimated_usd=0.0
    )
    print(json.dumps(asdict(run_ai(demo)), ensure_ascii=False, indent=2))
'''

CATALOG.write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")
BUDGET.write_text(json.dumps(budget, ensure_ascii=False, indent=2), encoding="utf-8")
RUNTIME.write_text("\n".join(runtime) + "\n", encoding="utf-8")
LEDGER.parent.mkdir(parents=True, exist_ok=True)
LEDGER.touch(exist_ok=True)

INIT.write_text("", encoding="utf-8")
COST_GUARD.write_text(cost_guard_code.strip() + "\n", encoding="utf-8")
REGISTRY.write_text(registry_code.strip() + "\n", encoding="utf-8")
ROUTER.write_text(router_code.strip() + "\n", encoding="utf-8")

report = {
    "status": "AI_TRACE_FREE_TOOLS_REGISTRY_INSTALLED",
    "created_at": now(),
    "summary": summary,
    "findings": findings,
    "local_tools": local_tools,
    "catalog_file": rel(CATALOG),
    "budget_file": rel(BUDGET),
    "runtime_file": rel(RUNTIME),
    "ledger_file": rel(LEDGER),
    "registry_file": rel(REGISTRY),
    "cost_guard_file": rel(COST_GUARD),
    "router_file": rel(ROUTER),
    "policy": {
        "gemini_blocked_by_default": True,
        "openai_blocked_until_budget_configured": True,
        "browser_logged_accounts_backend_allowed": False,
        "free_first_order": catalog["default_order"]
    },
    "next_recommendation": "Instalar Ollama local se ainda nao existir e usar local_stub/ollama_local para testes sem custo de API."
}

REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

print(json.dumps({
    "status": report["status"],
    "files_scanned": summary["files_scanned"],
    "gemini_files": summary["gemini_files"],
    "openai_files": summary["openai_files"],
    "cost_risk_files": summary["cost_risk_files"],
    "ollama_installed": local_tools["ollama"]["installed"],
    "catalog": rel(CATALOG),
    "budget": rel(BUDGET),
    "router": rel(ROUTER),
    "ledger": rel(LEDGER)
}, ensure_ascii=False, indent=2))