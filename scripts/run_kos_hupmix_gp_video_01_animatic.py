from pathlib import Path
import json
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]
KIT_PATH = ROOT / "campaigns" / "hupmix_gp_recovery" / "GP_VIDEO_01_PRODUCTION_KIT.json"
OUT_DIR = ROOT / "local_runtime" / "kos_video_previews" / "hupmix"
OUT_DIR.mkdir(parents=True, exist_ok=True)

GIF_PATH = OUT_DIR / "GP_VIDEO_01_PREVIEW.gif"
PNG_PATH = OUT_DIR / "GP_VIDEO_01_STORYBOARD.png"

if not KIT_PATH.exists():
    raise SystemExit("Production Kit nao encontrado.")

try:
    from PIL import Image, ImageDraw, ImageFont
except Exception as exc:
    raise SystemExit("Pillow/PIL nao disponivel para gerar preview visual: " + str(exc))

kit = json.loads(KIT_PATH.read_text(encoding="utf-8"))
scenes = kit.get("scenes", []) or []
caption = kit.get("final_caption", "")
title = kit.get("title", "O heroi da limpeza chegou")

W, H = 540, 960

def get_font(size=32, bold=False):
    candidates = []
    if bold:
        candidates += [
            "C:/Windows/Fonts/arialbd.ttf",
            "C:/Windows/Fonts/segoeuib.ttf",
        ]
    candidates += [
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
    ]
    for item in candidates:
        try:
            return ImageFont.truetype(item, size)
        except Exception:
            pass
    return ImageFont.load_default()

FONT_BIG = get_font(46, True)
FONT_MED = get_font(28, True)
FONT_BODY = get_font(23, False)
FONT_SMALL = get_font(19, False)
FONT_TINY = get_font(16, False)

def wrap_text(draw, text, font, max_width):
    text = str(text or "")
    words = text.split()
    lines = []
    line = ""
    for word in words:
        test = (line + " " + word).strip()
        try:
            width = draw.textbbox((0, 0), test, font=font)[2]
        except Exception:
            width = len(test) * 10
        if width <= max_width:
            line = test
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines

def draw_wrapped(draw, xy, text, font, fill, max_width, line_gap=8, max_lines=None):
    x, y = xy
    lines = wrap_text(draw, text, font, max_width)
    if max_lines:
        lines = lines[:max_lines]
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        try:
            h = draw.textbbox((x, y), line, font=font)[3] - draw.textbbox((x, y), line, font=font)[1]
        except Exception:
            h = 24
        y += h + line_gap
    return y

def rounded(draw, box, radius, fill, outline=None, width=1):
    try:
        draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)
    except Exception:
        draw.rectangle(box, fill=fill, outline=outline)

def make_gradient():
    img = Image.new("RGB", (W, H), (15, 23, 42))
    pix = img.load()
    for y in range(H):
        t = y / max(H - 1, 1)
        r = int(15 + (20 - 15) * t)
        g = int(23 + (83 - 23) * t)
        b = int(42 + (45 - 42) * t)
        for x in range(W):
            pix[x, y] = (r, g, b)
    return img

def make_frame(scene, idx, total):
    img = make_gradient()
    draw = ImageDraw.Draw(img)

    rounded(draw, (30, 30, W-30, H-30), 34, (248, 250, 252), outline=(17, 24, 39), width=6)

    draw.rectangle((30, 30, W-30, 92), fill=(255, 255, 255))
    rounded(draw, (52, 48, 84, 80), 16, (34, 197, 94))
    draw.text((96, 51), "@hupmix", font=FONT_SMALL, fill=(15, 23, 42))
    draw.text((W-135, 51), "Reel", font=FONT_SMALL, fill=(100, 116, 139))

    draw.rectangle((30, 92, W-30, 690), fill=(15, 23, 42))
    rounded(draw, (56, 124, 250, 158), 17, (22, 101, 52), outline=(187, 247, 208))
    draw.text((72, 130), "GP_VIDEO_01", font=FONT_TINY, fill=(240, 253, 244))

    draw_wrapped(draw, (58, 190), "A solucao que faltava!", FONT_BIG, (255,255,255), W-116, line_gap=6, max_lines=2)

    rounded(draw, (58, 330, W-58, 500), 26, (255,255,255))
    draw.text((82, 358), "Oxy Power 5L", font=FONT_MED, fill=(15,23,42))
    draw.text((82, 400), "Oxigenio Ativo", font=FONT_BODY, fill=(22,101,52))
    draw.text((82, 438), "sem cloro | nao toxico", font=FONT_SMALL, fill=(71,85,105))
    draw.text((82, 470), "R$ 49,90", font=FONT_MED, fill=(220,38,38))

    speech = scene.get("speech") or scene.get("visual") or title
    draw_wrapped(draw, (58, 545), speech, FONT_BODY, (255,255,255), W-116, line_gap=8, max_lines=4)

    rounded(draw, (58, 632, W-58, 674), 21, (22,163,74))
    draw.text((82, 642), "Passe na HupMix ou chame no WhatsApp", font=FONT_TINY, fill=(255,255,255))

    bottom_y = 706
    draw.text((58, bottom_y), "Curtir  Comentar  Enviar", font=FONT_SMALL, fill=(15,23,42))
    draw_wrapped(draw, (58, bottom_y + 44), "hupmix " + caption, FONT_TINY, (15,23,42), W-116, line_gap=5, max_lines=5)

    scene_label = f"Cena {idx+1}/{total} - {scene.get('scene', '')}"
    draw.text((58, H-78), scene_label[:48], font=FONT_TINY, fill=(100,116,139))
    draw.text((58, H-54), "Publicacao bloqueada ate aprovacao humana", font=FONT_TINY, fill=(185,28,28))

    return img

if not scenes:
    scenes = [{"scene": "Cena unica", "speech": title, "take": "Preview visual"}]

frames = [make_frame(scene, i, len(scenes)) for i, scene in enumerate(scenes)]

frames[0].save(
    GIF_PATH,
    save_all=True,
    append_images=frames[1:],
    duration=1800,
    loop=0,
    optimize=True,
)

thumbs = []
for frame in frames:
    thumb = frame.copy()
    thumb.thumbnail((220, 390))
    thumbs.append(thumb)

storyboard = Image.new("RGB", (W, 120 + len(thumbs) * 420), (248,250,252))
draw = ImageDraw.Draw(storyboard)
draw.text((32, 28), "Storyboard GP_VIDEO_01 - Hupmix", font=FONT_MED, fill=(15,23,42))
y = 90
for i, thumb in enumerate(thumbs, start=1):
    storyboard.paste(thumb, (32, y))
    draw.text((280, y + 20), f"Cena {i}", font=FONT_MED, fill=(15,23,42))
    scene = scenes[i-1]
    draw_wrapped(draw, (280, y + 68), scene.get("speech", ""), FONT_SMALL, (51,65,85), 220, line_gap=6, max_lines=8)
    y += 420

storyboard.save(PNG_PATH)

print(json.dumps({
    "status": "KOS_GP_VIDEO_01_VISUAL_PREVIEW_READY",
    "gif": str(GIF_PATH),
    "storyboard": str(PNG_PATH),
    "frames": len(frames),
    "instagram_publish_executed": False
}, ensure_ascii=False, indent=2))
