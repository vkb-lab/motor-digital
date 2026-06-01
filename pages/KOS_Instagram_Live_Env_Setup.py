import streamlit as st
from k_atlas.ig_live_check.live_check_runner import build_live_ready_package

st.set_page_config(page_title="KOS Instagram Live Env Setup", layout="wide")

st.title("KOS Instagram Live Env Setup")
st.caption("Prepara o arquivo local de runtime. Nao coloque chaves no chat.")

if st.button("Gerar pacote live check", use_container_width=True):
    package = build_live_ready_package()
    st.session_state["phase13_package"] = package
    st.success("Pacote gerado. Edite o arquivo local_runtime/ig_runtime.env no seu computador.")

package = st.session_state.get("phase13_package")
if package:
    st.metric("Status", package["status"])
    st.write("Arquivo local:")
    st.code(package["template_path"])
    st.json(package)
else:
    st.info("Clique para gerar o pacote.")
