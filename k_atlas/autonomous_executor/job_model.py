from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import List, Dict, Any

@dataclass
class AutonomousJob:
    job_id: str
    client_id: str
    command: str
    tasks: List[Dict[str, Any]]
    status: str = "PENDING_FINAL_APPROVAL"
    created_at: str = datetime.now(timezone.utc).isoformat()

    def to_dict(self):
        return asdict(self)
