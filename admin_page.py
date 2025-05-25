import streamlit as st
import os
import pandas as pd
import base64
import secrets
import string

st.set_page_config(layout="wide") #manage wideness of page

def generate_password(length=10):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def admin_page():
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

    # Users acceptance
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
                    
                    cola, colr = st.columns(2)

                    # Accept button logic
                    if cola.button("✅ Accepter"):
                        password = generate_password()

                        new_account = pd.DataFrame([{
                            "Email (username)": row['Email'],
                            "Password": password
                        }])

                        # Save accepted account to main file
                        if os.path.exists(account_file):
                            existing = pd.read_excel(account_file)
                            all_accounts = pd.concat([existing, new_account], ignore_index=True)
                        else:
                            all_accounts = new_account

                        all_accounts.to_excel(account_file, index=False)

                        # Remove request from pending list
                        requests.drop(index, inplace=True)
                        requests.to_excel(request_file, index=False)

                        st.success(f"Account created for {row['Email']} with password: {password}")
                        st.rerun()

                    # Reject button logic
                    if colr.button("❌ Rejeter"):
                        requests.drop(index, inplace=True)
                        requests.to_excel(request_file, index=False)
                        st.warning(f"Request for {row['Email']} has been rejected.")
                        st.rerun()
        
        
        else:
            st.info("Aucune demande en attente.")
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
                links_html = ""
                for filename in pdf_files:
                    file_path = os.path.join(pdf_folder, filename)
                    with open(file_path, "rb") as f:
                        b64 = base64.b64encode(f.read()).decode()
                        link = f'<a href="data:application/pdf;base64,{b64}" download="{filename}" target="_blank" style="color: #00CFFF;">📄 {filename}</a>'
                        links_html += f"<div style='margin-bottom: 10px;'>{link}</div>"

                
                st.components.v1.html(f"""
                    <div style="
                        background-color: #2e2e2e;
                        padding: 15px;
                        border-radius: 10px;
                        max-height: 300px;
                        overflow-y: auto;
                        color: white;
                    ">
                        {links_html}
                    </div>
                """, height=300)
        else:
            st.warning("Le dossier des PDF n'existe pas.")

    #include User's list
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

                    # Cambiar contraseña
                    with col1:
                        new_password = st.text_input(f"Nouveau mot de passe pour {row['Email (username)']}", "", key=f"newpwd_{index}")
                        if st.button("🔑 Changer mot de passe", key=f"update_{index}"):
                            users_df.at[index, "Password"] = new_password
                            users_df.to_excel(user_file, index=False)
                            st.success(f"Mot de passe mis à jour pour {row['Email (username)']}")
                            st.rerun()

                    # Eliminar usuario
                    with col3:
                        if st.button("🗑️ Supprimer utilisateur", key=f"delete_{index}"):
                            users_df.drop(index, inplace=True)
                            users_df.to_excel(user_file, index=False)
                            st.warning(f"Utilisateur supprimé : {row['Email (username)']}")
                            st.rerun()
    else:
        st.warning("Fichier d'utilisateurs non trouvé.")

    col4, col5, col6, col7 = st.columns([2,2,2,2])

    with col4:
        if st.button("user page"):
            st.session_state.page = "user"
            st.rerun()
    with col5:
        if st.button("pdf page"):
            st.session_state.page = "viewer"
            st.rerun()
    with col7:
        if st.button("user's request"):
            st.session_state.page = "request"
            st.rerun()