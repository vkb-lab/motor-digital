from pathlib import Path
from datetime import datetime
import json

BASE = Path.cwd()
PRODUCTS_DIR = BASE / "k_atlas" / "products" / "data"
PRODUCTS_DIR.mkdir(parents=True, exist_ok=True)


def create_product_draft(
    name: str,
    category: str = "",
    barcode: str = "",
    price: str = "",
    source: str = "manual",
):
    product_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = PRODUCTS_DIR / f"product_{product_id}.json"

    data = {
        "id": product_id,
        "name": name,
        "category": category,
        "barcode": barcode,
        "price": price,
        "source": source,
        "status": "draft",
        "created_at": datetime.now().isoformat(),
        "enrichment": {
            "description_short": "",
            "description_marketplace": "",
            "instagram_caption": "",
            "customer_need": "",
            "sales_angle": "",
            "keywords": []
        },
        "media": {
            "original_image": "",
            "processed_image": "",
            "gallery": []
        },
        "publishing": {
            "instagram": "not_ready",
            "facebook": "not_ready",
            "marketplaces": []
        }
    }

    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print(f"Produto criado: {path}")
    return path


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Criar rascunho de produto no K-Atlas.")
    parser.add_argument("--name", required=True)
    parser.add_argument("--category", default="")
    parser.add_argument("--barcode", default="")
    parser.add_argument("--price", default="")
    parser.add_argument("--source", default="manual")

    args = parser.parse_args()

    create_product_draft(
        name=args.name,
        category=args.category,
        barcode=args.barcode,
        price=args.price,
        source=args.source,
    )