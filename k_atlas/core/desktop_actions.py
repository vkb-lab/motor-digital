import webbrowser
from pathlib import Path
from datetime import datetime


def open_url(url: str):
    webbrowser.open(url)
    return f"Navegador aberto em: {url}"


def scan_desktop():
    desktop = Path.home() / "Desktop"
    items = []
    for item in desktop.iterdir():
        items.append({
            "name": item.name,
            "path": str(item),
            "type": "folder" if item.is_dir() else "file",
            "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat()
        })
    return items


def create_desktop_report():
    reports = Path.cwd() / "k_atlas" / "reports"
    reports.mkdir(parents=True, exist_ok=True)

    items = scan_desktop()
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = reports / f"desktop_report_{stamp}.md"

    lines = ["# Relatório da Área de Trabalho", ""]
    for item in items:
        lines.append(f"- {item['name']} | {item['type']} | {item['path']}")

    out.write_text("\n".join(lines), encoding="utf-8")
    return f"Relatório criado em: {out}"


def suggest_desktop_organization():
    reports = Path.cwd() / "k_atlas" / "reports"
    reports.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = reports / f"desktop_organization_plan_{stamp}.md"

    content = """# Plano de Organização da Área de Trabalho

## Regra principal
Não mover nada automaticamente sem confirmação.

## Sugestão de categorias
- Projetos
- Imagens
- PDFs
- Documentos
- Instalações
- Zips
- Atalhos
- Outros

## Próximo passo
Revisar este plano antes de qualquer movimentação.
"""
    out.write_text(content, encoding="utf-8")
    return f"Plano de organização criado em: {out}"
