import streamlit as st
import os
import base64

def pdf_viewer_page():
    # Vérifie les paramètres de la requête pour récupérer le nom du fichier PDF
    query_params = st.query_params
    if query_params.get("pdf_to_view", None):
        filename = query_params["pdf_to_view"]
        pdf_folder = "pdf_reports"  # Le dossier où sont stockés les PDF
        file_path = os.path.join(pdf_folder, filename)

        # Si le fichier existe
        if os.path.exists(file_path):
            # Lire le contenu du fichier PDF et l'encoder en base64
            with open(file_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()

            # Afficher le PDF dans un iframe
            st.markdown(f'<iframe src="data:application/pdf;base64,{b64}" width="700" height="600"></iframe>', unsafe_allow_html=True)
        else:
            st.error("Le fichier PDF n'existe pas.")
    else:
        st.error("Aucun fichier PDF spécifié.")

    # Ajouter des boutons pour naviguer entre les pages
    button_user = st.button("Retour à l'utilisateur")
    button_admin = st.button("Retour à l'admin")

    # Navigation vers la page utilisateur
    if button_user:
        st.session_state.page = "user"
        st.rerun()

    # Navigation vers la page admin
    if button_admin:
        st.session_state.page = "admin"
        st.rerun()
