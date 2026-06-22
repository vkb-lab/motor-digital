
from pathlib import Path
from datetime import datetime
import json

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
CAMPAIGN = ROOT / "campaigns" / "hupmix_gp_recovery"
CONTENT = ROOT / "content_packs" / "hupmix_gp_video_02"
ASSETS = CONTENT / "assets_inbox"

REPORTS.mkdir(exist_ok=True)
CAMPAIGN.mkdir(parents=True, exist_ok=True)
CONTENT.mkdir(parents=True, exist_ok=True)
ASSETS.mkdir(parents=True, exist_ok=True)

AUDIT_PATH = REPORTS / "KOS_HUPMIX_INSTAGRAM_CONTINUITY_AUDIT.json"
CAPTURE_JSON = CAMPAIGN / "GP_VIDEO_02_CAPTURE_MISSION.json"
CAPTURE_MD = CAMPAIGN / "GP_VIDEO_02_CAPTURE_MISSION.md"
REPORT_JSON = REPORTS / "KOS_HUPMIX_GP_VIDEO_02_CAPTURE_MISSION_V1.json"
REPORT_MD = REPORTS / "KOS_HUPMIX_GP_VIDEO_02_CAPTURE_MISSION_V1.md"

def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")

def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

def write_if_changed(path: Path, content: str):
    if path.exists() and path.read_text(encoding="utf-8", errors="ignore") == content:
        return False
    path.write_text(content, encoding="utf-8")
    return True

existing = read_json(CAPTURE_JSON)
if existing.get("status") == "KOS_HUPMIX_GP_VIDEO_02_CAPTURE_MISSION_READY":
    report = {
        "status": "KOS_HUPMIX_GP_VIDEO_02_CAPTURE_MISSION_V1_READY",
        "created_at": existing.get("created_at"),
        "mission": rel(CAPTURE_JSON),
        "mission_md": rel(CAPTURE_MD),
        "assets_inbox": rel(ASSETS),
        "based_on_instagram_reference": bool((existing.get("based_on") or {}).get("instagram_reference_video")),
        "required_takes": len(((existing.get("capture_mission") or {}).get("required_real_assets") or [])),
        "next_step": existing.get("next_step"),
        "policy": existing.get("policy", {})
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0)

audit = read_json(AUDIT_PATH)
instagram = audit.get("instagram", {})
latest = instagram.get("latest_item") or {}
download = instagram.get("download") or {}
score = instagram.get("gp_relevance_from_caption") or {}

created_at = datetime.now().isoformat()

mission = {
    "status": "KOS_HUPMIX_GP_VIDEO_02_CAPTURE_MISSION_READY",
    "created_at": created_at,
    "campaign": {
        "brand": "Hupmix",
        "product": "Oxy Power 5L",
        "character": "Garoto Oxy",
        "price": "R$ 49,90",
        "video_id": "GP_VIDEO_02",
        "objective": "Continuar a campanha existente com uma nova captacao real, sem inventar footage."
    },
    "based_on": {
        "instagram_reference_video": download.get("stored_path"),
        "instagram_timestamp": latest.get("timestamp"),
        "instagram_permalink": latest.get("permalink"),
        "caption_score": score,
        "audit_report": "reports/KOS_HUPMIX_INSTAGRAM_CONTINUITY_AUDIT.json"
    },
    "creative_direction": {
        "positioning": "Continuidade da campanha Garoto Oxy, agora mostrando uso real do Oxy Power.",
        "tone": "simples, direto, demonstrativo e comercial",
        "do_not_do": [
            "nao gerar video fake",
            "nao repostar o video antigo como se fosse novo",
            "nao usar cena inventada como prova real",
            "nao publicar sem OK humano"
        ]
    },
    "capture_mission": {
        "assets_inbox": "content_packs/hupmix_gp_video_02/assets_inbox",
        "required_real_assets": [
            {
                "id": "take_01_product_intro",
                "type": "video_or_photo",
                "duration_target": "3-5s",
                "description": "Produto Oxy Power 5L em quadro, com rotulo visivel.",
                "instruction": "Gravar vertical, boa luz, produto parado ou leve movimento de mao."
            },
            {
                "id": "take_02_problem_before",
                "type": "video",
                "duration_target": "4-6s",
                "description": "Cena real de sujeira, gordura, piso, box, roupa ou superficie antes da limpeza.",
                "instruction": "Mostrar problema real sem exagero. Evitar tremedeira."
            },
            {
                "id": "take_03_application",
                "type": "video",
                "duration_target": "5-8s",
                "description": "Aplicacao do Oxy Power na superficie.",
                "instruction": "Mostrar o produto sendo usado. Se possivel, mao aplicando e superficie visivel."
            },
            {
                "id": "take_04_action_wait_clean",
                "type": "video",
                "duration_target": "4-6s",
                "description": "Produto agindo ou limpeza sendo feita.",
                "instruction": "Mostrar pano, escova ou processo de limpeza."
            },
            {
                "id": "take_05_after_result",
                "type": "video_or_photo",
                "duration_target": "4-6s",
                "description": "Resultado depois da limpeza.",
                "instruction": "Mesmo angulo aproximado da cena antes."
            },
            {
                "id": "take_06_offer_cta",
                "type": "video_or_photo",
                "duration_target": "3-5s",
                "description": "Produto + preco R$ 49,90 + chamada para Hupmix/WhatsApp.",
                "instruction": "Pode ser produto na prateleira ou produto em mesa com preco."
            }
        ]
    },
    "script": {
        "hook": "O Garoto Oxy voltou com teste real.",
        "voice_lines": [
            "Olha o que o Oxy Power consegue fazer no uso real.",
            "Produto sem cloro, com oxigenio ativo e alto poder de limpeza.",
            "Aqui e antes. Agora vamos aplicar.",
            "Deixa agir, limpa e olha o resultado.",
            "Oxy Power 5 litros por R$ 49,90 na HupMix."
        ],
        "caption_suggestion": "O Garoto Oxy voltou em teste real. Oxy Power 5L com oxigenio ativo, sem cloro e por R$ 49,90 na HupMix. Chama no WhatsApp ou passa na loja.",
        "cta": "Chame a HupMix no WhatsApp ou passe na loja."
    },
    "production_rules": {
        "format": "vertical 9:16",
        "target_duration": "20-30s",
        "capture_device": "celular",
        "minimum_quality": "boa luz, audio opcional, imagem estavel",
        "editing_after_capture": "K-OS monta preview real apenas depois dos assets reais entrarem no assets_inbox"
    },
    "policy": {
        "no_publish": True,
        "no_paid_ai": True,
        "no_scraping": True,
        "no_logged_browser_automation": True,
        "human_gate_required": True
    },
    "next_step": "Captar ou anexar os takes reais em content_packs/hupmix_gp_video_02/assets_inbox."
}

CAPTURE_JSON.write_text(json.dumps(mission, ensure_ascii=False, indent=2), encoding="utf-8")

md = []
md.append("# GP_VIDEO_02 Capture Mission — Hupmix / Garoto Oxy")
md.append("")
md.append("Status: KOS_HUPMIX_GP_VIDEO_02_CAPTURE_MISSION_READY")
md.append("")
md.append("## Objetivo")
md.append("Continuar a campanha existente com nova captacao real, sem inventar footage.")
md.append("")
md.append("## Referencia")
md.append(f"- Video Instagram: `{download.get('stored_path')}`")
md.append(f"- Data: {latest.get('timestamp')}")
md.append(f"- Score Oxy: {score.get('score')}")
md.append("")
md.append("## Takes obrigatorios")
for item in mission["capture_mission"]["required_real_assets"]:
    md.append(f"### {item['id']}")
    md.append(f"- Tipo: {item['type']}")
    md.append(f"- Duracao alvo: {item['duration_target']}")
    md.append(f"- Descricao: {item['description']}")
    md.append(f"- Instrucao: {item['instruction']}")
    md.append("")
md.append("## Falas sugeridas")
for line in mission["script"]["voice_lines"]:
    md.append(f"- {line}")
md.append("")
md.append("## Legenda sugerida")
md.append(mission["script"]["caption_suggestion"])
md.append("")
md.append("## Pasta de assets reais")
md.append("`content_packs/hupmix_gp_video_02/assets_inbox`")
md.append("")
md.append("## Politica")
md.append("- Sem publicacao automatica")
md.append("- Sem IA paga")
md.append("- Sem scraping")
md.append("- OK humano obrigatorio")

CAPTURE_MD.write_text("\n".join(md), encoding="utf-8")

report = {
    "status": "KOS_HUPMIX_GP_VIDEO_02_CAPTURE_MISSION_V1_READY",
    "created_at": created_at,
    "mission": rel(CAPTURE_JSON),
    "mission_md": rel(CAPTURE_MD),
    "assets_inbox": rel(ASSETS),
    "based_on_instagram_reference": bool(download.get("stored_path")),
    "required_takes": len(mission["capture_mission"]["required_real_assets"]),
    "next_step": mission["next_step"],
    "policy": mission["policy"]
}

REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
REPORT_MD.write_text(
    "# K-OS Hupmix GP_VIDEO_02 Capture Mission V1\n\n"
    f"Status: {report['status']}\n\n"
    f"- Mission: `{report['mission']}`\n"
    f"- Assets inbox: `{report['assets_inbox']}`\n"
    f"- Required takes: {report['required_takes']}\n"
    "- Proximo passo: captar/anexar material real.\n",
    encoding="utf-8"
)

print(json.dumps(report, ensure_ascii=False, indent=2))
