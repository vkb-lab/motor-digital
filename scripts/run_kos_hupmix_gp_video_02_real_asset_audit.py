
from pathlib import Path
from datetime import datetime
import json
import re

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "content_packs" / "hupmix_gp_video_02" / "assets_inbox"
OUT = ROOT / "local_runtime" / "kos_video_previews" / "hupmix" / "gp_video_02_real"
REPORTS = ROOT / "reports"
CAMPAIGN = ROOT / "campaigns" / "hupmix_gp_recovery"

ASSETS.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)
REPORTS.mkdir(exist_ok=True)
CAMPAIGN.mkdir(parents=True, exist_ok=True)

PREVIEW = OUT / "GP_VIDEO_02_REAL_ASSET_PREVIEW.mp4"
STORYBOARD = OUT / "GP_VIDEO_02_REAL_ASSET_STORYBOARD.png"
REPORT = REPORTS / "KOS_HUPMIX_GP_VIDEO_02_REAL_ASSET_AUDIT.json"
REPORT_MD = REPORTS / "KOS_HUPMIX_GP_VIDEO_02_REAL_ASSET_AUDIT.md"
BRIEF_JSON = CAMPAIGN / "GP_VIDEO_02_REAL_PRODUCTION_BRIEF.json"
BRIEF_MD = CAMPAIGN / "GP_VIDEO_02_REAL_PRODUCTION_BRIEF.md"

VIDEO_EXT = {".mp4", ".mov", ".m4v", ".avi", ".webm"}
IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp"}

WIDTH = 720
HEIGHT = 1280
FPS = 24

def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")

def remove_fake_outputs():
    for old in [PREVIEW, STORYBOARD]:
        if old.exists():
            old.unlink()

def list_assets():
    items = []
    for path in sorted(ASSETS.iterdir()):
        if path.name.startswith("."):
            continue
        ext = path.suffix.lower()
        if ext in VIDEO_EXT:
            kind = "video"
        elif ext in IMAGE_EXT:
            kind = "image"
        else:
            continue
        items.append({
            "path": path,
            "kind": kind,
            "ext": ext,
            "size": path.stat().st_size
        })
    return items

def waiting_report(items):
    remove_fake_outputs()

    brief = {
        "status": "KOS_HUPMIX_GP_VIDEO_02_WAITING_FOR_REAL_ASSETS",
        "created_at": datetime.now().isoformat(),
        "campaign": "Hupmix / Garoto Oxy Power / Oxy Power",
        "rule": "Nao gerar video fake. GP_VIDEO_02 real exige footage real ou imagens reais anexadas.",
        "assets_inbox": rel(ASSETS),
        "required_assets": [
            "video vertical curto do produto Oxy Power",
            "cena de antes: piso, box, roupa, gordura ou sujeira real",
            "cena aplicando o produto",
            "cena de resultado/depois",
            "opcional: foto do produto 5L e preco R$ 49,90"
        ],
        "shotlist": [
            "Cena 1: continuidade do Garoto Oxy com produto real em quadro",
            "Cena 2: problema real de limpeza",
            "Cena 3: aplicacao do Oxy Power",
            "Cena 4: resultado visual honesto",
            "Cena 5: oferta 5L por R$ 49,90 + WhatsApp/loja"
        ],
        "policy": {
            "no_publish": True,
            "no_paid_ai": True,
            "no_scraping": True,
            "human_gate_required": True
        }
    }

    BRIEF_JSON.write_text(json.dumps(brief, ensure_ascii=False, indent=2), encoding="utf-8")
    BRIEF_MD.write_text(
        "# GP_VIDEO_02 Real Production Brief\n\n"
        "Status: aguardando assets reais.\n\n"
        "Regra: o K-OS nao deve gerar video falso para o proximo post.\n\n"
        f"Pasta de entrada: `{rel(ASSETS)}`\n\n"
        "Assets minimos:\n\n"
        "- video vertical curto do produto\n"
        "- cena antes\n"
        "- cena aplicando\n"
        "- cena depois\n"
        "- produto/preco/CTA\n",
        encoding="utf-8"
    )

    report = {
        "status": "KOS_HUPMIX_GP_VIDEO_02_WAITING_FOR_REAL_ASSETS",
        "created_at": datetime.now().isoformat(),
        "assets_found": len(items),
        "assets_inbox": rel(ASSETS),
        "preview_created": False,
        "brief": rel(BRIEF_JSON),
        "next_step": "Anexar footage real do produto/cenas pelo painel ou copiar para assets_inbox.",
        "policy": brief["policy"]
    }

    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    REPORT_MD.write_text(
        "# K-OS Hupmix GP_VIDEO_02 Real Asset Audit\n\n"
        "Status: aguardando assets reais.\n\n"
        f"- Pasta: `{rel(ASSETS)}`\n"
        "- Nenhum preview real foi criado.\n"
        "- Publicacao bloqueada.\n",
        encoding="utf-8"
    )
    return report

def render_with_real_assets(items):
    try:
        import imageio
        from PIL import Image, ImageDraw, ImageFont, ImageOps
        import numpy as np
    except Exception as exc:
        return {
            "status": "KOS_HUPMIX_GP_VIDEO_02_REAL_ASSET_DEPENDENCY_ERROR",
            "error": str(exc),
            "preview_created": False
        }

    def font(size, bold=False):
        candidates = [
            r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
            r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
        ]
        for c in candidates:
            p = Path(c)
            if p.exists():
                return ImageFont.truetype(str(p), size)
        return ImageFont.load_default()

    F_H1 = font(48, True)
    F_H2 = font(34, True)
    F_BODY = font(28, False)
    F_SMALL = font(22, False)

    extracted = []
    asset_summary = []

    def save_thumb(img, source_path, idx):
        img = img.convert("RGB")
        thumb = ImageOps.contain(img, (620, 720))
        safe = re.sub(r"[^a-zA-Z0-9_-]+", "_", source_path.stem)
        out = OUT / f"{safe}_real_frame_{idx}.jpg"
        thumb.save(out, quality=88)
        extracted.append({
            "image": out,
            "source": source_path
        })

    for item in items:
        path = item["path"]
        if item["kind"] == "image":
            try:
                img = Image.open(path).convert("RGB")
                save_thumb(img, path, 1)
                asset_summary.append({
                    "path": rel(path),
                    "kind": "image",
                    "size": item["size"],
                    "image_size": list(img.size)
                })
            except Exception as exc:
                asset_summary.append({"path": rel(path), "kind": "image", "error": str(exc)})
        else:
            try:
                reader = imageio.get_reader(str(path))
                meta = {}
                try:
                    meta = reader.get_meta_data()
                except Exception:
                    meta = {}
                fps = meta.get("fps") or 24
                duration = meta.get("duration") or 6
                indexes = [0, int(duration * fps * 0.33), int(duration * fps * 0.66)]
                for idx, frame_index in enumerate(indexes, start=1):
                    try:
                        frame = reader.get_data(max(0, frame_index))
                        img = Image.fromarray(frame).convert("RGB")
                        save_thumb(img, path, idx)
                    except Exception:
                        pass
                try:
                    reader.close()
                except Exception:
                    pass
                asset_summary.append({
                    "path": rel(path),
                    "kind": "video",
                    "size": item["size"],
                    "duration": duration,
                    "fps": fps,
                    "meta_size": meta.get("size")
                })
            except Exception as exc:
                asset_summary.append({"path": rel(path), "kind": "video", "error": str(exc)})

    if not extracted:
        return waiting_report(items)

    scenes = [
        ("CONTINUIDADE REAL", "Novo GP_VIDEO_02 usando footage real anexado."),
        ("PROBLEMA REAL", "Mostrar sujeira, mancha, piso, box ou gordura."),
        ("APLICACAO", "Aplicar Oxy Power e mostrar o produto em uso."),
        ("RESULTADO", "Depois limpo, claro e honesto."),
        ("OFERTA", "Oxy Power 5L por R$ 49,90. Chamar HupMix no WhatsApp.")
    ]

    def draw_center(draw, text, y, fnt, fill, max_width):
        words = str(text).split()
        lines = []
        cur = ""
        for w in words:
            test = (cur + " " + w).strip()
            box = draw.textbbox((0, 0), test, font=fnt)
            if box[2] <= max_width:
                cur = test
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)

        for line in lines:
            box = draw.textbbox((0, 0), line, font=fnt)
            x = (WIDTH - (box[2] - box[0])) // 2
            draw.text((x, y), line, font=fnt, fill=fill)
            y += (box[3] - box[1]) + 10
        return y

    def make_frame(scene_idx):
        title, subtitle = scenes[scene_idx]
        src = extracted[scene_idx % len(extracted)]["image"]

        img = Image.new("RGB", (WIDTH, HEIGHT), (245, 248, 246))
        draw = ImageDraw.Draw(img)

        draw.rectangle((0, 0, WIDTH, 150), fill=(18, 97, 65))
        draw.text((38, 34), "HupMix | GP_VIDEO_02 REAL", font=F_H2, fill=(255, 255, 255))
        draw.text((38, 88), "preview criado somente com assets reais", font=F_SMALL, fill=(228, 246, 236))

        real = Image.open(src).convert("RGB")
        real = ImageOps.contain(real, (620, 700))
        x = (WIDTH - real.width) // 2
        y = 190
        img.paste(real, (x, y))
        draw.rounded_rectangle((x-8, y-8, x+real.width+8, y+real.height+8), radius=24, outline=(18, 97, 65), width=5)

        y2 = 930
        y2 = draw_center(draw, title, y2, F_H1, (18, 97, 65), WIDTH - 90)
        draw_center(draw, subtitle, y2 + 10, F_BODY, (35, 45, 48), WIDTH - 100)

        draw.rectangle((0, HEIGHT - 125, WIDTH, HEIGHT), fill=(18, 97, 65))
        draw.text((38, HEIGHT - 92), "Sem publicacao automatica | OK humano obrigatorio", font=F_SMALL, fill=(255, 255, 255))
        draw.text((38, HEIGHT - 55), "Oxy Power 5L | R$ 49,90", font=F_SMALL, fill=(228, 246, 236))

        return img

    writer = imageio.get_writer(str(PREVIEW), fps=FPS, macro_block_size=16)
    try:
        for scene_idx in range(len(scenes)):
            frame = make_frame(scene_idx)
            arr = np.array(frame)
            for _ in range(3 * FPS):
                writer.append_data(arr)
    finally:
        writer.close()

    tiles = [make_frame(i).resize((216, 384)) for i in range(len(scenes))]
    story = Image.new("RGB", (216 * len(tiles), 384), (255, 255, 255))
    for i, tile in enumerate(tiles):
        story.paste(tile, (i * 216, 0))
    story.save(STORYBOARD)

    brief = {
        "status": "KOS_HUPMIX_GP_VIDEO_02_REAL_PRODUCTION_BRIEF_READY",
        "created_at": datetime.now().isoformat(),
        "campaign": "Hupmix / Garoto Oxy Power / Oxy Power",
        "source_rule": "Preview criado somente com assets reais anexados.",
        "assets_used": [rel(x["source"]) for x in extracted],
        "shotlist": scenes,
        "price": "R$ 49,90",
        "policy": {
            "no_publish": True,
            "no_paid_ai": True,
            "no_scraping": True,
            "human_gate_required": True
        }
    }

    BRIEF_JSON.write_text(json.dumps(brief, ensure_ascii=False, indent=2), encoding="utf-8")
    BRIEF_MD.write_text(
        "# GP_VIDEO_02 Real Production Brief\n\n"
        "Status: briefing real criado com assets anexados.\n\n"
        f"- Preview: `{rel(PREVIEW)}`\n"
        f"- Storyboard: `{rel(STORYBOARD)}`\n"
        "- Publicacao bloqueada.\n",
        encoding="utf-8"
    )

    report = {
        "status": "KOS_HUPMIX_GP_VIDEO_02_REAL_ASSET_PREVIEW_READY",
        "created_at": datetime.now().isoformat(),
        "assets_found": len(items),
        "assets_summary": asset_summary,
        "frames_extracted": [rel(x["image"]) for x in extracted],
        "preview_created": True,
        "outputs": {
            "preview": rel(PREVIEW),
            "preview_size": PREVIEW.stat().st_size,
            "storyboard": rel(STORYBOARD),
            "storyboard_size": STORYBOARD.stat().st_size,
            "brief": rel(BRIEF_JSON)
        },
        "next_step": "Validar preview real no painel e registrar OK humano ou pedir ajuste.",
        "policy": brief["policy"]
    }

    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    REPORT_MD.write_text(
        "# K-OS Hupmix GP_VIDEO_02 Real Asset Audit\n\n"
        "Status: preview real criado.\n\n"
        f"- Preview: `{rel(PREVIEW)}`\n"
        f"- Storyboard: `{rel(STORYBOARD)}`\n"
        "- Gerado somente com assets reais anexados.\n"
        "- Publicacao bloqueada.\n",
        encoding="utf-8"
    )
    return report

items = list_assets()
if not items:
    result = waiting_report(items)
else:
    result = render_with_real_assets(items)

print(json.dumps(result, ensure_ascii=False, indent=2))
