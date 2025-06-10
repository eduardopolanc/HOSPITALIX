import streamlit as st
import streamlit.components.v1 as components
import os
import pandas as pd
import base64
import secrets
import string
from email.message import EmailMessage
import smtplib
from dotenv import load_dotenv
import urllib.parse

# Estado inicial para el usuario seleccionado
if "selected_user_type" not in st.session_state:
    st.session_state.selected_user_type = None
if "selected_user_data" not in st.session_state:
    st.session_state.selected_user_data = None

def generate_password(length=10):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def admin_page():
    st.set_page_config(layout="wide")

    # Titulo y logout
    cola, cols, cold = st.columns([2, 2, 2])
    with cols:
        st.markdown("<h1 style='text-align: center;'>Admin Page</h1>", unsafe_allow_html=True)
    with cold:
        if st.button("log out"):
            st.session_state.page = "login"
            st.rerun()

    search_email = st.text_input("🔍 Rechercher un utilisateur (email)").strip().lower()

    col1, col2 = st.columns([2, 3])

    with col1:
        st.markdown("### ✅ Utilisateurs existants")
        accepted_users = pd.read_excel("accepted_user_information.xlsm") if os.path.exists("accepted_user_information.xlsm") else pd.DataFrame()
        if search_email:
            accepted_users = accepted_users[accepted_users['Email (username)'].str.lower().str.contains(search_email)]

        html = "<div style='max-height: 300px; overflow-y: auto; padding-right: 8px;'>"
        for i, (_, row) in enumerate(accepted_users.iterrows()):
            email = row['Email (username)']
            selected = (st.session_state.selected_user_data and st.session_state.selected_user_data.get("Email (username)") == email)
            bg = '#ffdddd' if selected else '#1e1e1e'
            border = '2px solid red' if selected else '1px solid #444'
            html += f"<form action=\"\" method=\"post\"><button name=\"accepted_{i}\" style=\"width:100%; text-align:left; background:{bg}; border:{border}; color:white; padding:10px; border-radius:5px; margin-bottom:5px;\">{email}</button></form>"
            if st.session_state.get(f"accepted_{i}"):
                st.session_state.selected_user_type = "accepted"
                st.session_state.selected_user_data = row.to_dict()
        html += "</div>"
        components.html(html, height=320)

        st.markdown("---")
        st.markdown("### 🕒 Demandes en attente")
        requests = pd.read_excel("demandes_en_attente.xlsx") if os.path.exists("demandes_en_attente.xlsx") else pd.DataFrame()
        if search_email:
            requests = requests[requests['Email'].str.lower().str.contains(search_email)]

        html2 = "<div style='max-height: 300px; overflow-y: auto; padding-right: 8px;'>"
        for i, (_, row) in enumerate(requests.iterrows()):
            email = row['Email']
            selected = (st.session_state.selected_user_data and st.session_state.selected_user_data.get("Email") == email)
            bg = '#ffdddd' if selected else '#1e1e1e'
            border = '2px solid red' if selected else '1px solid #444'
            html2 += f"<form action=\"\" method=\"post\"><button name=\"pending_{i}\" style=\"width:100%; text-align:left; background:{bg}; border:{border}; color:white; padding:10px; border-radius:5px; margin-bottom:5px;\">{email}</button></form>"
            if st.session_state.get(f"pending_{i}"):
                st.session_state.selected_user_type = "pending"
                st.session_state.selected_user_data = row.to_dict()
        html2 += "</div>"
        components.html(html2, height=320)

        st.markdown("---")
        st.subheader("📄 PDF générés")
        pdf_folder = "pdf_reports"
        search_term = st.text_input("Rechercher un PDF", "", key="pdf_search")
        if os.path.exists(pdf_folder):
            pdf_files = sorted(
                [f for f in os.listdir(pdf_folder) if f.endswith(".pdf")],
                reverse=True
            )
            if search_term:
                pdf_files = [f for f in pdf_files if search_term.lower() in f.lower()]
            if not pdf_files:
                st.info("Aucun PDF trouvé.")
            else:
                pdf_html = "<div style=\"max-height: 300px; overflow-y: auto; padding-right: 8px;\">"
                for filename in pdf_files[:50]:
                    file_path = os.path.join(pdf_folder, filename)
                    with open(file_path, "rb") as f:
                        b64 = base64.b64encode(f.read()).decode()
                    filename_encoded = urllib.parse.quote(filename)
                    filename_safe = filename.replace('"', '&quot;').replace("'", "&#39;")
                    pdf_html += f"""
                        <div style=\"display: flex; align-items: center; justify-content: space-between;
                                    background-color: #ffffff; border: 1px solid #ccc;
                                    padding: 6px 12px; border-radius: 6px; margin-bottom: 8px;
                                    box-shadow: 0 1px 3px rgba(0,0,0,0.05); font-size: 14px; color: black;\">
                            <div style=\"flex-grow: 1; display: flex; align-items: center;\">
                                <span style=\"font-weight: 500; color: black; white-space: nowrap;
                                            overflow: hidden; text-overflow: ellipsis;
                                            max-width: 500px; display: inline-block;\"
                                    title=\"{filename_safe}\">
                                    📄 {filename_safe}
                                </span>
                            </div>
                            <div style=\"display: flex; gap: 6px;\">
                                <a href=\"data:application/pdf;base64,{b64}\" download=\"{filename_safe}\" target=\"_blank\">
                                    <button style=\"font-size: 12px; padding: 4px 8px; background-color: #e0e0e0;
                                                color: black; border: none; border-radius: 4px;\">
                                        ⬇️ Télécharger
                                    </button>
                                </a>
                                <button onclick=\"window.location.href='/?pdf_to_view={filename_encoded}'\"
                                    style=\"font-size: 12px; padding: 4px 8px; background-color: #d0e7ff;
                                        color: black; border: none; border-radius: 4px;\">
                                    👁️ Voir
                                </button>
                            </div>
                        </div>
                    """
                pdf_html += "</div>"
                components.html(pdf_html, height=300, scrolling=False)
        else:
            st.warning("Le dossier des PDF n'existe pas.")

    with col2:
        if st.session_state.selected_user_data:
            user = st.session_state.selected_user_data
            user_type = st.session_state.selected_user_type

            if user_type == "accepted":
                st.markdown("### 👤 Détails de l'utilisateur accepté")
                st.write(f"**Email :** {user.get('Email (username)', '')}")
                st.write(f"**Mot de passe :** {user.get('Password', '')}")
                if st.button("🗑️ Supprimer l'utilisateur"):
                    accepted_users = accepted_users[accepted_users['Email (username)'] != user['Email (username)']]
                    accepted_users.to_excel("accepted_user_information.xlsm", index=False)
                    st.success("Utilisateur supprimé.")
                    st.session_state.selected_user_data = None
                    st.rerun()

            elif user_type == "pending":
                st.markdown("### ✉️ Détails de la demande d'inscription")
                st.write(f"**Nom :** {user.get('Nom')}")
                st.write(f"**Prénom :** {user.get('Prenom')}")
                st.write(f"**Téléphone :** {user.get('Téléphone')}")
                st.write(f"**Entreprise :** {user.get('Entreprise')}")
                st.write(f"**Rôle :** {user.get('Rôle')}")
                st.write(f"**Email :** {user.get('Email')}")
                colA, colB = st.columns(2)
                with colA:
                    if st.button("✅ Accepter la demande"):
                        password = generate_password()
                        new_account = pd.DataFrame([{
                            "Email (username)": user['Email'],
                            "Password": password
                        }])
                        if os.path.exists("accepted_user_information.xlsm"):
                            existing = pd.read_excel("accepted_user_information.xlsm")
                            all_accounts = pd.concat([existing, new_account], ignore_index=True)
                        else:
                            all_accounts = new_account
                        all_accounts.to_excel("accepted_user_information.xlsm", index=False)
                        requests = requests[requests['Email'] != user['Email']]
                        requests.to_excel("demandes_en_attente.xlsx", index=False)
                        st.success("Utilisateur accepté.")
                        st.session_state.selected_user_data = None
                        st.rerun()
                with colB:
                    if st.button("❌ Rejeter la demande"):
                        requests = requests[requests['Email'] != user['Email']]
                        requests.to_excel("demandes_en_attente.xlsx", index=False)
                        st.warning("Demande rejetée.")
                        st.session_state.selected_user_data = None
                        st.rerun()
        else:
            st.info("Sélectionnez un utilisateur dans la colonne de gauche pour voir les détails.")
