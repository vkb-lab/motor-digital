import sys
import platform
from pathlib import Path
from datetime import datetime

base = Path.cwd()
exports = base / "k_atlas" / "exports"
exports.mkdir(parents=True, exist_ok=True)

report = []
report.append("# Diagnóstico K-Atlas Local")
report.append("")
report.append(f"Data: {datetime.now()}")
report.append(f"Sistema: {platform.system()} {platform.release()}")
report.append(f"Python: {sys.version}")
report.append(f"Pasta atual: {base}")
report.append("")
report.append("## Arquivos principais")

for name in ["agent_core.py", "local_dashboard.py", "self_evolution.py", ".env", "requirements.txt"]:
    path = base / name
    report.append(f"- {name}: {'OK' if path.exists() else 'NÃO ENCONTRADO'}")

report.append("")
report.append("## Pastas K-Atlas")

for folder in ["k_atlas/core", "k_atlas/agents", "k_atlas/memory", "k_atlas/projects", "k_atlas/exports"]:
    path = base / folder
    report.append(f"- {folder}: {'OK' if path.exists() else 'NÃO ENCONTRADO'}")

out = exports / "diagnostico-k-atlas-local.md"
out.write_text("\n".join(report), encoding="utf-8")

print(f"Diagnóstico gerado em: {out}")
