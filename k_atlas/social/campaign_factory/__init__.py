# -*- coding: utf-8 -*-
"""Campaign factory module.

Exports CampaignGenerator directly.
Other builders are loaded lazily to avoid circular imports.
"""

from .campaign_generator import CampaignGenerator

__all__ = [
    "CampaignGenerator",
    "SocialCampaignPackageExporter",
    "SocialCampaignPackageIndexer",
    "SocialOperationBuilder",
]


def __getattr__(name: str):
    if name == "SocialOperationBuilder":
        from .social_operation_builder import SocialOperationBuilder
        return SocialOperationBuilder

    if name == "SocialCampaignPackageExporter":
        from .social_campaign_package_exporter import SocialCampaignPackageExporter
        return SocialCampaignPackageExporter

    if name == "SocialCampaignPackageIndexer":
        from .social_campaign_package_indexer import SocialCampaignPackageIndexer
        return SocialCampaignPackageIndexer

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
