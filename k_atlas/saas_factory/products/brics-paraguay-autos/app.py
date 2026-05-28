
from pathlib import Path
import json
import uuid
import streamlit as st

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "listings.json"
PHOTOS = ROOT / "data" / "photos"

TXT = {
    "pt": {
        "title": "BRICS Paraguay Autos",
        "caption": "Marketplace de automoveis com camera, IA assistida e revisao humana.",
        "new": "Novo anuncio",
        "review": "Revisao",
        "ads": "Anuncios",
        "dash": "Dashboard",
        "save": "Salvar para revisao",
        "approve": "Aprovar"
    },
    "es": {
        "title": "BRICS Paraguay Autos",
        "caption": "Marketplace de autos con camara, IA asistida y revision humana.",
        "new": "Nuevo anuncio",
        "review": "Revision",
        "ads": "Anuncios",
        "dash": "Panel",
        "save": "Guardar para revision",
        "approve": "Aprobar"
    }
}

def load():
    DATA.parent.mkdir(parents=True, exist_ok=True)
    PHOTOS.mkdir(parents=True, exist_ok=True)
    if not DATA.exists():
        DATA.write_text("[]", encoding="utf-8")
    return json.loads(DATA.read_text(encoding="utf-8"))

def save(items):
    DATA.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")

def save_photo(upload):
    if upload is None:
        return ""
    ext = Path(upload.name if hasattr(upload, "name") else "camera.jpg").suffix.lower()
    if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
        ext = ".jpg"
    name = "auto-" + str(uuid.uuid4())[:8] + ext
    path = PHOTOS / name
    path.write_bytes(upload.getvalue())
    return "data/photos/" + name

def ai_mock(photo_name, cor):
    name = (photo_name or "").lower()
    marca = ""
    modelo = ""
    for b in ["toyota", "honda", "ford", "chevrolet", "hyundai", "kia", "nissan", "fiat"]:
        if b in name:
            marca = b.title()
    for m in ["hilux", "civic", "corolla", "gol", "s10"]:
        if m in name:
            modelo = m.title()
    titulo = (marca + " " + modelo).strip() or "Veiculo em venda"
    return {
        "titulo_pt": titulo + " no Paraguay",
        "titulo_es": titulo + " en Paraguay",
        "marca": marca,
        "modelo": modelo,
        "cor": cor,
        "estado_visual": "revisar por humano",
        "descricao_pt": "Sugestao inicial da IA. Revise todos os dados antes de publicar.",
        "descricao_es": "Sugerencia inicial de IA. Revise todos los datos antes de publicar."
    }

st.set_page_config(page_title="BRICS Paraguay Autos", layout="wide")

lang = st.sidebar.radio("Idioma", ["pt", "es"], horizontal=True)
t = TXT[lang]
items = load()

st.title(t["title"])
st.caption(t["caption"])

c1, c2, c3 = st.columns(3)
c1.metric("Total", len(items))
c2.metric("Pendentes", len([i for i in items if i.get("status") == "pendente"]))
c3.metric("Aprovados", len([i for i in items if i.get("status") == "aprovado"]))

tab1, tab2, tab3, tab4 = st.tabs([t["new"], t["review"], t["ads"], t["dash"]])

with tab1:
    st.subheader(t["new"])
    modo = st.radio("Foto", ["upload", "camera"], horizontal=True)
    foto = st.camera_input("Camera") if modo == "camera" else st.file_uploader("Upload", type=["jpg", "jpeg", "png", "webp"])
    cor_hint = st.text_input("Cor aparente")
    ai = ai_mock(getattr(foto, "name", ""), cor_hint)
    st.markdown("### IA assistida")
    st.json(ai)

    with st.form("form_auto"):
        titulo_pt = st.text_input("Titulo PT", value=ai["titulo_pt"])
        titulo_es = st.text_input("Titulo ES", value=ai["titulo_es"])
        marca = st.text_input("Marca", value=ai["marca"])
        modelo = st.text_input("Modelo", value=ai["modelo"])
        ano = st.text_input("Ano")
        preco = st.text_input("Preco")
        cidade = st.text_input("Cidade")
        telefone = st.text_input("Telefone")
        desc_pt = st.text_area("Descricao PT", value=ai["descricao_pt"])
        desc_es = st.text_area("Descripcion ES", value=ai["descricao_es"])
        revisado = st.checkbox("Confirmo que revisei as sugestoes da IA")
        ok = st.form_submit_button(t["save"])

    if ok:
        items.append({
            "id": str(uuid.uuid4()),
            "titulo_pt": titulo_pt,
            "titulo_es": titulo_es,
            "marca": marca,
            "modelo": modelo,
            "ano": ano,
            "preco": preco,
            "cidade": cidade,
            "telefone": telefone,
            "descricao_pt": desc_pt,
            "descricao_es": desc_es,
            "foto": save_photo(foto),
            "ai_reviewed": bool(revisado),
            "status": "pendente"
        })
        save(items)
        st.success("Anuncio salvo para revisao.")

with tab2:
    st.subheader(t["review"])
    for item in [x for x in items if x.get("status") == "pendente"]:
        with st.container(border=True):
            st.write(item.get("titulo_pt"))
            st.write("IA revisada:", item.get("ai_reviewed"))
            if st.button(t["approve"], key=item["id"]):
                item["status"] = "aprovado"
                item["ai_reviewed"] = True
                save(items)
                st.success("Aprovado. Recarregue a pagina.")

with tab3:
    st.subheader(t["ads"])
    for item in items:
        with st.container(border=True):
            title = item.get("titulo_pt") if lang == "pt" else item.get("titulo_es")
            desc = item.get("descricao_pt") if lang == "pt" else item.get("descricao_es")
            st.markdown("### " + str(title))
            if item.get("foto") and (ROOT / item["foto"]).exists():
                st.image(str(ROOT / item["foto"]), width=220)
            st.write("Marca/Modelo:", item.get("marca"), item.get("modelo"))
            st.write("Preco:", item.get("preco"))
            st.write("Cidade:", item.get("cidade"))
            st.write("Status:", item.get("status"))
            st.write(desc)

with tab4:
    st.subheader(t["dash"])
    st.json({
        "total": len(items),
        "pendentes": len([i for i in items if i.get("status") == "pendente"]),
        "aprovados": len([i for i in items if i.get("status") == "aprovado"]),
        "ia_nao_revisada": len([i for i in items if not i.get("ai_reviewed")])
    })
    st.dataframe(items, width="stretch")
