from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping

from .permission_model import (
    AutonomyLevel,
    ChannelPermission,
    PermissionDecision,
    evaluate_permission,
    normalize_autonomy_level,
)


class ApprovalStatus(str, Enum):
    BLOCKED = "blocked"
    APPROVED_FOR_DRY_RUN = "approved_for_dry_run"
    PENDING_HUMAN_REVIEW = "pending_human_review"
    APPROVED_FOR_TEST_PAGE = "approved_for_test_page"
    APPROVED_FOR_DRAFT = "approved_for_draft"
    APPROVED_FOR_LIMITED_PUBLISH = "approved_for_limited_publish"


@dataclass(frozen=True)
class ApprovalResult:
    status: ApprovalStatus
    reasons: list[str] = field(default_factory=list)
    allowed_actions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "reasons": list(self.reasons),
            "allowed_actions": list(self.allowed_actions),
        }


def has_human_approval(payload: Mapping[str, Any]) -> bool:
    approval = payload.get("human_approval") or {}
    if not isinstance(approval, Mapping):
        return False

    return bool(approval.get("approved")) and bool(str(approval.get("reviewer", "")).strip())


class ApprovalPolicy:
    def evaluate(
        self,
        payload: Mapping[str, Any],
        permission: ChannelPermission,
    ) -> ApprovalResult:
        channel = str(payload.get("channel") or permission.channel)
        level = normalize_autonomy_level(payload.get("autonomy_level", AutonomyLevel.LEVEL_0_STRATEGY.value))

        decision, permission_reasons = evaluate_permission(
            channel=channel,
            autonomy_level=level,
            payload=payload,
            permissions={permission.channel: permission},
        )

        if decision == PermissionDecision.DENY:
            return ApprovalResult(
                status=ApprovalStatus.BLOCKED,
                reasons=permission_reasons,
                allowed_actions=[],
            )

        if level in (AutonomyLevel.LEVEL_0_STRATEGY, AutonomyLevel.LEVEL_1_CAMPAIGN_PACKAGE):
            return ApprovalResult(
                status=ApprovalStatus.APPROVED_FOR_DRY_RUN,
                reasons=["low_risk_strategy_or_package"],
                allowed_actions=["dry_run"],
            )

        if level == AutonomyLevel.LEVEL_2_SANDBOX_PAGE:
            if permission.can_test_page:
                if permission.requires_human_review and not has_human_approval(payload):
                    return ApprovalResult(
                        status=ApprovalStatus.PENDING_HUMAN_REVIEW,
                        reasons=["human_review_required_for_test_page"],
                        allowed_actions=["review"],
                    )
                return ApprovalResult(
                    status=ApprovalStatus.APPROVED_FOR_TEST_PAGE,
                    reasons=["sandbox_page_allowed"],
                    allowed_actions=["dry_run", "test_page_publish"],
                )

            return ApprovalResult(
                status=ApprovalStatus.APPROVED_FOR_DRY_RUN,
                reasons=["test_page_not_enabled_for_channel"],
                allowed_actions=["dry_run"],
            )

        if level == AutonomyLevel.LEVEL_2_5_TEST_ADAPTER:
            if permission.requires_human_review and not has_human_approval(payload):
                return ApprovalResult(
                    status=ApprovalStatus.PENDING_HUMAN_REVIEW,
                    reasons=["human_review_required_for_test_adapter"],
                    allowed_actions=["review", "dry_run"],
                )

            return ApprovalResult(
                status=ApprovalStatus.APPROVED_FOR_DRAFT if permission.can_schedule_draft else ApprovalStatus.APPROVED_FOR_TEST_PAGE,
                reasons=["test_adapter_gate_passed"],
                allowed_actions=["dry_run", "sandbox_adapter"],
            )

        if level == AutonomyLevel.LEVEL_3_SCHEDULE_DRAFT:
            if not permission.can_schedule_draft:
                return ApprovalResult(
                    status=ApprovalStatus.BLOCKED,
                    reasons=["schedule_draft_not_allowed"],
                    allowed_actions=[],
                )
            if permission.requires_human_review and not has_human_approval(payload):
                return ApprovalResult(
                    status=ApprovalStatus.PENDING_HUMAN_REVIEW,
                    reasons=["human_review_required_for_scheduling"],
                    allowed_actions=["review"],
                )
            return ApprovalResult(
                status=ApprovalStatus.APPROVED_FOR_DRAFT,
                reasons=["draft_scheduling_allowed"],
                allowed_actions=["dry_run", "schedule_draft"],
            )

        if level == AutonomyLevel.LEVEL_4_LIMITED_REAL_PUBLISH:
            if not permission.can_publish_real:
                return ApprovalResult(
                    status=ApprovalStatus.BLOCKED,
                    reasons=["limited_real_publish_not_enabled"],
                    allowed_actions=[],
                )
            if permission.requires_human_review and not has_human_approval(payload):
                return ApprovalResult(
                    status=ApprovalStatus.PENDING_HUMAN_REVIEW,
                    reasons=["human_review_required_for_limited_publish"],
                    allowed_actions=["review"],
                )
            return ApprovalResult(
                status=ApprovalStatus.APPROVED_FOR_LIMITED_PUBLISH,
                reasons=["limited_publish_allowed_by_policy"],
                allowed_actions=["publish_real_limited"],
            )

        return ApprovalResult(
            status=ApprovalStatus.BLOCKED,
            reasons=["level_5_requires_dedicated_governance_module"],
            allowed_actions=[],
        )