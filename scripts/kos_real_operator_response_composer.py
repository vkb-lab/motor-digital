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
    "Evid?ncia local",
    "Evidencia local",
    "Registro tecnico",
    "Registro t?cnico",
    "Comandos internos",
    "Limite de seguran?a",
    "A??o segura dispon?vel",
    "Acao segura disponivel",
    "Responda por texto",
    "Publicacao executada",
    "Publica??o executada",
    "Navegador logado usado",
    "Scraping usado",
    "returncode=",
    "provider=",
    "risco=",
    "target=",
    "status=",
    "publish bloqueado",
    "blocked_without_human_gate",
    "validate_read_only",
]


STOP_MARKERS = [
    "Seguranca",
    "Seguran?a",
    "Evid?ncia local",
    "Evidencia local",
    "Registro tecnico",
    "Registro t?cnico",
    "Guardrails ativos",
    "Nada foi publicado",
]


def _first_match(pattern: str, text: str, default: str = "") -> str:
    match = re.search(pattern, text, flags=re.IGNORECASE)
    if not match:
        return default
    return match.group(1).strip()


def _has(text: str, value: str) -> bool:
    return value.lower() in text.lower()


def _format_instagram_audit(text: str) -> str | None:
    lower = text.lower()

    if "instagram conectado operacionalmente" not in lower and "@hupmix" not in lower:
        return None

    account = _first_match(r"Conta:\s*(@[A-Za-z0-9_.]+)", text, "@hupmix")
    ig_id = _first_match(r"IG ID:\s*([0-9]+)", text)
    media_total = _first_match(r"Midias no perfil:\s*([0-9]+)", text) or _first_match(r"M?dias no perfil:\s*([0-9]+)", text)
    recent = _first_match(r"Midias recentes lidas:\s*([0-9]+)", text) or _first_match(r"M?dias recentes lidas:\s*([0-9]+)", text)

    lines: list[str] = []

    lines.append("Instagram conectado agora: Hupmix.")

    found = []
    if _has(text, "Casa da Limpeza") or _has(text, "casa_da_limpeza"):
        found.append("Casa da Limpeza: registrada localmente.")
    if _has(text, "Parada Atlantida") or _has(text, "Parada Atl?ntida") or _has(text, "parada_atlantida"):
        found.append("Parada Atl?ntida: travada para a??es externas.")

    if found:
        lines.append("")
        lines.append("Tamb?m encontrei:")
        for item in found:
            lines.append(f"- {item}")

    lines.append("")
    lines.append("Valida??o oficial da Hupmix:")
    if account:
        lines.append(f"- Conta: {account}")
    if ig_id:
        lines.append(f"- IG ID: {ig_id}")
    if media_total:
        lines.append(f"- M?dias no perfil: {media_total}")
    if recent:
        lines.append(f"- M?dias recentes lidas: {recent}")

    lines.append("")
    lines.append("Posso revisar a ?ltima publica??o, gerar uma legenda melhor ou comparar as ?ltimas postagens.")

    return "\n".join(lines).strip()


def _strip_noise(text: str) -> str:
    cleaned_lines = []

    for raw in text.splitlines():
        line = raw.strip()

        if not line:
            cleaned_lines.append("")
            continue

        if any(marker.lower() in line.lower() for marker in BANNED_MAIN_MARKERS):
            continue

        # Remove linhas t?cnicas com pipes de registry.
        if "|" in line and any(x in line.lower() for x in ["target=", "status=", "provider=", "risco=", "publish"]):
            continue

        cleaned_lines.append(raw)

    clean = "\n".join(cleaned_lines).strip()
    clean = re.sub(r"\n{3,}", "\n\n", clean)
    return clean


def extract_real_operator_answer(raw_text: str) -> str:
    text = raw_text or ""

    instagram = _format_instagram_audit(text)
    if instagram:
        return instagram

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
