import streamlit as st
import os
import base64

def pdf_viewer_page():
    st.set_page_config(layout="centered")
    st.markdown("<h3 style='text-align: center;'>Visualiseur de PDF</h3>", unsafe_allow_html=True)

    # Recupera el nombre del PDF desde la URL
    params = st.query_params
    filename = params.get("pdf_to_view", None)

    if not filename:
        st.warning("Aucun PDF sélectionné.")
        return

    file_path = os.path.join("pdf_reports", filename)

    if not os.path.exists(file_path):
        st.error("Le fichier PDF sélectionné n'existe pas.")
        return

    # Leer el contenido y convertir a base64
    with open(file_path, "rb") as f:
        b64_pdf = base64.b64encode(f.read()).decode()

    # Mostrar el PDF embebido
    pdf_display = f"""
        <iframe src="data:application/pdf;base64,{b64_pdf}" width="100%" height="700px"
                style="border: none;"></iframe>
    """
    st.components.v1.html(pdf_display, height=720, scrolling=False)

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
