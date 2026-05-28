
# -*- coding: utf-8 -*-
"""
K-Atlas OS - Creative Intelligence

Camada de decisao criativa e estrategica para produtos, apps, campanhas e interfaces.

Nao cria app.
Nao executa deploy.
Nao copia concorrentes.
Gera Creative Brief antes da producao.
"""

from __future__ import annotations

import argparse
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "k_atlas" / "creative_intelligence"
KNOWLEDGE_DIR = BASE / "knowledge"
BRIEFS_DIR = BASE / "briefs"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_slug(value: str) -> str:
    clean = "".join(char.lower() if char.isalnum() else "-" for char in value.strip())
    while "--" in clean:
        clean = clean.replace("--", "-")
    return clean.strip("-") or "creative-brief"


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_knowledge(root_path: Path | None = None) -> Dict[str, Any]:
    root = root_path or ROOT
    knowledge = root / "k_atlas" / "creative_intelligence" / "knowledge"

    return {
        "principles": read_json(knowledge / "principles.json"),
        "color_psychology": read_json(knowledge / "color_psychology.json"),
        "naming_rules": read_json(knowledge / "naming_rules.json"),
        "market_contexts": read_json(knowledge / "market_contexts.json"),
    }


def score_name(name: str, target_market: str, knowledge: Dict[str, Any]) -> Dict[str, Any]:
    clean = name.strip()
    length = len(clean)

    memorability = 8 if length <= 12 else 6
    sound = 8 if len(clean.split()) <= 2 else 6
    market_fit = 8
    visual_identity = 8
    expansion_potential = 8
    cultural_risk = 3

    if target_market == "paraguay_marketplace" and clean.lower() == "brics":
        memorability = 9
        sound = 8
        market_fit = 7
        visual_identity = 9
        expansion_potential = 8
        cultural_risk = 5

    if target_market == "female_wardrobe_winter_2026" and clean.lower() == "closet pilot":
        memorability = 8
        sound = 8
        market_fit = 9
        visual_identity = 8
        expansion_potential = 9
        cultural_risk = 2

    total = round(
        (
            memorability
            + sound
            + market_fit
            + visual_identity
            + expansion_potential
            + (10 - cultural_risk)
        )
        / 6,
        2,
    )

    return {
        "name": clean,
        "score": total,
        "memorability": memorability,
        "sound": sound,
        "market_fit": market_fit,
        "visual_identity": visual_identity,
        "expansion_potential": expansion_potential,
        "cultural_risk": cultural_risk,
    }


def palette_for_context(context_key: str) -> Dict[str, Any]:
    if context_key == "paraguay_marketplace":
        return {
            "primary": "green",
            "secondary": "yellow",
            "support": ["white", "deep green", "warm gray"],
            "psychology": "verde transmite confianca e crescimento; amarelo transmite oportunidade e movimento comercial.",
            "warning": "nao usar amarelo em excesso para evitar percepcao barata."
        }

    if context_key == "female_wardrobe_winter_2026":
        return {
            "primary": "burgundy",
            "secondary": "cream",
            "support": ["black", "warm gray", "soft gold"],
            "psychology": "burgundy e preto elevam sofisticacao; cream aquece a experiencia; dourado suave sugere cuidado e valor.",
            "warning": "nao transformar em tela fria de cadastro; usar linguagem editorial."
        }

    return {
        "primary": "blue",
        "secondary": "white",
        "support": ["gray"],
        "psychology": "azul transmite confianca e estabilidade.",
        "warning": "pode parecer generico se nao houver identidade."
    }


def build_closet_pilot_brief(knowledge: Dict[str, Any]) -> Dict[str, Any]:
    context_key = "female_wardrobe_winter_2026"
    context = knowledge["market_contexts"][context_key]

    return {
        "success": True,
        "brief_id": str(uuid.uuid4()),
        "created_at": now_iso(),
        "project": "Closet Pilot",
        "context_key": context_key,
        "type": "fashion_lifestyle_micro_saas",
        "audience": context["audience"],
        "season": context["season"],
        "strategic_intent": "Transformar o guarda-roupa feminino em uma experiencia visual, organizada e emocionalmente inteligente.",
        "emotional_goal": context["emotional_drivers"],
        "market_reading": "Em 2026, produtos femininos de organizacao pessoal precisam parecer assistentes de estilo, nao planilhas. O valor esta em reduzir indecisao, recuperar pecas esquecidas e aumentar autoestima.",
        "visual_direction": context["design_direction"],
        "palette": palette_for_context(context_key),
        "name_analysis": score_name("Closet Pilot", context_key, knowledge),
        "ux_principles": [
            "menos formulario frio, mais experiencia de closet",
            "mostrar foto antes de tabela sempre que possivel",
            "destacar onde a peca esta guardada",
            "transformar cadastro em sensacao de curadoria",
            "sugerir looks como consultora pratica, nao como planilha"
        ],
        "avoid": [
            "interface generica",
            "botoes sem contexto emocional",
            "cadastro longo demais",
            "IA visual antes de validar uso manual",
            "design frio de dashboard"
        ],
        "next_product_move": "Criar modo visual premium para cards de pecas e looks, mantendo persistencia JSON local.",
        "unicorn_delta": "Sair de app de cadastro para experiencia de closet inteligente com memoria visual e narrativa de estilo."
    }


def build_brics_paraguay_brief(knowledge: Dict[str, Any]) -> Dict[str, Any]:
    context_key = "paraguay_marketplace"
    context = knowledge["market_contexts"][context_key]

    return {
        "success": True,
        "brief_id": str(uuid.uuid4()),
        "created_at": now_iso(),
        "project": "BRICS Paraguay",
        "context_key": context_key,
        "type": "classifieds_marketplace",
        "audience": "compradores e vendedores locais no Paraguai",
        "strategic_intent": "Criar um marketplace local de classificados com energia comercial, confianca e identidade propria.",
        "emotional_goal": context["emotional_drivers"],
        "market_reading": "Classificados locais vencem quando parecem rapidos, confiaveis e populares. O diferencial nao deve ser copiar OLX, mas melhorar percepcao de seguranca, organizacao e oportunidade.",
        "visual_direction": context["design_direction"],
        "palette": palette_for_context(context_key),
        "name_analysis": score_name("BRICS", context_key, knowledge),
        "positioning": [
            "compra e venda local",
            "negocio rapido",
            "visual mais confiavel",
            "foco Paraguai",
            "verde e amarelo com energia de oportunidade"
        ],
        "legal_guardrail": [
            "nao copiar OLX",
            "nao copiar marca, layout, codigo, iconografia ou identidade visual de concorrentes",
            "usar apenas categoria de produto como referencia: classificados"
        ],
        "ux_principles": [
            "busca grande e clara",
            "cards visuais fortes",
            "sinais de confianca",
            "destaque para preco e local",
            "publicar anuncio com baixa friccao",
            "evitar aparencia de clone"
        ],
        "avoid": [
            "copia fiel de concorrente",
            "visual barato",
            "excesso de amarelo",
            "botoes genericos",
            "fluxo pesado para publicar anuncio"
        ],
        "next_product_move": "Criar Product Spec supervisionado para BRICS Paraguay antes de qualquer scaffold de app.",
        "unicorn_delta": "Transformar classificados em uma experiencia mais confiavel, visual e localmente posicionada."
    }


def render_markdown(brief: Dict[str, Any]) -> str:
    lines: List[str] = []

    lines.append("# Creative Brief - " + brief["project"])
    lines.append("")
    lines.append("## Intencao estrategica")
    lines.append(str(brief.get("strategic_intent", "")))
    lines.append("")
    lines.append("## Leitura de mercado")
    lines.append(str(brief.get("market_reading", "")))
    lines.append("")
    lines.append("## Meta emocional")
    for item in brief.get("emotional_goal", []):
        lines.append("- " + str(item))
    lines.append("")
    lines.append("## Direcao visual")
    lines.append(str(brief.get("visual_direction", "")))
    lines.append("")
    lines.append("## Paleta e psicologia")
    lines.append(json.dumps(brief.get("palette", {}), ensure_ascii=False, indent=2))
    lines.append("")
    lines.append("## Analise do nome")
    lines.append(json.dumps(brief.get("name_analysis", {}), ensure_ascii=False, indent=2))
    lines.append("")
    lines.append("## Principios de UX")
    for item in brief.get("ux_principles", []):
        lines.append("- " + str(item))
    lines.append("")
    lines.append("## Evitar")
    for item in brief.get("avoid", []):
        lines.append("- " + str(item))
    lines.append("")
    lines.append("## Proximo movimento")
    lines.append(str(brief.get("next_product_move", "")))
    lines.append("")
    lines.append("## Delta unicornio")
    lines.append(str(brief.get("unicorn_delta", "")))
    lines.append("")

    return "\n".join(lines)


def save_brief(brief: Dict[str, Any], root_path: Path | None = None) -> Dict[str, Any]:
    root = root_path or ROOT
    briefs_dir = root / "k_atlas" / "creative_intelligence" / "briefs"
    briefs_dir.mkdir(parents=True, exist_ok=True)

    slug = safe_slug(brief["project"])
    timestamp = now_iso().replace(":", "").replace("-", "").split(".")[0]
    json_path = briefs_dir / (timestamp + "_" + slug + ".json")
    md_path = briefs_dir / (timestamp + "_" + slug + ".md")

    json_path.write_text(json.dumps(brief, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown(brief), encoding="utf-8")

    return {
        "success": True,
        "json_path": str(json_path),
        "md_path": str(md_path),
        "brief": brief
    }


def generate(preset: str, root_path: Path | None = None) -> Dict[str, Any]:
    knowledge = load_knowledge(root_path)

    if preset == "closet-pilot-winter-2026":
        brief = build_closet_pilot_brief(knowledge)
    elif preset == "brics-paraguay-marketplace":
        brief = build_brics_paraguay_brief(knowledge)
    else:
        return {"success": False, "error": "Preset desconhecido: " + preset}

    return save_brief(brief, root_path)


def main() -> int:
    parser = argparse.ArgumentParser(description="K-Atlas Creative Intelligence")
    parser.add_argument("action", choices=["generate"])
    parser.add_argument("--preset", required=True)
    parser.add_argument("--root", default=None)
    args = parser.parse_args()

    root_path = Path(args.root) if args.root else None
    result = generate(args.preset, root_path)

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("success") else 1


if __name__ == "__main__":
    raise SystemExit(main())
