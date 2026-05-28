import json
from pathlib import Path
from datetime import datetime


class InstagramContentPack:

    def __init__(self):
        self.output_dir = Path("k_atlas/content_packs")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def load_product(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def build_caption(self, name, category, price):
        category_lower = category.lower()

        if "piscina" in category_lower:
            return (
                f"{name} para quem precisa cuidar da piscina com mais segurança e praticidade.\n\n"
                f"Quando a água começa a ficar verde ou perde a aparência cristalina, "
                f"o ideal é agir rápido para evitar mais trabalho depois.\n\n"
                f"Produto indicado para ajudar no tratamento e manutenção da água da piscina.\n\n"
                f"Valor: R$ {price}"
            )

        return (
            f"{name} com qualidade, praticidade e ótimo custo-benefício.\n\n"
            f"Produto indicado para quem busca uma solução simples e eficiente.\n\n"
            f"Valor: R$ {price}"
        )

    def build_cta(self, category):
        if "piscina" in category.lower():
            return "Chame no WhatsApp e peça ajuda para escolher o produto certo para sua piscina."

        return "Chame no WhatsApp e consulte disponibilidade."

    def build_strategy(self, category):
        if "piscina" in category.lower():
            return "Venda consultiva com foco em urgência, segurança da família e água cristalina."

        return "Venda direta com foco em benefício, confiança e praticidade."

    def build_pack(self, product):
        category = product.get("category", "")
        name = product.get("name", "")
        price = product.get("price", "")

        strategy = self.build_strategy(category)
        caption = self.build_caption(name, category, price)
        cta = self.build_cta(category)

        hashtags = [
            "#promocao",
            "#oferta",
            "#qualidade",
            "#instashop",
            "#marketingdigital"
        ]

        if "piscina" in category.lower():
            hashtags.extend([
                "#piscina",
                "#cloro",
                "#verao",
                "#aguacristalina"
            ])

        post = {
            "created_at": datetime.now().isoformat(),
            "platform": "instagram",
            "product_name": name,
            "price": price,
            "sales_strategy": strategy,
            "caption": caption,
            "cta": cta,
            "hashtags": hashtags,
            "full_post": f"{caption}\n\n{cta}\n\n{' '.join(hashtags)}"
        }

        return post

    def save_pack(self, pack):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"instagram_pack_{timestamp}.json"

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(pack, f, indent=2, ensure_ascii=False)

        print(f"[OK] Pacote salvo em: {output_file}")

    def execute(self, file_path):
        product = self.load_product(file_path)
        pack = self.build_pack(product)

        print(json.dumps(pack, indent=2, ensure_ascii=False))
        self.save_pack(pack)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True)

    args = parser.parse_args()

    app = InstagramContentPack()
    app.execute(args.file)