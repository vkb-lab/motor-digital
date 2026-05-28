# -*- coding: utf-8 -*-
"""Main orchestrator for K-Social Intelligence System.

Coordinates audience intelligence, campaign factory, creative engine and audit.
It only generates supervised strategy artifacts.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from k_atlas.social.audit import SocialAuditor
from k_atlas.social.audience_intelligence import AudienceMapper
from k_atlas.social.campaign_factory import CampaignGenerator
from k_atlas.social.creative_engine import CreativeBriefGenerator


class SocialOrchestrator:
    """High-level interface for supervised social intelligence operations."""

    def __init__(self, memory_dir: Optional[Path] = None) -> None:
        self.audience_mapper = AudienceMapper(memory_dir=memory_dir)
        self.creative_brief_generator = CreativeBriefGenerator()
        self.campaign_generator = CampaignGenerator()
        self.social_auditor = SocialAuditor()

    def create_audience_map(
        self,
        product: str,
        market: str,
        personas: List[str],
        region: str = "Brasil",
        language: str = "pt-BR",
    ) -> Dict[str, Any]:
        return self.audience_mapper.map_audience(
            product=product,
            market=market,
            personas=personas,
            region=region,
            language=language,
        )

    def create_creative_brief(
        self,
        product: str,
        objective: str,
        target_audience: List[str],
        key_messages: List[str],
        format_type: str = "reel",
        brand_tone: str = "profissional, claro e direto",
        seasonal_context: Optional[str] = None,
    ) -> Dict[str, Any]:
        return self.creative_brief_generator.generate_brief(
            product=product,
            objective=objective,
            target_audience=target_audience,
            key_messages=key_messages,
            format_type=format_type,
            brand_tone=brand_tone,
            seasonal_context=seasonal_context,
        )

    def create_campaign(
        self,
        objective: str,
        segments: List[Dict[str, Any]],
        channels: List[str],
        duration_days: int,
        key_messages: List[str],
        campaign_name: str = "K-Social Campaign Draft",
        seasonal_context: Optional[str] = None,
    ) -> Dict[str, Any]:
        return self.campaign_generator.generate_campaign(
            objective=objective,
            segments=segments,
            channels=channels,
            duration_days=duration_days,
            key_messages=key_messages,
            campaign_name=campaign_name,
            seasonal_context=seasonal_context,
        )

    def audit_campaign(self, campaign: Dict[str, Any]) -> Dict[str, Any]:
        return self.social_auditor.audit_campaign(campaign)

    def plan_social_operation(
        self,
        product: str,
        market: str,
        personas: List[str],
        objective: str,
        channels: List[str],
        duration_days: int,
        key_messages: List[str],
        format_type: str = "reel",
        brand_tone: str = "profissional, claro e direto",
        region: str = "Brasil",
        language: str = "pt-BR",
        seasonal_context: Optional[str] = None,
    ) -> Dict[str, Any]:
        audience = self.create_audience_map(
            product=product,
            market=market,
            personas=personas,
            region=region,
            language=language,
        )

        target_audience = [segment["persona"] for segment in audience["segments"]]

        creative_brief = self.create_creative_brief(
            product=product,
            objective=objective,
            target_audience=target_audience,
            key_messages=key_messages,
            format_type=format_type,
            brand_tone=brand_tone,
            seasonal_context=seasonal_context,
        )

        campaign = self.create_campaign(
            objective=objective,
            segments=audience["segments"],
            channels=channels,
            duration_days=duration_days,
            key_messages=key_messages,
            campaign_name=f"{product} - {objective}",
            seasonal_context=seasonal_context,
        )

        audit = self.audit_campaign(campaign)

        return {
            "system": "K-Social Intelligence System",
            "operation_status": "draft_ready_for_human_review",
            "audience": audience,
            "creative_brief": creative_brief,
            "campaign": campaign,
            "audit": audit,
            "human_review_required": True,
            "publication_permission": False,
            "external_api_used": False,
        }
