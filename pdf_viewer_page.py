import streamlit as st
import os
import base64

def pdf_viewer_page():
    st.set_page_config(layout="centered")
    st.markdown("<h3 style='text-align: center;'>Visualiseur de PDF</h3>", unsafe_allow_html=True)

    # Recupera el nombre del PDF desde la URL
    filename = st.session_state.get("pdf_to_view", None)

    if not filename:
        st.warning("Aucun PDF sélectionné.")
        return

    file_path = os.path.join("pdf_reports", filename)

    if not os.path.exists(file_path):
        st.error("Le fichier PDF sélectionné n'existe pas.")
        return

    # Leer el contenido y convertir a base64
    st.markdown(f"""
        <p>Cliquez ci-dessous pour ouvrir le PDF dans un nouvel onglet :</p>
        <a href="./pdf_reports/{filename}" target="_blank" style="font-size: 18px;">📄 {filename}</a>
    """, unsafe_allow_html=True)

    # Botones de navegación
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Retour Admin"):
            st.session_state.page = "admin"
            st.rerun()
    with col2:
        if st.button("🏠 Accueil Utilisateur"):
            st.session_state.page = "user"
            st.rerun()
