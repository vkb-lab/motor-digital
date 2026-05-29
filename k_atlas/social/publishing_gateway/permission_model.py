from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping, Optional


class AutonomyLevel(str, Enum):
    LEVEL_0_STRATEGY = "level_0_strategy"
    LEVEL_1_CAMPAIGN_PACKAGE = "level_1_campaign_package"
    LEVEL_2_SANDBOX_PAGE = "level_2_sandbox_page"
    LEVEL_2_5_TEST_ADAPTER = "level_2_5_test_adapter"
    LEVEL_3_SCHEDULE_DRAFT = "level_3_schedule_draft"
    LEVEL_4_LIMITED_REAL_PUBLISH = "level_4_limited_real_publish"
    LEVEL_5_GOVERNED_OPERATIONS = "level_5_governed_operations"


class PermissionDecision(str, Enum):
    ALLOW = "allow"
    REVIEW_REQUIRED = "review_required"
    DENY = "deny"


@dataclass(frozen=True)
class ChannelPermission:
    channel: str
    allowed_levels: tuple[AutonomyLevel, ...]
    can_dry_run: bool = True
    can_test_page: bool = False
    can_schedule_draft: bool = False
    can_publish_real: bool = False
    requires_human_review: bool = True
    requires_credential_vault: bool = True
    allow_mass_messaging: bool = False
    allow_browser_automation: bool = False
    max_posts_per_hour: int = 2
    max_posts_per_day: int = 5


SECRET_KEY_PARTS = ("token", "secret", "password", "api_key", "access_key")


def utc_safe_text(value: Any) -> str:
    return str(value).strip()


def is_vault_ref(value: Any) -> bool:
    return isinstance(value, str) and value.startswith("vault://") and len(value) > len("vault://")


def normalize_autonomy_level(value: Any) -> AutonomyLevel:
    if isinstance(value, AutonomyLevel):
        return value

    text = utc_safe_text(value).lower()
    aliases = {
        "0": AutonomyLevel.LEVEL_0_STRATEGY,
        "level_0": AutonomyLevel.LEVEL_0_STRATEGY,
        "strategy": AutonomyLevel.LEVEL_0_STRATEGY,
        "1": AutonomyLevel.LEVEL_1_CAMPAIGN_PACKAGE,
        "level_1": AutonomyLevel.LEVEL_1_CAMPAIGN_PACKAGE,
        "package": AutonomyLevel.LEVEL_1_CAMPAIGN_PACKAGE,
        "2": AutonomyLevel.LEVEL_2_SANDBOX_PAGE,
        "level_2": AutonomyLevel.LEVEL_2_SANDBOX_PAGE,
        "sandbox": AutonomyLevel.LEVEL_2_SANDBOX_PAGE,
        "2.5": AutonomyLevel.LEVEL_2_5_TEST_ADAPTER,
        "level_2_5": AutonomyLevel.LEVEL_2_5_TEST_ADAPTER,
        "test_adapter": AutonomyLevel.LEVEL_2_5_TEST_ADAPTER,
        "3": AutonomyLevel.LEVEL_3_SCHEDULE_DRAFT,
        "level_3": AutonomyLevel.LEVEL_3_SCHEDULE_DRAFT,
        "draft": AutonomyLevel.LEVEL_3_SCHEDULE_DRAFT,
        "4": AutonomyLevel.LEVEL_4_LIMITED_REAL_PUBLISH,
        "level_4": AutonomyLevel.LEVEL_4_LIMITED_REAL_PUBLISH,
        "limited_publish": AutonomyLevel.LEVEL_4_LIMITED_REAL_PUBLISH,
        "5": AutonomyLevel.LEVEL_5_GOVERNED_OPERATIONS,
        "level_5": AutonomyLevel.LEVEL_5_GOVERNED_OPERATIONS,
    }
    if text in aliases:
        return aliases[text]

    for level in AutonomyLevel:
        if text in {level.value.lower(), level.name.lower()}:
            return level

    raise ValueError(f"Autonomy level invalido: {value!r}")


def find_plaintext_secrets(data: Any, prefix: str = "") -> list[str]:
    findings: list[str] = []

    if isinstance(data, Mapping):
        for key, value in data.items():
            key_text = str(key)
            lowered = key_text.lower()
            current_path = f"{prefix}.{key_text}" if prefix else key_text

            if any(part in lowered for part in SECRET_KEY_PARTS):
                if value not in (None, "", []):
                    if not is_vault_ref(value):
                        findings.append(current_path)

            findings.extend(find_plaintext_secrets(value, current_path))

    elif isinstance(data, (list, tuple)):
        for index, item in enumerate(data):
            current_path = f"{prefix}[{index}]"
            findings.extend(find_plaintext_secrets(item, current_path))

    return sorted(set(findings))


def default_channel_permissions() -> dict[str, ChannelPermission]:
    return {
        "dry_run": ChannelPermission(
            channel="dry_run",
            allowed_levels=(
                AutonomyLevel.LEVEL_0_STRATEGY,
                AutonomyLevel.LEVEL_1_CAMPAIGN_PACKAGE,
                AutonomyLevel.LEVEL_2_SANDBOX_PAGE,
            ),
            can_dry_run=True,
            can_test_page=False,
            can_schedule_draft=False,
            can_publish_real=False,
            requires_human_review=False,
            requires_credential_vault=False,
            max_posts_per_hour=20,
            max_posts_per_day=100,
        ),
        "test_page": ChannelPermission(
            channel="test_page",
            allowed_levels=(
                AutonomyLevel.LEVEL_2_SANDBOX_PAGE,
                AutonomyLevel.LEVEL_2_5_TEST_ADAPTER,
            ),
            can_dry_run=True,
            can_test_page=True,
            can_schedule_draft=False,
            can_publish_real=False,
            requires_human_review=True,
            requires_credential_vault=False,
            max_posts_per_hour=5,
            max_posts_per_day=20,
        ),
        "instagram_sandbox": ChannelPermission(
            channel="instagram_sandbox",
            allowed_levels=(
                AutonomyLevel.LEVEL_2_5_TEST_ADAPTER,
                AutonomyLevel.LEVEL_3_SCHEDULE_DRAFT,
            ),
            can_dry_run=True,
            can_test_page=False,
            can_schedule_draft=True,
            can_publish_real=False,
            requires_human_review=True,
            requires_credential_vault=True,
            max_posts_per_hour=2,
            max_posts_per_day=6,
        ),
        "whatsapp_sandbox": ChannelPermission(
            channel="whatsapp_sandbox",
            allowed_levels=(
                AutonomyLevel.LEVEL_2_5_TEST_ADAPTER,
                AutonomyLevel.LEVEL_3_SCHEDULE_DRAFT,
            ),
            can_dry_run=True,
            can_test_page=False,
            can_schedule_draft=True,
            can_publish_real=False,
            requires_human_review=True,
            requires_credential_vault=True,
            allow_mass_messaging=False,
            max_posts_per_hour=1,
            max_posts_per_day=3,
        ),
        "email_sandbox": ChannelPermission(
            channel="email_sandbox",
            allowed_levels=(
                AutonomyLevel.LEVEL_2_5_TEST_ADAPTER,
                AutonomyLevel.LEVEL_3_SCHEDULE_DRAFT,
            ),
            can_dry_run=True,
            can_test_page=False,
            can_schedule_draft=True,
            can_publish_real=False,
            requires_human_review=True,
            requires_credential_vault=True,
            allow_mass_messaging=False,
            max_posts_per_hour=2,
            max_posts_per_day=5,
        ),
        "instagram_official": ChannelPermission(
            channel="instagram_official",
            allowed_levels=(
                AutonomyLevel.LEVEL_0_STRATEGY,
                AutonomyLevel.LEVEL_1_CAMPAIGN_PACKAGE,
                AutonomyLevel.LEVEL_2_SANDBOX_PAGE,
                AutonomyLevel.LEVEL_2_5_TEST_ADAPTER,
                AutonomyLevel.LEVEL_3_SCHEDULE_DRAFT,
            ),
            can_dry_run=True,
            can_test_page=False,
            can_schedule_draft=True,
            can_publish_real=False,
            requires_human_review=True,
            requires_credential_vault=True,
            max_posts_per_hour=1,
            max_posts_per_day=2,
        ),
        "whatsapp_official": ChannelPermission(
            channel="whatsapp_official",
            allowed_levels=(
                AutonomyLevel.LEVEL_0_STRATEGY,
                AutonomyLevel.LEVEL_1_CAMPAIGN_PACKAGE,
                AutonomyLevel.LEVEL_2_SANDBOX_PAGE,
            ),
            can_dry_run=True,
            can_test_page=False,
            can_schedule_draft=False,
            can_publish_real=False,
            requires_human_review=True,
            requires_credential_vault=True,
            allow_mass_messaging=False,
            max_posts_per_hour=1,
            max_posts_per_day=1,
        ),
        "email_official": ChannelPermission(
            channel="email_official",
            allowed_levels=(
                AutonomyLevel.LEVEL_0_STRATEGY,
                AutonomyLevel.LEVEL_1_CAMPAIGN_PACKAGE,
                AutonomyLevel.LEVEL_2_SANDBOX_PAGE,
                AutonomyLevel.LEVEL_3_SCHEDULE_DRAFT,
            ),
            can_dry_run=True,
            can_test_page=False,
            can_schedule_draft=True,
            can_publish_real=False,
            requires_human_review=True,
            requires_credential_vault=True,
            allow_mass_messaging=False,
            max_posts_per_hour=1,
            max_posts_per_day=2,
        ),
    }


def get_permission(channel: str, permissions: Optional[Mapping[str, ChannelPermission]] = None) -> ChannelPermission:
    registry = dict(permissions or default_channel_permissions())
    if channel not in registry:
        raise KeyError(f"Canal nao registrado no permission model: {channel}")
    return registry[channel]


def evaluate_permission(
    channel: str,
    autonomy_level: Any,
    payload: Optional[Mapping[str, Any]] = None,
    permissions: Optional[Mapping[str, ChannelPermission]] = None,
) -> tuple[PermissionDecision, list[str]]:
    request_payload: Mapping[str, Any] = payload or {}
    reasons: list[str] = []
    permission = get_permission(channel, permissions)
    level = normalize_autonomy_level(autonomy_level)

    if level not in permission.allowed_levels:
        reasons.append(f"autonomy_level_not_allowed:{level.value}")

    secret_paths = find_plaintext_secrets(request_payload)
    if secret_paths:
        reasons.append("plaintext_secret_blocked:" + ",".join(secret_paths))

    if bool(request_payload.get("mass_messaging")) and not permission.allow_mass_messaging:
        reasons.append("mass_messaging_blocked")

    if bool(request_payload.get("browser_automation")) and not permission.allow_browser_automation:
        reasons.append("browser_automation_blocked")

    external_api_used = bool(request_payload.get("external_api_used"))
    if external_api_used and permission.requires_credential_vault:
        vault_ref = request_payload.get("credential_vault_ref")
        if not is_vault_ref(vault_ref):
            reasons.append("credential_vault_required")

    publish_real = bool(request_payload.get("publish_real"))
    if publish_real and not permission.can_publish_real:
        reasons.append("real_publish_not_allowed")

    if reasons:
        return PermissionDecision.DENY, reasons

    if permission.requires_human_review:
        return PermissionDecision.REVIEW_REQUIRED, ["human_review_required"]

    return PermissionDecision.ALLOW, ["permission_allowed"]