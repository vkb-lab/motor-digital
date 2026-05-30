from __future__ import annotations

import json
import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.publish_approval_gate.gate import SecurePublishApprovalGate
from k_atlas.core.publish_approval_gate.policy import validate_publish_approval_payload


REPORT = Path("reports/publish_approval_gate/latest_publish_approval_gate.json")

st.set_page_config(page_title="K-Atlas Secure Publish Approval Gate", layout="wide")

st.title("K-Atlas Secure Publish Approval Gate")
st.caption("Fila de aprovação humana antes de publicação, envio, deploy ou chamada externa real.")

gate = SecurePublishApprovalGate()
latest = json.loads(REPORT.read_text(encoding="utf-8")) if REPORT.exists() else gate.save_report()
counts = latest.get("counts", {})

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Pendentes", counts.get("pending", 0))

with col2:
    st.metric("Aprovados", counts.get("approved_waiting_execution_gate", 0))

with col3:
    st.metric("Negados", counts.get("denied", 0))

with col4:
    st.metric("Execução ativa", str(latest.get("execution_enabled", False)))

st.divider()

tab_create, tab_pending, tab_all, tab_report = st.tabs(["Criar pedido", "Pendentes", "Fila completa", "Relatório"])

with tab_create:
    payload_text = st.text_area(
        "Payload de aprovação",
        value=json.dumps(gate.default_payload(), ensure_ascii=False, indent=2),
        height=420,
    )

    if st.button("Criar pedido de aprovação", type="primary"):
        try:
            payload = json.loads(payload_text)
        except json.JSONDecodeError as exc:
            st.error(f"JSON inválido: {exc}")
        else:
            validation = validate_publish_approval_payload(payload)
            if not validation["ok"]:
                st.error("Pedido bloqueado pela política.")
                st.json(validation)
            else:
                request = gate.create_request(payload)
                st.success("Pedido criado. Aguardando aprovação humana.")
                st.json(request)

with tab_pending:
    pending = gate.pending()

    if not pending:
        st.info("Nenhum pedido pendente.")
    else:
        for item in pending:
            with st.expander(f"{item.get('payload', {}).get('title')} | {item.get('request_id')}"):
                st.json(item)

                col_a, col_b = st.columns(2)

                with col_a:
                    if st.button(f"Aprovar {item.get('request_id')}", key=f"approve_{item.get('request_id')}"):
                        result = gate.decide(
                            item.get("request_id"),
                            "approved",
                            reviewer="streamlit_operator",
                            notes="Aprovado pelo cockpit. Sem execução externa automática.",
                        )
                        st.success("Aprovação registrada. Execução externa segue bloqueada.")
                        st.json(result)

                with col_b:
                    if st.button(f"Negar {item.get('request_id')}", key=f"deny_{item.get('request_id')}"):
                        result = gate.decide(
                            item.get("request_id"),
                            "denied",
                            reviewer="streamlit_operator",
                            notes="Negado pelo cockpit.",
                        )
                        st.warning("Pedido negado.")
                        st.json(result)

with tab_all:
    report = gate.save_report()
    for item in report.get("queue", []):
        with st.expander(f"{item.get('status')} | {item.get('payload', {}).get('title')}"):
            st.json(item)

with tab_report:
    st.json(gate.save_report())
