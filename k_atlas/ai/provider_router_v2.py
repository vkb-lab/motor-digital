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
