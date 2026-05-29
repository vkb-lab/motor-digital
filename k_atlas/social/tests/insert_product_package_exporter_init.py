from pathlib import Path

path = Path("k_atlas/social/campaign_factory/__init__.py")
text = path.read_text(encoding="utf-8")

if '"SocialProductCampaignPackageExporter",' not in text:
    text = text.replace(
        '"SocialOperationBuilder",',
        '"SocialOperationBuilder",\n    "SocialProductCampaignPackageExporter",'
    )

if 'if name == "SocialProductCampaignPackageExporter":' not in text:
    insert = '''
    if name == "SocialProductCampaignPackageExporter":
        from .social_product_campaign_package_exporter import SocialProductCampaignPackageExporter
        return SocialProductCampaignPackageExporter

'''
    marker = '    if name == "AutonomousSocialCampaignRunner":'
    if marker not in text:
        raise RuntimeError("Ponto de insercao nao encontrado em campaign_factory/__init__.py")
    text = text.replace(marker, insert + marker, 1)

path.write_text(text, encoding="utf-8")
print("campaign_factory __init__ atualizado.")
