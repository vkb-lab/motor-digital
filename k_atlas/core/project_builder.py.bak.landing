from pathlib import Path
from datetime import datetime
import re


def safe_slug(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9áàâãéêíóôõúç\s_-]", "", text)
    text = text.replace(" ", "_")
    return text[:60] or "projeto_k_atlas"


def create_project_folder(command: str, project_type: str = "project"):
    workspace = Path.cwd() / "k_atlas" / "workspace"
    workspace.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name = safe_slug(command)
    project_path = workspace / f"{name}_{stamp}"

    project_path.mkdir(parents=True, exist_ok=True)

    readme = project_path / "README.md"
    readme.write_text(
        f"""# Projeto K-Atlas

## Tipo
{project_type}

## Pedido original
{command}

## Criado em
{datetime.now().isoformat()}

## Status
Estrutura inicial criada pelo K-Atlas Local.
""",
        encoding="utf-8"
    )

    return project_path


def create_basic_web_files(project_path: Path):
    index = project_path / "index.html"
    css = project_path / "style.css"
    js = project_path / "script.js"

    index.write_text("""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <title>K-Atlas Projeto</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <main>
    <h1>Projeto criado pelo K-Atlas</h1>
    <p>Base inicial pronta para evolução.</p>
  </main>
  <script src="script.js"></script>
</body>
</html>
""", encoding="utf-8")

    css.write_text("""body {
  font-family: Arial, sans-serif;
  background: #0f172a;
  color: #f8fafc;
  margin: 0;
  padding: 40px;
}

main {
  max-width: 900px;
  margin: auto;
}
""", encoding="utf-8")

    js.write_text("""console.log("K-Atlas projeto iniciado");
""", encoding="utf-8")

    return [index, css, js]


def create_architecture_doc(project_path: Path, command: str):
    doc = project_path / "ARQUITETURA.md"
    doc.write_text(
        f"""# Arquitetura inicial

## Pedido
{command}

## Stack sugerida
- Next.js ou React
- Supabase
- GitHub
- Tailwind CSS

## Módulos iniciais
- Dashboard
- Login
- Projetos
- Prompt Center
- Banco de dados
- Logs
""",
        encoding="utf-8"
    )
    return doc
