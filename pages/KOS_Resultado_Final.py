import json
from pathlib import Path
import streamlit as st

st.set_page_config(page_title="Resultado Final K-OS", layout="wide")

st.title("Resultado Final K-OS")
st.caption("Conferencia final antes de qualquer acao real")

ROOT = Path.cwd()
demo_path = ROOT / "reports" / "KOS_PHASE6_AUTONOMOUS_DEMO_RESULT.json"

if demo_path.exists():
    data = json.loads(demo_path.read_text(encoding="utf-8-sig"))
    st.metric("Status", data.get("status", ""))
    st.metric("Cliente", data.get("client_id", ""))
    st.subheader("Final Review")
    st.json(data.get("final_review", {}))
    st.subheader("Artefatos")
    st.json(data.get("artifacts", {}))
    st.warning("Acoes reais continuam bloqueadas ate aprovacao final.")
else:
    st.info("Nenhum resultado final encontrado. Rode o Autopilot Demo primeiro.")
