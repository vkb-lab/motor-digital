from __future__ import annotations

from typing import Any

from .brief import CreativeBrief


def build_prompt_pack(brief: CreativeBrief) -> dict[str, Any]:
    base_context = (
        f"Projeto: {brief.project_name}. "
        f"Objetivo: {brief.objective}. "
        f"Público: {brief.target_audience}. "
        f"Oferta: {brief.offer}. "
        f"Tom: {brief.tone}. "
        f"Direção visual: {brief.visual_style}."
    )

    return {
        "status": "ready_for_human_review",
        "external_api_used": False,
        "generation_allowed": False,
        "provider_targets": [
            "google_flow_manual",
            "gemini_image_future",
            "imagen_future",
            "veo_future",
            "local_placeholder",
        ],
        "prompts": {
            "hero_image": (
                base_context
                + " Criar uma imagem hero cinematográfica, premium, limpa, com sensação de sistema operacional de IA em execução real. "
                + "Composição forte, espaço para headline, estética tecnológica, sem poluição visual."
            ),
            "vertical_video_9_16": (
                base_context
                + " Criar roteiro visual para vídeo vertical 9:16 de 8 a 15 segundos. "
                + "Mostrar objetivo virando tarefas, agentes, aprovação humana, execução e log. "
                + "Estilo: motion graphics + interface real + energia de startup ambiciosa."
            ),
            "carousel_5_cards": (
                base_context
                + " Criar carrossel de 5 cards: problema, virada, sistema, prova operacional e chamada para acompanhar."
            ),
            "landing_page_hero": (
                base_context
                + " Criar visual de hero section para landing page moderna, com cockpit IA, blocos modulares e CTA forte."
            ),
            "reel_script": [
                "Hook: Isso não é chatbot. É um sistema operacional de agentes IA.",
                "Cena 1: objetivo entra no cockpit.",
                "Cena 2: agentes recebem tarefas.",
                "Cena 3: supervisor aprova.",
                "Cena 4: executor roda com logs.",
                "CTA: acompanhe a construção do K-Atlas OS.",
            ],
        },
        "negative_prompt": [
            "visual genérico de SaaS antigo",
            "layout poluído",
            "promessa exagerada sem prova",
            "robôs humanóides clichês",
            "texto ilegível",
            "excesso de neon",
        ],
        "usage_rules": [
            "não publicar sem revisão humana",
            "não usar imagem de terceiros sem licença",
            "não chamar API externa sem vault",
            "salvar pacote antes de qualquer geração real",
        ],
    }