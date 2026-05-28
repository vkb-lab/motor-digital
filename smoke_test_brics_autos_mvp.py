# -*- coding: utf-8 -*-
from pathlib import Path
import json
import py_compile

ROOT = Path.cwd()
PRODUCT = ROOT / "k_atlas" / "saas_factory" / "products" / "brics-paraguay-autos"
APP = PRODUCT / "app.py"
DATA = PRODUCT / "data" / "listings.json"
SERVER = PRODUCT / "server" / "server_config.json"

if not APP.exists():
    raise SystemExit("app.py nao existe")

if not DATA.exists():
    raise SystemExit("listings.json nao existe")

if not SERVER.exists():
    raise SystemExit("server_config.json nao existe")

py_compile.compile(str(APP), doraise=True)

text = APP.read_text(encoding="utf-8")

required = [
    "BRICS Paraguay Autos",
    "camera_input",
    "file_uploader",
    "ai_mock",
    "Confirmo que revisei",
    "Aprovar",
    "pt",
    "es"
]

for marker in required:
    if marker not in text:
        raise SystemExit("Marcador ausente: " + marker)

items = json.loads(DATA.read_text(encoding="utf-8"))
config = json.loads(SERVER.read_text(encoding="utf-8"))

if not isinstance(items, list):
    raise SystemExit("listings.json precisa ser lista")

if config.get("port") != 8602:
    raise SystemExit("porta esperada: 8602")

if config.get("policy", {}).get("human_review_required") is not True:
    raise SystemExit("revisao humana precisa ser obrigatoria")

if config.get("policy", {}).get("ai_assistive_only") is not True:
    raise SystemExit("IA precisa ser apenas assistiva")

if config.get("policy", {}).get("no_auto_publish") is not True:
    raise SystemExit("publicacao automatica precisa estar bloqueada")

print("BRICS Autos MVP smoke test OK")
print("url:", config.get("url"))
