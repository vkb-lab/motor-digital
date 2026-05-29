from __future__ import annotations

from typing import Any, Mapping

from k_atlas.security.credential_vault import (
    VaultResolutionError,
    get_bool_env,
    resolve_secret,
    sanitize_mapping,
    validate_no_plaintext_secrets,
)

from .approval_policy import ApprovalPolicy, ApprovalStatus
from .audit_log import AuditLog
from .channel_registry import build_default_channel_registry


class TestPageAPIAdapter:
    """
    Adapter LEVEL 2.5.

    Objetivo:
    - preparar envio real para endpoint de teste
    - exigir credential vault
    - bloquear por padrao em cloud/local
    - nunca publicar em conta oficial
    - nunca fazer mass messaging
    """

    def __init__(
        self,
        audit_log: AuditLog | None = None,
        approval_policy: ApprovalPolicy | None = None,
        endpoint_ref: str = "vault://env/K_SOCIAL_TEST_PAGE_ENDPOINT",
        token_ref: str = "vault://env/K_SOCIAL_TEST_PAGE_TOKEN",
    ) -> None:
        self.audit_log = audit_log or AuditLog()
        self.approval_policy = approval_policy or ApprovalPolicy()
        self.registry = build_default_channel_registry()
        self.endpoint_ref = endpoint_ref
        self.token_ref = token_ref

    def publish(self, payload: Mapping[str, Any], actor: str = "k_social_operator") -> dict[str, Any]:
        clean_payload = sanitize_mapping(dict(payload))

        vault_check = validate_no_plaintext_secrets(dict(payload))
        if not vault_check.ok:
            result = {
                "ok": False,
                "status": "blocked_plaintext_secret",
                "adapter": "test_page_api_adapter",
                "side_effects": "none",
                "reasons": vault_check.reasons,
                "payload": clean_payload,
            }
            self._audit("blocked_plaintext_secret", actor, result, vault_check.reasons)
            return result

        if bool(payload.get("publish_real")):
            return self._blocked("real_publish_blocked", actor, clean_payload, ["real_publish_not_allowed"])

        if bool(payload.get("mass_messaging")):
            return self._blocked("mass_messaging_blocked", actor, clean_payload, ["mass_messaging_not_allowed"])

        if bool(payload.get("browser_automation")):
            return self._blocked("browser_automation_blocked", actor, clean_payload, ["browser_automation_not_allowed"])

        if str(payload.get("channel")) != "test_page":
            return self._blocked("invalid_channel", actor, clean_payload, ["only_test_page_channel_allowed"])

        permission = self.registry.get("test_page").permission
        approval = self.approval_policy.evaluate(payload, permission)

        if approval.status not in {
            ApprovalStatus.APPROVED_FOR_TEST_PAGE,
            ApprovalStatus.APPROVED_FOR_DRAFT,
        }:
            return self._blocked(approval.status.value, actor, clean_payload, approval.reasons)

        if not get_bool_env("K_SOCIAL_EXTERNAL_API_ENABLED", default=False):
            result = {
                "ok": False,
                "status": "external_api_disabled",
                "adapter": "test_page_api_adapter",
                "side_effects": "none",
                "reasons": ["K_SOCIAL_EXTERNAL_API_ENABLED_false"],
                "payload": clean_payload,
            }
            self._audit("external_api_disabled", actor, result, result["reasons"])
            return result

        if get_bool_env("K_SOCIAL_AUTO_PUBLISH", default=False):
            return self._blocked("auto_publish_blocked", actor, clean_payload, ["K_SOCIAL_AUTO_PUBLISH_must_remain_false"])

        try:
            endpoint = resolve_secret(self.endpoint_ref)
            token = resolve_secret(self.token_ref)
        except VaultResolutionError as exc:
            return self._blocked("missing_vault_secret", actor, clean_payload, [str(exc)])

        if not endpoint.startswith("https://"):
            return self._blocked("invalid_endpoint", actor, clean_payload, ["endpoint_must_use_https"])

        import requests

        response = requests.post(
            endpoint,
            json={
                "source": "k_atlas_social_publishing_gateway",
                "mode": "level_2_5_test_page_api",
                "payload": clean_payload,
            },
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            timeout=20,
        )

        result = {
            "ok": 200 <= response.status_code < 300,
            "status": "sent_to_test_page_api" if 200 <= response.status_code < 300 else "test_page_api_error",
            "adapter": "test_page_api_adapter",
            "side_effects": "external_test_page_api_only",
            "http_status": response.status_code,
            "reasons": ["sent_with_vault_credentials"],
            "payload": clean_payload,
        }

        self._audit(result["status"], actor, result, result["reasons"])
        return result

    def _blocked(
        self,
        status: str,
        actor: str,
        payload: Mapping[str, Any],
        reasons: list[str],
    ) -> dict[str, Any]:
        result = {
            "ok": False,
            "status": status,
            "adapter": "test_page_api_adapter",
            "side_effects": "none",
            "reasons": reasons,
            "payload": dict(payload),
        }
        self._audit(status, actor, result, reasons)
        return result

    def _audit(
        self,
        status: str,
        actor: str,
        payload: Mapping[str, Any],
        reasons: list[str],
    ) -> None:
        self.audit_log.write_event(
            action="test_page_api_adapter.publish",
            status=status,
            actor=actor,
            payload=payload,
            reasons=reasons,
        )