# -*- coding: utf-8 -*-
"""
K-Atlas OS - SaaS Factory Product Spec

Gera especificacoes iniciais de micro-SaaS em modo supervisionado.

Nao executa deploy.
Nao cria cobranca.
Nao publica produto.
Nao usa IA externa sozinho.
"""

from __future__ import annotations

import argparse
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


ROOT = Path(__file__).resolve().parents[2]
PRODUCTS_DIR = ROOT / "k_atlas" / "saas_factory" / "products"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_slug(value: str) -> str:
    clean = "".join(char.lower() if char.isalnum() else "-" for char in value.strip())
    while "--" in clean:
        clean = clean.replace("--", "-")
    return clean.strip("-") or "micro-saas"


def build_wardrobe_product_spec() -> Dict[str, Any]:
    created_at = now_iso()

    return {
        "success": True,
        "product_id": str(uuid.uuid4()),
        "created_at": created_at,
        "name": "Closet Pilot",
        "slug": "closet-pilot",
        "category": "micro_saas",
        "audience": "Mulheres que querem organizar guarda-roupa, montar looks e reduzir indecisao na rotina.",
        "problem": "Muitas mulheres possuem um guarda-roupa com roupas suficientes, mas perdem tempo decidindo o que vestir, esquecem pecas que ja possuem e compram itens repetidos por falta de organizacao visual.",
        "solution": "Um micro-SaaS simples para cadastrar pecas do guarda-roupa, classificar por categoria, cor, ocasiao e estacao, montar combinacoes basicas e planejar looks para trabalho, eventos, viagens e rotina.",
        "mvp_scope": [
            "Cadastro manual de pecas",
            "Categorias: blusa, calca, saia, vestido, casaco, sapato, acessorio",
            "Cores e ocasioes",
            "Status da peca: ativa, pouco usada, favorita",
            "Gerador simples de combinacoes por ocasiao",
            "Planejador semanal de looks",
            "Resumo do guarda-roupa por categoria e cor"
        ],
        "not_now": [
            "IA externa obrigatoria",
            "Upload automatico de imagem",
            "Marketplace",
            "Login multiusuario",
            "Pagamento",
            "Deploy cloud",
            "Recomendacao fashion complexa"
        ],
        "first_test": {
            "type": "streamlit_local_mvp",
            "goal": "Validar se a experiencia basica de cadastro e sugestao de looks funciona localmente.",
            "input_data": [
                "peca",
                "categoria",
                "cor",
                "ocasiao",
                "estacao",
                "favorita"
            ],
            "expected_output": [
                "lista de pecas cadastradas",
                "metricas simples do guarda-roupa",
                "sugestao basica de combinacao",
                "planejamento semanal manual"
            ]
        },
        "success_criteria": [
            "App local abre sem erro",
            "Usuario consegue cadastrar pecas",
            "Usuario consegue visualizar pecas",
            "Sistema sugere pelo menos uma combinacao simples",
            "Smoke test valida estrutura do produto"
        ],
        "risks": [
            "Escopo virar app de moda complexo cedo demais",
            "Adicionar IA visual antes de validar fluxo manual",
            "Criar login e pagamento antes do MVP",
            "Focar em design antes de validar utilidade"
        ],
        "next_step_correct": "Gerar scaffold local Streamlit do Closet Pilot com dados JSON e smoke test.",
        "next_step_wrong": "Criar marketplace, login, pagamento ou IA visual antes do MVP local.",
        "policy": {
            "mode": "supervised",
            "can_generate_files": True,
            "can_deploy": False,
            "can_charge_users": False,
            "requires_human_operator": True
        }
    }


def render_markdown(spec: Dict[str, Any]) -> str:
    return "\n".join([
        "# " + spec["name"],
        "",
        "## Publico",
        spec["audience"],
        "",
        "## Problema",
        spec["problem"],
        "",
        "## Solucao",
        spec["solution"],
        "",
        "## MVP",
        "\n".join("- " + item for item in spec["mvp_scope"]),
        "",
        "## Nao fazer agora",
        "\n".join("- " + item for item in spec["not_now"]),
        "",
        "## Primeiro teste",
        json.dumps(spec["first_test"], ensure_ascii=False, indent=2),
        "",
        "## Criterios de sucesso",
        "\n".join("- " + item for item in spec["success_criteria"]),
        "",
        "## Riscos",
        "\n".join("- " + item for item in spec["risks"]),
        "",
        "## Proximo passo correto",
        spec["next_step_correct"],
        "",
        "## Proximo passo errado",
        spec["next_step_wrong"],
        "",
    ])


def save_spec(spec: Dict[str, Any]) -> Dict[str, Any]:
    product_dir = PRODUCTS_DIR / spec["slug"]
    product_dir.mkdir(parents=True, exist_ok=True)

    json_path = product_dir / "product_spec.json"
    md_path = product_dir / "product_spec.md"

    json_path.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown(spec), encoding="utf-8")

    return {
        "success": True,
        "product_dir": str(product_dir),
        "json_path": str(json_path),
        "md_path": str(md_path),
        "spec": spec
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="K-Atlas SaaS Factory Product Spec")
    parser.add_argument("action", choices=["wardrobe-spec"])
    args = parser.parse_args()

    if args.action == "wardrobe-spec":
        result = save_spec(build_wardrobe_product_spec())
    else:
        result = {"success": False, "message": "Acao desconhecida."}

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("success") else 1


if __name__ == "__main__":
    raise SystemExit(main())
