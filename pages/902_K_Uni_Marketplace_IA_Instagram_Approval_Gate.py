from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
POSTS_PATH = PROJECT_ROOT / "content_packs" / "marketplace_ia" / "instagram_posts_v2.json"
APPROVAL_PATH = PROJECT_ROOT / "live" / "marketplace_ia" / "instagram_approval_decision.json"

st.set_page_config(page_title="Marketplace IA Approval Gate", layout="wide")

st.title("Marketplace IA - Instagram Approval Gate")
st.caption("Revisao humana antes de qualquer publicacao externa.")

if not POSTS_PATH.exists():
    st.error("Arquivo de campanha nao encontrado.")
    st.stop()

posts = json.loads(POSTS_PATH.read_text(encoding="utf-8-sig"))

st.warning("Publicacao real esta bloqueada. Este gate apenas registra aprovacao ou reprova localmente.")

approved_items = []

for index, post in enumerate(posts, start=1):
    with st.expander(f"{index}. {post['title']}", expanded=True):
        st.write(post["caption"])
        st.code("\n".join(post["hashtags"]), language="text")
        approved = st.checkbox(f"Aprovar post {index}", key=f"approve_{index}")
        approved_items.append(approved)

notes = st.text_area("Observacoes do operador")

col1, col2 = st.columns(2)

with col1:
    if st.button("Aprovar campanha localmente", type="primary"):
        APPROVAL_PATH.parent.mkdir(parents=True, exist_ok=True)

        decision = {
            "ok": True,
            "decision": "approved_local_only",
            "approved_at": datetime.now(timezone.utc).isoformat(),
            "approved_posts": sum(1 for item in approved_items if item),
            "total_posts": len(posts),
            "notes": notes,
            "external_publish_enabled": False,
            "human_approval_recorded": True,
        }

        APPROVAL_PATH.write_text(json.dumps(decision, ensure_ascii=False, indent=2), encoding="utf-8")
        st.success("Aprovacao local registrada. Nenhuma publicacao externa foi feita.")
        st.json(decision)

with col2:
    if st.button("Reprovar campanha"):
        APPROVAL_PATH.parent.mkdir(parents=True, exist_ok=True)

        decision = {
            "ok": True,
            "decision": "rejected",
            "rejected_at": datetime.now(timezone.utc).isoformat(),
            "notes": notes,
            "external_publish_enabled": False,
            "human_approval_recorded": True,
        }

        APPROVAL_PATH.write_text(json.dumps(decision, ensure_ascii=False, indent=2), encoding="utf-8")
        st.error("Reprovacao registrada.")
        st.json(decision)

if APPROVAL_PATH.exists():
    st.divider()
    st.subheader("Ultima decisao")
    st.json(json.loads(APPROVAL_PATH.read_text(encoding="utf-8-sig")))
