import streamlit as st
import os
import pandas as pd

def admin_page():
    st.set_page_config(layout="wide")  # Opcional: hace que la columna izquierda tenga más espacio útil
    st.title("Admin Page")

    # Leer solicitudes pendientes
    request_file = "demandes_en_attente.xlsx"
    requests = pd.DataFrame()
    if os.path.exists(request_file):
        try:
            requests = pd.read_excel(request_file)
        except:
            st.error("Erreur lors du chargement du fichier de demandes.")

    # Crear columnas: izquierda = navegación + solicitudes, derecha vacía
    col1, col2 = st.columns([2, 6])

    with col1:
        st.subheader("Navigation")

        if st.button("user page"):
            st.session_state.page = "user"
            st.rerun()
        if st.button("pdf page"):
            st.session_state.page = "viewer"
            st.rerun()
        if st.button("log out"):
            st.session_state.page = "login"
            st.rerun()
        if st.button("user's request"):
            st.session_state.page = "request"
            st.rerun()

        st.markdown("---")
        st.subheader("Demandes d'inscription")

        if not requests.empty:
            for index, row in requests.iterrows():
                with st.expander(f"{row['First Name']} {row['Last Name']} - {row['Email']}"):
                    st.write(f"**Nom :** {row['Last Name']}")
                    st.write(f"**Prénom :** {row['First Name']}")
                    st.write(f"**Téléphone :** {row['Phone']}")
                    st.write(f"**Rôle :** {row['Role']}")
                    st.write(f"**Entreprise :** {row['Company']}")
                    st.write(f"**Email :** {row['Email']}")
        else:
            st.info("Aucune demande en attente.")
    