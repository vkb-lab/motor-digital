from pathlib import Path
from datetime import datetime
import json

BASE = Path.cwd()
PRODUCTS_DIR = BASE / "k_atlas" / "products" / "data"


def load_product(product_path: str):
    path = Path(product_path)

    if not path.exists():
        raise FileNotFoundError(f"Produto não encontrado: {path}")

    return path, json.loads(path.read_text(encoding="utf-8"))


def enrich_product(data: dict):
    name = data.get("name", "")

    category = data.get("category", "")

    short_description = (
        f"{name} ideal para clientes que buscam praticidade, "
        f"qualidade e resultado profissional."
    )

    marketplace_description = (
        f"{name} da categoria {category}. "
        f"Produto indicado para uso eficiente, "
        f"com excelente desempenho e ótima aceitação comercial."
    )

    instagram_caption = (
        f"🔥 {name}\n\n"
        f"Mais eficiência e qualidade para seu dia a dia.\n"
        f"Entre em contato e peça agora.\n\n"
        f"#promoção #qualidade #oferta"
    )

    customer_need = (
        "Cliente busca resolver uma necessidade prática "
        "com rapidez e confiança."
    )

    sales_angle = (
        "Foco em benefício direto, praticidade e confiança."
    )

    keywords = [
        name.lower(),
        category.lower(),
        "promoção",
        "qualidade",
        "oferta"
    ]

    data["enrichment"] = {
        "description_short": short_description,
        "description_marketplace": marketplace_description,
        "instagram_caption": instagram_caption,
        "customer_need": customer_need,
        "sales_angle": sales_angle,
        "keywords": keywords,
        "generated_at": datetime.now().isoformat()
    }

    data["status"] = "enriched"

    return data


def save_product(path: Path, data: dict):
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Enriquecedor comercial de produtos do K-Atlas"
    )

    parser.add_argument("--file", required=True)

    args = parser.parse_args()

    product_path, product_data = load_product(args.file)

    enriched = enrich_product(product_data)

    save_product(product_path, enriched)

    print(f"Produto enriquecido com sucesso: {product_path}")