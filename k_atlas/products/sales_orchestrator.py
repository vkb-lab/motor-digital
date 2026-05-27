from pathlib import Path
import json
from datetime import datetime

from k_atlas.products.customer_profiler import profile_customer


BASE = Path.cwd()
PRODUCTS_DIR = BASE / "k_atlas" / "products" / "data"


def load_product(product_file: str):
    path = Path(product_file)

    if not path.exists():
        raise FileNotFoundError(f"Produto não encontrado: {path}")

    return json.loads(path.read_text(encoding="utf-8"))


def build_sales_strategy(product: dict, customer_profile: dict):
    enrichment = product.get("enrichment", {})

    strategy = {
        "generated_at": datetime.now().isoformat(),
        "product": product.get("name"),
        "customer_type": customer_profile.get("customer_type"),
        "emotion": customer_profile.get("emotion"),
        "urgency": customer_profile.get("urgency"),
        "recommended_channel": "WhatsApp",
        "content_format": "mensagem consultiva",
        "sales_angle": customer_profile.get("best_sales_angle"),
        "cta": customer_profile.get("recommended_cta"),
        "instagram_caption": enrichment.get("instagram_caption"),
        "short_description": enrichment.get("description_short"),
        "recommended_offer": "",
        "response_message": "",
        "next_action": ""
    }

    urgency = customer_profile.get("urgency")

    if urgency == "alta":
        strategy["recommended_offer"] = (
            "Atendimento rápido com solução imediata."
        )

        strategy["next_action"] = (
            "Levar cliente direto para fechamento."
        )

    else:
        strategy["recommended_offer"] = (
            "Apresentar benefícios e gerar confiança."
        )

        strategy["next_action"] = (
            "Educar cliente antes da oferta."
        )

    strategy["response_message"] = (
        f"{strategy['short_description']}\n\n"
        f"{strategy['sales_angle']}.\n\n"
        f"{strategy['cta']}"
    )

    return strategy


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Orquestrador comercial do K-Atlas"
    )

    parser.add_argument("--product", required=True)
    parser.add_argument("--message", required=True)

    args = parser.parse_args()

    product = load_product(args.product)

    customer_profile = profile_customer(args.message)

    strategy = build_sales_strategy(
        product,
        customer_profile
    )

    print(json.dumps(strategy, ensure_ascii=False, indent=2))