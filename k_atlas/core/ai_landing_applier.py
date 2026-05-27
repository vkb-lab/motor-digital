from pathlib import Path
from datetime import datetime


def apply_ai_landing_plan(landing_path: str | Path, plan_path: str | Path | None = None):
    landing = Path(landing_path)

    if not landing.exists():
        raise FileNotFoundError(f"Landing não encontrada: {landing}")

    index = landing / "index.html"
    css = landing / "style.css"
    js = landing / "script.js"
    applied = landing / "AI_APPLIED.md"

    plan_text = ""
    if plan_path:
        plan_file = Path(plan_path)
        if plan_file.exists():
            plan_text = plan_file.read_text(encoding="utf-8", errors="ignore")

    index.write_text("""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Parada Atlântida | Promoção Chopp Grátis</title>
  <meta name="description" content="Promoção especial da Parada Atlântida em Cachoeira do Bom Jesus. Chopp grátis, experiência de praia e chamada rápida para WhatsApp.">
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <header class="hero">
    <nav class="nav">
      <strong>Parada Atlântida</strong>
      <a href="#whatsapp">WhatsApp</a>
    </nav>

    <section class="hero-content">
      <span class="badge">Promoção por tempo limitado</span>
      <h1>Chopp grátis na Parada Atlântida</h1>
      <p>Está na Cachoeira do Bom Jesus? Passe aqui, veja as regras da campanha e aproveite uma experiência leve, divertida e com clima de praia.</p>

      <div class="actions">
        <a class="cta" href="#whatsapp">Quero participar</a>
        <a class="secondary" href="#regras">Ver regras</a>
      </div>
    </section>
  </header>

  <main>
    <section class="section proof">
      <p class="eyebrow">Cachoeira do Bom Jesus • Florianópolis</p>
      <h2>Uma parada rápida pode virar o melhor momento do seu dia.</h2>
      <p>A campanha foi pensada para gerar curiosidade, movimento e conversão direta pelo WhatsApp e pelo fluxo presencial.</p>
    </section>

    <section class="grid">
      <article class="card">
        <span>01</span>
        <h3>Veja a campanha</h3>
        <p>Entre na Parada Atlântida e confira a comunicação da promoção.</p>
      </article>

      <article class="card">
        <span>02</span>
        <h3>Fale com a equipe</h3>
        <p>Confirme as regras, disponibilidade e como participar no dia.</p>
      </article>

      <article class="card">
        <span>03</span>
        <h3>Aproveite com os amigos</h3>
        <p>Curta o clima da praia, compartilhe e volte quando quiser.</p>
      </article>
    </section>

    <section id="regras" class="section rules">
      <h2>Regras importantes</h2>
      <ul>
        <li>Promoção sujeita a disponibilidade e limite diário.</li>
        <li>Consulte a equipe no local para confirmar as regras vigentes.</li>
        <li>Campanha válida apenas durante o período definido pela operação.</li>
        <li>Consumo responsável. Venda proibida para menores de 18 anos.</li>
      </ul>
    </section>

    <section class="section conversion">
      <h2>Por que passar aqui?</h2>
      <div class="conversion-grid">
        <div>
          <h3>Benefício imediato</h3>
          <p>Uma chamada simples, clara e fácil de entender.</p>
        </div>
        <div>
          <h3>Experiência local</h3>
          <p>Clima de praia, atendimento próximo e ponto estratégico.</p>
        </div>
        <div>
          <h3>WhatsApp direto</h3>
          <p>Você pode tirar dúvidas e confirmar detalhes antes de ir.</p>
        </div>
      </div>
    </section>

    <section id="whatsapp" class="section cta-box">
      <h2>Quer confirmar a promoção?</h2>
      <p>Chame no WhatsApp ou venha direto até a Parada Atlântida.</p>
      <a class="cta" href="https://wa.me/" target="_blank" rel="noopener">Chamar no WhatsApp</a>
    </section>
  </main>

  <footer>
    <p>Parada Atlântida • Landing evoluída pelo K-Atlas AI Brain</p>
  </footer>

  <script src="script.js"></script>
</body>
</html>
""", encoding="utf-8")

    css.write_text("""* {
  box-sizing: border-box;
}

html {
  scroll-behavior: smooth;
}

body {
  margin: 0;
  font-family: Arial, Helvetica, sans-serif;
  background: #061826;
  color: #f8fafc;
}

.hero {
  min-height: 94vh;
  padding: 28px;
  background:
    linear-gradient(135deg, rgba(6,24,38,.97), rgba(0,119,182,.74)),
    radial-gradient(circle at 82% 18%, rgba(255,214,10,.45), transparent 24%),
    radial-gradient(circle at 18% 78%, rgba(46,196,182,.30), transparent 28%);
}

.nav {
  max-width: 1140px;
  margin: auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nav strong {
  font-size: 23px;
  letter-spacing: .8px;
}

.nav a,
.cta {
  background: #ffd60a;
  color: #061826;
  padding: 14px 22px;
  border-radius: 999px;
  font-weight: 900;
  text-decoration: none;
  box-shadow: 0 12px 30px rgba(255,214,10,.22);
}

.hero-content {
  max-width: 980px;
  margin: 118px auto 0;
}

.badge,
.eyebrow {
  display: inline-block;
  color: #ffd60a;
  background: rgba(255,214,10,.13);
  border: 1px solid rgba(255,214,10,.42);
  padding: 9px 15px;
  border-radius: 999px;
  font-weight: 800;
}

h1 {
  font-size: clamp(48px, 9vw, 108px);
  line-height: .9;
  margin: 28px 0;
  letter-spacing: -3px;
}

.hero p {
  max-width: 760px;
  color: #dbeafe;
  font-size: 23px;
  line-height: 1.5;
}

.actions {
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
  margin-top: 30px;
}

.secondary {
  color: #f8fafc;
  border: 1px solid rgba(255,255,255,.35);
  padding: 14px 22px;
  border-radius: 999px;
  text-decoration: none;
  font-weight: 800;
}

main {
  max-width: 1140px;
  margin: auto;
  padding: 68px 28px;
}

.section {
  margin: 74px 0;
}

.section h2 {
  font-size: clamp(34px, 5vw, 58px);
  line-height: 1;
  letter-spacing: -1.5px;
}

.section p,
li {
  font-size: 18px;
  color: #cbd5e1;
  line-height: 1.65;
}

.grid,
.conversion-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 18px;
}

.card,
.rules,
.conversion {
  background: rgba(255,255,255,.078);
  border: 1px solid rgba(255,255,255,.13);
  padding: 30px;
  border-radius: 26px;
  backdrop-filter: blur(10px);
}

.card span {
  color: #ffd60a;
  font-size: 34px;
  font-weight: 900;
}

.cta-box {
  background: #f8fafc;
  color: #061826;
  padding: 44px;
  border-radius: 30px;
}

.cta-box p {
  color: #334155;
}

footer {
  text-align: center;
  color: #94a3b8;
  padding: 36px;
}

@media (max-width: 840px) {
  .grid,
  .conversion-grid {
    grid-template-columns: 1fr;
  }

  .hero-content {
    margin-top: 84px;
  }

  .nav {
    align-items: flex-start;
    gap: 16px;
    flex-direction: column;
  }

  h1 {
    letter-spacing: -1px;
  }
}
""", encoding="utf-8")

    js.write_text("""console.log("Plano IA aplicado pelo K-Atlas");

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

    applied.write_text(f"""# Plano IA aplicado

Data: {datetime.now().isoformat()}

## Arquivos atualizados
- index.html
- style.css
- script.js

## Fonte
{plan_path or "Plano IA mais recente"}

## Resumo
A landing recebeu melhorias de conversão, CTA para WhatsApp, regras da promoção, estrutura visual mais forte e copy mais direta.

## Observação
Ainda falta configurar:
- número real do WhatsApp
- logo real
- imagens reais
- regras finais da campanha

## Trecho do plano usado
{plan_text[:3000]}
""", encoding="utf-8")

    return [index, css, js, applied]
