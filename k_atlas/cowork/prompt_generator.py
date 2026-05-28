
# -*- coding: utf-8 -*-
"""
K-Atlas OS - Cowork Prompt Generator

Analisa o estado operacional do K-Atlas OS e sugere o proximo passo seguro.

Nao executa comandos.
Nao modifica codigo.
Nao aprova patches.
Nao aplica patches.
Nao controla navegador.
Nao acessa ChatGPT sozinho.
"""

from __future__ import annotations

import argparse
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


ROOT = Path(__file__).resolve().parents[2]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_slug(value: str) -> str:
    clean = "".join(char.lower() if char.isalnum() else "-" for char in value.strip())
    while "--" in clean:
        clean = clean.replace("--", "-")
    return clean.strip("-") or "next-step"


def ensure_dirs(root_path: Optional[str | Path] = None) -> Dict[str, Path]:
    root = Path(root_path) if root_path else ROOT
    base = root / "k_atlas" / "cowork"

    paths = {
        "next_steps": base / "next_steps",
        "recommendations": base / "recommendations",
        "lousa_cards": root / "k_atlas" / "lousa" / "cards",
        "cowork_sessions": root / "k_atlas" / "cowork" / "sessions",
        "cowork_steps": root / "k_atlas" / "cowork" / "steps",
        "cowork_reviews": root / "k_atlas" / "cowork" / "reviews",
        "module_reports": root / "reports" / "module_reports",
        "dev_runner_report": root / "reports" / "dev_runner_report.json",
        "patch_inbox": root / "k_atlas" / "self_evolution" / "patch_inbox",
        "patch_approved": root / "k_atlas" / "self_evolution" / "patch_approved",
    }

    for key in ["next_steps", "recommendations"]:
        paths[key].mkdir(parents=True, exist_ok=True)

    return paths


def read_json(path: Path) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"error": str(exc), "path": str(path)}


def load_json_folder(folder: Path, limit: int = 50) -> List[Dict[str, Any]]:
    folder.mkdir(parents=True, exist_ok=True)
    items: List[Dict[str, Any]] = []

    for path in sorted(folder.glob("*.json"))[-limit:]:
        items.append(
            {
                "name": path.name,
                "path": str(path),
                "data": read_json(path),
            }
        )

    return items


def collect_state(root_path: Optional[str | Path] = None) -> Dict[str, Any]:
    paths = ensure_dirs(root_path)
    dev_runner = {}

    if paths["dev_runner_report"].exists():
        dev_runner = read_json(paths["dev_runner_report"])

    return {
        "success": True,
        "created_at": now_iso(),
        "dev_runner_report": dev_runner,
        "lousa_cards": load_json_folder(paths["lousa_cards"], 100),
        "cowork_sessions": load_json_folder(paths["cowork_sessions"], 20),
        "cowork_steps": load_json_folder(paths["cowork_steps"], 100),
        "cowork_reviews": load_json_folder(paths["cowork_reviews"], 20),
        "module_reports": list(paths["module_reports"].glob("*.md"))[-30:] if paths["module_reports"].exists() else [],
        "patch_inbox": load_json_folder(paths["patch_inbox"], 50),
        "patch_approved": load_json_folder(paths["patch_approved"], 50),
        "policy": {
            "mode": "analysis-only",
            "can_execute_commands": False,
            "can_modify_code": False,
            "can_approve_patches": False,
            "can_apply_patches": False,
            "can_control_browser": False,
            "can_access_chatgpt": False,
            "requires_human_operator": True,
        },
    }



def is_generic_title(title: str) -> bool:
    value = title.strip().lower()

    generic_titles = {
        "proximo movimento seguro",
        "próximo movimento seguro",
        "proximo passo seguro",
        "próximo passo seguro",
        "next step",
        "next safe step",
    }

    return value in generic_titles


def card_specificity_score(card: Dict[str, Any]) -> int:
    title = str(card.get("title", "")).strip()
    description = str(card.get("description", "")).strip()
    priority = str(card.get("priority", "normal")).strip().lower()
    tags = card.get("tags", [])

    score = 0

    if title:
        score += 10

    if description:
        score += min(len(description) // 20, 20)

    if not is_generic_title(title):
        score += 25
    else:
        score -= 20

    if priority == "high":
        score += 15
    elif priority == "normal":
        score += 5

    if isinstance(tags, list):
        score += min(len(tags) * 2, 10)

    keywords = [
        "cockpit",
        "lousa",
        "prompt generator",
        "self evolution",
        "cowork",
        "governance",
        "dev_runner",
        "read-only",
        "relatorio",
        "teste",
    ]

    joined = (title + " " + description).lower()

    for keyword in keywords:
        if keyword in joined:
            score += 3

    return score


def card_to_next_step(card: Dict[str, Any]) -> str:
    title = str(card.get("title", "")).strip()
    description = str(card.get("description", "")).strip()

    if is_generic_title(title) and description:
        return description

    return title or description or "Executar proximo card especifico da Lousa."


def select_best_backlog_card(cards: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    candidates: List[Dict[str, Any]] = []

    for item in cards:
        data = item.get("data", {})
        if not isinstance(data, dict):
            continue

        lane = str(data.get("lane", "")).lower()
        status = str(data.get("status", "")).lower()

        if lane != "backlog":
            continue

        if status in ["done", "completed", "closed"]:
            continue

        candidates.append(data)

    if not candidates:
        return None

    candidates = sorted(candidates, key=card_specificity_score, reverse=True)
    return candidates[0]


def choose_next_step(state: Dict[str, Any]) -> Dict[str, Any]:
    dev = state.get("dev_runner_report", {})
    cards = state.get("lousa_cards", [])
    approved = state.get("patch_approved", [])
    inbox = state.get("patch_inbox", [])

    priority = "normal"
    risk = "low"
    signals: List[str] = []
    bottlenecks: List[str] = []
    risks: List[str] = []

    if dev.get("success") is False:
        priority = "high"
        risk = "medium"
        next_step = "Corrigir falha do dev_runner antes de expandir."
        justification = "O gate de qualidade falhou. Expandir com validacao quebrada aumenta risco."
        dangerous = "Criar novos modulos antes de restaurar dev_runner."
    else:
        best_card = select_best_backlog_card(cards)

        if best_card:
            next_step = card_to_next_step(best_card)
            priority = str(best_card.get("priority", "normal")).lower() or "normal"
            justification = "A Lousa possui um card de backlog especifico e ainda nao concluido para orientar o proximo movimento."
            dangerous = "Ignorar a Lousa e iniciar automacao nova sem review."
            signals.append("Card selecionado por score de especificidade: " + str(best_card.get("title", "")))
        else:
            next_step = "Criar novo card objetivo na Lousa antes de expandir."
            justification = "Nao ha card de backlog especifico disponivel. O proximo movimento seguro e organizar a decisao antes de executar."
            dangerous = "Executar desenvolvimento novo sem card, sem prioridade e sem criterio de review."

    if approved:
        risks.append("Existem patches aprovados apenas para revisao. Nao aplicar automaticamente.")
        if risk == "low":
            risk = "medium"

    if inbox:
        signals.append("Existem propostas em patch_inbox para revisar.")

    if dev.get("success") is True:
        signals.append("dev_runner_report indica validacao OK.")

    prompt = (
        "Quero executar o proximo passo seguro do K-Atlas OS.\n\n"
        "Proximo passo correto: " + next_step + "\n\n"
        "Prioridade: " + priority + "\n"
        "Risco: " + risk + "\n\n"
        "Justificativa: " + justification + "\n\n"
        "Nao fazer agora: " + dangerous + "\n\n"
        "Requisitos:\n"
        "- Python puro\n"
        "- UTF-8\n"
        "- compatibilidade Windows\n"
        "- comandos completos PowerShell\n"
        "- smoke test\n"
        "- dev_runner quando aplicavel\n"
        "- commit Git\n"
        "- modo supervisionado\n"
        "- sem autoexecucao\n"
        "- sem autoaplicacao de patch\n"
        "- sem controle automatico de navegador\n\n"
        "Entregue o comando completo para executar este passo com seguranca."
    )

    return {
        "priority": priority,
        "risk": risk,
        "justification": justification,
        "next_step_correct": next_step,
        "next_step_dangerous": dangerous,
        "prompt_for_engineer": prompt,
        "signals": signals,
        "bottlenecks": bottlenecks,
        "risks": risks,
    }


def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(path)


def render_markdown(data: Dict[str, Any]) -> str:
    analysis = data["analysis"]

    return (
        "# K-Atlas Cowork - Next Step Recommendation\n\n"
        "## Prioridade\n\n" + analysis["priority"] + "\n\n"
        "## Risco\n\n" + analysis["risk"] + "\n\n"
        "## Justificativa\n\n" + analysis["justification"] + "\n\n"
        "## Proximo passo correto\n\n" + analysis["next_step_correct"] + "\n\n"
        "## Proximo passo perigoso\n\n" + analysis["next_step_dangerous"] + "\n\n"
        "## Prompt sugerido para o engenheiro IA\n\n"
        "```text\n" + analysis["prompt_for_engineer"] + "\n```\n"
    )


def generate_next_prompt(root_path: Optional[str | Path] = None) -> Dict[str, Any]:
    paths = ensure_dirs(root_path)
    state = collect_state(root_path)
    analysis = choose_next_step(state)

    created_at = now_iso()
    filename = created_at.replace(":", "").replace("-", "").split(".")[0] + "_" + safe_slug(analysis["next_step_correct"])

    result = {
        "success": True,
        "recommendation_id": str(uuid.uuid4()),
        "created_at": created_at,
        "analysis": analysis,
        "state_summary": {
            "dev_runner_success": state.get("dev_runner_report", {}).get("success"),
            "lousa_cards": len(state.get("lousa_cards", [])),
            "cowork_steps": len(state.get("cowork_steps", [])),
            "cowork_reviews": len(state.get("cowork_reviews", [])),
            "module_reports": len(state.get("module_reports", [])),
            "patch_inbox": len(state.get("patch_inbox", [])),
            "patch_approved": len(state.get("patch_approved", [])),
        },
        "policy": state["policy"],
    }

    recommendation_path = paths["recommendations"] / (filename + ".json")
    next_json = paths["next_steps"] / (filename + ".json")
    next_md = paths["next_steps"] / (filename + ".md")

    write_json(recommendation_path, result)
    write_json(next_json, result)
    next_md.write_text(render_markdown(result), encoding="utf-8")

    return {
        "success": True,
        "message": "Proximo prompt supervisionado gerado.",
        "recommendation_path": str(recommendation_path),
        "next_step_json_path": str(next_json),
        "next_step_md_path": str(next_md),
        "analysis": analysis,
        "state_summary": result["state_summary"],
        "policy": result["policy"],
    }


def status(root_path: Optional[str | Path] = None) -> Dict[str, Any]:
    paths = ensure_dirs(root_path)
    recs = load_json_folder(paths["recommendations"], 50)
    steps = load_json_folder(paths["next_steps"], 50)

    return {
        "success": True,
        "recommendations_total": len(recs),
        "next_steps_total": len(steps),
        "policy": {
            "mode": "analysis-only",
            "can_execute_commands": False,
            "can_modify_code": False,
            "can_apply_patches": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="K-Atlas Cowork Prompt Generator")
    sub = parser.add_subparsers(dest="action", required=True)

    generate = sub.add_parser("generate")
    generate.add_argument("--root", default=None)

    check = sub.add_parser("status")
    check.add_argument("--root", default=None)

    args = parser.parse_args()

    if args.action == "generate":
        result = generate_next_prompt(args.root)
    else:
        result = status(args.root)

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("success") else 1


if __name__ == "__main__":
    raise SystemExit(main())
