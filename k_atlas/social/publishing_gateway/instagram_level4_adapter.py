from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from k_atlas.ig_final_run.final_runner import (
    FINAL_TYPED_CONFIRMATION,
    build_phase14_final_package,
    execute_phase14_if_confirmed,
)
from k_atlas.ig_real_gate.readiness import inspect_ig_real_readiness

from .audit_log import AuditLog, sanitize_for_audit
from .permission_model import find_plaintext_secrets


DEFAULT_ALLOWED_TEST_ACCOUNTS = frozenset({
    "kos_official",
    "k_os_official",
    "kos_viking",
    "viking",
    "hupmix",
})

DEFAULT_BLOCKED_CLIENTS = frozenset({
    "parada_atlantida",
    "parada-atlantida",
})


@dataclass(frozen=True)
class InstagramLevel4Policy:
    """Runtime policy for the governed Instagram adapter.

    The adapter exists to bring the legacy `ig_real_gate` into the publishing
    gateway without weakening the existing Fase 12/13/14 locks.
    """

    allowed_test_accounts: frozenset[str] = field(default_factory=lambda: DEFAULT_ALLOWED_TEST_ACCOUNTS)
    blocked_clients: frozenset[str] = field(default_factory=lambda: DEFAULT_BLOCKED_CLIENTS)
    max_caption_chars: int = 2200


class InstagramLevel4Adapter:
    """Governed wrapper around the legacy Instagram real gate.

    Default behavior is preview/block. A real Graph API call can only happen when
    the caller supplies the explicit execute switch, typed confirmation, and the
    legacy final gate also reports ready.
    """

    def __init__(
        self,
        audit_log: AuditLog | None = None,
        policy: InstagramLevel4Policy | None = None,
    ) -> None:
        self.audit_log = audit_log or AuditLog()
        self.policy = policy or InstagramLevel4Policy()

    def prepare(self, payload: Mapping[str, Any], actor: str = "k_social_operator") -> dict[str, Any]:
        return self.publish(payload, actor=actor, execute_real_confirmed=False, typed_confirmation="")

    def publish(
        self,
        payload: Mapping[str, Any],
        actor: str = "k_social_operator",
        *,
        execute_real_confirmed: bool = False,
        typed_confirmation: str = "",
    ) -> dict[str, Any]:
        clean_payload = sanitize_for_audit(dict(payload))
        policy_reasons = self._validate_payload(payload)
        readiness = inspect_ig_real_readiness()

        if policy_reasons:
            return self._audit_result(
                "blocked_by_instagram_level4_policy",
                actor,
                {
                    "ok": False,
                    "status": "blocked_by_instagram_level4_policy",
                    "adapter": "instagram_level4_adapter",
                    "side_effects": "none",
                    "reasons": policy_reasons,
                    "readiness": readiness,
                    "payload": clean_payload,
                },
                policy_reasons,
            )

        if not bool(payload.get("publish_real")):
            return self._audit_result(
                "ready_for_level4_preview",
                actor,
                {
                    "ok": True,
                    "status": "ready_for_level4_preview",
                    "adapter": "instagram_level4_adapter",
                    "side_effects": "none",
                    "reasons": ["publish_real_false_preview_only"],
                    "required_typed_confirmation": FINAL_TYPED_CONFIRMATION,
                    "readiness": readiness,
                    "package_preview": self._package_preview(payload),
                    "payload": clean_payload,
                },
                ["publish_real_false_preview_only"],
            )

        if not execute_real_confirmed:
            return self._audit_result(
                "blocked_by_execute_switch",
                actor,
                {
                    "ok": False,
                    "status": "blocked_by_execute_switch",
                    "adapter": "instagram_level4_adapter",
                    "side_effects": "none",
                    "reasons": ["execute_real_confirmed_required"],
                    "required_typed_confirmation": FINAL_TYPED_CONFIRMATION,
                    "readiness": readiness,
                    "package_preview": self._package_preview(payload),
                    "payload": clean_payload,
                },
                ["execute_real_confirmed_required"],
            )

        if typed_confirmation != FINAL_TYPED_CONFIRMATION:
            return self._audit_result(
                "blocked_by_typed_confirmation",
                actor,
                {
                    "ok": False,
                    "status": "blocked_by_typed_confirmation",
                    "adapter": "instagram_level4_adapter",
                    "side_effects": "none",
                    "reasons": ["typed_confirmation_required"],
                    "required_typed_confirmation": FINAL_TYPED_CONFIRMATION,
                    "readiness": readiness,
                    "package_preview": self._package_preview(payload),
                    "payload": clean_payload,
                },
                ["typed_confirmation_required"],
            )

        package = build_phase14_final_package(
            client_id=str(payload.get("client_id", "kos_viking")),
            campaign_name=str(payload.get("campaign_name", "kos_official_test")),
            image_url=str(payload.get("image_url", "https://placehold.co/1080x1080/png")),
            caption=str(payload.get("caption", "K-OS official test.")),
            load_runtime=True,
        )

        result = execute_phase14_if_confirmed(
            package,
            typed_confirmation=typed_confirmation,
            execute_real_confirmed=True,
        )

        side_effects = "instagram_graph_api" if result.get("real_action_executed") else "none"
        status = str(result.get("status", "unknown"))
        return self._audit_result(
            status,
            actor,
            {
                "ok": bool(result.get("real_action_executed")),
                "status": status,
                "adapter": "instagram_level4_adapter",
                "side_effects": side_effects,
                "result": sanitize_for_audit(result),
                "payload": clean_payload,
            },
            [status],
        )

    def _validate_payload(self, payload: Mapping[str, Any]) -> list[str]:
        reasons: list[str] = []
        client_id = str(payload.get("client_id", "")).strip().lower()
        account_alias = str(payload.get("account_alias", "")).strip().lower()
        channel = str(payload.get("channel", "")).strip()
        level = str(payload.get("autonomy_level", "")).strip()
        caption = str(payload.get("caption", ""))
        image_url = str(payload.get("image_url", ""))

        if channel != "instagram_official":
            reasons.append("channel_must_be_instagram_official")
        if level != "level_4_limited_real_publish":
            reasons.append("autonomy_level_must_be_level_4_limited_real_publish")
        if client_id in self.policy.blocked_clients:
            reasons.append(f"client_blocked_for_real_publish:{client_id}")
        if account_alias not in self.policy.allowed_test_accounts:
            reasons.append("account_alias_not_allowlisted_for_level4_test")
        if bool(payload.get("browser_automation")):
            reasons.append("browser_automation_blocked")
        if bool(payload.get("mass_messaging")):
            reasons.append("mass_messaging_blocked")
        if len(caption) > self.policy.max_caption_chars:
            reasons.append("caption_too_long")
        if not image_url.startswith("https://"):
            reasons.append("image_url_must_be_public_https")

        secret_paths = find_plaintext_secrets(payload)
        if secret_paths:
            reasons.append("plaintext_secret_blocked:" + ",".join(secret_paths))

        return reasons

    def _package_preview(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        return sanitize_for_audit({
            "status": "LEVEL4_PACKAGE_PREVIEW",
            "client_id": payload.get("client_id", "kos_viking"),
            "account_alias": payload.get("account_alias", "kos_viking"),
            "campaign_name": payload.get("campaign_name", "kos_official_test"),
            "image_url": payload.get("image_url", ""),
            "caption": payload.get("caption", ""),
            "real_action_executed": False,
            "external_call_executed": False,
            "legacy_phase14_package_written": False,
        })

    def _audit_result(
        self,
        status: str,
        actor: str,
        result: dict[str, Any],
        reasons: list[str],
    ) -> dict[str, Any]:
        self.audit_log.write_event(
            action="instagram_level4_adapter.publish",
            status=status,
            actor=actor,
            payload=result,
            reasons=reasons,
        )
        return result
