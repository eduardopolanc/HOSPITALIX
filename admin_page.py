import streamlit as st
import os
import pandas as pd

def admin_page():
    # Mostrar solicitudes pendientes directamente
    st.subheader("Demandes d'inscription en attente")

    request_file = "demandes_en_attente.xlsx"
    if os.path.exists(request_file):
        requests = pd.read_excel(request_file)

        if requests.empty:
            st.info("Aucune demande en attente.")
        else:
            for index, row in requests.iterrows():
                with st.expander(f"{row['First Name']} {row['Last Name']} - {row['Email']}"):
                    st.write(f"**Nom :** {row['Last Name']}")
                    st.write(f"**Prénom :** {row['First Name']}")
                    st.write(f"**Téléphone :** {row['Phone']}")
                    st.write(f"**Rôle :** {row['Role']}")
                    st.write(f"**Entreprise :** {row['Company']}")
                    st.write(f"**Email :** {row['Email']}")
    else:
        st.info("Fichier de demandes non trouvé.")
    
    request_file = "demandes_en_attente.xlsx"
    pending_count = 0
    if os.path.exists(request_file):
        try:
            requests = pd.read_excel(request_file)
            pending_count = len(requests)
        except:
            pass
    
    col1, col2 = st.columns([6, 1])
    with col2:
        if pending_count > 0:
            if st.button(f"🔔 {pending_count}"):
                st.session_state.page = "request"
                st.rerun()

    button_user = st.button("user page")
    button_pdf = st.button("pdf page")
    button_out = st.button("log out")
    

    if button_user:
        st.session_state.page = "user"
        st.rerun()

    if button_pdf:
        st.session_state.page = "viewer"
        st.rerun()

    if button_out:
        st.session_state.page = "login"
        st.rerun()

    button_re = st.button("user's request")
    
    if button_re:
            st.session_state.page = "request"
            st.rerun()
    