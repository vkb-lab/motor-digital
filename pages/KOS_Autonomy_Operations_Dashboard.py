from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_PATH = ROOT / "local_runtime" / "kos_autonomy_operations" / "latest_operations_snapshot.json"


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"status": "SNAPSHOT_NOT_FOUND", "path": str(path)}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        return {"status": "SNAPSHOT_READ_FAILED", "error": str(exc), "path": str(path)}


st.set_page_config(page_title="K-OS Autonomy Operations", layout="wide")
st.title("K-OS Autonomy Operations Dashboard")

snapshot = read_json(SNAPSHOT_PATH)

col1, col2, col3 = st.columns(3)
col1.metric("Snapshot", str(snapshot.get("status", "UNKNOWN")))
col2.metric("Kill Switch engaged", str(snapshot.get("kill_switch_engaged", "UNKNOWN")))
col3.metric("Paid AI locked", str(snapshot.get("paid_ai_locked", True)))

st.subheader("Report statuses")
st.json(snapshot.get("report_statuses", {}))

st.subheader("Runtime files")
st.json(snapshot.get("runtime_files", {}))

st.subheader("Operator commands")
for key in [
    "operator_command",
    "batch_command",
    "mission_command",
    "mission_queue_submit_command",
    "mission_queue_process_command",
]:
    st.code(snapshot.get(key, ""), language="powershell")

st.subheader("Emergency controls")
st.code(snapshot.get("kill_switch_engage_command", ""), language="powershell")
st.code(snapshot.get("kill_switch_disengage_command", ""), language="powershell")
