from pathlib import Path
import json
import html

from k_atlas.deploy_bridge.deploy_manifest import build_deploy_manifest

ROOT = Path(__file__).resolve().parents[2]

def export_public_status():
    manifest = build_deploy_manifest()

    status_path = ROOT / "public" / "kos" / "status.json"
    status_path.parent.mkdir(parents=True, exist_ok=True)
    status_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    page = f"""
<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>K-OS Production Bridge</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 48px; color: #111827; }}
    .card {{ border: 1px solid #e5e7eb; border-radius: 16px; padding: 24px; max-width: 860px; }}
    .status {{ font-size: 32px; font-weight: 700; }}
    code, pre {{ background: #f3f4f6; padding: 12px; border-radius: 12px; display: block; overflow:auto; }}
  </style>
</head>
<body>
  <div class="card">
    <h1>K-Atlas OS</h1>
    <p>Production Deploy Bridge</p>
    <div class="status">{html.escape(manifest["status"])}</div>
    <h2>Estado</h2>
    <pre>{html.escape(json.dumps(manifest, ensure_ascii=False, indent=2))}</pre>
    <p>Nenhuma publicacao real foi executada. A proxima etapa conecta o canal real com revisao humana.</p>
  </div>
</body>
</html>
"""
    index_path = ROOT / "public" / "kos" / "index.html"
    index_path.write_text(page, encoding="utf-8")

    confirmation = f"""
<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>K-OS Deploy Confirmation</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 48px; color: #111827; }}
    .box {{ border: 1px solid #e5e7eb; border-radius: 16px; padding: 24px; max-width: 860px; }}
    .ok {{ color: #047857; font-size: 30px; font-weight: 700; }}
  </style>
</head>
<body>
  <div class="box">
    <h1>K-OS Deploy Confirmation</h1>
    <div class="ok">READY_FOR_VERCEL_PREVIEW</div>
    <p>Fase 10 preparada. Deploy real depende do Vercel CLI estar autenticado neste computador.</p>
    <p>Real publish: false</p>
    <p>External call executed by K-OS: false</p>
    <p>Manual review required: true</p>
  </div>
</body>
</html>
"""
    confirm_path = ROOT / "public" / "kos" / "phase10_confirmation.html"
    confirm_path.write_text(confirmation, encoding="utf-8")

    return {
        "status": "PUBLIC_EXPORT_READY",
        "manifest": manifest,
        "status_path": str(status_path),
        "index_path": str(index_path),
        "confirmation_path": str(confirm_path),
    }
