from pathlib import Path

path = Path("k_atlas/social/ui/social_cockpit_view.py")
text = path.read_text(encoding="utf-8")

if "render_social_command_center" not in text:
    marker = '    st.subheader("K-Social Intelligence System")\n'

    insert = '''    try:
        from k_atlas.social.ui.social_command_center_view import render_social_command_center

        render_social_command_center()
        st.divider()
    except Exception as command_center_error:
        st.warning("K-Social Command Center ainda nao foi carregado.")
        st.caption(str(command_center_error))

'''

    if marker not in text:
        raise RuntimeError("Ponto de insercao nao encontrado em social_cockpit_view.py")

    text = text.replace(marker, marker + insert, 1)
    path.write_text(text, encoding="utf-8")

print("social_cockpit_view.py atualizado com Command Center.")
