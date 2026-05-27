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


MODEL_CANDIDATES = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
]


def configure():
    api_key = get_secret("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("GEMINI_API_KEY não configurada no .env")

    genai.configure(api_key=api_key)


def generate_with_model(model_name: str, prompt: str) -> str:
    model = genai.GenerativeModel(
        model_name=model_name,
        system_instruction=SYSTEM_PROMPT
    )

    response = model.generate_content(prompt)

    if not response or not getattr(response, "text", None):
        return ""

    return response.text


def ask_ai(prompt: str) -> tuple[str, str]:
    configure()

    last_error = None

    for model_name in MODEL_CANDIDATES:
        try:
            answer = generate_with_model(model_name, prompt)
            if answer:
                return answer, model_name
        except Exception as e:
            last_error = e

    raise RuntimeError(f"Nenhum modelo Gemini respondeu. Último erro: {last_error}")


def save_ai_report(prompt: str, answer: str, model_name: str) -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = REPORTS / f"ai_brain_{stamp}.md"

    content = []
    content.append("# K-Atlas AI Brain")
    content.append("")
    content.append(f"Data: {datetime.now().isoformat()}")
    content.append(f"Modelo: {model_name}")
    content.append("")
    content.append("## Pedido")
    content.append(prompt)
    content.append("")
    content.append("## Resposta")
    content.append(answer)

    out.write_text("\n".join(content), encoding="utf-8")
    return out


def think(prompt: str):
    answer, model_name = ask_ai(prompt)
    report = save_ai_report(prompt, answer, model_name)
    return answer, report, model_name


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print('Uso: python -m k_atlas.core.ai_brain "seu pedido"')
        raise SystemExit(0)

    prompt = " ".join(sys.argv[1:])

    try:
        answer, report, model_name = think(prompt)

        print("")
        print("🧠 K-Atlas Brain")
        print(f"Modelo usado: {model_name}")
        print("")
        print(answer)
        print("")
        print(f"Relatório salvo em: {report}")

    except Exception as e:
        print("")
        print("⚠️ K-Atlas Brain não conseguiu responder.")
        print(str(e))
        print("")
        print("Próximo passo:")
        print("Verifique se GEMINI_API_KEY está correta e se existe modelo disponível para sua conta.")
