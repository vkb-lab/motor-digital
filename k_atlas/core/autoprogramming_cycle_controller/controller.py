from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from k_atlas.core.autoprogramming_cycle_dashboard.dashboard import AutoprogrammingCycleDashboard
from .policy import validate_cycle_control_request

def now():
    return datetime.now(timezone.utc).isoformat()

class AutoprogrammingCycleController:
    def __init__(self, project_root=".", live_dir="live/autoprogramming_cycle_controller", memory_dir="memory/autoprogramming_cycle_controller", reports_dir="reports/autoprogramming_cycle_controller"):
        self.project_root = Path(project_root)
        self.live_dir = self.project_root / live_dir
        self.memory_dir = self.project_root / memory_dir
        self.reports_dir = self.project_root / reports_dir
        self.queue_path = self.live_dir / "cycle_decision_queue.json"
        self.events_path = self.memory_dir / "events.jsonl"

    def load_list(self, path):
        if not Path(path).exists():
            return []
        try:
            data = json.loads(Path(path).read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except Exception:
            return []

    def save_list(self, path, rows):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(json.dumps(rows, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")

    def event(self, event_type, payload):
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        row = {"timestamp": now(), "event_type": event_type, "payload": payload}
        with self.events_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    def build_state(self):
        report = AutoprogrammingCycleDashboard(project_root=self.project_root).build_report()
        summary = report.get("summary", {})
        return {
            "ok": True,
            "generated_at": now(),
            "dashboard_status": report.get("status"),
            "cycle_ready": bool(summary.get("cycle_ready", False)),
            "checkpoints_total": summary.get("checkpoints_total", 0),
            "checkpoints_operational": summary.get("checkpoints_operational", 0),
            "queues": report.get("queues", {}),
            "execution_enabled": False,
            "real_execution_enabled": False,
            "external_side_effects": "none",
        }

    def decide_next_action(self, state):
        queues = state.get("queues", {}) or {}
        if not state.get("cycle_ready"):
            return {"action": "stabilize_autoprogramming_cycle", "priority": "high", "reason": "cycle_not_ready", "human_instruction": "Abrir dashboard 71 e corrigir incompletos.", "suggested_checkpoint": "71_fix"}
        if queues.get("manual_apply_manifest", 0) > queues.get("manual_rollback_manifest", 0):
            return {"action": "confirm_rollback_readiness", "priority": "medium", "reason": "manual_apply_without_matching_rollback", "human_instruction": "Abrir pagina 70 e rodar dry-run de rollback.", "suggested_checkpoint": "70_review"}
        return {"action": "prepare_next_safe_autoprogramming_proposal", "priority": "medium", "reason": "cycle_ready_and_reversible", "human_instruction": "Preparar nova proposta assistida sem execucao automatica.", "suggested_checkpoint": "73"}

    def build_decision(self, request=None):
        request = dict(request or {"mode": "recommend"})
        validation = validate_cycle_control_request(request)
        decision_id = str(uuid4())
        if not validation["ok"]:
            decision = {"ok": False, "checkpoint": "72", "name": "Autoprogramming Cycle Controller", "decision_id": decision_id, "generated_at": now(), "status": "blocked_by_policy", "request_validation": validation, "execution_enabled": False, "real_execution_enabled": False, "external_side_effects": "none"}
            self.save_report(decision)
            return decision
        state = self.build_state()
        decision = {
            "ok": True,
            "checkpoint": "72",
            "name": "Autoprogramming Cycle Controller",
            "decision_id": decision_id,
            "generated_at": now(),
            "status": "decision_ready",
            "mode": validation["mode"],
            "state": state,
            "next_action": self.decide_next_action(state),
            "human_approval_required": True,
            "automatic_execution_allowed": False,
            "execution_enabled": False,
            "real_execution_enabled": False,
            "external_side_effects": "none",
            "guardrails": [
                "controller apenas recomenda",
                "controller nao aplica arquivos",
                "controller nao executa rollback",
                "controller nao chama API externa",
                "controller exige humano para qualquer acao real",
            ],
        }
        q = self.load_list(self.queue_path)
        q.append(decision)
        self.save_list(self.queue_path, q)
        self.save_report(decision)
        self.event("autoprogramming_cycle_controller.decision_ready", {"decision_id": decision_id, "action": decision["next_action"]["action"]})
        return decision

    def summary(self):
        q = self.load_list(self.queue_path)
        state = self.build_state()
        return {"ok": True, "checkpoint": "72", "name": "Autoprogramming Cycle Controller", "generated_at": now(), "status": "operational", "state": state, "summary": {"decision_queue_total": len(q), "cycle_ready": state.get("cycle_ready"), "execution_enabled": False, "real_execution_enabled": False, "external_side_effects": "none"}, "latest_decision": q[-1] if q else None}

    def save_report(self, report):
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        (self.reports_dir / "latest_autoprogramming_cycle_controller.json").write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        md = ["# K-Atlas Autoprogramming Cycle Controller", "", f"Checkpoint: {report.get('checkpoint')}", f"Status: {report.get('status')}", "", "## Guardrails"]
        for g in report.get("guardrails", []):
            md.append(f"- {g}")
        (self.reports_dir / "latest_autoprogramming_cycle_controller.md").write_text("\n".join(md), encoding="utf-8")
        return report
