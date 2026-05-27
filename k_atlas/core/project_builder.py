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


def infer_landing_context(command: str):
    low = command.lower()

    context = {
        "brand": "Projeto K-Atlas",
        "headline": "Oferta especial criada pelo K-Atlas",
        "subheadline": "Uma experiência simples, direta e pronta para conversão.",
        "offer": "Oferta especial por tempo limitado",
        "cta": "Quero saber mais",
        "whatsapp": "#",
        "location": "Local a definir",
        "audience": "clientes e visitantes",
        "theme": "digital"
    }

    if "parada atlântida" in low or "parada atlantida" in low:
        context.update({
            "brand": "Parada Atlântida",
            "headline": "Chopp grátis é na Parada Atlântida",
            "subheadline": "Entre no clima da praia, aproveite a promoção e viva a experiência da Parada Atlântida.",
            "offer": "Promoção especial de chopp grátis conforme regras da campanha",
            "cta": "Quero participar da promoção",
            "location": "Cachoeira do Bom Jesus, Florianópolis",
            "audience": "moradores, turistas e amigos da praia",
            "theme": "beach"
        })

    if "chopp" in low:
        context["offer"] = "Promoção de chopp grátis para atrair movimento e fortalecer a experiência no local."

    return context


def create_basic_web_files(project_path: Path, command: str = ""):
    context = infer_landing_context(command)

    index = project_path / "index.html"
    css = project_path / "style.css"
    js = project_path / "script.js"
    copy = project_path / "copy.md"
    briefing = project_path / "briefing.md"
    assets = project_path / "assets.md"

    index.write_text(f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{context['brand']} | Promoção</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <header class="hero">
    <nav class="nav">
      <strong>{context['brand']}</strong>
      <a href="#participar">Participar</a>
    </nav>

    <section class="hero-content">
      <span class="badge">Promoção especial</span>
      <h1>{context['headline']}</h1>
      <p>{context['subheadline']}</p>
      <a class="cta" href="#participar">{context['cta']}</a>
    </section>
  </header>

  <main>
    <section class="section">
      <h2>A oferta</h2>
      <p>{context['offer']}</p>
    </section>

    <section class="grid">
      <div class="card">
        <h3>1. Chegue no local</h3>
        <p>Visite a {context['brand']} e entre no clima da campanha.</p>
      </div>
      <div class="card">
        <h3>2. Confira as regras</h3>
        <p>A equipe informa como participar e aproveitar o benefício.</p>
      </div>
      <div class="card">
        <h3>3. Aproveite</h3>
        <p>Curta a experiência, compartilhe e volte com os amigos.</p>
      </div>
    </section>

    <section class="section highlight">
      <h2>Por que participar?</h2>
      <ul>
        <li>Experiência de praia com energia positiva.</li>
        <li>Promoção pensada para moradores e turistas.</li>
        <li>Ambiente simples, direto e acolhedor.</li>
        <li>Boa oportunidade para conhecer a {context['brand']}.</li>
      </ul>
    </section>

    <section id="participar" class="section cta-box">
      <h2>Quer participar?</h2>
      <p>Venha até a {context['brand']} em {context['location']}.</p>
      <a class="cta" href="{context['whatsapp']}">{context['cta']}</a>
    </section>
  </main>

  <footer>
    <p>{context['brand']} — campanha criada com apoio do K-Atlas.</p>
  </footer>

  <script src="script.js"></script>
</body>
</html>
""", encoding="utf-8")

    css.write_text("""* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: Arial, Helvetica, sans-serif;
  background: #071827;
  color: #f8fafc;
}

.hero {
  min-height: 90vh;
  background:
    linear-gradient(135deg, rgba(7,24,39,.95), rgba(0,119,182,.75)),
    radial-gradient(circle at top right, rgba(255,214,10,.35), transparent 30%);
  padding: 28px;
}

.nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1120px;
  margin: auto;
}

.nav a {
  color: #071827;
  background: #ffd60a;
  padding: 10px 18px;
  border-radius: 999px;
  text-decoration: none;
  font-weight: bold;
}

.hero-content {
  max-width: 900px;
  margin: 120px auto 0;
}

.badge {
  background: rgba(255,214,10,.18);
  border: 1px solid rgba(255,214,10,.45);
  color: #ffd60a;
  padding: 8px 14px;
  border-radius: 999px;
  font-weight: bold;
}

h1 {
  font-size: clamp(42px, 8vw, 88px);
  line-height: .95;
  margin: 28px 0;
}

.hero p {
  font-size: 22px;
  max-width: 680px;
  color: #dbeafe;
}

.cta {
  display: inline-block;
  margin-top: 22px;
  background: #ffd60a;
  color: #071827;
  padding: 16px 24px;
  border-radius: 14px;
  font-weight: bold;
  text-decoration: none;
}

main {
  max-width: 1120px;
  margin: auto;
  padding: 60px 28px;
}

.section {
  margin: 60px 0;
}

.section h2 {
  font-size: 36px;
}

.grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 18px;
}

.card {
  background: rgba(255,255,255,.08);
  border: 1px solid rgba(255,255,255,.12);
  padding: 24px;
  border-radius: 18px;
}

.highlight {
  background: rgba(0,119,182,.25);
  padding: 30px;
  border-radius: 20px;
}

.cta-box {
  background: #f8fafc;
  color: #071827;
  padding: 40px;
  border-radius: 24px;
}

footer {
  text-align: center;
  padding: 30px;
  color: #94a3b8;
}

@media (max-width: 800px) {
  .grid {
    grid-template-columns: 1fr;
  }

  .hero-content {
    margin-top: 80px;
  }
}
""", encoding="utf-8")

    js.write_text("""console.log("Landing criada pelo K-Atlas");

document.querySelectorAll('a[href^="#"]').forEach((link) => {
  link.addEventListener("click", function(event) {
    const target = document.querySelector(this.getAttribute("href"));
    if (target) {
      event.preventDefault();
      target.scrollIntoView({ behavior: "smooth" });
    }
  });
});
""", encoding="utf-8")

    copy.write_text(f"""# Copy da Landing

## Headline
{context['headline']}

## Subheadline
{context['subheadline']}

## Oferta
{context['offer']}

## CTA
{context['cta']}

## Público
{context['audience']}

## Local
{context['location']}
""", encoding="utf-8")

    briefing.write_text(f"""# Briefing da Landing

## Pedido original
{command}

## Marca
{context['brand']}

## Objetivo
Criar uma landing page simples e direta para apresentar a promoção e gerar ação.

## Estrutura
- Hero com chamada forte
- Oferta
- Como participar
- Benefícios
- CTA final

## Observação
Esta é uma primeira versão gerada pelo K-Atlas. Pode ser refinada com identidade visual, imagens reais, regras detalhadas e WhatsApp.
""", encoding="utf-8")

    assets.write_text("""# Assets sugeridos

## Imagens
- Foto da fachada/local
- Foto do chopp/produto
- Logo da marca
- Elementos de praia
- QR Code para WhatsApp ou campanha

## Cores sugeridas
- Azul profundo
- Amarelo solar
- Branco
- Verde/turquesa

## Próximos ajustes
- Inserir logo real
- Inserir regras da promoção
- Inserir link real do WhatsApp
- Inserir imagens otimizadas
""", encoding="utf-8")

    return [index, css, js, copy, briefing, assets]


def create_architecture_doc(project_path: Path, command: str):
    doc = project_path / "ARQUITETURA.md"
    doc.write_text(
        f"""# Arquitetura inicial

## Pedido
{command}

## Stack sugerida
- HTML/CSS/JS para versão rápida
- Next.js para versão escalável
- Supabase para cadastros/campanhas
- GitHub para versionamento
- Vercel para deploy

## Módulos futuros
- Formulário de captura
- Integração WhatsApp
- Pixel Meta
- Analytics
- Painel de campanha
""",
        encoding="utf-8"
    )
    return doc
