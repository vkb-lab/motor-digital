from __future__ import annotations

import re
from pathlib import Path


BANNED_MAIN_MARKERS = [
    "O que posso acionar agora",
    "Safe Action",
    "Human Gate",
    "Action Packet",
    "Registry de tools",
    "Registry de conexoes",
    "Registry de tenants",
    "Guardrails ativos",
    "Nada foi publicado",
    "Evidência local",
    "Registro tecnico",
    "Comandos internos",
    "Limite de segurança",
    "Ação segura disponível",
    "Responda por texto",
]


STOP_MARKERS = [
    "Seguranca",
    "Segurança",
    "Evidência local",
    "Registro tecnico",
    "Registro técnico",
    "Guardrails ativos",
    "Nada foi publicado",
]


def _strip_noise(text: str) -> str:
    lines = []
    skip = False

    for raw in text.splitlines():
        line = raw.strip()

        if any(marker.lower() in line.lower() for marker in BANNED_MAIN_MARKERS):
            skip = True
            continue

        if skip:
            if line.startswith("Resposta direta") or line.startswith("Contas sociais") or line.startswith("Validacao oficial"):
                skip = False
            else:
                continue

        if any(marker.lower() in line.lower() for marker in BANNED_MAIN_MARKERS):
            continue

        lines.append(raw)

    clean = "\n".join(lines).strip()
    clean = re.sub(r"\n{3,}", "\n\n", clean)
    return clean


def extract_real_operator_answer(raw_text: str) -> str:
    text = raw_text or ""

    if "Resposta direta" in text:
        part = text.split("Resposta direta", 1)[1]
    elif "Rascunho operacional" in text:
        part = text.split("Rascunho operacional", 1)[1]
    else:
        part = text

    for marker in STOP_MARKERS:
        if marker in part:
            part = part.split(marker, 1)[0]

    clean = _strip_noise(part)

    if not clean:
        clean = _strip_noise(text)

    return clean.strip()


def latest_safe_action_answer(root: str | Path = ".") -> str:
    root = Path(root)
    folder = root / "local_runtime" / "kos_safe_actions"

    if not folder.exists():
        return ""

    files = sorted(folder.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)

    if not files:
        return ""

    raw = files[0].read_text(encoding="utf-8", errors="ignore")
    return extract_real_operator_answer(raw)


def compose_for_chat(raw_text: str, root: str | Path = ".") -> dict:
    main = extract_real_operator_answer(raw_text)

    if not main or len(main) < 40:
        main = latest_safe_action_answer(root)

    return {
        "user_response": main.strip(),
        "technical_evidence": raw_text.strip(),
    }
