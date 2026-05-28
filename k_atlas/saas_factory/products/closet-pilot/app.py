
from pathlib import Path
import json
import uuid
import streamlit as st

ROOT = Path(__file__).resolve().parent
DATA_FILE = ROOT / "data" / "wardrobe_items.json"
PHOTOS_DIR = ROOT / "data" / "photos"

def load_items():
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    PHOTOS_DIR.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        DATA_FILE.write_text("[]", encoding="utf-8")
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))

def save_items(items):
    DATA_FILE.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")

def save_photo(upload):
    if upload is None:
        return ""
    suffix = Path(upload.name).suffix.lower()
    if suffix not in [".jpg", ".jpeg", ".png", ".webp"]:
        suffix = ".jpg"
    name = "peca-" + str(uuid.uuid4())[:8] + suffix
    path = PHOTOS_DIR / name
    path.write_bytes(upload.getvalue())
    return "data/photos/" + name

def local_label(item):
    parts = [item.get("local_tipo",""), item.get("local_nome",""), item.get("local_detalhe",""), item.get("caixa","")]
    clean = [str(x).strip() for x in parts if str(x).strip()]
    return " / ".join(clean) if clean else "sem local"

def stats(items):
    locais = {}
    fotos = 0
    favoritas = 0
    for item in items:
        locais[local_label(item)] = locais.get(local_label(item), 0) + 1
        if item.get("foto"):
            fotos += 1
        if item.get("favorita"):
            favoritas += 1
    return {"total": len(items), "favoritas": favoritas, "fotos": fotos, "locais": locais}

def suggest_looks(items, ocasiao):
    pool = [i for i in items if i.get("ocasiao") in [ocasiao, "casual", "trabalho", "todas"]]
    tops = [i for i in pool if i.get("categoria") in ["blusa", "camisa", "top"]]
    bottoms = [i for i in pool if i.get("categoria") in ["calca", "saia", "short"]]
    dresses = [i for i in pool if i.get("categoria") == "vestido"]
    layers = [i for i in pool if i.get("categoria") in ["casaco", "blazer"]]
    looks = []
    for dress in dresses:
        selected = [dress] + layers[:1]
        looks.append({"nome": "Look com " + dress.get("nome","vestido"), "pecas": selected})
    for top in tops:
        for bottom in bottoms:
            selected = [top, bottom] + layers[:1]
            looks.append({"nome": top.get("nome","top") + " + " + bottom.get("nome","baixo"), "pecas": selected})
    return looks[:8]

st.set_page_config(page_title="Closet Pilot", layout="wide")

st.title("Closet Pilot v0.2")
st.caption("Guarda-roupa inteligente local: foto, localizacao, caixas e combinacao de looks.")

items = load_items()
s = stats(items)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Pecas", s["total"])
c2.metric("Favoritas", s["favoritas"])
c3.metric("Com foto", s["fotos"])
c4.metric("Locais", len(s["locais"]))

tabs = st.tabs(["Cadastrar com foto", "Guarda-roupa visual", "Mapa do closet", "Combinar looks", "Planejar evento"])

with tabs[0]:
    st.subheader("Cadastrar peca")
    with st.form("cadastro"):
        nome = st.text_input("Nome da peca")
        categoria = st.selectbox("Categoria", ["blusa","camisa","top","calca","saia","short","vestido","casaco","blazer","sapato","acessorio"])
        cor = st.text_input("Cor")
        ocasiao = st.selectbox("Ocasiao", ["trabalho","casual","evento","viagem","rotina","todas"])
        favorita = st.checkbox("Favorita")
        st.markdown("#### Onde esta guardada")
        local_tipo = st.selectbox("Tipo", ["closet","gaveta","caixa","mala","sapateira","outro"])
        local_nome = st.text_input("Nome do local", placeholder="Closet principal")
        local_detalhe = st.text_input("Detalhe", placeholder="Prateleira 2, cabideiro lateral")
        caixa = st.text_input("Codigo da caixa", placeholder="CX-INVERNO-01")
        notas = st.text_area("Notas")
        foto = st.file_uploader("Foto da peca", type=["jpg","jpeg","png","webp"])
        salvar = st.form_submit_button("Salvar")

    if salvar:
        if not nome.strip():
            st.error("Nome obrigatorio.")
        else:
            items.append({
                "id": str(uuid.uuid4()),
                "nome": nome.strip(),
                "categoria": categoria,
                "cor": cor.strip().lower(),
                "ocasiao": ocasiao,
                "favorita": favorita,
                "local_tipo": local_tipo,
                "local_nome": local_nome.strip(),
                "local_detalhe": local_detalhe.strip(),
                "caixa": caixa.strip(),
                "foto": save_photo(foto),
                "notas": notas.strip()
            })
            save_items(items)
            st.success("Peca salva. Atualize a pagina para ver nas metricas.")

with tabs[1]:
    st.subheader("Guarda-roupa visual")
    for item in items:
        with st.container(border=True):
            col_img, col_info = st.columns([1,3])
            photo = item.get("foto","")
            if photo and (ROOT / photo).exists():
                col_img.image(str(ROOT / photo), width=160)
            else:
                col_img.write("Sem foto")
            col_info.markdown("### " + item.get("nome","Peca"))
            col_info.write("Categoria:", item.get("categoria"))
            col_info.write("Cor:", item.get("cor"))
            col_info.write("Ocasiao:", item.get("ocasiao"))
            col_info.write("Local:", local_label(item))
            col_info.write("Notas:", item.get("notas",""))

with tabs[2]:
    st.subheader("Mapa do closet")
    rows = [{"peca":i.get("nome"),"categoria":i.get("categoria"),"cor":i.get("cor"),"local":local_label(i),"foto":"sim" if i.get("foto") else "nao"} for i in items]
    st.dataframe(rows, width="stretch")
    st.json(s["locais"])

with tabs[3]:
    st.subheader("Combinar looks")
    ocasiao = st.selectbox("Ocasiao para combinar", ["trabalho","casual","evento","viagem","rotina"])
    looks = suggest_looks(items, ocasiao)
    if not looks:
        st.warning("Sem pecas suficientes para combinar.")
    for idx, look in enumerate(looks, start=1):
        with st.expander("Look " + str(idx) + ": " + look["nome"]):
            for peca in look["pecas"]:
                st.write("- " + peca.get("nome","") + " | " + local_label(peca))

with tabs[4]:
    st.subheader("Planejar evento ou viagem")
    ocasiao_evento = st.selectbox("Ocasiao", ["trabalho","casual","evento","viagem","rotina"], key="evento")
    dias = st.number_input("Dias", min_value=1, max_value=14, value=3)
    looks_evento = suggest_looks(items, ocasiao_evento)
    for dia in range(1, int(dias) + 1):
        st.markdown("#### Dia " + str(dia))
        if looks_evento:
            look = looks_evento[(dia - 1) % len(looks_evento)]
            st.write(look["nome"])
            for peca in look["pecas"]:
                st.write("- " + peca.get("nome","") + " | " + local_label(peca))
        else:
            st.warning("Sem look disponivel.")
