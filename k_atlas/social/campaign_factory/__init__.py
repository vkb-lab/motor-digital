# -*- coding: utf-8 -*-
"""Campaign factory module.

Exports CampaignGenerator directly.
Other builders are loaded lazily to avoid circular imports.
"""

from .campaign_generator import CampaignGenerator

__all__ = [
    "AutonomousSocialCampaignRunner",
    "CampaignGenerator",
    "SocialCampaignPackageExporter",
    "SocialCampaignPackageIndexer",
    "SocialOperationBuilder",
    "SocialProductCampaignPackageExporter",
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


    if name == "SocialProductCampaignPackageExporter":
        from .social_product_campaign_package_exporter import SocialProductCampaignPackageExporter
        return SocialProductCampaignPackageExporter

    if name == "AutonomousSocialCampaignRunner":
        from .autonomous_social_campaign_runner import AutonomousSocialCampaignRunner
        return AutonomousSocialCampaignRunner

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
