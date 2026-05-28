# -*- coding: utf-8 -*-
from pathlib import Path
import json
import py_compile

ROOT = Path.cwd()
PRODUCT = ROOT / "k_atlas" / "saas_factory" / "products" / "closet-pilot"
APP = PRODUCT / "app.py"
DATA = PRODUCT / "data" / "wardrobe_items.json"
SERVER = PRODUCT / "server" / "server_config.json"

def fail(msg):
    raise SystemExit(msg)

if not APP.exists():
    fail("app.py nao existe")

if not DATA.exists():
    fail("wardrobe_items.json nao existe")

if not SERVER.exists():
    fail("server_config.json nao existe")

py_compile.compile(str(APP), doraise=True)

app_text = APP.read_text(encoding="utf-8")

required_markers = [
    "file_uploader",
    "Guarda-roupa visual",
    "Mapa do closet",
    "Combinar looks",
    "Planejar evento",
    "local_tipo",
    "caixa",
    "foto"
]

for marker in required_markers:
    if marker not in app_text:
        fail("Marcador ausente no app: " + marker)

items = json.loads(DATA.read_text(encoding="utf-8"))

if not isinstance(items, list):
    fail("wardrobe_items.json precisa ser lista")

if len(items) < 4:
    fail("wardrobe_items.json precisa ter pelo menos 4 pecas iniciais")

config = json.loads(SERVER.read_text(encoding="utf-8"))

if config.get("port") != 8601:
    fail("porta esperada: 8601")

print("Closet Pilot v0.2 smoke test OK")
print("items:", len(items))
print("url:", config.get("url"))
