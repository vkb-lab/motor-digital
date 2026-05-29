from pathlib import Path

path = Path("k_atlas/social/ui/social_cockpit_view.py")
text = path.read_text(encoding="utf-8")

if "render_social_content_refinement_queue" not in text:
    needle = "    report = load_social_report()\n"

    insert = '''    try:
        from k_atlas.social.ui.social_content_refinement_view import render_social_content_refinement_queue

        st.divider()
        render_social_content_refinement_queue()
    except Exception as refinement_error:
        st.warning("Fila de refinamento criativo ainda nao foi carregada.")
        st.caption(str(refinement_error))

'''

    if needle not in text:
        raise RuntimeError("Ponto de insercao nao encontrado em social_cockpit_view.py")

    text = text.replace(needle, insert + needle, 1)
    path.write_text(text, encoding="utf-8")

print("social_cockpit_view.py atualizado com fila de refinamento criativo.")
