
# -*- coding: utf-8 -*-
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent
APP = ROOT / "k_atlas" / "saas_factory" / "products" / "closet-pilot" / "app.py"
DATA = ROOT / "k_atlas" / "saas_factory" / "products" / "closet-pilot" / "data" / "wardrobe_items.json"
SERVER = ROOT / "k_atlas" / "saas_factory" / "products" / "closet-pilot" / "server" / "server_config.json"

if not APP.exists():
    raise SystemExit("app.py nao existe")

if not DATA.exists:
    raise SystemExit("wardrobe_items.json nao existe")

items = json.loads(DATA.read_text(encoding="utf-8"))

if not isinstance(items, list):
    raise SystemExit("wardrobe_items.json deve ser lista")

if len(items) < 1:
    raise SystemExit("wardrobe precisa ter itens iniciais")

config = json.loads(SERVER.read_text(encoding="utf-8"))

if config["host"] != "127.0.0.1":
    raise SystemExit("host local incorreto")

if config["port"] != 8601:
    raise SystemExit("porta incorreta")

print("Closet Pilot hosted-local smoke test OK")
print("app:", APP)
print("url:", config["url"])
