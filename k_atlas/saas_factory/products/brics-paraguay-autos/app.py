
from pathlib import Path
import json
import uuid
import streamlit as st

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "listings.json"
PHOTOS = ROOT / "data" / "photos"

TEXT = {
    "pt": {
        "hero": "Venda seu carro com fotos, IA e confiança.",
        "sub": "Marketplace automotivo com câmera, IA assistida e revisão humana.",
        "ads": "Vitrine",
        "new": "Anunciar",
        "review": "Revisão",
        "dash": "Dashboard",
        "save": "Salvar para revisão",
        "approve": "Aprovar anúncio"
    },
    "es": {
        "hero": "Venda tu auto con fotos, IA y confianza.",
        "sub": "Marketplace automotriz con cámara, IA asistida y revisión humana.",
        "ads": "Vitrina",
        "new": "Anunciar",
        "review": "Revisión",
        "dash": "Panel",
        "save": "Guardar para revisión",
        "approve": "Aprobar anuncio"
    }
}

DEMO = [
    {
        "id": "demo-1",
        "titulo_pt": "Toyota Hilux 2020 pronta para negociar",
        "titulo_es": "Toyota Hilux 2020 lista para negociar",
        "marca": "Toyota",
        "modelo": "Hilux",
        "ano": "2020",
        "preco": "185000000",
        "cidade": "Asuncion",
        "telefone": "",
        "descricao_pt": "Pickup forte, visual revisado e anúncio demonstrativo do BRICS.",
        "descricao_es": "Pickup fuerte, visual revisado y anuncio demostrativo de BRICS.",
        "foto": "",
        "ai_reviewed": True,
        "status": "aprovado"
    },
    {
        "id": "demo-2",
        "titulo_pt": "Honda Civic 2019 econômico e confortável",
        "titulo_es": "Honda Civic 2019 económico y cómodo",
        "marca": "Honda",
        "modelo": "Civic",
        "ano": "2019",
        "preco": "98000000",
        "cidade": "Ciudad del Este",
        "telefone": "",
        "descricao_pt": "Sedan elegante para cidade e estrada.",
        "descricao_es": "Sedán elegante para ciudad y ruta.",
        "foto": "",
        "ai_reviewed": True,
        "status": "aprovado"
    }
]

def ensure():
    DATA.parent.mkdir(parents=True, exist_ok=True)
    PHOTOS.mkdir(parents=True, exist_ok=True)
    if not DATA.exists():
        DATA.write_text(json.dumps(DEMO, ensure_ascii=False, indent=2), encoding="utf-8")
    else:
        try:
            items = json.loads(DATA.read_text(encoding="utf-8"))
            if isinstance(items, list) and len(items) == 0:
                DATA.write_text(json.dumps(DEMO, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            DATA.write_text(json.dumps(DEMO, ensure_ascii=False, indent=2), encoding="utf-8")

def load():
    ensure()
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

    for b in ["toyota", "honda", "ford", "chevrolet", "hyundai", "kia", "nissan", "fiat", "volkswagen"]:
        if b in name:
            marca = b.title()

    for m in ["hilux", "civic", "corolla", "gol", "s10", "sentra", "tucson"]:
        if m in name:
            modelo = m.title()

    base = (marca + " " + modelo).strip() or "Veículo"
    return {
        "titulo_pt": base + " em venda no Paraguay",
        "titulo_es": base + " en venta en Paraguay",
        "marca": marca,
        "modelo": modelo,
        "cor": cor,
        "estado_visual": "revisar por humano",
        "descricao_pt": "Sugestão inicial da IA. Revise marca, modelo, ano, preço e documentação antes de publicar.",
        "descricao_es": "Sugerencia inicial de IA. Revise marca, modelo, año, precio y documentación antes de publicar."
    }

def num(value):
    try:
        return int(str(value).replace(".", "").replace(",", "").replace(" ", ""))
    except Exception:
        return 0

def stats(items):
    return {
        "total": len(items),
        "pendentes": len([x for x in items if x.get("status") == "pendente"]),
        "aprovados": len([x for x in items if x.get("status") == "aprovado"]),
        "ia_nao_revisada": len([x for x in items if not x.get("ai_reviewed")])
    }

def card(item, lang):
    title = item.get("titulo_pt") if lang == "pt" else item.get("titulo_es")
    desc = item.get("descricao_pt") if lang == "pt" else item.get("descricao_es")
    st.markdown('<div class="vehicle-card">', unsafe_allow_html=True)
    c1, c2 = st.columns([1, 2.5])
    with c1:
        if item.get("foto") and (ROOT / item["foto"]).exists():
            st.image(str(ROOT / item["foto"]), use_container_width=True)
        else:
            st.markdown('<div class="car-box">BRICS<br><span>Auto</span></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="card-title">' + str(title) + '</div>', unsafe_allow_html=True)
        st.markdown('<div class="card-meta">' + str(item.get("marca","")) + " " + str(item.get("modelo","")) + " · " + str(item.get("ano","")) + " · " + str(item.get("cidade","")) + '</div>', unsafe_allow_html=True)
        st.markdown('<div class="card-price">Gs. ' + str(item.get("preco","Consultar")) + '</div>', unsafe_allow_html=True)
        st.write(desc)
        st.markdown('<span class="badge green">' + str(item.get("status","pendente")) + '</span> <span class="badge dark">IA assistida</span> <span class="badge yellow">Revisão humana</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.set_page_config(page_title="BRICS Paraguay Autos", layout="wide")

st.markdown('''
<style>
[data-testid="stSidebar"] { background: #0f2f1f; }
[data-testid="stSidebar"] * { color: white !important; }
.main .block-container { padding-top: 2rem; max-width: 1180px; }
.hero {
    background: linear-gradient(135deg, #0f3d2e 0%, #176b43 60%, #f6c343 100%);
    color: white;
    padding: 36px;
    border-radius: 30px;
    box-shadow: 0 18px 45px rgba(15,61,46,.25);
    margin-bottom: 24px;
}
.hero h1 { font-size: 48px; margin-bottom: 8px; }
.hero p { font-size: 19px; opacity: .95; max-width: 800px; }
.hero-badges span {
    display: inline-block;
    background: rgba(255,255,255,.18);
    padding: 8px 13px;
    border-radius: 999px;
    margin-right: 8px;
    margin-top: 12px;
    font-weight: 800;
}
.search-panel {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 22px;
    padding: 18px;
    box-shadow: 0 10px 32px rgba(0,0,0,.06);
    margin-bottom: 22px;
}
.vehicle-card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 24px;
    padding: 18px;
    box-shadow: 0 12px 30px rgba(0,0,0,.06);
    margin-bottom: 16px;
}
.car-box {
    height: 170px;
    border-radius: 18px;
    background: linear-gradient(135deg, #111827, #176b43 70%, #f6c343);
    color: white;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    font-size: 31px;
    font-weight: 900;
    letter-spacing: 2px;
}
.car-box span { font-size: 13px; letter-spacing: 0; }
.card-title { font-size: 24px; font-weight: 900; color: #10251b; }
.card-meta { color: #6b7280; margin: 5px 0 8px 0; }
.card-price { font-size: 30px; font-weight: 900; color: #176b43; margin: 7px 0; }
.badge {
    display: inline-block;
    color: white;
    padding: 6px 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 800;
    margin-right: 6px;
}
.green { background: #16a34a; }
.dark { background: #111827; }
.yellow { background: #f6c343; color: #10251b; }
</style>
''', unsafe_allow_html=True)

lang = st.sidebar.radio("Idioma", ["pt", "es"], horizontal=True)
t = TEXT[lang]
items = load()
s = stats(items)

hero_html = '<div class="hero"><h1>BRICS Paraguay Autos</h1><p>' + t["hero"] + '</p><p>' + t["sub"] + '</p><div class="hero-badges"><span>IA assistida</span><span>Revisão humana</span><span>Marketplace local</span></div></div>'
st.markdown(hero_html, unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Total", s["total"])
m2.metric("Pendentes", s["pendentes"])
m3.metric("Aprovados", s["aprovados"])
m4.metric("IA não revisada", s["ia_nao_revisada"])

st.markdown('<div class="search-panel">', unsafe_allow_html=True)
f1, f2, f3, f4 = st.columns([2, 1, 1, 1])
query = f1.text_input("Buscar veículo", placeholder="Toyota Hilux, Honda Civic...")
city = f2.text_input("Cidade", placeholder="Asuncion")
brand = f3.text_input("Marca", placeholder="Toyota")
max_price = f4.text_input("Preço máximo", placeholder="185000000")
st.markdown('</div>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([t["ads"], t["new"], t["review"], t["dash"]])

filtered = items[:]
if query.strip():
    q = query.lower()
    filtered = [x for x in filtered if q in json.dumps(x, ensure_ascii=False).lower()]
if city.strip():
    filtered = [x for x in filtered if city.lower() in str(x.get("cidade","")).lower()]
if brand.strip():
    filtered = [x for x in filtered if brand.lower() in str(x.get("marca","")).lower()]
if max_price.strip():
    limit = num(max_price)
    if limit > 0:
        filtered = [x for x in filtered if num(x.get("preco")) <= limit]

with tab1:
    st.subheader("Vitrine BRICS")
    for item in filtered:
        card(item, lang)

with tab2:
    st.subheader("Anunciar com câmera")
    modo = st.radio("Foto", ["upload", "camera"], horizontal=True)
    foto = st.camera_input("Camera") if modo == "camera" else st.file_uploader("Upload", type=["jpg", "jpeg", "png", "webp"])
    cor_hint = st.text_input("Cor aparente")
    ai = ai_mock(getattr(foto, "name", ""), cor_hint)

    st.markdown("### IA assistida")
    st.json(ai)

    with st.form("form_auto"):
        titulo_pt = st.text_input("Título PT", value=ai["titulo_pt"])
        titulo_es = st.text_input("Título ES", value=ai["titulo_es"])
        marca = st.text_input("Marca", value=ai["marca"])
        modelo = st.text_input("Modelo", value=ai["modelo"])
        ano = st.text_input("Ano")
        preco = st.text_input("Preço em guaranis")
        cidade_form = st.text_input("Cidade")
        telefone = st.text_input("Telefone")
        desc_pt = st.text_area("Descrição PT", value=ai["descricao_pt"])
        desc_es = st.text_area("Descripción ES", value=ai["descricao_es"])
        revisado = st.checkbox("Confirmo que revisei as sugestões da IA")
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
            "cidade": cidade_form,
            "telefone": telefone,
            "descricao_pt": desc_pt,
            "descricao_es": desc_es,
            "foto": save_photo(foto),
            "ai_reviewed": bool(revisado),
            "status": "pendente"
        })
        save(items)
        st.success("Anúncio salvo para revisão.")

with tab3:
    st.subheader(t["review"])
    pending = [x for x in items if x.get("status") == "pendente"]
    if not pending:
        st.info("Sem anúncios pendentes.")
    for item in pending:
        card(item, lang)
        if st.button(t["approve"], key="approve_" + item["id"]):
            item["status"] = "aprovado"
            item["ai_reviewed"] = True
            save(items)
            st.success("Aprovado. Recarregue a página.")

with tab4:
    st.subheader(t["dash"])
    st.json(s)
    st.dataframe(items, width="stretch")
