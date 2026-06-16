from pathlib import Path
import json
from datetime import datetime, timezone

ROOT = Path.cwd()

def now():
    return datetime.now(timezone.utc).isoformat()

def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

policy = {
    "status": "ACTIVE",
    "phase": "48",
    "module": "K-OS Autonomy Evidence Ledger",
    "mode": "LOCAL_AUDIT_LEDGER_ONLY",
    "goal": "registrar evidencias auditaveis dos ciclos autonomos locais do K-OS",
    "allowed_actions": {
        "read_health": True,
        "read_briefing": True,
        "read_scheduler_tick": True,
        "read_git_status": True,
        "write_local_evidence_ledger": True,
        "write_local_summary": True
    },
    "blocked_actions": {
        "instagram_publish": True,
        "paid_ai_call": True,
        "secret_exposure": True,
        "codex_auto_execute": True,
        "production_publish": True,
        "auto_commit": True,
        "auto_push": True
    },
    "hard_rules": {
        "local_only": True,
        "append_only_runtime": True,
        "no_paid_ai": True,
        "no_external_publish": True,
        "no_secret_exposure": True,
        "parada_atlantida_locked": True,
        "hupmix_test_only": True
    },
    "created_at": now()
}

evidence_code = r'''
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
import subprocess
import uuid

ROOT = Path(__file__).resolve().parents[2]
LOG_DIR = ROOT / "logs" / "kaizen" / "evidence"
LEDGER_PATH = LOG_DIR / "evidence_ledger.jsonl"
SUMMARY_PATH = LOG_DIR / "latest_evidence_summary.json"

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _run(cmd: list[str], timeout: int = 30) -> dict:
    try:
        proc = subprocess.run(
            cmd,
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "ok": proc.returncode == 0,
            "returncode": proc.returncode,
            "stdout": (proc.stdout or "")[-5000:],
            "stderr": (proc.stderr or "")[-5000:],
        }
    except Exception as exc:
        return {
            "ok": False,
            "returncode": -1,
            "stdout": "",
            "stderr": str(exc),
        }

def _read_json(path: Path, default):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8-sig"))
        except Exception as exc:
            return {"error": str(exc), "path": str(path)}
    return default

def _append_jsonl(path: Path, item: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")

def _write_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def get_git_status() -> dict:
    return {
        "branch": _run(["git", "branch", "--show-current"]).get("stdout", "").strip(),
        "status_short": _run(["git", "--no-pager", "status", "--short"]).get("stdout", ""),
        "last_commit": _run(["git", "--no-pager", "log", "--oneline", "-1"]).get("stdout", "").strip(),
    }

def build_evidence_entry(source: str = "manual", note: str = "", extra: dict | None = None) -> dict:
    health_path = ROOT / "logs" / "kaizen" / "health" / "last_health.json"
    briefing_path = ROOT / "logs" / "kaizen" / "briefing" / "daily_briefing_latest.json"
    scheduler_path = ROOT / "logs" / "kaizen" / "briefing_scheduler" / "last_briefing_scheduler_tick.json"
    startup_path = ROOT / "local_runtime" / "kaizen" / "startup_folder_status.json"

    health = _read_json(health_path, {})
    briefing = _read_json(briefing_path, {})
    scheduler = _read_json(scheduler_path, {})
    startup = _read_json(startup_path, {})
    git = get_git_status()

    runtime_locks = health.get("runtime_locks", {}) if isinstance(health, dict) else {}

    entry = {
        "status": "KOS_AUTONOMY_EVIDENCE_RECORDED",
        "evidence_id": "KOS-EVIDENCE-" + uuid.uuid4().hex[:12].upper(),
        "source": source,
        "note": note,
        "created_at": now(),
        "git": {
            "branch": git.get("branch"),
            "dirty": bool((git.get("status_short") or "").strip()),
            "status_short": git.get("status_short"),
            "last_commit": git.get("last_commit"),
        },
        "health": {
            "health_status": health.get("health_status"),
            "warnings": health.get("warnings", []),
            "startup_installed": health.get("startup_folder", {}).get("installed"),
            "background_running": health.get("background_processes", {}).get("running"),
            "scheduler_tick_exists": health.get("scheduler_last_tick", {}).get("exists"),
        },
        "briefing": {
            "status": briefing.get("status"),
            "risk_level": briefing.get("risk_level"),
            "health_status": briefing.get("health_status"),
            "priorities": briefing.get("priorities", []),
        },
        "scheduler": {
            "status": scheduler.get("status"),
            "cycle_id": scheduler.get("cycle_id"),
            "created_at": scheduler.get("created_at"),
        },
        "startup": {
            "installed": startup.get("installed"),
            "entry_path": startup.get("entry_path"),
        },
        "locks": {
            "production_publish_locked": runtime_locks.get("production_publish_locked", True),
            "paid_ai_locked": runtime_locks.get("paid_ai_locked", True),
            "parada_atlantida_locked": runtime_locks.get("parada_atlantida_locked", True),
            "hupmix_test_only": runtime_locks.get("hupmix_test_only", True),
        },
        "extra": extra or {},
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "external_side_effects_executed": False,
    }

    return entry

def append_evidence(source: str = "manual", note: str = "", extra: dict | None = None) -> dict:
    entry = build_evidence_entry(source=source, note=note, extra=extra)
    _append_jsonl(LEDGER_PATH, entry)
    summary = summarize_evidence(limit=10)
    _write_json(SUMMARY_PATH, summary)
    return entry

def summarize_evidence(limit: int = 10) -> dict:
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    entries = []
    if LEDGER_PATH.exists():
        lines = LEDGER_PATH.read_text(encoding="utf-8-sig", errors="replace").splitlines()
        for line in lines[-limit:]:
            if not line.strip():
                continue
            try:
                entries.append(json.loads(line))
            except Exception:
                pass

    latest = entries[-1] if entries else {}

    return {
        "status": "KOS_EVIDENCE_LEDGER_SUMMARY",
        "ledger_exists": LEDGER_PATH.exists(),
        "ledger_path": str(LEDGER_PATH.relative_to(ROOT)).replace("\\", "/"),
        "entries_returned": len(entries),
        "latest_evidence_id": latest.get("evidence_id"),
        "latest_source": latest.get("source"),
        "latest_health_status": latest.get("health", {}).get("health_status"),
        "latest_risk_level": latest.get("briefing", {}).get("risk_level"),
        "latest_git_dirty": latest.get("git", {}).get("dirty"),
        "last_entries": entries,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "external_side_effects_executed": False,
        "created_at": now(),
    }

if __name__ == "__main__":
    item = append_evidence(source="phase48_manual", note="manual evidence ledger run")
    print(json.dumps({
        "recorded": item,
        "summary": summarize_evidence(),
    }, ensure_ascii=False, indent=2))
'''

runner_code = r'''
from pathlib import Path
import sys
import json

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from k_atlas.kaizen.evidence_ledger import append_evidence, summarize_evidence

if __name__ == "__main__":
    entry = append_evidence(
        source="phase48_runner",
        note="Registro manual da Fase 48.",
        extra={"phase": "48"}
    )

    summary = summarize_evidence(limit=10)

    print(json.dumps({
        "status": "PHASE48_EVIDENCE_LEDGER_RECORDED",
        "evidence_id": entry.get("evidence_id"),
        "summary": summary,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False
    }, ensure_ascii=False, indent=2))
'''

page_code = r'''
import streamlit as st

from k_atlas.kaizen.evidence_ledger import append_evidence, summarize_evidence

st.set_page_config(page_title="KOS Evidence Ledger", layout="wide")

st.title("KOS Autonomy Evidence Ledger")
st.caption("Historico auditavel local dos ciclos autonomos do K-OS.")

summary = summarize_evidence(limit=20)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Ledger", "SIM" if summary.get("ledger_exists") else "NAO")
col2.metric("Entries", summary.get("entries_returned", 0))
col3.metric("Health", summary.get("latest_health_status", "N/A"))
col4.metric("Risk", summary.get("latest_risk_level", "N/A"))

if st.button("Registrar evidencia agora", use_container_width=True):
    entry = append_evidence(source="streamlit_manual", note="Registro manual pelo cockpit.")
    st.json(entry)
    st.rerun()

st.subheader("Resumo")
st.json(summary)

st.warning("Ledger local read-only/append-only. Nao publica, nao usa IA paga e nao executa Codex.")
'''

test_code = r'''
from k_atlas.kaizen.evidence_ledger import build_evidence_entry, append_evidence, summarize_evidence

def test_build_evidence_entry_is_safe():
    entry = build_evidence_entry(source="test", note="safe test")

    assert entry["status"] == "KOS_AUTONOMY_EVIDENCE_RECORDED"
    assert entry["real_action_executed"] is False
    assert entry["paid_ai_call_executed"] is False
    assert entry["instagram_publish_executed"] is False
    assert entry["external_side_effects_executed"] is False

def test_append_evidence_and_summary_are_safe():
    entry = append_evidence(source="test_phase48", note="test append")
    summary = summarize_evidence(limit=5)

    assert entry["evidence_id"]
    assert summary["status"] == "KOS_EVIDENCE_LEDGER_SUMMARY"
    assert summary["real_action_executed"] is False
    assert summary["paid_ai_call_executed"] is False
    assert summary["instagram_publish_executed"] is False
    assert summary["external_side_effects_executed"] is False
'''

save_json(ROOT / "config" / "kos_evidence_ledger_policy.json", policy)
write(ROOT / "k_atlas" / "kaizen" / "evidence_ledger.py", evidence_code.strip() + "\n")
write(ROOT / "scripts" / "run_phase48_evidence_ledger.py", runner_code.strip() + "\n")
write(ROOT / "pages" / "KOS_Evidence_Ledger.py", page_code.strip() + "\n")
write(ROOT / "tests" / "test_phase48_evidence_ledger.py", test_code.strip() + "\n")

briefing_scheduler_path = ROOT / "k_atlas" / "kaizen" / "briefing_scheduler.py"
if briefing_scheduler_path.exists():
    text = briefing_scheduler_path.read_text(encoding="utf-8-sig")
    if "append_evidence(source=\"briefing_scheduler_tick\"" not in text:
        old = '''    _save_json(LAST_TICK, report)
    return report
'''
        new = '''    try:
        from k_atlas.kaizen.evidence_ledger import append_evidence
        evidence = append_evidence(
            source="briefing_scheduler_tick",
            note=cycle_id,
            extra={
                "cycle_id": cycle_id,
                "tick_status": report.get("status")
            }
        )
        report["evidence_ledger"] = {
            "recorded": True,
            "evidence_id": evidence.get("evidence_id")
        }
    except Exception as exc:
        report["evidence_ledger"] = {
            "recorded": False,
            "error": str(exc)
        }

    _save_json(LAST_TICK, report)
    return report
'''
        if old in text:
            text = text.replace(old, new)
            briefing_scheduler_path.write_text(text, encoding="utf-8")

report = {
    "status": "PHASE48_EVIDENCE_LEDGER_BOOTSTRAPPED",
    "phase": "48",
    "created_files": [
        "config/kos_evidence_ledger_policy.json",
        "k_atlas/kaizen/evidence_ledger.py",
        "scripts/run_phase48_evidence_ledger.py",
        "pages/KOS_Evidence_Ledger.py",
        "tests/test_phase48_evidence_ledger.py"
    ],
    "modified_files": [
        "k_atlas/kaizen/briefing_scheduler.py"
    ],
    "runtime_files": [
        "logs/kaizen/evidence/evidence_ledger.jsonl",
        "logs/kaizen/evidence/latest_evidence_summary.json"
    ],
    "real_action_executed": False,
    "paid_ai_call_executed": False,
    "instagram_publish_executed": False,
    "created_at": now()
}

save_json(ROOT / "reports" / "KOS_PHASE48_EVIDENCE_LEDGER_BOOTSTRAP.json", report)

print(json.dumps(report, ensure_ascii=False, indent=2))