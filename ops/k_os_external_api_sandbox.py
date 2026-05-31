# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path.cwd()

POLICY_PATH = ROOT / "config" / "external_sandbox" / "k_os_external_api_sandbox_policy.json"
REPORT_DIR = ROOT / "reports" / "external_sandbox"
MEMORY_DIR = ROOT / "memory" / "external_sandbox"
LATEST_JSON = REPORT_DIR / "latest_external_api_sandbox_report.json"
LATEST_MD = REPORT_DIR / "latest_external_api_sandbox_report.md"
EVENTS_JSONL = MEMORY_DIR / "events.jsonl"


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return None


def policy() -> dict[str, Any]:
    data = load_json(POLICY_PATH)
    if not data:
        raise RuntimeError("Política do sandbox externo não encontrada.")
    return data


def provider_config(provider: str) -> dict[str, Any] | None:
    data = policy()
    for item in data.get("providers", []):
        if item.get("provider") == provider:
            return item
    return None


def run_risk_classifier(action: str, agent: str, target: str) -> dict[str, Any]:
    script = ROOT / "ops" / "k_os_ai_risk_classifier.py"
    if not script.exists():
        return {
            "available": False,
            "risk_level": "unknown",
            "decision": "requires_approval",
            "required_gates": ["human_operator_approval"],
        }

    completed = subprocess.run(
        [
            "python",
            str(script),
            "--mode",
            "classify",
            "--action",
            action,
            "--agent",
            agent,
            "--target",
            target,
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    if completed.returncode != 0:
        return {
            "available": True,
            "ok": False,
            "risk_level": "unknown",
            "decision": "requires_approval",
            "required_gates": ["human_operator_approval"],
            "stderr": completed.stderr,
        }

    try:
        parsed = json.loads(completed.stdout)
        results = parsed.get("results", [])
        if results:
            item = results[0]
            item["available"] = True
            return item
    except Exception:
        pass

    return {
        "available": True,
        "risk_level": "unknown",
        "decision": "requires_approval",
        "required_gates": ["human_operator_approval"],
    }


def vault_status() -> dict[str, Any]:
    report = load_json(ROOT / "reports" / "vault" / "latest_vault_guard_report.json")
    if not report:
        return {
            "available": False,
            "vault_report_exists": False,
            "raw_values_exposed": "unknown",
            "external_api_enabled": False,
        }

    return {
        "available": True,
        "vault_report_exists": True,
        "item_count": report.get("item_count", 0),
        "raw_values_exposed": report.get("raw_values_exposed", False),
        "external_api_enabled": report.get("external_api_enabled", False),
        "storage": report.get("storage", "unknown"),
    }


def license_status(customer_use: bool) -> dict[str, Any]:
    report = load_json(ROOT / "reports" / "license" / "latest_license_gate_report.json")
    if not customer_use:
        return {
            "required": False,
            "ok": True,
            "reason": "internal_or_demo_sandbox",
        }

    if not report:
        return {
            "required": True,
            "ok": False,
            "reason": "license_report_missing",
        }

    active = [
        item for item in report.get("licenses", [])
        if item.get("status") == "active" and item.get("emergency_lockdown") is False
    ]

    return {
        "required": True,
        "ok": len(active) > 0 and report.get("emergency_lockdown") is False,
        "active_count": len(active),
        "emergency_lockdown": report.get("emergency_lockdown", False),
    }


def build_payload(provider: str, use_case: str, prompt: str, agent: str, customer_use: bool) -> dict[str, Any]:
    provider_item = provider_config(provider)
    if not provider_item:
        raise RuntimeError(f"Provider não registrado no sandbox: {provider}")

    risk = run_risk_classifier(
        action=f"Sandbox external provider payload for {provider} {use_case}",
        agent=agent,
        target=provider,
    )

    vault = vault_status()
    license_gate = license_status(customer_use)

    payload_id = "sandbox_" + uuid.uuid4().hex[:12]

    payload = {
        "payload_id": payload_id,
        "created_at": now(),
        "provider": provider,
        "use_case": use_case,
        "agent_id": agent,
        "customer_use": customer_use,
        "dry_run": True,
        "real_provider_call_enabled": False,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "prompt_hash": sha256_text(prompt),
        "prompt_length": len(prompt),
        "prompt_preview_redacted": prompt[:80] + ("..." if len(prompt) > 80 else ""),
        "provider_status": provider_item.get("status"),
        "provider_category": provider_item.get("category"),
        "future_use": provider_item.get("future_use", []),
        "risk": risk,
        "vault": vault,
        "license_gate": license_gate,
        "required_gates_before_real_call": policy().get("required_gates_before_real_call", []),
        "blocked_by_default": policy().get("blocked_by_default", []),
    }

    blockers = []

    if provider_item.get("real_call_allowed") is not False:
        blockers.append("provider_policy_invalid_real_call_allowed_should_be_false")

    if risk.get("decision") in {"blocked_until_explicit_approval", "requires_approval"}:
        blockers.append("risk_gate_required")

    if customer_use and not license_gate.get("ok"):
        blockers.append("license_gate_not_satisfied")

    if vault.get("raw_values_exposed") is True:
        blockers.append("vault_raw_value_exposure_detected")

    payload["sandbox_decision"] = "sandbox_payload_ready"
    payload["real_call_decision"] = "blocked"
    payload["blockers_before_real_call"] = blockers
    payload["ok"] = True

    return payload


def simulate(provider: str, use_case: str, prompt: str, agent: str, customer_use: bool) -> dict[str, Any]:
    payload = build_payload(provider, use_case, prompt, agent, customer_use)

    mock_output = {
        "simulation_id": "sim_" + uuid.uuid4().hex[:12],
        "created_at": now(),
        "provider": provider,
        "use_case": use_case,
        "status": "simulated_only",
        "real_call_performed": False,
        "estimated_cost_usd": estimate_cost(provider, use_case),
        "mock_result": {
            "title": f"Sandbox result for {provider}/{use_case}",
            "summary": "Payload validado em modo sandbox. Nenhuma chamada externa foi feita.",
            "next_gate": "human_operator_approval",
        },
    }

    return {
        "ok": True,
        "checkpoint": "022",
        "module": "k_os_external_api_sandbox",
        "status": "simulated",
        "generated_at": now(),
        "payload": payload,
        "simulation": mock_output,
        "next_checkpoint": "023 - K-Enterprise Readiness Report",
    }


def estimate_cost(provider: str, use_case: str) -> float:
    key = f"{provider}:{use_case}".lower()

    if "video" in key or provider in {"runway", "luma", "sora"}:
        return 1.50

    if "voice" in key or provider == "elevenlabs":
        return 0.25

    if "image" in key or provider in {"openai", "comfyui", "midjourney"}:
        return 0.10

    if provider in {"instagram", "whatsapp", "google"}:
        return 0.02

    return 0.05


def smoke_test() -> dict[str, Any]:
    tests = [
        ("openai", "text_brief", "Gerar briefing seguro para campanha Marketplace IA.", "marketplace_ia_agent", False),
        ("runway", "video_storyboard", "Simular vídeo curto para landing pública.", "future_multimodal_connector", False),
        ("elevenlabs", "voice_narration", "Simular narração curta para anúncio.", "future_multimodal_connector", False),
        ("instagram", "post_draft", "Simular pacote de post sem publicar.", "marketplace_ia_agent", False),
        ("whatsapp", "manual_send_pack", "Simular mensagem manual sem envio.", "marketplace_ia_agent", True),
        ("google", "analytics_review", "Simular leitura de analytics sem conexão real.", "k_uni_cockpit", False),
    ]

    results = [
        simulate(provider, use_case, prompt, agent, customer_use)
        for provider, use_case, prompt, agent, customer_use in tests
    ]

    blockers = []
    for item in results:
        blockers.extend(item.get("payload", {}).get("blockers_before_real_call", []))

    return {
        "ok": True,
        "checkpoint": "022",
        "module": "k_os_external_api_sandbox",
        "status": "smoke_passed",
        "generated_at": now(),
        "results_count": len(results),
        "results": results,
        "real_provider_call_performed": False,
        "real_provider_call_enabled": False,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "blockers_before_real_call_count": len(blockers),
        "manual_approval_required": True,
        "next_checkpoint": "023 - K-Enterprise Readiness Report",
    }


def write_report(report: dict[str, Any]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)

    LATEST_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS External API Sandbox Report",
        "",
        f"- Status: {report.get('status')}",
        f"- OK: {report.get('ok')}",
        f"- Generated at: {report.get('generated_at')}",
        f"- Real provider call performed: {report.get('real_provider_call_performed', False)}",
        f"- External send enabled: {report.get('external_send_enabled', False)}",
        f"- External publish enabled: {report.get('external_publish_enabled', False)}",
        "",
        "## Results",
        "",
    ]

    for item in report.get("results", []):
        payload = item.get("payload", {})
        simulation = item.get("simulation", {})
        lines.append(
            f"- {payload.get('provider')}/{payload.get('use_case')} | decision={payload.get('real_call_decision')} | simulated={simulation.get('status')}"
        )

    if report.get("payload"):
        payload = report.get("payload", {})
        lines.append(
            f"- {payload.get('provider')}/{payload.get('use_case')} | decision={payload.get('real_call_decision')}"
        )

    LATEST_MD.write_text("\n".join(lines), encoding="utf-8")

    with EVENTS_JSONL.open("a", encoding="utf-8") as file:
        file.write(json.dumps({
            "event": "external_api_sandbox.report",
            "created_at": now(),
            "status": report.get("status"),
            "real_call_performed": report.get("real_provider_call_performed", False),
        }, ensure_ascii=False) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["smoke-test", "simulate", "show-policy"], required=True)
    parser.add_argument("--provider", default="openai")
    parser.add_argument("--use-case", default="text_brief")
    parser.add_argument("--prompt", default="Sandbox prompt sem dados sensíveis.")
    parser.add_argument("--agent", default="marketplace_ia_agent")
    parser.add_argument("--customer-use", action="store_true")
    args = parser.parse_args()

    if args.mode == "show-policy":
        data = policy()
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0

    if args.mode == "smoke-test":
        report = smoke_test()
        write_report(report)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    if args.mode == "simulate":
        report = simulate(args.provider, args.use_case, args.prompt, args.agent, args.customer_use)
        write_report(report)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())