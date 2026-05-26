import json

class MarketingManager:
    def __init__(self, core):
        self.core = core
        self.campaigns = {
            "Parada_Atlantida": "Atrasada - Campanha de Inverno",
            "Casa_da_Limpeza": "Atrasada - Tabela B2B Junho"
        }
        self.social_channels = [
            "Instagram_Parada", "Facebook_Parada", "Google_Parada",
            "Instagram_Limpeza", "Facebook_Limpeza", "LinkedIn_Limpeza"
        ]

    def generate_marketing_plan(self):
        """Usa a IA para criar um plano de recuperação de campanhas atrasadas"""
        prompt = f"Tenho 2 campanhas atrasadas: {self.campaigns}. E 6 redes sociais para gerenciar: {self.social_channels}. Crie um cronograma de ação imediata."
        plan = self.core.call_gemini(prompt, system_instruction="Você é um CMO (Chief Marketing Officer) focado em escala digital.")
        self.core.log("Plano de Marketing Gerado.")
        return plan

    def open_creative_tools(self):
        """Abre as ferramentas de criação no Windows"""
        self.core.open_browser("https://www.canva.com")
        self.core.open_browser("https://chat.openai.com")
        return "Ferramentas de criação abertas para trabalho."
