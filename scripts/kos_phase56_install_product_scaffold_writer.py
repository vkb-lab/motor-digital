from pathlib import Path
from datetime import datetime, timezone
import json

ROOT = Path.cwd()

report = {
    "status": "PHASE56_INSTALLER_RECOVERED",
    "phase": "56",
    "note": "Installer corrigido por recuperacao operacional. Arquivos da fase sao gerados pelo comando de recuperacao.",
    "created_at": datetime.now(timezone.utc).isoformat(),
    "real_action_executed": False,
    "paid_ai_call_executed": False,
    "instagram_publish_executed": False
}

print(json.dumps(report, ensure_ascii=False, indent=2))