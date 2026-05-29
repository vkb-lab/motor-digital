from pathlib import Path

view_path = Path("k_atlas/social/ui/social_campaign_packages_view.py")
text = view_path.read_text(encoding="utf-8")

if "def load_campaign_packages(" not in text:
    marker = "def render_social_campaign_packages() -> None:"
    compatibility_function = '''
def load_campaign_packages(packages_dir: Optional[Path] = None) -> Dict[str, Any]:
    """Backward-compatible alias for older imports."""

    return load_campaign_package_index(packages_dir=packages_dir)


'''

    if marker not in text:
        raise RuntimeError("Ponto de insercao nao encontrado em social_campaign_packages_view.py")

    text = text.replace(marker, compatibility_function + marker, 1)
    view_path.write_text(text, encoding="utf-8")

init_path = Path("k_atlas/social/ui/__init__.py")
init_text = init_path.read_text(encoding="utf-8")

init_text = init_text.replace(
    "load_campaign_package_index,",
    "load_campaign_package_index,\n    load_campaign_packages,"
)

if '"load_campaign_packages",' not in init_text:
    init_text = init_text.replace(
        '"load_campaign_package_index",',
        '"load_campaign_package_index",\n    "load_campaign_packages",'
    )

init_path.write_text(init_text, encoding="utf-8")

print("Compatibilidade load_campaign_packages corrigida.")
