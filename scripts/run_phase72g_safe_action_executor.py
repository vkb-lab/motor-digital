from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]
ACTION_ROUTER_DIR = ROOT / "local_runtime" / "kos_action_router"
LATEST_PACKET = ACTION_ROUTER_DIR / "latest_action_packet.json"
SAFE_DIR = ROOT / "local_runtime" / "kos_safe_actions"
LATEST_SAFE_ACTION = SAFE_DIR / "latest_safe_action.json"
EVENTS = SAFE_DIR / "events.jsonl"
TOOL_REGISTRY = ROOT / "memory" / "kos_governance" / "KOS_TOOL_REGISTRY.json"
CONNECTION_REGISTRY = ROOT / "memory" / "kos_governance" / "KOS_CONNECTION_REGISTRY.json"
TENANT_REGISTRY = ROOT / "memory" / "kos_governance" / "KOS_TENANT_REGISTRY.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path) -> dict:
    if not path.exists():
        return {"status": "MISSING", "path": str(path)}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        return {"status": "READ_ERROR", "error": str(exc), "path": str(path)}


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def as_lines(items: list[str]) -> str:
    return "\n".join("- " + item for item in items)


def normalize_ascii(text: str) -> str:
    table = str.maketrans({
        "á": "a", "à": "a", "â": "a", "ã": "a",
        "é": "e", "ê": "e",
        "í": "i",
        "ó": "o", "ô": "o", "õ": "o",
        "ú": "u",
        "ç": "c",
        "Á": "a", "À": "a", "Â": "a", "Ã": "a",
        "É": "e", "Ê": "e",
        "Í": "i",
        "Ó": "o", "Ô": "o", "Õ": "o",
        "Ú": "u",
        "Ç": "c",
    })
    return str(text or "").lower().translate(table)


def get_packet_tenant(packet: dict) -> dict:
    tenant = packet.get("tenant")
    if isinstance(tenant, dict):
        return tenant
    return {}


def get_packet_pack(packet: dict) -> dict:
    pack = packet.get("product_capability_pack")
    if isinstance(pack, dict):
        return pack
    return {}



def kos_is_social_read_request(value: str) -> bool:
    table = str.maketrans({
        "á": "a", "à": "a", "â": "a", "ã": "a",
        "é": "e", "ê": "e",
        "í": "i",
        "ó": "o", "ô": "o", "õ": "o",
        "ú": "u",
        "ç": "c",
        "Á": "a", "À": "a", "Â": "a", "Ã": "a",
        "É": "e", "Ê": "e",
        "Í": "i",
        "Ó": "o", "Ô": "o", "Õ": "o",
        "Ú": "u",
        "Ç": "c",
    })
    text = str(value or "").lower().translate(table)
    social_markers = ["hupmix", "instagram", "post", "publicacao", "publicacoes", "reels", "story", "stories", "perfil"]
    read_markers = ["veja", "ver", "olhar", "olhe", "ultima", "ultimo", "analisar", "analise", "avaliar", "auditar", "revisar", "ler", "leia"]
    return any(word in text for word in social_markers) and any(word in text for word in read_markers)


def build_social_read(packet: dict) -> dict:
    request_text = str(packet.get("request", "")).lower()
    if "hupmix" in request_text and ("gp_video_01" in request_text or "video_01" in request_text or "roteiro cena a cena" in request_text or "garoto oxy" in request_text or "checklist de grava" in request_text):
        return build_hupmix_gp_video_01_production_kit(packet)

    request = packet.get("request", "")

    def clip(value, limit=900):
        value = str(value or "")
        if len(value) <= limit:
            return value
        return value[:limit].rstrip() + "..."

    def safe_number(value):
        if value is None:
            return "nao informado"
        return str(value)

    def fallback(reason, detail=""):
        items = [
            "O K-OS tentou usar o conector oficial Meta/Instagram em modo read-only.",
            "Nenhum navegador logado foi usado.",
            "Nenhum scraping foi usado.",
            "Nenhuma publicacao foi executada.",
            "Motivo: " + str(reason),
        ]
        if detail:
            items.append("Detalhe tecnico resumido: " + clip(detail, 500))

        return {
            "title": "Analise oficial de publicacao Hupmix",
            "summary": "Conector oficial nao completou a leitura. Nenhuma acao externa foi executada.",
            "sections": [
                {"title": "Pedido original", "items": [request]},
                {"title": "Status", "items": items},
                {"title": "Proxima acao segura", "items": [
                    "Verificar token Meta, permissao do app ou relatorio local.",
                    "Nao publicar nada ate nova validacao."
                ]},
            ],
        }

    audit_script = ROOT / "scripts" / "run_phase69d_hupmix_instagram_audit.py"
    audit_report = ROOT / "local_runtime" / "kos_instagram_audit" / "hupmix" / "latest_hupmix_instagram_audit.json"

    if not audit_script.exists():
        return fallback("script oficial de auditoria Hupmix nao encontrado")

    try:
        subprocess = __import__("subprocess")
        sysmod = __import__("sys")
        completed = subprocess.run(
            [sysmod.executable, str(audit_script)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=90,
        )
    except Exception as exc:
        return fallback("erro ao chamar auditoria oficial", str(exc))

    if not audit_report.exists():
        return fallback("relatorio oficial de auditoria nao encontrado", completed.stderr or completed.stdout)

    audit = read_json(audit_report)

    if audit.get("status") != "KOS_HUPMIX_INSTAGRAM_AUDIT_CONNECTED":
        return fallback(
            audit.get("status", "auditoria nao conectada"),
            json.dumps(audit.get("graph_error", audit), ensure_ascii=False)[:900],
        )

    media_items = audit.get("recent_media_summary", []) or []
    latest = media_items[0] if media_items else {}

    caption = latest.get("caption_preview", "")
    caption_lower = caption.lower()
    first_line = caption.splitlines()[0].strip() if caption else "Sem legenda disponivel na amostra."
    likes = latest.get("like_count")
    comments = latest.get("comments_count")

    strengths = []
    risks = []
    suggestions = []

    if "r$" in caption_lower or "por apenas" in caption_lower:
        strengths.append("Oferta/preco aparece de forma clara na legenda.")
    if "passe na" in caption_lower or "direct" in caption_lower or "chame" in caption_lower:
        strengths.append("Existe chamada para acao ou direcao de contato.")
    if "sem cloro" in caption_lower or "nao toxico" in caption_lower or "limpa tudo" in caption_lower:
        strengths.append("Beneficios do produto aparecem de forma objetiva.")

    if not strengths:
        strengths.append("A publicacao possui conteudo suficiente para analise inicial.")

    if likes is not None and comments is not None and int(comments or 0) == 0:
        risks.append("Comentarios zerados indicam baixa conversa publica no post.")
    if len(caption) > 700:
        risks.append("Legenda longa. Pode precisar de gancho mais direto nos primeiros segundos.")
    if not risks:
        risks.append("Nenhum risco critico identificado na leitura resumida.")

    suggestions.append("Reforcar o gancho inicial com dor + promessa em uma frase curta.")
    suggestions.append("Adicionar CTA mais direto para WhatsApp, direct ou visita na loja.")
    suggestions.append("Transformar esta leitura em proximo post, story ou oferta da semana somente apos revisao humana.")

    latest_items = []
    if latest:
        latest_items = [
            "Tipo: " + str(latest.get("media_type", "nao informado")),
            "Data: " + str(latest.get("timestamp", "nao informado")),
            "Link: " + str(latest.get("permalink", "nao informado")),
            "Curtidas: " + safe_number(likes),
            "Comentarios: " + safe_number(comments),
            "Gancho inicial: " + clip(first_line, 280),
            "Legenda resumida: " + clip(caption, 900),
        ]
    else:
        latest_items = ["Nenhuma midia recente retornada pela auditoria oficial."]

    return {
        "title": "Analise oficial da ultima publicacao Hupmix",
        "summary": "Leitura feita via Meta Graph API oficial. Nenhum navegador, scraping ou publicacao foi usado.",
        "sections": [
            {"title": "Pedido original", "items": [request]},
            {"title": "Fonte oficial usada", "items": [
                "Meta Graph API oficial.",
                "Conta: @" + str(audit.get("username", "hupmix")),
                "IG ID: " + str(audit.get("ig_id", "")),
                "Midias totais no perfil: " + safe_number(audit.get("media_count")),
                "Publicacao executada: nao.",
                "Navegador logado usado: nao.",
                "Scraping usado: nao.",
            ]},
            {"title": "Ultima publicacao encontrada", "items": latest_items},
            {"title": "Pontos fortes", "items": strengths},
            {"title": "Pontos de atencao", "items": risks},
            {"title": "Sugestoes de melhoria", "items": suggestions},
            {"title": "Proxima acao segura", "items": [
                "Gerar sugestao de legenda revisada em rascunho.",
                "Criar plano de stories de apoio sem publicar automaticamente.",
                "Manter publicacao real bloqueada ate gate humano explicito."
            ]},
        ],
    }



def build_hupmix_gp_video_01_production_kit(packet: dict) -> dict:
    request = packet.get("request", "")

    package_path = ROOT / "campaigns" / "hupmix_gp_recovery" / "KOS_HUPMIX_GP_CONTINUITY_PACKAGE.json"
    kit_json_path = ROOT / "campaigns" / "hupmix_gp_recovery" / "GP_VIDEO_01_PRODUCTION_KIT.json"
    kit_md_path = ROOT / "campaigns" / "hupmix_gp_recovery" / "GP_VIDEO_01_PRODUCTION_KIT.md"

    if not package_path.exists():
        return {
            "title": "GP_VIDEO_01 Production Kit - Hupmix",
            "summary": "Pacote base GP Hupmix nao encontrado. Nenhuma publicacao foi executada.",
            "sections": [
                {"title": "Pedido original", "items": [request]},
                {"title": "Proxima acao segura", "items": [
                    "Recuperar o pacote KOS_HUPMIX_GP_CONTINUITY_PACKAGE.json.",
                    "Nao publicar nada."
                ]},
            ],
        }

    package = json.loads(package_path.read_text(encoding="utf-8"))
    videos = package.get("videos", []) or []
    video = next((v for v in videos if str(v.get("id", "")).upper() == "GP_VIDEO_01"), videos[0] if videos else {})
    stories_base = package.get("stories", []) or []

    existing_created_at = None
    if kit_json_path.exists():
        try:
            existing_created_at = json.loads(kit_json_path.read_text(encoding="utf-8")).get("created_at")
        except Exception:
            existing_created_at = None

    final_caption = (
        "A solução que faltava para a limpeza da sua casa chegou na HupMix. "
        "Oxy Power limpa com Oxigênio Ativo, sem cloro e sem toxicidade. "
        "Ideal para quem quer praticidade, rendimento e resultado de verdade. "
        "Passe na HupMix ou chame no WhatsApp e garanta o seu Oxy Power 5L."
    )

    scenes = [
        {
            "scene": "Cena 1 - Gancho inicial",
            "duration": "0s a 3s",
            "visual": "Garoto Oxy entra em cena segurando o Oxy Power 5L.",
            "speech": "A solução que faltava para a limpeza da sua casa chegou.",
            "screen_text": "A solução que faltava!",
            "take": "Plano medio, energia alta, produto visivel."
        },
        {
            "scene": "Cena 2 - Dor do cliente",
            "duration": "3s a 7s",
            "visual": "Mostrar piso, box, bancada ou cozinha com sujeira comum.",
            "speech": "Sujeira no piso, gordura na cozinha ou box embaçado? O Oxy Power ajuda.",
            "screen_text": "Limpeza difícil?",
            "take": "Take antes, aproximado, mostrando o problema."
        },
        {
            "scene": "Cena 3 - Aplicacao",
            "duration": "7s a 13s",
            "visual": "Aplicar o produto e passar pano/esponja na superfície.",
            "speech": "Ele usa Oxigênio Ativo para limpar de forma prática, sem cloro e sem toxicidade.",
            "screen_text": "Oxigênio Ativo",
            "take": "Close na aplicação e movimento de limpeza."
        },
        {
            "scene": "Cena 4 - Resultado",
            "duration": "13s a 20s",
            "visual": "Mostrar antes e depois com corte rapido.",
            "speech": "Olha a diferença. É limpeza forte para o dia a dia.",
            "screen_text": "Antes e depois",
            "take": "Comparativo visual claro, sem exagero."
        },
        {
            "scene": "Cena 5 - Oferta e CTA",
            "duration": "20s a 30s",
            "visual": "Close no produto, preço e chamada para loja/WhatsApp.",
            "speech": "Oxy Power 5 litros por R$ 49,90. Passe na HupMix ou chame no WhatsApp.",
            "screen_text": "5L por R$ 49,90",
            "take": "Produto centralizado, preço legível, CTA final."
        }
    ]

    talks = [
        "A solução que faltava para a limpeza da sua casa chegou.",
        "Sujeira no piso, gordura na cozinha ou box embaçado? O Oxy Power ajuda.",
        "Ele usa Oxigênio Ativo para limpar de forma prática, sem cloro e sem toxicidade.",
        "Olha a diferença. É limpeza forte para o dia a dia.",
        "Oxy Power 5 litros por R$ 49,90. Passe na HupMix ou chame no WhatsApp."
    ]

    takes = [
        "Produto Oxy Power 5L em destaque.",
        "Garoto Oxy segurando o produto.",
        "Superficie suja antes da aplicação.",
        "Aplicação do produto.",
        "Limpeza com pano ou esponja.",
        "Resultado depois da limpeza.",
        "Close no preço.",
        "Take final com CTA para HupMix/WhatsApp."
    ]

    stories = [
        "Story 1: Enquete - Qual parte da casa dá mais trabalho para limpar?",
        "Story 2: Bastidor curto do Garoto Oxy preparando o teste.",
        "Story 3: Antes/depois do teste com Oxy Power.",
        "Story 4: Oferta - Oxy Power 5L por R$ 49,90.",
        "Story 5: CTA - Quer reservar o seu? Chame no WhatsApp ou passe na HupMix."
    ]

    checklist = [
        "Confirmar preço atualizado antes de publicar.",
        "Confirmar estoque do Oxy Power 5L.",
        "Confirmar endereço, telefone ou WhatsApp correto.",
        "Separar produto limpo e bem apresentado.",
        "Gravar em local bem iluminado.",
        "Capturar antes e depois real.",
        "Evitar promessas exageradas.",
        "Revisar legenda final.",
        "Aprovar manualmente antes de qualquer publicação real."
    ]

    kit = {
        "status": "KOS_HUPMIX_GP_VIDEO_01_PRODUCTION_KIT_READY",
        "created_at": existing_created_at or datetime.now(timezone.utc).isoformat(),
        "brand": "Hupmix",
        "campaign": "GP / Garoto Oxy Power / Oxy Power",
        "video_id": "GP_VIDEO_01",
        "title": "O heroi da limpeza chegou",
        "format": "Reel 20-30s",
        "base_hook": video.get("hook", "A solucao que faltava para limpar tudo sem complicar."),
        "final_caption": final_caption,
        "scenes": scenes,
        "garoto_oxy_lines": talks,
        "takes": takes,
        "stories": stories,
        "recording_checklist": checklist,
        "safety": {
            "instagram_publish_executed": False,
            "browser_logged_account_automation_used": False,
            "scraping_used": False,
            "human_gate_required": True
        }
    }

    kit_json_path.write_text(json.dumps(kit, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = []
    lines.append("# GP_VIDEO_01 Production Kit - Hupmix")
    lines.append("")
    lines.append("Status: roteiro final de gravação gerado. Nada foi publicado.")
    lines.append("")
    lines.append("## Campanha")
    lines.append("- Marca: Hupmix")
    lines.append("- Campanha: GP / Garoto Oxy Power / Oxy Power")
    lines.append("- Formato: Reel 20-30s")
    lines.append("")
    lines.append("## Roteiro cena a cena")
    for scene in scenes:
        lines.append(f"### {scene['scene']}")
        lines.append(f"- Tempo: {scene['duration']}")
        lines.append(f"- Visual: {scene['visual']}")
        lines.append(f"- Fala: {scene['speech']}")
        lines.append(f"- Texto na tela: {scene['screen_text']}")
        lines.append(f"- Take: {scene['take']}")
        lines.append("")
    lines.append("## Falas do Garoto Oxy")
    for item in talks:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Lista de takes")
    for item in takes:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Legenda final")
    lines.append(final_caption)
    lines.append("")
    lines.append("## Stories de apoio")
    for item in stories:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Checklist de gravação")
    for item in checklist:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Guardrails")
    lines.append("- Não publicar automaticamente.")
    lines.append("- Não usar navegador logado.")
    lines.append("- Não fazer scraping.")
    lines.append("- Exigir aprovação humana antes de qualquer publicação real.")

    kit_md_path.write_text("\n".join(lines), encoding="utf-8")

    return {
        "title": "GP_VIDEO_01 Production Kit - Hupmix",
        "summary": "Roteiro final de gravação gerado a partir do pacote GP recuperado. Nenhuma publicação foi executada.",
        "sections": [
            {"title": "Pedido original", "items": [request]},
            {"title": "Campanha", "items": [
                "Marca: Hupmix",
                "Campanha: GP / Garoto Oxy Power / Oxy Power",
                "Video: GP_VIDEO_01 - O heroi da limpeza chegou",
                "Formato: Reel 20-30s"
            ]},
            {"title": "Roteiro cena a cena", "items": [
                f"{s['scene']} | {s['duration']} | Fala: {s['speech']} | Take: {s['take']}" for s in scenes
            ]},
            {"title": "Falas do Garoto Oxy", "items": talks},
            {"title": "Lista de takes", "items": takes},
            {"title": "Legenda final", "items": [final_caption]},
            {"title": "Stories de apoio", "items": stories},
            {"title": "Checklist de gravacao", "items": checklist},
            {"title": "Arquivos gerados", "items": [
                str(kit_md_path),
                str(kit_json_path)
            ]},
            {"title": "Seguranca operacional", "items": [
                "Publicacao executada: false",
                "Navegador logado usado: false",
                "Scraping usado: false",
                "Gate humano requerido: true"
            ]},
            {"title": "Proxima acao segura", "items": [
                "Gravar o GP_VIDEO_01 seguindo o checklist.",
                "Depois enviar o video final para readiness.",
                "Nao publicar sem aprovacao humana explicita."
            ]},
        ],
    }



def build_hupmix_gp_continuity(packet: dict) -> dict:
    request = packet.get("request", "")

    package_path = ROOT / "campaigns" / "hupmix_gp_recovery" / "KOS_HUPMIX_GP_CONTINUITY_PACKAGE.json"
    markdown_path = ROOT / "campaigns" / "hupmix_gp_recovery" / "KOS_HUPMIX_GP_CONTINUITY_PACKAGE.md"

    def clip(value, limit=700):
        value = str(value or "")
        if len(value) <= limit:
            return value
        return value[:limit].rstrip() + "..."

    if not package_path.exists():
        return {
            "title": "Continuidade GP Hupmix",
            "summary": "Pacote GP ainda nao encontrado. Nenhuma acao real foi executada.",
            "sections": [
                {"title": "Pedido original", "items": [request]},
                {"title": "Proxima acao segura", "items": [
                    "Gerar novamente o pacote de continuidade GP Hupmix.",
                    "Nao publicar nada ate o pacote ser recuperado."
                ]},
            ],
        }

    package = json.loads(package_path.read_text(encoding="utf-8"))

    videos = package.get("videos", []) or []
    stories = package.get("stories", []) or []
    calendar = package.get("calendar_7_days", []) or []
    approval = package.get("approval_gate", []) or []
    source = package.get("source", {}) or {}
    safety = package.get("safety", {}) or {}

    video_items = []
    for video in videos:
        video_items.append(
            str(video.get("id", "VIDEO")) + " - " +
            str(video.get("title", "Sem titulo")) +
            " | Formato: " + str(video.get("format", "nao informado")) +
            " | Gancho: " + clip(video.get("hook", ""), 180) +
            " | CTA: " + clip(video.get("cta", ""), 160)
        )

    first_video = videos[0] if videos else {}
    first_script = first_video.get("script", []) or []

    return {
        "title": "Continuidade oficial da campanha GP Hupmix",
        "summary": "Pacote de continuidade recuperado do repositorio. Nenhuma publicacao foi executada.",
        "sections": [
            {"title": "Pedido original", "items": [request]},
            {"title": "Campanha recuperada", "items": [
                "Marca: " + str(package.get("brand", "Hupmix")),
                "Campanha: " + str(package.get("campaign", "GP / Garoto Oxy Power / Oxy Power")),
                "Status: " + str(package.get("status", "pacote recuperado")),
                "Base Instagram: " + str(source.get("latest_permalink", "nao informado")),
                "Arquivos locais relacionados na auditoria: " + str(source.get("local_matches_count", "nao informado")),
            ]},
            {"title": "Proximos videos planejados", "items": video_items or ["Nenhum video planejado encontrado no pacote."]},
            {"title": "Proximo video recomendado", "items": [
                "ID: " + str(first_video.get("id", "nao informado")),
                "Titulo: " + str(first_video.get("title", "nao informado")),
                "Formato: " + str(first_video.get("format", "nao informado")),
                "Gancho: " + str(first_video.get("hook", "nao informado")),
                "Legenda base: " + clip(first_video.get("caption", "nao informado"), 500),
                "CTA: " + str(first_video.get("cta", "nao informado")),
            ]},
            {"title": "Roteiro do proximo video", "items": first_script or ["Roteiro nao encontrado."]},
            {"title": "Stories de apoio", "items": stories or ["Nenhum story planejado encontrado."]},
            {"title": "Calendario de 7 dias", "items": calendar or ["Calendario nao encontrado."]},
            {"title": "Gate humano obrigatorio", "items": approval or [
                "Revisar preco.",
                "Confirmar estoque.",
                "Aprovar manualmente antes de qualquer publicacao real."
            ]},
            {"title": "Seguranca operacional", "items": [
                "Publicacao executada: " + str(bool(safety.get("instagram_publish_executed", False))).lower(),
                "Navegador logado usado: " + str(bool(safety.get("browser_logged_account_automation_used", False))).lower(),
                "Scraping usado: " + str(bool(safety.get("scraping_used", False))).lower(),
                "Gate humano requerido: " + str(bool(safety.get("human_gate_required", True))).lower(),
                "Arquivo base: " + str(markdown_path),
            ]},
            {"title": "Proxima acao segura", "items": [
                "Gerar versao final do roteiro GP_VIDEO_01 para gravacao.",
                "Gerar lista de cenas e falas do Garoto Oxy.",
                "Gerar legenda final em rascunho.",
                "Nao publicar sem aprovacao humana explicita."
            ]},
        ],
    }



def build_social(packet: dict) -> dict:
    tenant = get_packet_tenant(packet)
    pack = get_packet_pack(packet)
    tenant_id = str(tenant.get("id") or "")
    tenant_name = str(tenant.get("name") or tenant_id or "Hupmix")
    pack_name = str(pack.get("name") or "Ki-Publica")
    if tenant_id == "casa_da_limpeza":
        request = packet.get("request", "")
        days = [
            "Dia 1: apresentar a Casa da Limpeza como solucao local para rotina de limpeza.",
            "Dia 2: dor comum do cliente: produto errado, perda de tempo e resultado fraco.",
            "Dia 3: dica pratica com produto/servico em destaque, sem promessa exagerada.",
            "Dia 4: bastidor de loja, atendimento ou organizacao de prateleira.",
            "Dia 5: oferta educativa com CTA para WhatsApp ou visita, apos revisar preco/estoque.",
            "Dia 6: prova social ou pergunta para gerar conversa.",
            "Dia 7: resumo da semana e convite para pedir indicacao personalizada."
        ]
        return {
            "title": "Rascunho seguro Ki-Publica - Casa da Limpeza",
            "summary": "Plano social de 7 dias criado para Casa da Limpeza dentro do capability pack Ki-Publica. Nada foi publicado.",
            "sections": [
                {"title": "Pedido original", "items": [request]},
                {"title": "Resolucao de contexto", "items": [
                    "Capability pack: " + pack_name,
                    "Tenant: " + tenant_name,
                    "Fallback Hupmix usado: false",
                    "Config tenant: " + str(tenant.get("config", "config/tenants/casa_da_limpeza.json")),
                    "Permissoes: " + str(tenant.get("client_permissions", "clients/casa_da_limpeza/permissions.json")),
                ]},
                {"title": "Plano de 7 dias", "items": days},
                {"title": "Evidencia consultada", "items": [
                    str(TOOL_REGISTRY),
                    str(TENANT_REGISTRY),
                    "config/products/ki_publica.json",
                    "config/tenants/casa_da_limpeza.json",
                    "clients/casa_da_limpeza/permissions.json"
                ]},
                {"title": "Proximo passo por texto", "items": [
                    "Digite confirmar para manter este rascunho como direcao.",
                    "Digite alterar e descreva o ajuste desejado.",
                    "Digite cancelar para encerrar sem criar nova acao."
                ]},
                {"title": "Bloqueios preservados", "items": [
                    "Publicacao automatica bloqueada.",
                    "Envio real, anuncio real, cobranca e edicao Google real bloqueados.",
                    "Human Gate obrigatorio antes de qualquer acao externa."
                ]},
            ],
        }

    request_text = str(packet.get("request", "")).lower()
    if "hupmix" in request_text and ("gp_video_01" in request_text or "video_01" in request_text or "roteiro cena a cena" in request_text or "garoto oxy" in request_text or "checklist de grava" in request_text):
        return build_hupmix_gp_video_01_production_kit(packet)

    request_text = str(packet.get("request", "")).lower()
    if "hupmix" in request_text and ("gp" in request_text or "garoto" in request_text or "oxy" in request_text):
        return build_hupmix_gp_continuity(packet)

    if kos_is_social_read_request(packet.get("request", "")):
        return build_social_read(packet)
    request = packet.get("request", "")
    days = [
        "Dia 1: promessa principal da Hupmix e chamada para conhecer a marca.",
        "Dia 2: dor do cliente e como a Hupmix resolve de forma simples.",
        "Dia 3: prova social ou bastidor leve.",
        "Dia 4: oferta educativa sem venda agressiva.",
        "Dia 5: comparativo antes/depois ou checklist.",
        "Dia 6: chamada para conversa ou direct.",
        "Dia 7: resumo da semana e convite para proximo passo."
    ]
    return {
        "title": "Rascunho seguro de campanha Hupmix",
        "summary": "Plano de 7 dias criado em modo rascunho. Nenhuma publicacao foi executada.",
        "sections": [
            {"title": "Pedido original", "items": [request]},
            {"title": "Plano de 7 dias", "items": days},
            {"title": "Proximo passo humano", "items": ["Revisar tema, imagens e legenda antes de qualquer publicacao."]},
            {"title": "Bloqueios preservados", "items": ["Publicacao automatica bloqueada.", "Instagram real exige confirmacao humana."]},
        ],
    }


def build_instagram_accounts_status(packet: dict) -> dict:
    request = packet.get("request", "")
    tenant_registry = read_json(TENANT_REGISTRY)
    connection_registry = read_json(CONNECTION_REGISTRY)

    instagram_connections = []
    for item in connection_registry.get("connections", []) or []:
        item_id = str(item.get("id", "")).lower()
        provider = str(item.get("provider", "")).lower()
        if "instagram" in item_id or "meta" in item_id or provider == "meta":
            instagram_connections.append(
                str(item.get("name", item.get("id")))
                + " | provider=" + str(item.get("provider", "n/a"))
                + " | status=" + str(item.get("status", "n/a"))
                + " | risco=" + str(item.get("risk", "n/a"))
            )

    registered_accounts = []
    for tenant in tenant_registry.get("tenants", []) or []:
        if "ki_publica" in (tenant.get("capability_packs", []) or []):
            publish = "publish bloqueado" if tenant.get("external_publish_enabled") is False else "publish permitido por config"
            registered_accounts.append(
                str(tenant.get("name", tenant.get("id")))
                + " | target=" + str(tenant.get("default_social_target", tenant.get("id")))
                + " | status=" + str(tenant.get("status", "unknown"))
                + " | " + publish
            )

    audit_items = []
    audit_script = ROOT / "scripts" / "run_phase69d_hupmix_instagram_audit.py"
    audit_report = ROOT / "local_runtime" / "kos_instagram_audit" / "hupmix" / "latest_hupmix_instagram_audit.json"
    if audit_script.exists():
        try:
            subprocess = __import__("subprocess")
            completed = subprocess.run(
                [sys.executable, str(audit_script)],
                cwd=str(ROOT),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=90,
            )
            audit_items.append("Auditoria Hupmix read-only executada: returncode=" + str(completed.returncode))
        except Exception as exc:
            audit_items.append("Auditoria Hupmix falhou antes de completar: " + str(exc))
    else:
        audit_items.append("Auditoria Hupmix nao encontrada: " + str(audit_script))

    audit = read_json(audit_report) if audit_report.exists() else {}
    if audit.get("status") == "KOS_HUPMIX_INSTAGRAM_AUDIT_CONNECTED":
        audit_items.extend([
            "Hupmix conectado via Meta Graph.",
            "Conta: @" + str(audit.get("username", "hupmix")),
            "IG ID: " + str(audit.get("ig_id", "")),
            "Midias no perfil: " + str(audit.get("media_count", "nao informado")),
            "Midias recentes lidas: " + str(audit.get("recent_media_count", "nao informado")),
            "Publicacao executada: nao.",
            "Navegador logado usado: nao.",
            "Scraping usado: nao.",
        ])
    elif audit:
        audit_items.extend([
            "Hupmix nao validou como conectado agora.",
            "Status: " + str(audit.get("status", "desconhecido")),
            "Motivo: " + str(audit.get("reason", "ver relatorio local")),
            "Token nao exibido.",
        ])
    else:
        audit_items.append("Relatorio Hupmix ainda nao existe.")

    direct = []
    if any("Hupmix conectado" in item for item in audit_items):
        direct.append("Instagram conectado operacionalmente agora: Hupmix.")
    else:
        direct.append("Nenhum Instagram validado operacionalmente agora; existem apenas registros/configuracoes.")

    locked = [item for item in registered_accounts if "locked" in item.lower()]
    if locked:
        direct.append("Contas travadas permanecem bloqueadas: " + "; ".join(locked))

    return {
        "title": "Instagram conectados no K-OS",
        "summary": "Auditoria de contas Instagram feita em modo read-only. Nenhum navegador, scraping ou publish foi usado.",
        "sections": [
            {"title": "Pedido original", "items": [request]},
            {"title": "Resposta direta", "items": direct},
            {"title": "Contas sociais registradas no K-OS", "items": registered_accounts or ["Nenhuma conta social registrada no tenant registry."]},
            {"title": "Conexoes Meta/Instagram no registry", "items": instagram_connections or ["Nenhuma conexao Meta/Instagram registrada."]},
            {"title": "Validacao oficial agora", "items": audit_items},
            {"title": "Seguranca", "items": [
                "Token Meta/Instagram nao foi impresso.",
                "Nenhuma publicacao foi feita.",
                "Nenhum navegador logado foi usado.",
                "Parada Atlantida continua travada."
            ]},
            {"title": "Proximo pedido natural", "items": [
                "revise a ultima publicacao da Hupmix",
                "gere uma legenda melhor para o ultimo reel da Hupmix sem publicar",
                "audite as conexoes Meta e Gmail"
            ]},
        ],
    }


def build_email_ops(packet: dict) -> dict:
    request = packet.get("request", "")
    connection_registry = read_json(CONNECTION_REGISTRY)
    gmail_registry = [
        item for item in connection_registry.get("connections", []) or []
        if "gmail" in str(item.get("id", "")).lower() or str(item.get("id", "")).lower() == "google_oauth"
    ]

    capability_items = []
    gmail_ready = False
    try:
        if str(ROOT) not in sys.path:
            sys.path.insert(0, str(ROOT))
        from k_atlas.core.capabilities import capability_status
        status = capability_status()
        gmail_ready = bool(status.get("gmail_oauth"))
        capability_items.extend([
            "gmail_oauth: " + ("configurado" if status.get("gmail_oauth") else "nao configurado"),
            "google_oauth: " + ("configurado" if status.get("google_oauth") else "nao configurado"),
            "segredos lidos apenas como booleano: sim",
        ])
    except Exception as exc:
        capability_items.append("Erro ao ler capabilities: " + str(exc))

    registry_items = [
        str(item.get("name", item.get("id")))
        + " | provider=" + str(item.get("provider", "n/a"))
        + " | status=" + str(item.get("status", "n/a"))
        + " | risco=" + str(item.get("risk", "n/a"))
        for item in gmail_registry
    ]

    gmail_report_items = []
    gmail_messages = []
    gmail_script = ROOT / "scripts" / "run_gmail_read_only_audit.py"
    gmail_report_path = ROOT / "local_runtime" / "kos_gmail_read_only" / "latest_gmail_read_only_audit.json"
    if gmail_script.exists():
        try:
            subprocess = __import__("subprocess")
            completed = subprocess.run(
                [sys.executable, str(gmail_script), "--limit", "10"],
                cwd=str(ROOT),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=90,
            )
            gmail_report_items.append("Gmail read-only audit executado: returncode=" + str(completed.returncode))
        except Exception as exc:
            gmail_report_items.append("Gmail read-only audit falhou antes de completar: " + str(exc))
    else:
        gmail_report_items.append("Script Gmail read-only nao encontrado: " + str(gmail_script))

    gmail_report = read_json(gmail_report_path) if gmail_report_path.exists() else {}
    gmail_status = gmail_report.get("status", "sem_relatorio")
    gmail_report_items.append("Status: " + str(gmail_status))

    if gmail_status == "KOS_GMAIL_READ_ONLY_CONNECTED":
        gmail_report_items.extend([
            "Conta: " + str(gmail_report.get("email_address", "nao informada")),
            "Mensagens retornadas: " + str(gmail_report.get("messages_returned", 0)),
            "Email enviado: nao.",
            "Email apagado: nao.",
            "Email arquivado: nao.",
            "Token impresso: nao.",
        ])
        for msg in gmail_report.get("messages", []) or []:
            gmail_messages.append(
                "De: " + str(msg.get("from", ""))
                + " | Assunto: " + str(msg.get("subject", ""))
                + " | Data: " + str(msg.get("date", ""))
                + " | Trecho: " + str(msg.get("snippet", ""))
            )
        direct = [
            "Gmail read-only conectado e lido agora.",
            "Foram retornadas " + str(gmail_report.get("messages_returned", 0)) + " mensagens recentes.",
            "Nada foi enviado, apagado, arquivado ou rotulado."
        ]
    elif gmail_status == "KOS_GMAIL_READ_ONLY_TOKEN_MISSING":
        direct = [
            "Gmail/OAuth tem client configurado, mas falta token autorizado de usuário para ler inbox.",
            "O K-OS nao deve fingir leitura de email sem esse token.",
            "Salve o token OAuth autorizado em local_runtime/kos_secrets/gmail_token.json para ativar leitura read-only."
        ]
        expected = gmail_report.get("expected_token_locations", []) or []
        gmail_report_items.extend(["Local esperado: " + str(item) for item in expected[:4]])
    elif gmail_ready:
        direct = [
            "Gmail/OAuth parece configurado por variavel/secret local.",
            "A rotina Gmail read-only existe, mas nao completou a leitura agora.",
            "Verifique o status do relatorio local antes de qualquer triagem."
        ]
    else:
        direct = [
            "Gmail nao esta pronto para leitura real dentro do K-OS local.",
            "O registry conhece Gmail OAuth, mas a capability booleana nao confirmou credenciais suficientes.",
            "Por isso o pedido 'revise meus emails' nao deve fingir que leu inbox."
        ]

    return {
        "title": "Email/Gmail no K-OS",
        "summary": "Auditoria de readiness de email feita. Nenhum email foi lido, enviado, arquivado ou apagado.",
        "sections": [
            {"title": "Pedido original", "items": [request]},
            {"title": "Resposta direta", "items": direct},
            {"title": "Status real de OAuth", "items": capability_items},
            {"title": "Gmail read-only agora", "items": gmail_report_items},
            {"title": "Mensagens recentes", "items": gmail_messages or ["Nenhuma mensagem foi lida nesta execução."]},
            {"title": "Registry de conexoes de email", "items": registry_items or ["Gmail nao encontrado no connection registry."]},
            {"title": "O que falta para funcionar de verdade", "items": [
                "Ter token OAuth autorizado de usuario em local_runtime/kos_secrets/gmail_token.json.",
                "Manter leitura no escopo Gmail read-only.",
                "Ler no maximo assuntos, remetentes, datas e snippets no primeiro passo.",
                "Pedir confirmacao antes de qualquer resposta, arquivamento, label ou delete."
            ]},
            {"title": "Proximo pedido natural", "items": [
                "audite Gmail e me diga o que falta configurar",
                "criar leitor Gmail read-only com Human Gate",
                "quando Gmail estiver conectado, triage os ultimos 10 emails sem alterar nada"
            ]},
        ],
    }


def build_local_files_downloads(packet: dict) -> dict:
    request = packet.get("request", "")
    downloads = Path.home() / "Downloads"

    if not downloads.exists():
        return {
            "title": "Organizacao de Downloads",
            "summary": "A pasta Downloads nao foi encontrada neste usuario. Nenhum arquivo foi movido.",
            "sections": [
                {"title": "Pedido original", "items": [request]},
                {"title": "Pasta procurada", "items": [str(downloads)]},
                {"title": "Proxima acao segura", "items": ["Informe o caminho correto da pasta que quer organizar."]},
            ],
        }

    files = [path for path in downloads.iterdir() if path.is_file()]
    dirs = [path for path in downloads.iterdir() if path.is_dir()]
    groups = {
        "Imagens": [".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"],
        "Videos": [".mp4", ".mov", ".m4v", ".avi", ".mkv"],
        "Audio": [".mp3", ".wav", ".m4a", ".aac", ".ogg"],
        "Documentos": [".pdf", ".doc", ".docx", ".txt", ".md", ".ppt", ".pptx"],
        "Planilhas/dados": [".xls", ".xlsx", ".csv", ".json", ".xml"],
        "Instaladores/compactados": [".exe", ".msi", ".zip", ".rar", ".7z"],
        "Outros": [],
    }
    counts = {name: 0 for name in groups}
    samples = {name: [] for name in groups}

    def safe_file_label(path: Path) -> str:
        name = path.name
        low = name.lower()
        sensitive_markers = [
            "secret",
            "client_secret",
            "private_key",
            "token",
            "credential",
            "certificate",
            ".pem",
            ".key",
        ]
        if any(marker in low for marker in sensitive_markers):
            return "[nome sensivel mascarado]" + (path.suffix.lower() or "")
        return name

    def bucket_for(path: Path) -> str:
        suffix = path.suffix.lower()
        for name, suffixes in groups.items():
            if suffix in suffixes:
                return name
        return "Outros"

    for path in files:
        bucket = bucket_for(path)
        counts[bucket] += 1
        if len(samples[bucket]) < 5:
            samples[bucket].append(safe_file_label(path))

    largest = sorted(files, key=lambda p: p.stat().st_size if p.exists() else 0, reverse=True)[:8]
    largest_items = []
    for path in largest:
        try:
            largest_items.append(f"{safe_file_label(path)} | {path.stat().st_size / (1024 * 1024):.1f} MB")
        except Exception:
            largest_items.append(path.name)

    inventory_items = [
        "Pasta: " + str(downloads),
        "Arquivos encontrados: " + str(len(files)),
        "Pastas existentes: " + str(len(dirs)),
    ]
    inventory_items.extend([name + ": " + str(count) + " arquivo(s)" for name, count in counts.items()])

    sample_items = []
    for name, values in samples.items():
        if values:
            sample_items.append(name + ": " + ", ".join(values))

    return {
        "title": "Inventario real da pasta Downloads",
        "summary": "Downloads foi lida em modo inventario. Nenhum arquivo foi movido, apagado ou renomeado.",
        "sections": [
            {"title": "Pedido original", "items": [request]},
            {"title": "Resposta direta", "items": inventory_items},
            {"title": "Amostras por tipo", "items": sample_items or ["Sem arquivos classificados."]},
            {"title": "Maiores arquivos", "items": largest_items or ["Nenhum arquivo encontrado."]},
            {"title": "Plano de organizacao supervisionado", "items": [
                "Criar pastas sugeridas: _KOS_Imagens, _KOS_Videos, _KOS_Audio, _KOS_Documentos, _KOS_Dados, _KOS_Instaladores, _KOS_Outros.",
                "Mover arquivos por extensao apenas depois de confirmacao humana.",
                "Nunca apagar arquivos automaticamente.",
                "Gerar manifest antes/depois se o operador aprovar a organizacao."
            ]},
            {"title": "Para executar de verdade", "items": [
                "confirmar organizar Downloads usando esse plano",
                "O K-OS deve gerar um manifest e pedir confirmacao final antes de mover qualquer arquivo."
            ]},
        ],
    }


def build_connections(packet: dict) -> dict:
    request = packet.get("request", "")
    connection_registry = read_json(CONNECTION_REGISTRY)
    tool_registry = read_json(TOOL_REGISTRY)

    capability_items = []
    try:
        if str(ROOT) not in sys.path:
            sys.path.insert(0, str(ROOT))
        from k_atlas.core.capabilities import capability_status
        status = capability_status()
        for key in [
            "ai_brain",
            "supabase_basic",
            "supabase_admin",
            "github_write",
            "meta_app",
            "instagram_publish",
            "google_oauth",
            "gmail_oauth",
        ]:
            value = status.get(key)
            label = "configurado" if value else "nao configurado"
            capability_items.append(key + ": " + label)
    except Exception as exc:
        capability_items.append("capability_status: erro de leitura - " + str(exc))

    local_items = [
        ".env: " + ("existe" if (ROOT / ".env").exists() else "nao encontrado"),
        "render.yaml: " + ("existe" if (ROOT / "render.yaml").exists() else "nao encontrado"),
        "vercel.json: " + ("existe" if (ROOT / "vercel.json").exists() else "nao encontrado"),
        "Git remoto origin: " + ("configurado" if (ROOT / ".git" / "config").exists() else "nao verificado"),
        "Token Meta local: " + ("arquivo presente, conteudo nao lido" if (ROOT / "local_runtime" / "kos_secrets" / "meta_access_token.txt").exists() else "arquivo nao encontrado"),
    ]

    registry_items = [
        "Connection Registry: " + str(connection_registry.get("status")),
        "Conexoes registradas: " + str(len(connection_registry.get("connections", []) or [])),
        "Tool Registry: " + str(tool_registry.get("status")),
        "Tools registradas: " + str(len(tool_registry.get("tools", []) or [])),
    ]

    return {
        "title": "Diagnostico read-only de conexoes K-OS",
        "summary": "Conexoes validadas por status booleano/arquivo local. Nenhum segredo foi exibido e nenhuma acao externa foi executada.",
        "sections": [
            {"title": "Pedido original", "items": [request]},
            {"title": "Status de capacidades", "items": capability_items or ["Nenhum status retornado."]},
            {"title": "Evidencia local sem segredo", "items": local_items},
            {"title": "Registry consultado", "items": registry_items},
            {"title": "Limites de seguranca", "items": [
                "Valores de tokens, passwords, secrets e API keys nao foram impressos.",
                "Arquivo local de token Meta nao foi aberto.",
                "Nenhum deploy Render/Vercel foi executado.",
                "Nenhuma publicacao, email, DM ou chamada paga foi executada."
            ]},
            {"title": "Proximo passo por texto", "items": [
                "Digite confirmar para registrar este diagnostico como evidencia.",
                "Digite alterar e diga qual conexao quer investigar em seguida.",
                "Digite cancelar para encerrar sem acao externa."
            ]},
        ],
    }


def build_saas(packet: dict) -> dict:
    request = packet.get("request", "")
    return {
        "title": "Blueprint seguro de MVP SaaS",
        "summary": "Escopo inicial de produto criado em modo rascunho. Nenhum deploy ou gasto externo foi executado.",
        "sections": [
            {"title": "Pedido original", "items": [request]},
            {"title": "Nome de trabalho", "items": ["K-OS Mini SaaS Pilot"]},
            {"title": "Publico inicial", "items": ["Pequenos negocios que precisam organizar operacao, campanhas e tarefas com baixa complexidade."]},
            {"title": "Promessa simples", "items": ["Transformar pedidos soltos em plano operacional claro, com proximas acoes seguras."]},
            {"title": "Primeira tela", "items": ["Uma caixa de pedido.", "Resumo do entendimento.", "Proximo passo seguro.", "Registro de bloqueios."]},
            {"title": "Entrega desta semana", "items": ["Blueprint do MVP.", "Uma tela Streamlit simples.", "Um JSON de estado do produto.", "Sem deploy automatico."]},
        ],
    }


def build_agents(packet: dict) -> dict:
    request = packet.get("request", "")

    def mtime_label(path: Path) -> str:
        try:
            return datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            return "sem data"

    def compact_value(value):
        if isinstance(value, (str, int, float, bool)):
            return str(value)
        if isinstance(value, list):
            return str(len(value)) + " item(ns)"
        if isinstance(value, dict):
            return str(len(value)) + " chave(s)"
        if value is None:
            return "vazio"
        return type(value).__name__

    def extract_signals(data) -> str:
        if not isinstance(data, dict):
            return "conteudo lido"

        preferred = [
            "status", "state", "ok", "health", "mode", "last_status",
            "queue_status", "runner_status", "processor_status",
            "pending_count", "processed_count", "error_count",
            "last_error", "updated_at", "created_at", "generated_at",
            "last_tick_at", "timestamp"
        ]

        signals = []
        for key in preferred:
            if key in data and data.get(key) not in [None, "", [], {}]:
                signals.append(str(key) + "=" + compact_value(data.get(key)))

        if len(signals) < 4:
            for key, value in data.items():
                low = str(key).lower()
                if any(token in low for token in ["queue", "mission", "job", "task", "action", "decision", "pending", "error"]):
                    if value not in [None, "", [], {}]:
                        item = str(key) + "=" + compact_value(value)
                        if item not in signals:
                            signals.append(item)
                if len(signals) >= 6:
                    break

        if not signals:
            signals.append("arquivo lido, sem sinal operacional explicito")

        return "; ".join(signals[:6])

    def summarize_json_file(label: str, path: Path) -> str:
        if not path.exists():
            return label + ": nao encontrado"

        data = read_json(path)
        if isinstance(data, dict) and data.get("status") == "READ_ERROR":
            return label + ": erro de leitura - " + str(data.get("error", "sem detalhe"))

        status = "lido"
        if isinstance(data, dict) and data.get("status"):
            status = str(data.get("status"))

        return label + ": " + status + "; atualizado em " + mtime_label(path) + "; " + extract_signals(data)

    def summarize_decision_queue(path: Path) -> str:
        if not path.exists():
            return "Fila de decisao humana: nao encontrada"

        data = read_json(path)
        if isinstance(data, dict) and data.get("status") == "READ_ERROR":
            return "Fila de decisao humana: erro de leitura - " + str(data.get("error", "sem detalhe"))

        count = None
        if isinstance(data, list):
            count = len(data)
        elif isinstance(data, dict):
            for key in ["queue", "items", "decisions", "pending", "requests", "tasks"]:
                if isinstance(data.get(key), list):
                    count = len(data.get(key))
                    break
            if count is None:
                count = len(data.keys())

        if count is None:
            return "Fila de decisao humana: arquivo lido; atualizado em " + mtime_label(path)

        return "Fila de decisao humana: " + str(count) + " registro(s); atualizado em " + mtime_label(path)

    def summarize_jsonl_events(label: str, path: Path, limit: int = 5) -> list:
        if not path.exists():
            return [label + ": nao encontrado"]

        try:
            rows = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        except Exception as exc:
            return [label + ": erro de leitura - " + str(exc)]

        if not rows:
            return [label + ": sem eventos registrados"]

        out = []
        for raw in rows[-limit:]:
            try:
                event = json.loads(raw)
                if isinstance(event, dict):
                    bits = []
                    for key in ["event", "status", "route", "action_id", "packet_id", "created_at", "timestamp"]:
                        if event.get(key) not in [None, "", [], {}]:
                            bits.append(str(key) + "=" + str(event.get(key)))
                    out.append("; ".join(bits[:6]) if bits else "evento lido")
                else:
                    out.append("evento lido")
            except Exception:
                out.append(raw[:160])

        return out

    runtime_items = [
        summarize_json_file(
            "Fila de missoes",
            ROOT / "local_runtime" / "kos_autonomy_missions" / "latest_queue_processor_status.json"
        ),
        summarize_json_file(
            "Tick da fila de missoes",
            ROOT / "local_runtime" / "kos_autonomy_missions" / "latest_mission_queue_loop_tick.json"
        ),
        summarize_json_file(
            "Runner de jobs autonomos",
            ROOT / "local_runtime" / "kos_autonomous_jobs" / "latest_autonomous_job_runner_status.json"
        ),
        summarize_json_file(
            "Tick do runner autonomo",
            ROOT / "local_runtime" / "kos_autonomous_jobs" / "latest_autonomous_job_runner_loop_tick.json"
        ),
        summarize_json_file(
            "Ultimo Action Packet",
            ROOT / "local_runtime" / "kos_action_router" / "latest_action_packet.json"
        ),
        summarize_json_file(
            "Ultima acao segura",
            ROOT / "local_runtime" / "kos_safe_actions" / "latest_safe_action.json"
        ),
        summarize_decision_queue(
            ROOT / "live" / "human_decision_center" / "decision_queue.json"
        ),
    ]

    event_items = []
    event_items.extend(summarize_jsonl_events(
        "Eventos do roteador",
        ROOT / "local_runtime" / "kos_action_router" / "events.jsonl",
        limit=3
    ))
    event_items.extend(summarize_jsonl_events(
        "Eventos de acoes seguras",
        ROOT / "local_runtime" / "kos_safe_actions" / "events.jsonl",
        limit=3
    ))

    attention = []
    joined = "\n".join(runtime_items + event_items).lower()

    if "erro" in joined or "read_error" in joined or "failed" in joined or "failure" in joined:
        attention.append("Existe sinal de erro ou falha nos registros. Revisar antes de executar qualquer acao real.")
    else:
        attention.append("Nenhum erro critico foi identificado na leitura resumida dos arquivos monitorados.")

    if "nao encontrado" in joined:
        attention.append("Alguns arquivos de runtime nao foram encontrados. Isso pode ser normal se o modulo ainda nao rodou.")
    else:
        attention.append("Arquivos principais de runtime foram encontrados.")

    attention.append("Manter publicacao, patch e deploy bloqueados ate aprovacao humana.")

    return {
        "title": "Diagnostico operacional real de agentes",
        "summary": "Estado real lido de local_runtime e live. Nenhum agente executou acao externa.",
        "sections": [
            {"title": "Pedido original", "items": [request]},
            {"title": "Resumo simples", "items": [
                "Leitura feita em arquivos locais de runtime, fila, jobs, Action Packets, acoes seguras e decisao humana.",
                "Este diagnostico apenas le dados. Nao executa agente, nao publica, nao aplica patch e nao faz deploy."
            ]},
            {"title": "Estado real encontrado", "items": runtime_items},
            {"title": "Ultimos eventos", "items": event_items},
            {"title": "Atencao necessaria", "items": attention},
            {"title": "Proxima acao segura", "items": [
                "Revisar somente itens com erro, pendencia ou arquivo ausente.",
                "Executar acoes reais apenas com gate humano explicito."
            ]},
        ],
    }


def build_runtime(packet: dict) -> dict:
    request = packet.get("request", "")
    return {
        "title": "Status seguro de runtime",
        "summary": "Plano de verificacao de runtime criado sem mexer em navegador, cookies ou sessao logada.",
        "sections": [
            {"title": "Pedido original", "items": [request]},
            {"title": "Itens de status", "items": [
                "Porta principal do K-OS.",
                "Processo Streamlit ativo.",
                "Ultimo Action Packet.",
                "Eventos locais recentes.",
                "Bloqueios ativos."
            ]},
        ],
    }


def build_admin(packet: dict) -> dict:
    request = packet.get("request", "")
    return {
        "title": "Resumo administrativo seguro",
        "summary": "Plano curto de organizacao criado sem executar acao externa.",
        "sections": [
            {"title": "Pedido original", "items": [request]},
            {"title": "Prioridades", "items": [
                "Manter entrada unica do K-OS.",
                "Reduzir comandos manuais.",
                "Executar apenas acoes seguras por botao.",
                "Registrar decisoes com gate humano."
            ]},
        ],
    }


def build_general(packet: dict) -> dict:
    request = packet.get("request", "")
    return {
        "title": "Plano operacional seguro",
        "summary": "Pedido transformado em plano simples. Nenhuma acao real foi executada.",
        "sections": [
            {"title": "Pedido original", "items": [request]},
            {"title": "Proximo passo", "items": ["Refinar o pedido ou escolher uma acao segura dentro do K-OS."]},
        ],
    }



def build_patches(packet: dict) -> dict:
    request = packet.get("request", "")
    return {
        "title": "Plano seguro de patch",
        "summary": "Plano de patch criado em rascunho. Nenhum arquivo foi alterado automaticamente.",
        "sections": [
            {"title": "Pedido original", "items": [request]},
            {"title": "Resumo simples", "items": [
                "O K-OS preparou apenas um rascunho seguro.",
                "Nenhum deploy, patch, publicacao ou acao externa foi executado."
            ]},
            {"title": "Atencao necessaria", "items": [
                "Patch automatico bloqueado. Revisar diff e aprovar manualmente antes de aplicar.",
                "Gate humano obrigatorio preservado."
            ]},
            {"title": "Proxima acao segura", "items": [
                "Gerar proposta de patch revisavel, sem aplicar automaticamente."
            ]},
        ],
    }

BUILDERS = {
    "social_publish": build_social,
    "social_read": build_social_read,
    "instagram_accounts_status": build_instagram_accounts_status,
    "email_ops": build_email_ops,
    "local_files_downloads": build_local_files_downloads,
    "products_saas": build_saas,
    "agents_orchestration": build_agents,
    "patches": build_patches,
    "runtime_bridge": build_runtime,
    "connections_status": build_connections,
    "admin": build_admin,
    "general": build_general,
}


def render_markdown(result: dict) -> str:
    lines = [
        "# " + result["title"],
        "",
        result["summary"],
        "",
    ]
    for section in result.get("sections", []):
        lines.append("## " + section.get("title", "Secao"))
        lines.append("")
        lines.append(as_lines([str(x) for x in section.get("items", [])]))
        lines.append("")
    lines.append("## Guardrails")
    lines.append("")
    lines.append("- Sem publicacao automatica.")
    lines.append("- Sem deploy automatico.")
    lines.append("- Sem patch automatico.")
    lines.append("- Sem IA paga.")
    lines.append("- Sem automacao de navegador logado.")
    lines.append("- Gate humano obrigatorio para acoes reais.")
    lines.append("")
    return "\n".join(lines)


def execute_safe_action(packet: dict) -> dict:
    SAFE_DIR.mkdir(parents=True, exist_ok=True)

    route = packet.get("route", "general")
    builder = BUILDERS.get(route, build_general)
    result = builder(packet)

    action_id = "kos_safe_action_" + datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S") + "_" + uuid4().hex[:8]
    md_path = SAFE_DIR / f"{action_id}.md"
    json_path = SAFE_DIR / f"{action_id}.json"

    payload = {
        "status": "KOS_SAFE_ACTION_READY",
        "action_id": action_id,
        "created_at": now_iso(),
        "source_packet_id": packet.get("packet_id"),
        "route": route,
        "route_label": packet.get("route_label"),
        "title": result["title"],
        "summary": result["summary"],
        "sections": result.get("sections", []),
        "guardrails": {
            "auto_publish": "blocked",
            "auto_deploy": "blocked",
            "auto_patch": "blocked",
            "paid_ai": "blocked",
            "logged_browser_automation": "blocked",
            "human_gate_required": True,
        },
        "files": {
            "json": str(json_path),
            "markdown": str(md_path),
        },
    }

    md_path.write_text(render_markdown(result), encoding="utf-8")
    write_json(json_path, payload)
    write_json(LATEST_SAFE_ACTION, payload)

    event = {
        "ts": now_iso(),
        "event": "kos_safe_action_created",
        "action_id": action_id,
        "route": route,
        "source_packet_id": packet.get("packet_id"),
    }
    with EVENTS.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event, ensure_ascii=False) + "\n")

    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet-path", default="")
    parser.add_argument("--latest", action="store_true")
    args = parser.parse_args()

    if args.packet_path:
        packet_path = Path(args.packet_path)
    else:
        packet_path = LATEST_PACKET

    packet = read_json(packet_path)
    if packet.get("status") != "KOS_ACTION_PACKET_READY":
        print(json.dumps({
            "status": "NO_VALID_ACTION_PACKET",
            "packet_path": str(packet_path),
            "packet_status": packet.get("status"),
        }, ensure_ascii=False, indent=2))
        return 1

    result = execute_safe_action(packet)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
