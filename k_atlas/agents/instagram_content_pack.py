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

    def build_pack(self, product):

        category = product.get("category", "")
        name = product.get("name", "")
        price = product.get("price", "")
        strategy = product.get("sales_angle", "")
        caption = product.get("instagram_caption", "")
        cta = product.get("cta", "")

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