from pathlib import Path
from datetime import datetime


BASE = Path.cwd()
WORKSPACE = BASE / "k_atlas" / "workspace"


def find_latest_landing():
    files = list(WORKSPACE.glob("**/index.html"))
    if not files:
        return None
    latest_index = sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)[0]
    return latest_index.parent


def evolve_landing(project_path: Path):
    if not project_path or not project_path.exists():
        raise FileNotFoundError("Nenhuma landing encontrada para evoluir.")

    index = project_path / "index.html"
    css = project_path / "style.css"
    js = project_path / "script.js"
    evolution = project_path / "EVOLUCAO.md"

    index.write_text("""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Parada Atlântida | Chopp Grátis</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <header class="hero">
    <nav class="nav">
      <strong>Parada Atlântida</strong>
      <a href="#participar">Participar agora</a>
    </nav>

    <section class="hero-content">
      <span class="badge">Promoção especial</span>
      <h1>Chopp grátis na Parada Atlântida</h1>
      <p>Uma chamada direta para moradores, turistas e amigos da praia aproveitarem uma experiência simples, divertida e memorável.</p>
      <div class="actions">
        <a class="cta" href="#participar">Quero participar</a>
        <a class="secondary" href="#regras">Ver regras</a>
      </div>
    </section>
  </header>

  <main>
    <section class="section intro">
      <p class="eyebrow">Cachoeira do Bom Jesus • Florianópolis</p>
      <h2>A promoção que transforma passagem em parada obrigatória.</h2>
      <p>A proposta é simples: criar movimento, gerar curiosidade e fazer a pessoa sentir que precisa entrar para entender a experiência.</p>
    </section>

    <section class="grid">
      <div class="card">
        <h3>1. Chegue no local</h3>
        <p>Venha até a Parada Atlântida e procure a comunicação da campanha.</p>
      </div>
      <div class="card">
        <h3>2. Confira como funciona</h3>
        <p>A equipe informa as regras e orienta como participar da promoção.</p>
      </div>
      <div class="card">
        <h3>3. Aproveite e compartilhe</h3>
        <p>Curta o momento, chame os amigos e fortaleça a energia da praia.</p>
      </div>
    </section>

    <section id="regras" class="section rules">
      <h2>Regras da promoção</h2>
      <ul>
        <li>Promoção válida conforme disponibilidade e regras internas da campanha.</li>
        <li>Consulte a equipe no local para confirmar participação.</li>
        <li>Ação sujeita a limite diário e horário de funcionamento.</li>
        <li>Consumo responsável. Venda proibida para menores de 18 anos.</li>
      </ul>
    </section>

    <section class="section impact">
      <h2>Por que isso funciona?</h2>
      <p>Porque une curiosidade, benefício imediato e experiência local. A pessoa vê a chamada, entende rápido e sente vontade de entrar.</p>
    </section>

    <section id="participar" class="section cta-box">
      <h2>Está perto? Então passa aqui.</h2>
      <p>Parada Atlântida — Cachoeira do Bom Jesus, Florianópolis.</p>
      <a class="cta" href="https://wa.me/">Falar no WhatsApp</a>
    </section>
  </main>

  <footer>
    <p>Parada Atlântida • Campanha evoluída pelo K-Atlas</p>
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
  background: #061826;
  color: #f8fafc;
}

.hero {
  min-height: 92vh;
  background:
    linear-gradient(135deg, rgba(6,24,38,.96), rgba(0,119,182,.70)),
    radial-gradient(circle at 80% 20%, rgba(255,214,10,.40), transparent 26%),
    radial-gradient(circle at 20% 80%, rgba(46,196,182,.28), transparent 24%);
  padding: 28px;
}

.nav {
  max-width: 1120px;
  margin: auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nav strong {
  font-size: 22px;
  letter-spacing: .5px;
}

.nav a,
.cta {
  background: #ffd60a;
  color: #061826;
  padding: 14px 22px;
  border-radius: 999px;
  font-weight: 800;
  text-decoration: none;
}

.hero-content {
  max-width: 980px;
  margin: 120px auto 0;
}

.badge,
.eyebrow {
  display: inline-block;
  color: #ffd60a;
  background: rgba(255,214,10,.13);
  border: 1px solid rgba(255,214,10,.38);
  padding: 8px 14px;
  border-radius: 999px;
  font-weight: 700;
}

h1 {
  font-size: clamp(46px, 9vw, 104px);
  line-height: .92;
  margin: 28px 0;
}

.hero p {
  max-width: 760px;
  color: #dbeafe;
  font-size: 23px;
}

.actions {
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
  margin-top: 28px;
}

.secondary {
  color: #f8fafc;
  border: 1px solid rgba(255,255,255,.35);
  padding: 14px 22px;
  border-radius: 999px;
  text-decoration: none;
  font-weight: 700;
}

main {
  max-width: 1120px;
  margin: auto;
  padding: 64px 28px;
}

.section {
  margin: 70px 0;
}

.section h2 {
  font-size: clamp(32px, 5vw, 56px);
  line-height: 1;
}

.section p,
li {
  font-size: 18px;
  color: #cbd5e1;
  line-height: 1.65;
}

.grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 18px;
}

.card,
.rules,
.impact {
  background: rgba(255,255,255,.075);
  border: 1px solid rgba(255,255,255,.12);
  padding: 28px;
  border-radius: 24px;
}

.cta-box {
  background: #f8fafc;
  color: #061826;
  padding: 42px;
  border-radius: 28px;
}

.cta-box p {
  color: #334155;
}

footer {
  text-align: center;
  color: #94a3b8;
  padding: 34px;
}

@media (max-width: 820px) {
  .grid {
    grid-template-columns: 1fr;
  }

  .hero-content {
    margin-top: 80px;
  }

  .nav {
    align-items: flex-start;
    gap: 16px;
    flex-direction: column;
  }
}
""", encoding="utf-8")

    js.write_text("""console.log("Landing evoluída pelo K-Atlas");

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

    evolution.write_text(f"""# Evolução aplicada

Data: {datetime.now().isoformat()}

## Melhorias feitas
- Headline comercial mais forte
- Seção de regras da promoção
- CTA principal e secundário
- Estrutura visual mais impactante
- Melhor responsividade mobile
- Seção explicando por que a campanha funciona
- CTA final com WhatsApp

## Próximos ajustes sugeridos
- Inserir logo real da Parada Atlântida
- Inserir fotos reais do local
- Configurar número real do WhatsApp
- Adicionar QR Code
- Adicionar regras definitivas da promoção
- Preparar versão para deploy
""", encoding="utf-8")

    return [index, css, js, evolution]
