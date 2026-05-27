import json
from pathlib import Path
from datetime import datetime


class CommercialBrain:

    def __init__(self):

        self.output_dir = Path("k_atlas/commercial_output")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def load_json(self, path):

        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def detect_sales_angle(self, product, profile):

        category = product.get("category", "").lower()
        urgency = profile.get("urgency", "")
        emotion = profile.get("emotion", "")

        if "piscina" in category:

            if urgency == "alta":
                return "solução imediata para água limpa e segura"

            if emotion == "cuidado":
                return "proteção da família e bem-estar"

            return "água cristalina com praticidade"

        return "qualidade e resultado profissional"

    def generate_cta(self, profile):

        urgency = profile.get("urgency", "")

        if urgency == "alta":
            return "Me chama agora que vou te ajudar a resolver isso hoje."

        return "Quer que eu te mostre a melhor opção?"

    def generate_caption(self, product, profile, angle):

        product_name = product.get("name", "")
        price = product.get("price", "")

        return (
            f"🔥 {product_name}\n\n"
            f"Mais eficiência e resultado profissional.\n"
            f"Ideal para quem busca praticidade e segurança.\n\n"
            f"💰 Oferta: R$ {price}\n"
            f"✅ {angle}"
        )

    def generate_hashtags(self, product):

        category = product.get("category", "").lower()

        tags = [
            "#promoção",
            "#oferta",
            "#qualidade",
            "#marketingdigital"
        ]

        if "piscina" in category:
            tags.extend([
                "#piscina",
                "#cloro",
                "#aguacristalina",
                "#verão"
            ])

        return tags

    def build_commercial_output(self, product, profile):

        angle = self.detect_sales_angle(product, profile)

        cta = self.generate_cta(profile)

        caption = self.generate_caption(
            product,
            profile,
            angle
        )

        hashtags = self.generate_hashtags(product)

        return {
            "created_at": datetime.now().isoformat(),
            "product": product.get("name"),
            "customer_profile": profile.get("customer_type"),
            "emotion": profile.get("emotion"),
            "urgency": profile.get("urgency"),
            "sales_angle": angle,
            "caption": caption,
            "cta": cta,
            "hashtags": hashtags,
            "full_post": f"{caption}\n\n{cta}\n\n{' '.join(hashtags)}"
        }

    def save_output(self, output):

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        file_path = (
            self.output_dir /
            f"commercial_output_{timestamp}.json"
        )

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f"[OK] Resultado salvo em: {file_path}")

    def execute(self, product_file, profile_file):

        product = self.load_json(product_file)

        profile = self.load_json(profile_file)

        output = self.build_commercial_output(
            product,
            profile
        )

        print(json.dumps(
            output,
            indent=2,
            ensure_ascii=False
        ))

        self.save_output(output)


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument("--product", required=True)

    parser.add_argument("--profile", required=True)

    args = parser.parse_args()

    app = CommercialBrain()

    app.execute(
        args.product,
        args.profile
    )