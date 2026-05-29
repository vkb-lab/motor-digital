from pathlib import Path

files = [
    Path("k_atlas/social/analytics/social_cockpit_adapter.py"),
    Path("k_atlas/social/reports/social_autoreporter.py"),
    Path("k_atlas/social/ui/social_cockpit_view.py"),
    Path("k_atlas/social/campaign_factory/social_operation_builder.py"),
]

for path in files:
    text = path.read_text(encoding="utf-8")
    text = text.replace('encoding="utf-8") as file:', 'encoding="utf-8-sig") as file:')
    path.write_text(text, encoding="utf-8")

print("Arquivos corrigidos para leitura utf-8-sig.")
