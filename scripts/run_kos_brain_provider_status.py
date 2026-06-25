from __future__ import annotations

import argparse
import json
import os
import subprocess
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "memory" / "kos_governance" / "KOS_BRAIN_PROVIDER_PRIORITY_REGISTRY.json"
REPORT_DIR = ROOT / "reports"


def load_registry() -> dict[str, Any]:
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8-sig"))


def run_cmd(cmd: list[str], timeout: int = 10) -> dict[str, Any]:
    try:
        proc = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, timeout=timeout)
        return {
            "ok": proc.returncode == 0,
            "returncode": proc.returncode,
            "stdout": (proc.stdout or "").strip(),
            "stderr": (proc.stderr or "").strip(),
        }
    except Exception as exc:
        return {
            "ok": False,
            "error": str(exc),
        }


def http_get_json(url: str, timeout: int = 3) -> dict[str, Any]:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            body = response.read().decode("utf-8", errors="replace")
            return {
                "ok": True,
                "json": json.loads(body),
            }
    except Exception as exc:
        return {
            "ok": False,
            "error": str(exc),
        }


def check_internal_brain() -> dict[str, Any]:
    files = {
        "brain_gateway": ROOT / "scripts" / "kos_brain_gateway.py",
        "operator_chat": ROOT / "pages" / "KOS_Operator_Chat.py",
        "orchestrator_root": ROOT / "memory" / "kos_governance" / "KOS_ORCHESTRATOR_ROOT_CONSCIOUSNESS_V1.md",
        "response_contract": ROOT / "memory" / "kos_governance" / "KOS_OPERATOR_CHAT_RESPONSE_CONTRACT_V1.md",
        "toolbelt_registry": ROOT / "memory" / "kos_governance" / "KOS_GOOGLE_AI_TOOLBELT_REGISTRY.json",
        "gmail_operator": ROOT / "scripts" / "run_gmail_operator.py",
    }

    missing = [name for name, path in files.items() if not path.exists()]
    return {
        "id": "kos_internal_evolutionary",
        "active": len(missing) == 0,
        "cost": "zero",
        "missing": missing,
        "present": [name for name, path in files.items() if path.exists()],
    }


def check_ollama() -> dict[str, Any]:
    version = run_cmd(["ollama", "--version"])
    models_cmd = run_cmd(["ollama", "list"])
    ps_cmd = run_cmd(["ollama", "ps"])
    api = http_get_json("http://localhost:11434/api/tags")

    models = []
    if api.get("ok"):
        models = api.get("json", {}).get("models", []) or []

    return {
        "id": "ollama_local",
        "active": bool(api.get("ok") and len(models) > 0),
        "api_reachable": bool(api.get("ok")),
        "models_count": len(models),
        "models": [m.get("name") for m in models if isinstance(m, dict)],
        "version": version,
        "list": models_cmd,
        "running": ps_cmd,
        "cost": "zero_after_installation",
    }


def check_lmstudio() -> dict[str, Any]:
    base_url = os.environ.get("KOS_LMSTUDIO_BASE_URL", "").strip()
    if not base_url:
        return {
            "id": "lmstudio_local",
            "active": False,
            "reason": "KOS_LMSTUDIO_BASE_URL not configured",
        }

    url = base_url.rstrip("/") + "/v1/models"
    api = http_get_json(url)
    models = api.get("json", {}).get("data", []) if api.get("ok") else []
    return {
        "id": "lmstudio_local",
        "active": bool(api.get("ok") and models),
        "base_url": base_url,
        "models_count": len(models),
        "cost": "zero_after_installation",
    }


def check_local_openai() -> dict[str, Any]:
    base_url = os.environ.get("KOS_LOCAL_OPENAI_BASE_URL", "").strip()
    if not base_url:
        return {
            "id": "localai_or_vllm",
            "active": False,
            "reason": "KOS_LOCAL_OPENAI_BASE_URL not configured",
        }

    url = base_url.rstrip("/") + "/v1/models"
    api = http_get_json(url)
    models = api.get("json", {}).get("data", []) if api.get("ok") else []
    return {
        "id": "localai_or_vllm",
        "active": bool(api.get("ok") and models),
        "base_url": base_url,
        "models_count": len(models),
        "cost": "zero_or_self_hosted",
    }


def check_gemini_free_guarded() -> dict[str, Any]:
    api_key_present = bool(os.environ.get("GEMINI_API_KEY", "").strip())
    enabled = os.environ.get("KOS_AI_GEMINI_ENABLED", "").strip().lower() == "true"
    daily_request_budget = int(os.environ.get("KOS_GEMINI_DAILY_REQUEST_BUDGET", "25"))
    daily_token_budget = int(os.environ.get("KOS_GEMINI_DAILY_TOKEN_BUDGET", "100000"))

    return {
        "id": "gemini_free_guarded",
        "active": bool(api_key_present and enabled),
        "api_key_present": api_key_present,
        "enabled_flag": enabled,
        "daily_request_budget": daily_request_budget,
        "daily_token_budget": daily_token_budget,
        "cost": "free_tier_first",
        "note": "K-OS uses local budgets and provider limits; it does not hardcode official Google quotas.",
    }


def choose_provider(status: dict[str, Any]) -> dict[str, Any]:
    order = [
        "kos_internal_evolutionary",
        "ollama_local",
        "lmstudio_local",
        "localai_or_vllm",
        "gemini_free_guarded",
    ]

    for provider_id in order:
        item = status["providers"].get(provider_id, {})
        if item.get("active"):
            return {
                "selected_provider": provider_id,
                "reason": "first active provider in free-first priority order",
                "paid_provider_used": False,
            }

    return {
        "selected_provider": "kos_internal_evolutionary",
        "reason": "fallback to internal planning only; no external/local model active",
        "paid_provider_used": False,
    }


def build_status() -> dict[str, Any]:
    registry = load_registry()
    providers = {
        "kos_internal_evolutionary": check_internal_brain(),
        "ollama_local": check_ollama(),
        "lmstudio_local": check_lmstudio(),
        "localai_or_vllm": check_local_openai(),
        "gemini_free_guarded": check_gemini_free_guarded(),
        "external_paid_locked": {
            "id": "external_paid_locked",
            "active": False,
            "reason": "blocked by default; requires vault, budget and Human Gate",
        },
    }

    status = {
        "status": "KOS_BRAIN_PROVIDER_STATUS_READY",
        "generated_at": datetime.now().isoformat(),
        "registry_status": registry.get("status"),
        "routing_order": [item["id"] for item in registry.get("routing_order", [])],
        "providers": providers,
    }
    status["decision"] = choose_provider(status)
    return status


def write_report(status: dict[str, Any]) -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = REPORT_DIR / f"KOS_BRAIN_PROVIDER_STATUS_{stamp}.md"

    providers = status["providers"]
    decision = status["decision"]

    lines = [
        "# KOS BRAIN PROVIDER STATUS",
        "",
        f"Generated: {status['generated_at']}",
        "",
        "## Decision",
        "",
        f"Selected provider: {decision['selected_provider']}",
        f"Reason: {decision['reason']}",
        f"Paid provider used: {decision['paid_provider_used']}",
        "",
        "## Priority order",
    ]

    for item in status["routing_order"]:
        lines.append(f"- {item}")

    lines += [
        "",
        "## Providers",
    ]

    for provider_id, provider in providers.items():
        lines += [
            "",
            f"### {provider_id}",
            "",
            f"Active: {provider.get('active')}",
            f"Cost: {provider.get('cost', 'n/a')}",
        ]

        if provider_id == "ollama_local":
            lines += [
                f"API reachable: {provider.get('api_reachable')}",
                f"Models count: {provider.get('models_count')}",
                "Models:",
            ]
            for model in provider.get("models", []):
                lines.append(f"- {model}")

        if provider_id == "gemini_free_guarded":
            lines += [
                f"API key present: {provider.get('api_key_present')}",
                f"Enabled flag: {provider.get('enabled_flag')}",
                f"Daily request budget: {provider.get('daily_request_budget')}",
                f"Daily token budget: {provider.get('daily_token_budget')}",
            ]

        if provider.get("reason"):
            lines.append(f"Reason: {provider.get('reason')}")

    lines += [
        "",
        "## CTO readout",
        "",
        "- K-OS must always consult internal intelligence first.",
        "- Local free AI comes before cloud tokens.",
        "- Gemini free guarded comes before paid providers.",
        "- Paid/external providers remain locked by default.",
    ]

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["status", "report"], default="status")
    args = parser.parse_args()

    status = build_status()

    if args.mode == "report":
        report = write_report(status)
        print(json.dumps({
            "status": status["status"],
            "selected_provider": status["decision"]["selected_provider"],
            "report": str(report),
        }, ensure_ascii=False, indent=2))
        return

    print(json.dumps(status, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
