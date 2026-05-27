from pathlib import Path
from datetime import datetime
import json


APPROVAL_DIR = Path.cwd() / "k_atlas" / "execution" / "pending"
APPROVAL_DIR.mkdir(parents=True, exist_ok=True)


def create_approval_request(plan, step):
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = APPROVAL_DIR / f"approval_{stamp}_{step.action}.json"

    data = {
        "created_at": datetime.now().isoformat(),
        "status": "pending",
        "plan_summary": plan.summary,
        "original_command": plan.original_command,
        "step": {
            "title": step.title,
            "description": step.description,
            "action": step.action,
            "risk_level": step.risk_level,
            "payload": step.payload,
        },
        "instruction": "Para aprovar, use o painel ou mova este item para execution/approved em versão futura."
    }

    file_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return file_path


def approval_message(step, approval_file):
    return (
        f"A etapa '{step.title}' exige confirmação antes de executar.\n\n"
        f"Motivo: risco nível {step.risk_level}.\n\n"
        f"Pedido de aprovação criado em:\n{approval_file}"
    )
