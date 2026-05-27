import json
from pathlib import Path
from datetime import datetime


BASE = Path.cwd()
K = BASE / "k_atlas"
REPORTS = K / "reports"
WORKSPACE = K / "workspace"
PENDING = K / "execution" / "pending"


def latest_file(path: Path, pattern: str):
    files = list(path.glob(pattern))
    if not files:
        return None
    return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)[0]


def latest_landing_folder():
    files = list(WORKSPACE.glob("**/index.html"))
    if not files:
        return None
    latest_index = sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)[0]
    return latest_index.parent


def create_ai_evolution_plan():
    latest_report = latest_file(REPORTS, "ai_brain_*.md")
    landing = latest_landing_folder()

    if not latest_report:
        raise FileNotFoundError("Nenhum relatório AI Brain encontrado.")

    if not landing:
        raise FileNotFoundError("Nenhuma landing encontrada no workspace.")

    ai_text = latest_report.read_text(encoding="utf-8", errors="ignore")

    out = landing / "AI_EVOLUTION_PLAN.md"
    out.write_text(
        f"""# Plano de evolução com IA

Data: {datetime.now().isoformat()}

## Landing alvo
{landing}

## Relatório IA usado
{latest_report}

---

{ai_text}

---

## Próximas ações sugeridas

1. Revisar este plano.
2. Aprovar aplicação prática.
3. Atualizar HTML/CSS/JS conforme as recomendações.
4. Abrir landing no navegador.
5. Salvar no GitHub.
""",
        encoding="utf-8"
    )

    PENDING.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    approval = PENDING / f"approval_{stamp}_apply_ai_landing_plan.json"

    payload = {
        "created_at": datetime.now().isoformat(),
        "status": "pending",
        "plan_summary": "Aplicar plano de evolução gerado pela IA na última landing.",
        "original_command": "aplicar evolução IA na última landing",
        "step": {
            "title": "Aplicar evolução IA na landing",
            "description": "Usar o plano AI_EVOLUTION_PLAN.md para evoluir HTML, CSS e copy da última landing.",
            "action": "apply_ai_landing_plan",
            "risk_level": 2,
            "payload": {
                "landing_path": str(landing),
                "plan_path": str(out),
                "ai_report_path": str(latest_report)
            }
        },
        "instruction": "Aprovar para aplicar evolução prática na landing."
    }

    approval.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Plano IA criado em: {out}")
    print(f"Aprovação criada em: {approval}")


if __name__ == "__main__":
    create_ai_evolution_plan()
