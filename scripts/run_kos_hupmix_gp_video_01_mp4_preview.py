from pathlib import Path
import json
import sys
import math

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]
KIT_PATH = ROOT / "campaigns" / "hupmix_gp_recovery" / "GP_VIDEO_01_PRODUCTION_KIT.json"
OUT_DIR = ROOT / "local_runtime" / "kos_video_previews" / "hupmix"
OUT_DIR.mkdir(parents=True, exist_ok=True)

MP4_PATH = OUT_DIR / "GP_VIDEO_01_PREVIEW.mp4"
STORYBOARD_PATH = OUT_DIR / "GP_VIDEO_01_STORYBOARD.png"

if not KIT_PATH.exists():
    raise SystemExit("Production Kit nao encontrado.")

from PIL import Image, ImageDraw, ImageFont
import numpy as np
import imageio.v2 as imageio

kit = json.loads(KIT_PATH.read_text(encoding="utf-8"))
scenes = kit.get("scenes", []) or []
caption = kit.get("final_caption", "")

W, H = 540, 960
FPS = 24
SECONDS_PER_SCENE = 3.2

def font(size=28, bold=False):
    paths = []
    if bold:
        paths += ["C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/segoeuib.ttf"]
    paths += ["C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/segoeui.ttf"]
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            pass
    return ImageFont.load_default()

F_BIG = font(48, True)
F_TITLE = font(34, True)
F_MED = font(27, True)
F_BODY = font(23, False)
F_SMALL = font(18, False)
F_TINY = font(15, False)

def wrap(draw, text, fnt, max_w):
    words = str(text or "").split()
    lines, line = [], ""
    for word in words:
        test = (line + " " + word).strip()
        try:
            width = draw.textbbox((0,0), test, font=fnt)[2]
        except Exception:
            width = len(test) * 10
        if width <= max_w:
            line = test
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines

def draw_wrap(draw, xy, text, fnt, fill, max_w, max_lines=4, gap=7):
    x, y = xy
    lines = wrap(draw, text, fnt, max_w)[:max_lines]
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += fnt.size + gap
    return y

def rr(draw, box, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)

def bg_frame():
    img = Image.new("RGB", (W, H), (15, 23, 42))
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        color = (int(14 + 10*t), int(32 + 75*t), int(64 + 5*t))
        d.line((0, y, W, y), fill=color)
    return img

def make_frame(scene, scene_idx, frame_idx, frames_per_scene):
    t = frame_idx / max(frames_per_scene - 1, 1)
    img = bg_frame()
    draw = ImageDraw.Draw(img)

    rr(draw, (24, 24, W-24, H-24), 38, (248,250,252), (17,24,39), 6)

    draw.rectangle((24, 24, W-24, 88), fill=(255,255,255))
    rr(draw, (48, 44, 82, 78), 17, (22,163,74))
    draw.text((96, 48), "@hupmix", font=F_SMALL, fill=(15,23,42))
    draw.text((W-140, 48), "Reel preview", font=F_TINY, fill=(100,116,139))

    draw.rectangle((24, 88, W-24, 695), fill=(15,23,42))

    pulse = int(18 * math.sin(t * math.pi))
    rr(draw, (54, 122, 250 + pulse, 158), 18, (22,101,52), (187,247,208), 1)
    draw.text((72, 130), "GP_VIDEO_01", font=F_TINY, fill=(240,253,244))

    title_x = int(58 + 12 * math.sin(t * math.pi))
    draw_wrap(draw, (title_x, 190), "A solução que faltava!", F_BIG, (255,255,255), W-116, 2, 4)

    card_y = int(330 - 8 * math.sin(t * math.pi))
    rr(draw, (58, card_y, W-58, card_y+180), 28, (255,255,255))
    draw.text((84, card_y+28), "Oxy Power 5L", font=F_TITLE, fill=(15,23,42))
    draw.text((84, card_y+78), "Oxigênio Ativo", font=F_BODY, fill=(22,101,52))
    draw.text((84, card_y+114), "sem cloro | não tóxico", font=F_SMALL, fill=(71,85,105))
    draw.text((84, card_y+142), "R$ 49,90", font=F_MED, fill=(220,38,38))

    speech = scene.get("speech") or scene.get("visual") or "Oxy Power chegou na HupMix."
    draw_wrap(draw, (58, 545), speech, F_BODY, (255,255,255), W-116, 4, 8)

    rr(draw, (58, 632, W-58, 674), 21, (22,163,74))
    draw.text((82, 642), "Passe na HupMix ou chame no WhatsApp", font=F_TINY, fill=(255,255,255))

    progress_w = int((W-116) * ((scene_idx + t) / max(len(scenes), 1)))
    draw.rectangle((58, 682, W-58, 688), fill=(51,65,85))
    draw.rectangle((58, 682, 58+progress_w, 688), fill=(34,197,94))

    bottom = 715
    draw.text((58, bottom), "Curtir  Comentar  Enviar", font=F_SMALL, fill=(15,23,42))
    draw_wrap(draw, (58, bottom+42), "hupmix " + caption, F_TINY, (15,23,42), W-116, 6, 5)

    draw.text((58, H-78), f"Cena {scene_idx+1}/{len(scenes)} - {scene.get('scene','')}"[:55], font=F_TINY, fill=(100,116,139))
    draw.text((58, H-54), "Publicação bloqueada até aprovação humana", font=F_TINY, fill=(185,28,28))
    return img

if not scenes:
    scenes = [{"scene": "Cena única", "speech": "A solução que faltava para a limpeza da sua casa chegou."}]

frames_per_scene = int(FPS * SECONDS_PER_SCENE)

with imageio.get_writer(str(MP4_PATH), fps=FPS, codec="libx264", quality=8, macro_block_size=1) as writer:
    for sidx, scene in enumerate(scenes):
        for fidx in range(frames_per_scene):
            frame = make_frame(scene, sidx, fidx, frames_per_scene)
            writer.append_data(np.asarray(frame))

thumbs = []
for idx, scene in enumerate(scenes):
    frame = make_frame(scene, idx, frames_per_scene//2, frames_per_scene)
    frame.thumbnail((220, 390))
    thumbs.append((frame.copy(), scene))

storyboard = Image.new("RGB", (W, 120 + len(thumbs)*420), (248,250,252))
draw = ImageDraw.Draw(storyboard)
draw.text((32, 28), "Storyboard GP_VIDEO_01 - Hupmix", font=F_MED, fill=(15,23,42))
y = 90
for idx, (thumb, scene) in enumerate(thumbs, start=1):
    storyboard.paste(thumb, (32, y))
    draw.text((280, y+20), f"Cena {idx}", font=F_MED, fill=(15,23,42))
    draw_wrap(draw, (280, y+68), scene.get("speech", ""), F_SMALL, (51,65,85), 220, 8, 6)
    y += 420
storyboard.save(STORYBOARD_PATH)

print(json.dumps({
    "status": "KOS_GP_VIDEO_01_MP4_PREVIEW_READY",
    "mp4": str(MP4_PATH),
    "storyboard": str(STORYBOARD_PATH),
    "scenes": len(scenes),
    "fps": FPS,
    "instagram_publish_executed": False
}, ensure_ascii=False, indent=2))
