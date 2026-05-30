from __future__ import annotations

import json
import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.planning_approval_packager.packager import PlanningApprovalPackager
from k_atlas.core.planning_approval_packager.policy import validate_planning_approval_packager_payload


REPORT = Path("reports/planning_approval_packager/latest_planning_approval_packager.json")

st.set_page_config(page_title="K-Atlas Planning Approval Packager", layout="wide")

st.title("K-Atlas Planning Approval Packager")
st.caption("Empacota planos para aprovação humana. Não executa comandos.")

packager = PlanningApprovalPackager()
latest = json.loads(REPORT.read_text(encoding="utf-8")) if REPORT.exists() else packager.save_report()
summary = latest.get("summary", {}) if latest else {}

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Planning queue", summary.get("planning_queue_total", 0))

with col2:
    st.metric("Pacotes", summary.get("approval_packages_total", 0))

with col3:
    st.metric("Criados", summary.get("packages_created", 0))

with col4:
    st.metric("Execucao real", str(summary.get("real_execution_enabled", False)))

st.divider()

tab_run, tab_packages, tab_plans, tab_report = st.tabs(["Empacotar", "Pacotes", "Planos", "Relatorio"])

with tab_run:
    scope = st.selectbox("Escopo", ["all", "core", "social", "saas", "external", "ops", "creative", "growth"])
    limit = st.number_input("Limite", min_value=1, max_value=100, value=25)

    payload = {
        "scope": scope,
        "limit": int(limit),
        "objective": "empacotar planos para aprovacao humana",
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

    if st.button("Criar pacotes de aprovacao", type="primary"):
        validation = validate_planning_approval_packager_payload(payload)
        if not validation["ok"]:
            st.error("Payload bloqueado pela politica.")
            st.json(validation)
        else:
            result = packager.package_plans(payload)
            st.success("Pacotes criados sem execucao real.")
            st.json(result)

with tab_packages:
    current = packager.summary()
    packages = current.get("package_queue", [])

    if not packages:
        st.info("Nenhum pacote ainda.")
    else:
        for item in packages:
            with st.expander(f"{item.get('status')} | {item.get('objective')}"):
                st.json(item)

with tab_plans:
    current = packager.summary()
    plans = current.get("planning_queue", [])

    if not plans:
        st.info("Nenhum plano encontrado.")
    else:
        for item in plans:
            with st.expander(f"{item.get('status')} | {item.get('objective')}"):
                st.json(item)

with tab_report:
    st.json(packager.save_report())
