from __future__ import annotations

import json
import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.adapter_dry_run_orchestrator.orchestrator import AdapterDryRunOrchestrator
from k_atlas.core.adapter_dry_run_orchestrator.policy import validate_adapter_dry_run_payload


REPORT = Path("reports/adapter_dry_run_orchestrator/latest_adapter_dry_run_orchestrator.json")

st.set_page_config(page_title="K-Atlas Adapter Dry Run Orchestrator", layout="wide")

st.title("K-Atlas Adapter Dry Run Orchestrator")
st.caption("Valida contratos de adapters reais em modo seco. Sem chamada externa.")

orchestrator = AdapterDryRunOrchestrator()
latest = json.loads(REPORT.read_text(encoding="utf-8")) if REPORT.exists() else {}
summary = latest.get("summary", {}) if latest else {}

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Checados", summary.get("contracts_checked", 0))

with col2:
    st.metric("Passaram", summary.get("dry_run_passed", 0))

with col3:
    st.metric("Falharam", summary.get("dry_run_failed", 0))

with col4:
    st.metric("Execucao real", str(summary.get("real_execution_enabled", False)))

st.divider()

tab_run, tab_results, tab_guardrails, tab_report = st.tabs(["Rodar dry run", "Resultados", "Guardrails", "Relatorio"])

with tab_run:
    scope = st.selectbox(
        "Escopo",
        ["all", "instagram", "whatsapp", "render", "github", "openai", "google", "meta"],
    )

    payload = {
        "scope": scope,
        "objective": "validar adapters em modo seco",
        "live_call": False,
        "real_execute": False,
        "auto_publish": False,
        "auto_send": False,
        "auto_deploy": False,
        "mass_messaging": False,
        "browser_automation": False,
        "bypass_human_approval": False,
    }

    st.json(payload)

    if st.button("Executar dry run", type="primary"):
        validation = validate_adapter_dry_run_payload(payload)
        if not validation["ok"]:
            st.error("Payload bloqueado pela politica.")
            st.json(validation)
        else:
            result = orchestrator.run(payload)
            st.success("Dry run executado sem efeitos externos.")
            st.json(result)

with tab_results:
    if not latest:
        st.info("Nenhum dry run ainda.")
    else:
        for item in latest.get("dry_runs", []):
            with st.expander(f"{item.get('adapter_id')} | {item.get('status')}"):
                st.json(item)

with tab_guardrails:
    if not latest:
        st.info("Sem guardrails ainda.")
    else:
        for item in latest.get("guardrails", []):
            st.write(f"- {item}")

with tab_report:
    if latest:
        st.json(latest)
    else:
        st.info("Nenhum relatorio ainda.")
