
# -*- coding: utf-8 -*-
"""
K-Atlas OS - Specialist Council

Conselho de especialistas para decisoes futuras.

Nao cria app.
Nao executa deploy.
Nao gera parecer juridico definitivo.
Nao gera parecer tributario definitivo.
Apenas identifica especialistas, riscos, checklists e proximos passos supervisionados.
"""

from __future__ import annotations

import argparse
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "k_atlas" / "specialist_council"
REVIEWS = BASE / "reviews"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_slug(value: str) -> str:
    clean = "".join(char.lower() if char.isalnum() else "-" for char in value.strip())
    while "--" in clean:
        clean = clean.replace("--", "-")
    return clean.strip("-") or "specialist-review"


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_registry(root: Path | None = None) -> Dict[str, Any]:
    base = (root or ROOT) / "k_atlas" / "specialist_council"
    return load_json(base / "specialist_registry.json")


def load_rules(root: Path | None = None) -> Dict[str, Any]:
    base = (root or ROOT) / "k_atlas" / "specialist_council"
    return load_json(base / "decision_rules.json")


def unique(items: List[str]) -> List[str]:
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def build_context_from_preset(preset: str) -> Dict[str, Any]:
    if preset == "brics-paraguay-marketplace":
        return {
            "project": "BRICS Paraguay",
            "product_type": "marketplace",
            "country": "paraguay",
            "languages": ["pt", "es"],
            "audience": "compradores e vendedores locais no Paraguai",
            "theme": "verde e amarelo",
            "inspiration": "classificados de compra e venda, sem copiar OLX",
            "domain_required": True,
            "dashboard_required": True,
            "legal_sensitive": True,
            "tax_sensitive": True,
            "scale_intent": "regional_to_large",
            "notes": "Cliente quer portugues e espanhol, dominio proprio, documentacao e base para escala."
        }

    if preset == "closet-pilot-evolution":
        return {
            "project": "Closet Pilot",
            "product_type": "fashion_lifestyle",
            "country": "brasil",
            "languages": ["pt"],
            "audience": "mulheres que organizam guarda-roupa e looks",
            "theme": "premium feminino inverno 2026",
            "inspiration": "assistente visual de closet, nao planilha",
            "domain_required": True,
            "dashboard_required": False,
            "legal_sensitive": False,
            "tax_sensitive": False,
            "scale_intent": "micro_saas_to_premium",
            "notes": "Produto deve evoluir com foto, memoria de localizacao, looks e experiencia acima da media."
        }

    raise ValueError("Preset desconhecido: " + preset)


def required_specialists(context: Dict[str, Any], rules: Dict[str, Any]) -> List[str]:
    specialists: List[str] = [
        "product_strategy_agent",
        "creative_intelligence_agent",
        "ux_ui_agent",
    ]

    product_type = str(context.get("product_type", "")).lower()
    country = str(context.get("country", "")).lower()
    languages = context.get("languages", [])

    specialists.extend(rules.get("product_type_rules", {}).get(product_type, []))
    specialists.extend(rules.get("country_rules", {}).get(country, []))

    if isinstance(languages, list) and len(languages) > 1:
        specialists.extend(rules.get("language_rules", {}).get("multilingual", []))

    if context.get("domain_required"):
        specialists.extend(rules.get("scale_rules", {}).get("domain_required", []))

    if context.get("dashboard_required"):
        specialists.extend(rules.get("scale_rules", {}).get("dashboard_required", []))

    if context.get("legal_sensitive"):
        specialists.append("legal_context_agent")

    if context.get("tax_sensitive"):
        specialists.append("tax_context_agent")

    specialists.append("growth_marketing_agent")

    return unique(specialists)


def build_checklists(context: Dict[str, Any]) -> Dict[str, List[str]]:
    product_type = str(context.get("product_type", "")).lower()
    country = str(context.get("country", "")).lower()
    languages = context.get("languages", [])

    checklist: Dict[str, List[str]] = {
        "product": [
            "definir proposta de valor",
            "definir publico e dor principal",
            "definir MVP minimo",
            "definir criterio de sucesso",
            "definir o que nao fazer agora"
        ],
        "creative": [
            "confirmar Creative Brief",
            "validar psicologia das cores",
            "avaliar naming",
            "avaliar risco de parecer generico",
            "definir padrao visual acima da media"
        ],
        "documentation": [
            "criar README operacional",
            "criar guia de setup",
            "criar guia de uso",
            "registrar politica do produto",
            "preparar documentacao de dominio/deploy"
        ],
        "scale_dashboard": [
            "definir metricas principais",
            "definir status operacional",
            "definir ultimas acoes",
            "definir painel administrativo",
            "preparar estrutura para multiusuario no futuro"
        ]
    }

    if product_type == "marketplace":
        checklist["marketplace"] = [
            "categorias de anuncio",
            "fluxo de publicar anuncio",
            "busca e filtros",
            "preco e localizacao",
            "sinais de confianca",
            "moderacao futura",
            "denuncia e remocao futura",
            "painel de anuncios"
        ]

    if country:
        checklist["localization"] = [
            "idioma principal",
            "idioma secundario se existir",
            "moeda local",
            "termos culturais",
            "formatos de telefone/endereco",
            "tom de comunicacao regional"
        ]

    if isinstance(languages, list) and len(languages) > 1:
        checklist["multilingual"] = [
            "portugues",
            "espanhol",
            "chaves de traducao",
            "texto sem hardcode quando possivel",
            "terminologia local"
        ]

    if context.get("legal_sensitive"):
        checklist["legal_context"] = [
            "termos de uso",
            "politica de privacidade",
            "responsabilidade sobre anuncios",
            "politica de itens proibidos",
            "processo de denuncia",
            "validacao com profissional juridico antes de producao"
        ]

    if context.get("tax_sensitive"):
        checklist["tax_context"] = [
            "mapear se ha comissao",
            "mapear se ha intermediacao de pagamento",
            "mapear obrigacoes fiscais por pais",
            "mapear relatorios para contabilidade",
            "validacao com contador antes de monetizacao"
        ]

    return checklist


def risk_assessment(context: Dict[str, Any]) -> Dict[str, Any]:
    risks: List[str] = []
    level = "low"

    if context.get("legal_sensitive"):
        risks.append("Produto exige checklist juridico antes de producao real.")
        level = "medium"

    if context.get("tax_sensitive"):
        risks.append("Produto exige checklist tributario/contabil antes de monetizacao.")
        level = "medium"

    if "olx" in str(context.get("inspiration", "")).lower():
        risks.append("Risco de copia percebida. Usar apenas inspiracao estrutural, nunca identidade visual/codigo/marca.")
        level = "medium"

    if context.get("dashboard_required"):
        risks.append("Produto deve nascer com pensamento de escala e painel operacional.")
        if level == "low":
            level = "medium"

    return {
        "level": level,
        "items": risks,
        "legal_notice": "Este conselho nao substitui advogado, contador ou especialista local. Serve como checklist operacional."
    }


def build_review(context: Dict[str, Any], root: Path | None = None) -> Dict[str, Any]:
    registry = load_registry(root)
    rules = load_rules(root)

    specialist_ids = required_specialists(context, rules)
    specialists = registry["specialists"]

    selected = []
    for sid in specialist_ids:
        if sid in specialists:
            selected.append({
                "id": sid,
                "area": specialists[sid]["area"],
                "mission": specialists[sid]["mission"]
            })

    checklists = build_checklists(context)
    risks = risk_assessment(context)

    scaffold_allowed = False
    blockers = [
        "Creative Brief deve existir antes do Product Spec.",
        "Specialist Council deve ser revisado antes do scaffold.",
    ]

    if context.get("legal_sensitive"):
        blockers.append("Checklist juridico deve ser tratado como pendencia antes de producao real.")

    if context.get("tax_sensitive"):
        blockers.append("Checklist tributario deve ser tratado como pendencia antes de monetizacao.")

    return {
        "success": True,
        "review_id": str(uuid.uuid4()),
        "created_at": now_iso(),
        "context": context,
        "required_specialists": selected,
        "checklists": checklists,
        "risk": risks,
        "governance": {
            "scaffold_allowed_now": scaffold_allowed,
            "requires_human_operator": True,
            "requires_creative_brief": True,
            "requires_product_spec": True,
            "requires_legal_validation_if_sensitive": bool(context.get("legal_sensitive")),
            "requires_tax_validation_if_sensitive": bool(context.get("tax_sensitive")),
            "blockers": blockers
        },
        "next_step_correct": "Gerar Product Spec supervisionado somente depois de revisar este conselho e confirmar Creative Brief.",
        "next_step_wrong": "Criar app diretamente sem especialistas, sem brief, sem checklist juridico/tributario e sem estrategia de escala."
    }


def render_markdown(review: Dict[str, Any]) -> str:
    context = review["context"]

    lines: List[str] = []
    lines.append("# Specialist Council Review - " + context.get("project", "Projeto"))
    lines.append("")
    lines.append("## Contexto")
    lines.append(json.dumps(context, ensure_ascii=False, indent=2))
    lines.append("")
    lines.append("## Especialistas obrigatorios")
    for item in review["required_specialists"]:
        lines.append("- **" + item["id"] + "**: " + item["mission"])
    lines.append("")
    lines.append("## Checklists")
    for name, items in review["checklists"].items():
        lines.append("### " + name)
        for item in items:
            lines.append("- " + item)
        lines.append("")
    lines.append("## Risco")
    lines.append("Nivel: " + review["risk"]["level"])
    for item in review["risk"]["items"]:
        lines.append("- " + item)
    lines.append("")
    lines.append("## Governanca")
    lines.append(json.dumps(review["governance"], ensure_ascii=False, indent=2))
    lines.append("")
    lines.append("## Proximo passo correto")
    lines.append(review["next_step_correct"])
    lines.append("")
    lines.append("## Proximo passo errado")
    lines.append(review["next_step_wrong"])
    lines.append("")
    return "\n".join(lines)


def save_review(review: Dict[str, Any], root: Path | None = None) -> Dict[str, Any]:
    base = (root or ROOT) / "k_atlas" / "specialist_council" / "reviews"
    base.mkdir(parents=True, exist_ok=True)

    slug = safe_slug(review["context"].get("project", "review"))
    timestamp = now_iso().replace(":", "").replace("-", "").split(".")[0]

    json_path = base / (timestamp + "_" + slug + ".json")
    md_path = base / (timestamp + "_" + slug + ".md")

    json_path.write_text(json.dumps(review, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown(review), encoding="utf-8")

    return {
        "success": True,
        "json_path": str(json_path),
        "md_path": str(md_path),
        "review": review
    }


def generate_from_preset(preset: str, root: Path | None = None) -> Dict[str, Any]:
    context = build_context_from_preset(preset)
    review = build_review(context, root)
    return save_review(review, root)


def main() -> int:
    parser = argparse.ArgumentParser(description="K-Atlas Specialist Council")
    parser.add_argument("action", choices=["review"])
    parser.add_argument("--preset", required=True)
    parser.add_argument("--root", default=None)
    args = parser.parse_args()

    root = Path(args.root) if args.root else None
    result = generate_from_preset(args.preset, root)

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("success") else 1


if __name__ == "__main__":
    raise SystemExit(main())
