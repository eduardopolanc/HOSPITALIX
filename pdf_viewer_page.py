import streamlit as st
import os
import base64

def pdf_viewer_page():
    st.set_page_config(layout="centered")
    st.markdown("<h3 style='text-align: center;'>Visualiseur de PDF</h3>", unsafe_allow_html=True)

    # Bouton "Retour à la page précédente" sans flèche
    if st.button("Retour à la page précédente"):
        st.session_state.page = "user"
        st.rerun()

    filename = st.session_state.get("pdf_to_view", None)

    if not filename:
        st.warning("Aucun PDF sélectionné.")
        return

    file_path = os.path.join("static", "pdf_reports", filename)

    if not os.path.exists(file_path):
        st.error("Le fichier PDF sélectionné n'existe pas.")
        return

    # Affichage du PDF
    st.markdown(f"""
        <iframe src="/static/pdf_reports/{filename}" width="100%" height="700px"
                style="border: none;"></iframe>
    """, unsafe_allow_html=True)

    # Boutons en bas
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Retour Admin"):
            st.session_state.page = "admin"
            st.rerun()
    with col2:
        if st.button("Accueil Utilisateur"):
            st.session_state.page = "user"
            st.rerun()
