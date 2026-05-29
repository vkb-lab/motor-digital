from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4

from .approval_policy import ApprovalPolicy, ApprovalStatus
from .audit_log import AuditLog
from .channel_registry import ChannelRegistry, build_default_channel_registry
from .permission_model import normalize_autonomy_level


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def utc_now_iso() -> str:
    return utc_now().isoformat()


def parse_iso_datetime(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None

    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None

    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


class PublishQueue:
    def __init__(
        self,
        path: str | Path = "memory/social_publish_queue.json",
        registry: ChannelRegistry | None = None,
        audit_log: AuditLog | None = None,
        approval_policy: ApprovalPolicy | None = None,
    ) -> None:
        self.path = Path(path)
        self.registry = registry or build_default_channel_registry()
        self.audit_log = audit_log or AuditLog()
        self.approval_policy = approval_policy or ApprovalPolicy()

    def load(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []

        with self.path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, list):
            raise ValueError("Publish queue corrompida: esperado uma lista JSON")

        return data

    def save(self, items: list[dict[str, Any]]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as file:
            json.dump(items, file, ensure_ascii=False, indent=2, sort_keys=True)

    def enqueue(self, payload: Mapping[str, Any], actor: str = "k_social_operator") -> dict[str, Any]:
        request = dict(payload)
        request.setdefault("request_id", str(uuid4()))
        request.setdefault("created_at", utc_now_iso())

        if "channel" not in request:
            raise ValueError("Payload precisa conter channel")

        if "autonomy_level" not in request:
            raise ValueError("Payload precisa conter autonomy_level")

        request["autonomy_level"] = normalize_autonomy_level(request["autonomy_level"]).value
        channel = self.registry.get(str(request["channel"]))
        permission = channel.permission

        approval_result = self.approval_policy.evaluate(request, permission)
        request["status"] = approval_result.status.value
        request["approval"] = approval_result.to_dict()
        request["adapter_name"] = channel.adapter_name

        current_items = self.load()
        spam_reasons = self._spam_guard_reasons(current_items, request, permission.max_posts_per_hour, permission.max_posts_per_day)
        if spam_reasons:
            request["status"] = ApprovalStatus.BLOCKED.value
            request["approval"] = {
                "status": ApprovalStatus.BLOCKED.value,
                "reasons": approval_result.reasons + spam_reasons,
                "allowed_actions": [],
            }

        current_items.append(request)
        self.save(current_items)

        self.audit_log.write_event(
            action="publish_queue.enqueue",
            status=request["status"],
            actor=actor,
            payload=request,
            reasons=request["approval"]["reasons"],
        )

        return request

    def _spam_guard_reasons(
        self,
        existing_items: list[dict[str, Any]],
        request: Mapping[str, Any],
        max_posts_per_hour: int,
        max_posts_per_day: int,
    ) -> list[str]:
        now = utc_now()
        channel = str(request.get("channel"))
        one_hour_ago = now - timedelta(hours=1)
        one_day_ago = now - timedelta(days=1)

        hourly_count = 0
        daily_count = 0

        for item in existing_items:
            if str(item.get("channel")) != channel:
                continue

            if item.get("status") == ApprovalStatus.BLOCKED.value:
                continue

            created_at = parse_iso_datetime(item.get("created_at"))
            if created_at is None:
                continue

            if created_at >= one_hour_ago:
                hourly_count += 1
            if created_at >= one_day_ago:
                daily_count += 1

        reasons: list[str] = []
        if hourly_count >= max_posts_per_hour:
            reasons.append("spam_guard_hourly_limit_reached")
        if daily_count >= max_posts_per_day:
            reasons.append("spam_guard_daily_limit_reached")

        return reasons