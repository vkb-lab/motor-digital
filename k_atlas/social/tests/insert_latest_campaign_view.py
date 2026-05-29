from pathlib import Path

path = Path("k_atlas/social/ui/social_cockpit_view.py")
text = path.read_text(encoding="utf-8")

if "render_latest_manual_approved_campaign" not in text:
    marker = '    st.subheader("K-Social Intelligence System")\n'

    insert = '''    try:
        from k_atlas.social.ui.social_latest_campaign_view import render_latest_manual_approved_campaign

        render_latest_manual_approved_campaign()
        st.divider()
    except Exception as latest_campaign_error:
        st.warning("Campanha principal aprovada ainda nao foi carregada.")
        st.caption(str(latest_campaign_error))

'''

    if marker not in text:
        raise RuntimeError("Ponto de insercao nao encontrado em social_cockpit_view.py")

    text = text.replace(marker, marker + insert, 1)
    path.write_text(text, encoding="utf-8")

print("social_cockpit_view.py atualizado com campanha principal aprovada.")
