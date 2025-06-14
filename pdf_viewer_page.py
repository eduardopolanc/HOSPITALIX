import streamlit as st
import os

def pdf_viewer_page():
    st.set_page_config(layout="centered")
    st.markdown("<h3 style='text-align: center;'>Visualiseur de PDF</h3>", unsafe_allow_html=True)

    # Get the name of the PDF to display from session state
    filename = st.session_state.get("pdf_to_view", None)

    if not filename:
        st.warning("Aucun PDF sélectionné.")
        return

    file_path = os.path.join("static", filename)

    if not os.path.exists(file_path):
        st.error("Le fichier PDF sélectionné n'existe pas.")
        return

    # Embed the PDF in an iframe
    st.markdown(f"""
        <iframe src="static/{filename}" width="100%" height="700px"
                style="border: none;"></iframe>
    """, unsafe_allow_html=True)

    # Navigation buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Retour Admin"):
            st.session_state.page = "admin"
            st.rerun()
    with col2:
        if st.button("Accueil Utilisateur"):
            st.session_state.page = "user"
            st.rerun()
