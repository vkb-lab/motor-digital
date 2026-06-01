import json
from pathlib import Path
import streamlit as st

from k_atlas.deploy_bridge import inspect_vercel_readiness

st.set_page_config(page_title="KOS Vercel Readiness", layout="wide")

st.title("KOS Vercel Readiness")
st.caption("Diagnostico do deploy bridge.")

readiness = inspect_vercel_readiness()
st.metric("Status", readiness.get("status"))
st.json(readiness)

preview_path = Path("reports/KOS_PHASE10_VERCEL_PREVIEW_RESULT.json")
if preview_path.exists():
    st.subheader("Ultimo preview")
    st.json(json.loads(preview_path.read_text(encoding="utf-8-sig")))
else:
    st.info("Nenhum preview Vercel registrado ainda.")
