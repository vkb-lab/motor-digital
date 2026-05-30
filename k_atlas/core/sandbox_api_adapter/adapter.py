from __future__ import annotations

from typing import Any, Mapping

from .audit import SandboxAPIAuditLog
from .policy import validate_sandbox_api_payload
from .providers import build_provider_registry


class SandboxAPIAdapter:
    def __init__(self, audit_log: SandboxAPIAuditLog | None = None) -> None:
        self.audit_log = audit_log or SandboxAPIAuditLog()
        self.providers = build_provider_registry()

    def list_providers(self) -> list[dict[str, Any]]:
        return [provider.to_dict() for provider in self.providers.values()]

    def execute(
        self,
        provider_id: str,
        operation: str,
        payload: Mapping[str, Any] | None = None,
        requested_by: str = "human_operator",
    ) -> dict[str, Any]:
        data = dict(payload or {})

        provider = self.providers.get(provider_id)
        if provider is None:
            result = {
                "ok": False,
                "status": "provider_not_registered",
                "provider_id": provider_id,
                "operation": operation,
            }
            self.audit_log.append({
                "requested_by": requested_by,
                "provider_id": provider_id,
                "operation": operation,
                "payload": data,
                "result": result,
            })
            return result

        if operation not in provider.operations:
            result = {
                "ok": False,
                "status": "operation_not_supported",
                "provider_id": provider_id,
                "operation": operation,
                "supported_operations": provider.operations,
            }
            self.audit_log.append({
                "requested_by": requested_by,
                "provider_id": provider_id,
                "operation": operation,
                "payload": data,
                "result": result,
            })
            return result

        validation = validate_sandbox_api_payload(data)

        if not validation["ok"]:
            result = {
                "ok": False,
                "status": "blocked_by_sandbox_policy",
                "provider": provider.to_dict(),
                "operation": operation,
                "validation": validation,
            }
            self.audit_log.append({
                "requested_by": requested_by,
                "provider_id": provider_id,
                "operation": operation,
                "payload": data,
                "result": result,
            })
            return result

        result = {
            "ok": True,
            "status": "sandbox_simulation_completed",
            "provider": provider.to_dict(),
            "operation": operation,
            "validation": validation,
            "side_effects": "none",
            "network_used": False,
            "external_api_used": False,
            "credential_required_now": False,
            "credential_required_future": provider.required_vault_refs_future,
            "simulated_response": self._simulate_response(provider_id, operation, data),
        }

        self.audit_log.append({
            "requested_by": requested_by,
            "provider_id": provider_id,
            "operation": operation,
            "payload": data,
            "result": result,
        })

        return result

    def _simulate_response(self, provider_id: str, operation: str, payload: dict[str, Any]) -> dict[str, Any]:
        if provider_id == "google_ai_sandbox":
            return {
                "creative_job_status": "planned",
                "prompt_preview": str(payload.get("prompt") or payload.get("objective") or "")[:500],
                "output_type": "image_or_video_plan",
            }

        if provider_id == "meta_graph_sandbox":
            return {
                "instagram_job_status": "planned",
                "media_type": payload.get("media_type", "feed_or_reel"),
                "caption_preview": str(payload.get("caption") or "")[:500],
            }

        if provider_id == "whatsapp_cloud_sandbox":
            return {
                "message_job_status": "simulated_single_message_only",
                "consent_required": True,
                "recipient_count_allowed": 1,
            }

        if provider_id == "email_sandbox":
            return {
                "email_job_status": "simulated_single_email_only",
                "unsubscribe_required": True,
                "recipient_count_allowed": 1,
            }

        return {
            "status": "generic_simulation",
        }
