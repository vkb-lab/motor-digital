# -*- coding: utf-8 -*-
"""
K-Atlas OS - Cowork Mode

Modo de cowork supervisionado entre:
- operador humano
- engenheiro IA
- K-Atlas OS

Este modulo NAO controla navegador.
Este modulo NAO acessa ChatGPT automaticamente.
Este modulo NAO executa patches sozinho.

Ele registra ciclos operacionais do tipo:
1. pedir proximo passo
2. executar comando
3. colar resultado
4. validar
5. registrar aprendizado
6. repetir ate 10 passos
"""

from __future__ import annotations

import argparse
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


ROOT = Path(__file__).resolve().parents[2]
COWORK_DIR = ROOT / "k_atlas" / "cowork"
SESSIONS_DIR = COWORK_DIR / "sessions"
STEPS_DIR = COWORK_DIR / "steps"
REVIEWS_DIR = COWORK_DIR / "reviews"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_dirs() -> None:
    for path in [COWORK_DIR, SESSIONS_DIR, STEPS_DIR, REVIEWS_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(path)


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def latest_session_file() -> Optional[Path]:
    ensure_dirs()
    files = sorted(SESSIONS_DIR.glob("*.json"))
    if not files:
        return None
    return files[-1]


def start_session(goal: str, max_steps: int = 10) -> Dict[str, Any]:
    ensure_dirs()

    session_id = str(uuid.uuid4())
    created_at = now_iso()

    data = {
        "session_id": session_id,
        "goal": goal,
        "status": "active",
        "max_steps": max_steps,
        "current_step": 0,
        "created_at": created_at,
        "updated_at": created_at,
        "rules": {
            "supervised": True,
            "human_pastes_commands": True,
            "no_browser_control": True,
            "no_auto_patch_apply": True,
            "no_auto_approval": True,
            "evaluate_after_10_steps": True
        },
        "steps": []
    }

    path = SESSIONS_DIR / (created_at.replace(":", "").replace("-", "").split(".")[0] + "_" + session_id + ".json")
    write_json(path, data)

    return {
        "success": True,
        "message": "Sessao Cowork iniciada.",
        "session_path": str(path),
        "session": data,
        "next_instruction": "Peça ao engenheiro IA o próximo passo operacional e registre com cowork.py step."
    }


def get_status() -> Dict[str, Any]:
    path = latest_session_file()

    if path is None:
        return {
            "success": True,
            "active": False,
            "message": "Nenhuma sessao Cowork encontrada."
        }

    data = read_json(path)

    return {
        "success": True,
        "active": data.get("status") == "active",
        "session_path": str(path),
        "session": data
    }


def add_step(
    title: str,
    command: str,
    result_summary: str = "",
    status: str = "pending",
    risk: str = "low",
) -> Dict[str, Any]:
    ensure_dirs()

    path = latest_session_file()
    if path is None:
        raise RuntimeError("Nenhuma sessao ativa. Rode primeiro: python .\\k_atlas\\cowork\\cowork.py start")

    session = read_json(path)

    step_number = int(session.get("current_step", 0)) + 1
    step_id = str(uuid.uuid4())
    created_at = now_iso()

    step = {
        "step_id": step_id,
        "step_number": step_number,
        "title": title,
        "command": command,
        "result_summary": result_summary,
        "status": status,
        "risk": risk,
        "created_at": created_at,
        "updated_at": created_at,
    }

    session["current_step"] = step_number
    session["updated_at"] = created_at
    session.setdefault("steps", []).append(step)

    if step_number >= int(session.get("max_steps", 10)):
        session["status"] = "ready_for_review"

    write_json(path, session)

    step_path = STEPS_DIR / (created_at.replace(":", "").replace("-", "").split(".")[0] + "_step_" + str(step_number) + ".json")
    write_json(step_path, step)

    return {
        "success": True,
        "message": "Passo registrado.",
        "session_path": str(path),
        "step_path": str(step_path),
        "step": step,
        "session_status": session["status"]
    }


def review_session() -> Dict[str, Any]:
    path = latest_session_file()
    if path is None:
        raise RuntimeError("Nenhuma sessao encontrada.")

    session = read_json(path)
    steps = session.get("steps", [])

    done = [item for item in steps if item.get("status") in ["done", "ok", "success"]]
    failed = [item for item in steps if item.get("status") in ["failed", "error"]]
    pending = [item for item in steps if item.get("status") == "pending"]

    score = 0
    if steps:
        score = round((len(done) / len(steps)) * 10, 1)

    review = {
        "review_id": str(uuid.uuid4()),
        "session_id": session.get("session_id"),
        "created_at": now_iso(),
        "goal": session.get("goal"),
        "steps_total": len(steps),
        "done": len(done),
        "failed": len(failed),
        "pending": len(pending),
        "score": score,
        "decision": "avaliar com professor",
        "recommendation": "Continuar apenas se os passos forem pequenos, testados e commitados.",
        "next_safe_step": "Gerar relatorio AutoReporter da sessao Cowork.",
        "session_path": str(path),
    }

    review_path = REVIEWS_DIR / (review["created_at"].replace(":", "").replace("-", "").split(".")[0] + "_review.json")
    write_json(review_path, review)

    return {
        "success": True,
        "message": "Review da sessao Cowork gerado.",
        "review_path": str(review_path),
        "review": review
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="K-Atlas Cowork Mode")
    sub = parser.add_subparsers(dest="action", required=True)

    start = sub.add_parser("start")
    start.add_argument("--goal", required=True)
    start.add_argument("--max-steps", type=int, default=10)

    sub.add_parser("status")

    step = sub.add_parser("step")
    step.add_argument("--title", required=True)
    step.add_argument("--command", required=True)
    step.add_argument("--result-summary", default="")
    step.add_argument("--status", default="pending")
    step.add_argument("--risk", default="low")

    sub.add_parser("review")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.action == "start":
        result = start_session(goal=args.goal, max_steps=args.max_steps)

    elif args.action == "status":
        result = get_status()

    elif args.action == "step":
        result = add_step(
            title=args.title,
            command=args.command,
            result_summary=args.result_summary,
            status=args.status,
            risk=args.risk,
        )

    elif args.action == "review":
        result = review_session()

    else:
        result = {
            "success": False,
            "message": "Acao desconhecida."
        }

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("success") else 1


if __name__ == "__main__":
    raise SystemExit(main())
