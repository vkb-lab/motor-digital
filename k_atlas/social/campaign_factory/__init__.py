# -*- coding: utf-8 -*-
"""Campaign factory module.

Exports CampaignGenerator directly and SocialOperationBuilder lazily.
This avoids circular imports between SocialOrchestrator and SocialOperationBuilder.
"""

from .campaign_generator import CampaignGenerator

__all__ = ["CampaignGenerator", "SocialOperationBuilder"]


def __getattr__(name: str):
    if name == "SocialOperationBuilder":
        from .social_operation_builder import SocialOperationBuilder

        return SocialOperationBuilder

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
