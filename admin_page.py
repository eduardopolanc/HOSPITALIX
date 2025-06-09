import streamlit as st
import os
import pandas as pd
import base64
import secrets
import string

def generate_password(length=10):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def admin_page():
    st.set_page_config(layout="wide")
    cola, cols, cold = st.columns([2,2,2])
    with cols:
        st.markdown("<h1 style='text-align: center;'>Admin Page</h1>", unsafe_allow_html=True)
    with cold:
        colq, colw = st.columns([2,2])
        with colw:
            if st.button("log out"):
                st.session_state.page = "login"
                st.rerun()

    # Leer solicitudes pendientes
    request_file = "demandes_en_attente.xlsx"
    account_file = "accepted_user_information.xlsm"
    requests = pd.DataFrame()
    if os.path.exists(request_file):
        try:
            requests = pd.read_excel(request_file)
        except:
            st.error("Erreur lors du chargement du fichier de demandes.")

    col1, col2  = st.columns([3, 5])

    # Solicitudes
    with col1:
        st.markdown("#### <small>Demandes d'inscription</small>", unsafe_allow_html=True)
        st.markdown("---")
        if not requests.empty:
            for index, row in requests.iterrows():
                with st.expander(f"{row['Nom']} {row['Prenom']} - {row['Email']}"):
                    st.write(f"**Nom :** {row['Nom']}")
                    st.write(f"**Prénom :** {row['Prenom']}")
                    st.write(f"**Téléphone :** {row['Téléphone']}")
                    st.write(f"**Rôle :** {row['Rôle']}")
                    st.write(f"**Entreprise :** {row['Entreprise']}")
                    st.write(f"**Email :** {row['Email']}")
                    
                    cola, colr = st.columns(2)

                    if cola.button("✅ Accepter", key=f"accept_{index}"):
                        password = generate_password()

                        new_account = pd.DataFrame([{
                            "Email (username)": row['Email'],
                            "Password": password
                        }])

                        if os.path.exists(account_file):
                            existing = pd.read_excel(account_file)
                            all_accounts = pd.concat([existing, new_account], ignore_index=True)
                        else:
                            all_accounts = new_account

                        all_accounts.to_excel(account_file, index=False)
                        requests.drop(index, inplace=True)
                        requests.to_excel(request_file, index=False)

                        st.success(f"Compte créé pour {row['Email']} avec mot de passe : {password}")
                        st.rerun()

                    if colr.button("❌ Rejeter", key=f"reject_{index}"):
                        requests.drop(index, inplace=True)
                        requests.to_excel(request_file, index=False)
                        st.warning(f"Demande rejetée pour : {row['Email']}")
                        st.rerun()
        else:
            st.info("Aucune demande en attente.")

    # PDFs
    with col2:
        pdf_folder = "pdf_reports"
        st.subheader("📄 PDF générés")

        if os.path.exists(pdf_folder):
            pdf_files = sorted(
                [f for f in os.listdir(pdf_folder) if f.endswith(".pdf")],
                reverse=True
            )

            if not pdf_files:
                st.info("Aucun PDF trouvé.")
            else:
                for filename in pdf_files[:5]:
                    file_path = os.path.join(pdf_folder, filename)
                    with open(file_path, "rb") as f:
                        b64 = base64.b64encode(f.read()).decode()

                    # Tarjeta PDF
                    st.markdown(f"""
                        <div style="display: flex; align-items: center; justify-content: space-between; 
                                    background-color: #ffffff; border: 1px solid #ccc; 
                                    padding: 6px 12px; border-radius: 6px; margin-bottom: 8px;
                                    box-shadow: 0 1px 3px rgba(0,0,0,0.05); font-size: 14px; color: black;">
                            <div style="flex-grow: 1; display: flex; align-items: center;">
                                <span style="font-size: 16px; margin-right: 8px;">📄</span>
                                <span style="font-weight: 500; color: black;">{filename}</span>
                            </div>
                            <div style="display: flex; gap: 6px;">
                                <a href="data:application/pdf;base64,{b64}" download="{filename}" target="_blank">
                                    <button style="font-size: 12px; padding: 4px 8px; background-color: #e0e0e0; color: black; border: none; border-radius: 4px;">
                                        ⬇️ Télécharger
                                    </button>
                                </a>
                                <button onclick="window.location.href='/?pdf_to_view={filename}'"
                                    style="font-size: 12px; padding: 4px 8px; background-color: #d0e7ff; color: black; border: none; border-radius: 4px;">
                                    👁️ Voir
                                </button>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                    # Capturar redirección
                    query_params = st.experimental_get_query_params()
                    if query_params.get("pdf_to_view", [None])[0] == filename:
                        st.session_state.pdf_to_view = filename
                        st.session_state.page = "viewer"
                        st.experimental_set_query_params()  # limpia URL
                        st.rerun()
        else:
            st.warning("Le dossier des PDF n'existe pas.")

        if st.button("Generar un PDF"):
            st.session_state.page = "user"
            st.rerun()

    # Usuarios
    st.markdown("---")
    st.subheader("👤 Gestion des utilisateurs")

    user_file = "accepted_user_information.xlsm"

    if os.path.exists(user_file):
        users_df = pd.read_excel(user_file)

        if users_df.empty:
            st.info("Aucun utilisateur enregistré.")
        else:
            for index, row in users_df.iterrows():
                with st.expander(f"{row['Email (username)']}"):
                    st.write(f"**Mot de passe actuel :** {row['Password']}")

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        new_password = st.text_input(f"Nouveau mot de passe pour {row['Email (username)']}", "", key=f"newpwd_{index}")
                        if st.button("🔑 Changer mot de passe", key=f"update_{index}"):
                            users_df.at[index, "Password"] = new_password
                            users_df.to_excel(user_file, index=False)
                            st.success(f"Mot de passe mis à jour pour {row['Email (username)']}")
                            st.rerun()

                    with col3:
                        if st.button("🗑️ Supprimer utilisateur", key=f"delete_{index}"):
                            users_df.drop(index, inplace=True)
                            users_df.to_excel(user_file, index=False)
                            st.warning(f"Utilisateur supprimé : {row['Email (username)']}")
                            st.rerun()
    else:
        st.warning("Fichier d'utilisateurs non trouvé.")

    col4, col5, col6, col7 = st.columns([2,2,2,2])
    with col5:
        if st.button("pdf page"):
            st.session_state.page = "viewer"
            st.rerun()
