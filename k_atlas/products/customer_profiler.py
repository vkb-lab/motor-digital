from datetime import datetime
import json


def profile_customer(message: str):
    text = message.lower()

    profile = {
        "input": message,
        "created_at": datetime.now().isoformat(),
        "customer_type": "geral",
        "intent": "informacao",
        "urgency": "media",
        "emotion": "neutro",
        "language_style": "claro, simples e consultivo",
        "main_need": "",
        "best_sales_angle": "",
        "recommended_cta": "",
        "objections": [],
        "signals": []
    }

    if any(x in text for x in ["preço", "valor", "quanto", "barato"]):
        profile["intent"] = "comparacao_preco"
        profile["emotion"] = "cautela"
        profile["best_sales_angle"] = "mostrar custo-beneficio e rendimento"
        profile["recommended_cta"] = "Posso te indicar a opção que rende melhor pelo valor?"

    if any(x in text for x in ["urgente", "hoje", "agora", "preciso", "rapido", "rápido"]):
        profile["urgency"] = "alta"
        profile["emotion"] = "pressa"
        profile["best_sales_angle"] = "solucao imediata e pratica"
        profile["recommended_cta"] = "Quer que eu te indique a opção mais rápida para resolver agora?"

    if any(x in text for x in ["piscina", "água", "agua", "cloro", "algas", "verde"]):
        profile["customer_type"] = "cliente_piscina"
        profile["main_need"] = "manter a piscina limpa, segura e pronta para uso"
        profile["signals"].append("interesse_em_tratamento_de_piscina")

    if any(x in text for x in ["criança", "crianca", "filho", "familia", "família"]):
        profile["emotion"] = "cuidado"
        profile["best_sales_angle"] = "seguranca da familia e agua saudavel"
        profile["recommended_cta"] = "Posso te mostrar a opção mais segura para sua família?"

    if any(x in text for x in ["profissional", "cliente", "serviço", "servico", "piscineiro"]):
        profile["customer_type"] = "profissional"
        profile["language_style"] = "tecnico, direto e orientado a rendimento"
        profile["best_sales_angle"] = "rendimento, padronizacao e economia operacional"
        profile["recommended_cta"] = "Quer que eu monte uma sugestão pensando em rendimento para atendimento profissional?"

    if not profile["main_need"]:
        profile["main_need"] = "resolver uma necessidade pratica com confianca"

    if not profile["best_sales_angle"]:
        profile["best_sales_angle"] = "beneficio direto, praticidade e confianca"

    if not profile["recommended_cta"]:
        profile["recommended_cta"] = "Quer que eu te indique a melhor opção?"

    return profile


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Perfilador de cliente do K-Atlas")
    parser.add_argument("--message", required=True)

    args = parser.parse_args()

    result = profile_customer(args.message)

    print(json.dumps(result, ensure_ascii=False, indent=2))