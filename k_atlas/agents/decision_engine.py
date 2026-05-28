import json
import argparse
from datetime import datetime


class DecisionEngine:

    def analyze(self, command):

        normalized = command.lower()

        context = {
            "created_at": datetime.now().isoformat(),
            "input": command,
            "emotion": "neutro",
            "urgency": "normal",
            "segment": "geral",
            "sales_strategy": "consultiva",
            "cta": "Fale conosco no WhatsApp."
        }

        if any(word in normalized for word in [
            "urgente",
            "hoje",
            "agora",
            "desesperado",
            "rapido",
            "rápido"
        ]):
            context["urgency"] = "alta"

        if any(word in normalized for word in [
            "filhos",
            "familia",
            "família",
            "seguranca",
            "segurança",
            "criança",
            "crianca"
        ]):
            context["emotion"] = "protecao_familiar"

        if any(word in normalized for word in [
            "piscina",
            "cloro",
            "agua verde",
            "água verde"
        ]):
            context["segment"] = "piscina"
            context["sales_strategy"] = "Venda consultiva com foco em seguranca familiar, urgencia e agua cristalina."
            context["cta"] = "Chame agora no WhatsApp e resolva sua piscina hoje."

        elif any(word in normalized for word in [
            "gordura",
            "restaurante",
            "cozinha",
            "desengordurante"
        ]):
            context["segment"] = "limpeza_pesada"
            context["sales_strategy"] = "Foco em limpeza profissional pesada, economia de tempo e resultado visivel."
            context["cta"] = "Fale conosco e encontre o produto ideal para limpeza pesada."

        if any(word in normalized for word in [
            "black friday",
            "promocao",
            "promoção",
            "campanha",
            "oferta"
        ]):
            context["sales_strategy"] += " Aplicar gatilhos promocionais, escassez e chamada direta para compra."

        return context


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--command", default="cliente desesperado piscina verde filhos vao usar hoje")

    args = parser.parse_args()

    engine = DecisionEngine()
    result = engine.analyze(args.command)

    print(json.dumps(result, indent=2, ensure_ascii=False))
