# -*- coding: utf-8 -*-
"""K-Social UI package."""

from .social_approval_view import render_social_approval_queue
from .social_campaign_package_approval_view import render_social_campaign_package_approval_queue
from .social_campaign_packages_view import (
    load_campaign_package_index,
    load_campaign_packages,
    render_social_campaign_packages,
)
from .social_command_center_view import render_social_command_center
from .social_content_refinement_view import render_social_content_refinement_queue
from .social_cockpit_view import (
    build_social_cockpit_summary,
    build_social_report_summary,
    load_social_report,
    load_social_snapshot,
    render_social_cockpit,
    render_social_operation_builder,
)
from .social_latest_campaign_view import (
    load_latest_manual_approved_campaign,
    render_latest_manual_approved_campaign,
)
from .social_refinement_outputs_view import (
    load_refinement_outputs,
    render_social_refinement_outputs,
)

__all__ = [
    "build_social_cockpit_summary",
    "build_social_report_summary",
    "load_campaign_package_index",
    "load_campaign_packages",
    "load_latest_manual_approved_campaign",
    "load_refinement_outputs",
    "load_social_report",
    "load_social_snapshot",
    "render_latest_manual_approved_campaign",
    "render_social_approval_queue",
    "render_social_campaign_package_approval_queue",
    "render_social_campaign_packages",
    "render_social_command_center",
    "render_social_content_refinement_queue",
    "render_social_cockpit",
    "render_social_operation_builder",
    "render_social_refinement_outputs",
]
