import streamlit as st
import os
import pandas as pd

def admin_page():
    st.markdown("<style>div.block-container{padding-top: 1rem;}</style>", unsafe_allow_html=True)
    st.set_page_config(layout="wide")  # Opcional: hace que la columna izquierda tenga más espacio útil
    st.markdown("<h1 style='text-align: center;'>Admin Page</h1>", unsafe_allow_html=True)

    # Leer solicitudes pendientes
    request_file = "demandes_en_attente.xlsx"
    requests = pd.DataFrame()
    if os.path.exists(request_file):
        try:
            requests = pd.read_excel(request_file)
        except:
            st.error("Erreur lors du chargement du fichier de demandes.")

    # Crear columnas: izquierda = navegación + solicitudes, derecha vacía
    col1, col2, col3 = st.columns([2, 6, 2])

    with col1:
        st.markdown("#### <small>Demandes d'inscription</small>", unsafe_allow_html=True)
        st.markdown("---")
        if not requests.empty:
            for index, row in requests.iterrows():
                with st.expander(f"{row['First Name']} {row['Last Name']} - {row['Email']}"):
                    st.write(f"**Last Name:** {row['Last Name']}")
                    st.write(f"**First Name:** {row['First Name']}")
                    st.write(f"**Phone:** {row['Phone']}")
                    st.write(f"**Role:** {row['Role']}")
                    st.write(f"**Company:** {row['Company']}")
                    st.write(f"**Email:** {row['Email']}")
        else:
            st.info("Aucune demande en attente.")
    
    st.markdown("<h3 style='text-align: center;'>Navigation</h3>", unsafe_allow_html=True)

    col4, col5, col6, col7 = st.columns([2,2,2,2])

    with col4:
        if st.button("user page"):
            st.session_state.page = "user"
            st.rerun()
    with col5:
        if st.button("pdf page"):
            st.session_state.page = "viewer"
            st.rerun()
    with col6:
        if st.button("log out"):
            st.session_state.page = "login"
            st.rerun()
    with col7:
        if st.button("user's request"):
            st.session_state.page = "request"
            st.rerun()