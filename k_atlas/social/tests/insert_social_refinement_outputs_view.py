from pathlib import Path

path = Path("k_atlas/social/ui/social_cockpit_view.py")
text = path.read_text(encoding="utf-8")

if "render_social_refinement_outputs" not in text:
    needle = "    report = load_social_report()\n"

    insert = '''    try:
        from k_atlas.social.ui.social_refinement_outputs_view import render_social_refinement_outputs

        st.divider()
        render_social_refinement_outputs()
    except Exception as outputs_error:
        st.warning("Refinamentos criativos ainda nao foram carregados.")
        st.caption(str(outputs_error))

'''

    if needle not in text:
        raise RuntimeError("Ponto de insercao nao encontrado em social_cockpit_view.py")

    text = text.replace(needle, insert + needle, 1)
    path.write_text(text, encoding="utf-8")

print("social_cockpit_view.py atualizado com viewer de refinamentos.")
