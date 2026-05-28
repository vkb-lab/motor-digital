import json
from pathlib import Path
from datetime import datetime


class MarketingManager:

    def __init__(self):
        self.base_dir = Path("k_atlas")
        self.campaigns_dir = self.base_dir / "campaigns"
        self.campaigns_dir.mkdir(parents=True, exist_ok=True)

    def create_campaign_folder(self):
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        folder = self.campaigns_dir / f"campaign_{stamp}"
        folder.mkdir(parents=True, exist_ok=True)
        return folder

    def build_strategy(self, command):
        text = command.lower()

        segment = "geral"
        if "piscina" in text or "cloro" in text:
            segment = "piscina"
        elif "gordura" in text or "cozinha" in text or "restaurante" in text:
            segment = "limpeza_pesada"

        urgency = "alta" if any(x in text for x in ["urgente", "hoje", "agora", "desesperado"]) else "normal"
        campaign_type = "promocional" if any(x in text for x in ["campanha", "promocao", "promoção", "black friday"]) else "conteudo"

        return {
            "created_at": datetime.now().isoformat(),
            "command": command,
            "segment": segment,
            "urgency": urgency,
            "campaign_type": campaign_type,
            "goal": "gerar atencao, conversa no WhatsApp e venda consultiva"
        }

    def build_instagram_post(self, strategy):
        if strategy["segment"] == "piscina":
            caption = (
                "Sua piscina ficou verde ou perdeu a aparência cristalina?\n\n"
                "Quando a água muda de cor, o ideal é agir rápido para evitar mais trabalho depois.\n\n"
                "Aqui na Casa da Limpeza você encontra produtos para ajudar no tratamento da piscina com orientação prática."
            )
            cta = "Chame no WhatsApp e peça ajuda para escolher o produto certo para sua piscina."
            hashtags = "#piscina #cloro #aguacristalina #verao #casadalimpeza"
        elif strategy["segment"] == "limpeza_pesada":
            caption = (
                "Gordura pesada em cozinha ou restaurante precisa de produto certo.\n\n"
                "A escolha correta economiza tempo, esforço e melhora o resultado da limpeza profissional."
            )
            cta = "Chame no WhatsApp e consulte a melhor opção para limpeza pesada."
            hashtags = "#limpezapesada #restaurante #cozinhaindustrial #desengordurante"
        else:
            caption = (
                "Produto certo faz diferença no resultado.\n\n"
                "Conte com atendimento consultivo para escolher a melhor solução."
            )
            cta = "Chame no WhatsApp e fale com nossa equipe."
            hashtags = "#oferta #qualidade #atendimento"

        return {
            "caption": caption,
            "cta": cta,
            "hashtags": hashtags,
            "full_post": f"{caption}\n\n{cta}\n\n{hashtags}"
        }

    def build_whatsapp_copy(self, strategy):
        if strategy["urgency"] == "alta":
            return (
                "Olá! Vi que você precisa resolver isso com urgência. "
                "Me chama aqui que eu te ajudo a escolher a opção mais indicada para resolver hoje."
            )

        return (
            "Olá! Posso te ajudar a escolher o produto certo conforme sua necessidade. "
            "Me diga onde você pretende usar e qual resultado espera."
        )

    def build_reels_script(self, strategy):
        return {
            "hook": "Sua limpeza ou piscina precisa de resultado rápido?",
            "scene_1": "Mostrar o problema real do cliente.",
            "scene_2": "Apresentar a solução com produto certo.",
            "scene_3": "Mostrar orientação da loja.",
            "cta": "Chame no WhatsApp ou venha até a Casa da Limpeza."
        }

    def build_image_prompt(self, strategy):
        if strategy["segment"] == "piscina":
            return "Imagem comercial de piscina limpa e cristalina, familia feliz ao fundo, produto de limpeza em destaque, estilo profissional para Instagram."
        if strategy["segment"] == "limpeza_pesada":
            return "Imagem comercial de cozinha profissional limpa, brilho em inox, produto desengordurante em destaque, estilo premium para Instagram."
        return "Imagem comercial limpa e profissional para divulgação de produto em loja local."

    def execute(self, command):
        folder = self.create_campaign_folder()
        strategy = self.build_strategy(command)
        instagram = self.build_instagram_post(strategy)
        whatsapp = self.build_whatsapp_copy(strategy)
        reels = self.build_reels_script(strategy)
        image_prompt = self.build_image_prompt(strategy)

        (folder / "strategy.json").write_text(json.dumps(strategy, indent=2, ensure_ascii=False), encoding="utf-8")
        (folder / "instagram_post.json").write_text(json.dumps(instagram, indent=2, ensure_ascii=False), encoding="utf-8")
        (folder / "whatsapp_copy.txt").write_text(whatsapp, encoding="utf-8")
        (folder / "reels_script.json").write_text(json.dumps(reels, indent=2, ensure_ascii=False), encoding="utf-8")
        (folder / "image_prompt.txt").write_text(image_prompt, encoding="utf-8")

        print(f"[OK] Campanha completa criada em: {folder}")
        print("")
        print(instagram["full_post"])


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--command", required=True)

    args = parser.parse_args()

    MarketingManager().execute(args.command)
