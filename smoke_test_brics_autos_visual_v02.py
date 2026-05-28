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
config = json.loads(SERVER.read_text(encoding="utf-8"))
items = json.loads(DATA.read_text(encoding="utf-8"))

required_markers = [
    "BRICS Paraguay Autos",
    "vehicle-card",
    "search-panel",
    "car-box",
    "linear-gradient",
    "camera_input",
    "file_uploader",
    "ai_mock",
    "Confirmo que revisei",
    "Aprovar anúncio",
    "pt",
    "es"
]

for marker in required_markers:
    if marker not in text:
        raise SystemExit("Marcador ausente: " + marker)

if config.get("version") != "0.2.0":
    raise SystemExit("versao esperada: 0.2.0")

if config.get("port") != 8602:
    raise SystemExit("porta esperada: 8602")

policy = config.get("policy", {})

if policy.get("human_review_required") is not True:
    raise SystemExit("revisao humana precisa ser obrigatoria")

if policy.get("ai_assistive_only") is not True:
    raise SystemExit("IA precisa ser apenas assistiva")

if policy.get("no_auto_publish") is not True:
    raise SystemExit("publicacao automatica precisa estar bloqueada")

if policy.get("no_clone") is not True:
    raise SystemExit("politica anti-clone precisa estar ativa")

if not isinstance(items, list):
    raise SystemExit("listings.json precisa ser lista")

print("BRICS Autos visual premium v0.2 smoke test OK")
print("url:", config.get("url"))
print("items:", len(items))
