# -*- coding: utf-8 -*-
"""K-Social Operation Builder.

Builds supervised social operations from JSON request files.
It does not publish content, does not call external APIs and does not operate browsers.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from k_atlas.social.analytics.social_cockpit_adapter import SocialCockpitAdapter
from k_atlas.social.reports.social_autoreporter import SocialAutoReporter
from k_atlas.social.social_orchestrator import SocialOrchestrator


class SocialOperationBuilder:
    """Creates supervised K-Social operations from request JSON files."""

    REQUIRED_FIELDS = {
        "product",
        "market",
        "personas",
        "objective",
        "channels",
        "duration_days",
        "key_messages",
    }

    def __init__(
        self,
        requests_dir: Optional[Path] = None,
        reports_dir: Optional[Path] = None,
    ) -> None:
        base_dir = Path(__file__).resolve().parents[1]
        self.requests_dir = Path(requests_dir) if requests_dir else base_dir / "memory"
        self.reports_dir = Path(reports_dir) if reports_dir else base_dir / "reports"
        self.requests_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _timestamp_slug(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    def _slugify(self, value: str) -> str:
        value = value.lower().strip()
        value = re.sub(r"[^a-z0-9]+", "-", value)
        value = value.strip("-")
        return value or "social-operation"

    def load_request(self, request_path: Path) -> Dict[str, Any]:
        """Load and validate request JSON."""

        path = Path(request_path)

        if not path.exists():
            raise FileNotFoundError(f"Request file not found: {path}")

        with path.open("r", encoding="utf-8-sig") as file:
            request = json.load(file)

        if not isinstance(request, dict):
            raise ValueError("Request JSON must be an object.")

        missing = self.REQUIRED_FIELDS.difference(set(request.keys()))
        if missing:
            missing_list = ", ".join(sorted(missing))
            raise ValueError(f"Missing required fields: {missing_list}")

        if not isinstance(request["personas"], list) or not request["personas"]:
            raise ValueError("personas must be a non-empty list.")

        if not isinstance(request["channels"], list) or not request["channels"]:
            raise ValueError("channels must be a non-empty list.")

        if not isinstance(request["key_messages"], list) or not request["key_messages"]:
            raise ValueError("key_messages must be a non-empty list.")

        if int(request["duration_days"]) <= 0:
            raise ValueError("duration_days must be greater than zero.")

        return request

    def build_operation(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Build a supervised social operation from a validated request."""

        orchestrator = SocialOrchestrator()

        operation = orchestrator.plan_social_operation(
            product=request["product"],
            market=request["market"],
            personas=request["personas"],
            objective=request["objective"],
            channels=request["channels"],
            duration_days=int(request["duration_days"]),
            key_messages=request["key_messages"],
            format_type=request.get("format_type", "reel"),
            brand_tone=request.get("brand_tone", "profissional, claro e direto"),
            region=request.get("region", "Brasil"),
            language=request.get("language", "pt-BR"),
            seasonal_context=request.get("seasonal_context"),
        )

        operation["request_metadata"] = {
            "created_from": "SocialOperationBuilder",
            "built_at": self._now(),
            "request_name": request.get("request_name", "unnamed_request"),
            "owner": request.get("owner", "K-Atlas Operator"),
            "approval_status": "pending_human_review",
        }

        operation["publication_permission"] = False
        operation["external_api_used"] = False
        operation["human_review_required"] = True

        return operation

    def save_operation(self, operation: Dict[str, Any]) -> Path:
        """Save operation report as JSON."""

        audience = operation.get("audience", {})
        product = audience.get("product", "social-operation")
        slug = self._slugify(str(product))
        timestamp = self._timestamp_slug()

        output_path = self.reports_dir / f"operation_{slug}_{timestamp}.json"

        with output_path.open("w", encoding="utf-8-sig") as file:
            json.dump(operation, file, ensure_ascii=False, indent=2)

        return output_path

    def refresh_dashboard_outputs(self) -> Dict[str, Any]:
        """Refresh cockpit snapshot and daily report."""

        adapter = SocialCockpitAdapter(reports_dir=self.reports_dir)
        snapshot = adapter.save_snapshot()

        reporter = SocialAutoReporter(
            snapshot_path=self.reports_dir / "social_dashboard_snapshot.json",
            reports_dir=self.reports_dir,
        )
        daily_report = reporter.run()

        return {
            "snapshot": snapshot,
            "daily_report": daily_report,
        }

    def run_from_request_file(self, request_path: Path) -> Dict[str, Any]:
        """Run the complete operation creation flow."""

        request = self.load_request(Path(request_path))
        operation = self.build_operation(request)
        output_path = self.save_operation(operation)
        dashboard_outputs = self.refresh_dashboard_outputs()

        return {
            "status": "operation_created",
            "operation_file": str(output_path),
            "publication_permission": False,
            "external_api_used": False,
            "human_review_required": True,
            "snapshot_total_operations": dashboard_outputs["snapshot"]["total_operations"],
            "daily_report_total_operations": dashboard_outputs["daily_report"]["summary"]["total_operations"],
        }


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Build a supervised K-Social operation from JSON.")
    parser.add_argument(
        "--request",
        required=True,
        help="Path to the JSON request file.",
    )

    args = parser.parse_args()

    builder = SocialOperationBuilder()
    result = builder.run_from_request_file(Path(args.request))

    print("K-Social operation created.")
    print("Operation file:", result["operation_file"])
    print("Snapshot operations:", result["snapshot_total_operations"])
    print("Daily report operations:", result["daily_report_total_operations"])
    print("Publication permission:", result["publication_permission"])
    print("External API used:", result["external_api_used"])
    print("Human review required:", result["human_review_required"])


if __name__ == "__main__":
    main()
