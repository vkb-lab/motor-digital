from pathlib import Path
from datetime import datetime

import google.generativeai as genai

from k_atlas.core.secrets_manager import get_secret


BASE = Path.cwd()
REPORTS = BASE / "k_atlas" / "reports"
REPORTS.mkdir(parents=True, exist_ok=True)


SYSTEM_PROMPT = """
Você é o K-Atlas Brain, o cérebro estratégico e técnico do K-Atlas.

Você trabalha para transformar pedidos em execução real.

Regras:
1. Seja direto, prático e estruturado.
2. Sempre separe diagnóstico, plano, execução e próximo passo.
3. Nunca finja ter executado algo que não executou.
4. Quando envolver risco, diga que precisa aprovação.
5. Gere respostas úteis para criação de código, apps, landing pages, automações e estratégias digitais.
6. Priorize simplicidade, baixo custo e execução rápida.
7. Pense como arquiteto de sistemas, desenvolvedor, estrategista e operador digital.
"""


def get_model():
    api_key = get_secret("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("GEMINI_API_KEY não configurada no .env")

    genai.configure(api_key=api_key)

    return genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=SYSTEM_PROMPT
    )


def ask_ai(prompt: str) -> str:
    model = get_model()

    response = model.generate_content(prompt)

    if not response or not getattr(response, "text", None):
        return "A IA não retornou texto."

    return response.text


def save_ai_report(prompt: str, answer: str) -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = REPORTS / f"ai_brain_{stamp}.md"

    content = []
    content.append("# K-Atlas AI Brain")
    content.append("")
    content.append(f"Data: {datetime.now().isoformat()}")
    content.append("")
    content.append("## Pedido")
    content.append(prompt)
    content.append("")
    content.append("## Resposta")
    content.append(answer)

    out.write_text("\n".join(content), encoding="utf-8")
    return out


def think(prompt: str):
    answer = ask_ai(prompt)
    report = save_ai_report(prompt, answer)
    return answer, report


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print('Uso: python -m k_atlas.core.ai_brain "seu pedido"')
        raise SystemExit(0)

    prompt = " ".join(sys.argv[1:])
    answer, report = think(prompt)

    print("")
    print("🧠 K-Atlas Brain")
    print("")
    print(answer)
    print("")
    print(f"Relatório salvo em: {report}")
