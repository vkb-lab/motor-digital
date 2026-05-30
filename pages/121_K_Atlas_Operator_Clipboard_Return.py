from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.operator_clipboard_return.clipboard_return import OperatorClipboardReturn

st.set_page_config(page_title="K-Atlas Clipboard Return", layout="wide")
st.title("K-Atlas Operator Clipboard Return")

module = OperatorClipboardReturn()
status = st.selectbox("Status", ["ok", "erro"])
details = st.text_area("Detalhes", value="retorno operacional")

if st.button("Gerar retorno"):
    st.json(module.build_return(status, details))
