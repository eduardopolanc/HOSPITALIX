import streamlit as st
import os
import pandas as pd

def admin_page():
    st.set_page_config(layout="wide")

    # Encabezado con botón de logout alineado
    col_title, col_logout = st.columns([6, 1])
    with col_title:
        st.markdown("<h1 style='text-align: center; margin-top: -30px;'>Admin Page</h1>", unsafe_allow_html=True)
    with col_logout:
        st.markdown("<div style='text-align: right; margin-top: -10px;'>", unsafe_allow_html=True)
        if st.button("log out"):
            st.session_state.page = "login"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # Leer solicitudes pendientes
    request_file = "demandes_en_attente.xlsx"
    requests = pd.DataFrame()
    if os.path.exists(request_file):
        try:
            requests = pd.read_excel(request_file)
        except:
            st.error("Erreur lors du chargement du fichier de demandes.")

    # Panel lateral para las solicitudes
    col_left, _ = st.columns([3, 9])
    with col_left:
        st.markdown("""
            <div style="background-color: #2e2e2e; padding: 20px; border-radius: 10px;">
                <h4 style="color: white;">Demandes d'inscription</h4>
        """, unsafe_allow_html=True)

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

        st.markdown("</div>", unsafe_allow_html=True)

    # Navegación en la parte inferior
    st.markdown("<h3 style='text-align: center;'>Navigation</h3>", unsafe_allow_html=True)
    col4, col5, col6, col7 = st.columns([2, 2, 2, 2])

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