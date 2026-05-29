from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4

from .approval_policy import ApprovalStatus, ApprovalPolicy
from .audit_log import AuditLog, sanitize_for_audit, utc_now_iso
from .channel_registry import build_default_channel_registry


class TestPageAdapter:
    def __init__(
        self,
        output_path: str | Path = "reports/social_test_page_posts.jsonl",
        audit_log: AuditLog | None = None,
        approval_policy: ApprovalPolicy | None = None,
    ) -> None:
        self.output_path = Path(output_path)
        self.audit_log = audit_log or AuditLog()
        self.approval_policy = approval_policy or ApprovalPolicy()
        self.registry = build_default_channel_registry()

    def publish(self, payload: Mapping[str, Any], actor: str = "k_social_operator") -> dict[str, Any]:
        if str(payload.get("channel")) != "test_page":
            raise ValueError("TestPageAdapter aceita somente channel='test_page'")

        permission = self.registry.get("test_page").permission
        approval = self.approval_policy.evaluate(payload, permission)

        if approval.status != ApprovalStatus.APPROVED_FOR_TEST_PAGE:
            status = approval.status.value
            self.audit_log.write_event(
                action="test_page_adapter.publish",
                status=status,
                actor=actor,
                payload=payload,
                reasons=approval.reasons,
            )
            return {
                "ok": False,
                "status": status,
                "adapter": "test_page_adapter",
                "side_effects": "none",
                "reasons": approval.reasons,
            }

        record = {
            "test_post_id": str(uuid4()),
            "timestamp": utc_now_iso(),
            "channel": "test_page",
            "campaign_id": payload.get("campaign_id"),
            "content": sanitize_for_audit(payload.get("content", {})),
            "metadata": sanitize_for_audit(payload.get("metadata", {})),
            "side_effects": "local_jsonl_only",
        }

        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        with self.output_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

        self.audit_log.write_event(
            action="test_page_adapter.publish",
            status="published_to_test_page",
            actor=actor,
            payload=record,
            reasons=approval.reasons,
        )

        return {
            "ok": True,
            "status": "published_to_test_page",
            "adapter": "test_page_adapter",
            "side_effects": "local_jsonl_only",
            "record": record,
            "reasons": approval.reasons,
        }