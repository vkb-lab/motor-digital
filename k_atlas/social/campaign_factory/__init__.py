# -*- coding: utf-8 -*-
"""Campaign factory module.

Exports CampaignGenerator directly.
SocialOperationBuilder is loaded lazily to avoid circular imports.
"""

from .campaign_generator import CampaignGenerator

__all__ = ["CampaignGenerator", "SocialOperationBuilder"]


def __getattr__(name: str):
    if name == "SocialOperationBuilder":
        from .social_operation_builder import SocialOperationBuilder
        return SocialOperationBuilder

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
