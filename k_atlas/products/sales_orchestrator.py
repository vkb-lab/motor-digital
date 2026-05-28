from pathlib import Path
import json
import sys
from datetime import datetime

from k_atlas.products.customer_profiler import profile_customer


BASE = Path.cwd()
PRODUCTS_DIR = BASE / "k_atlas" / "products" / "data"


def clean_text(value):
    if value is None:
        return ""

    text = str(value)

    replacements = {
        "🔥": "",
        "�": "",
        "\ufffd": "",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text


def safe_print_json(data):
    text = json.dumps(
        data,
        ensure_ascii=False,
        indent=2
    )

    try:
        print(text)
    except UnicodeEncodeError:
        sys.stdout.buffer.write(
            text.encode("utf-8", errors="replace")
        )
        sys.stdout.buffer.write(b"\n")


def load_product(product_file: str):
    path = Path(product_file)

    if not path.exists():
        raise FileNotFoundError(f"Produto nao encontrado: {path}")

    return json.loads(
        path.read_text(
            encoding="utf-8",
            errors="ignore"
        )
    )


def build_sales_strategy(product: dict, customer_profile: dict):
    enrichment = product.get("enrichment", {})

    urgency = clean_text(customer_profile.get("urgency"))
    segment = clean_text(customer_profile.get("customer_type"))
    emotion = clean_text(customer_profile.get("emotion"))

    short_description = clean_text(
        enrichment.get("description_short")
        or product.get("description")
        or product.get("name")
    )

    sales_angle = clean_text(
        customer_profile.get("best_sales_angle")
        or "beneficio pratico e resultado visivel"
    )

    cta = clean_text(
        customer_profile.get("recommended_cta")
        or "Chame no WhatsApp para atendimento."
    )

    strategy = {
        "generated_at": datetime.now().isoformat(),
        "product": clean_text(product.get("name")),
        "customer_type": segment,
        "emotion": emotion,
        "urgency": urgency,
        "recommended_channel": "WhatsApp",
        "content_format": "mensagem consultiva",
        "sales_angle": sales_angle,
        "cta": cta,
        "instagram_caption": clean_text(enrichment.get("instagram_caption")),
        "short_description": short_description,
        "recommended_offer": "",
        "response_message": "",
        "next_action": ""
    }

    if urgency == "alta":
        strategy["recommended_offer"] = "Atendimento rapido com solucao imediata."
        strategy["next_action"] = "Levar cliente direto para fechamento."
    else:
        strategy["recommended_offer"] = "Apresentar beneficios e gerar confianca."
        strategy["next_action"] = "Educar cliente antes da oferta."

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

    safe_print_json(strategy)
