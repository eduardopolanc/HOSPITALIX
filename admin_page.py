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

# Fonction pour générer un mot de passe aléatoire
def generate_password(length=10):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

# Fonction pour envoyer l'email de validation à l'utilisateur
def send_account_email(to_email, password):
    load_dotenv()
    EMAIL_SENDER = os.getenv("EMAIL_SENDER")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

    if not (EMAIL_SENDER and EMAIL_PASSWORD):
        return False

    try:
        msg = EmailMessage()
        msg["Subject"] = "Votre compte ALIX a été activé"
        msg["From"] = EMAIL_SENDER
        msg["To"] = to_email
        msg.set_content(f"""
Bonjour,

Votre compte ALIX a été validé.

Voici vos identifiants :
- Email : {to_email}
- Mot de passe : {password}

Rendez-vous ici pour vous connecter : http://alix.iparme.com/

Cordialement,
L'équipe Droits Quotidiens Legal Tech
""")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            smtp.send_message(msg)
        return True
    except Exception as e:
        print(f"Erreur envoi email : {e}")
        return False

# Page Admin
def admin_page():
    st.set_page_config(layout="wide")
    cola, cols, cold = st.columns([2, 2, 2])

    # Titre de la page Admin
    with cols:
        st.markdown("<h1 style='text-align: center;'>Admin Page</h1>", unsafe_allow_html=True)

    with cold:
        colq, colw = st.columns([2, 2])
        with colw:
            if st.button("log out"):
                st.session_state.page = "login"
                st.rerun()

    request_file = "demandes_en_attente.xlsx"
    account_file = "accepted_user_information.xlsm"
    requests = pd.DataFrame()
    if os.path.exists(request_file):
        try:
            requests = pd.read_excel(request_file)
        except:
            st.error("Erreur lors du chargement du fichier de demandes.")
    
    col_Z, col_x = st.columns([1, 2])

    with col_Z:
        st.subheader("📄 PDF générés")

    with col_x:
        search_term = st.text_input("Rechercher un PDF", "", key="pdf_search")

    pdf_folder = "pdf_reports"

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
            # Empieza HTML completo para el scrollable container
            pdf_html = """
            <div style="max-height: 300px; overflow-y: auto; padding-right: 8px;">
            """

            for filename in pdf_files[:50]:
                file_path = os.path.join(pdf_folder, filename)
                with open(file_path, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode()
                filename_encoded = urllib.parse.quote(filename)
                filename_safe = filename.replace('"', '&quot;').replace("'", "&#39;")

                pdf_html += f"""
                    <div style="display: flex; align-items: center; justify-content: space-between;
                                background-color: #ffffff; border: 1px solid #ccc;
                                padding: 6px 12px; border-radius: 6px; margin-bottom: 8px;
                                box-shadow: 0 1px 3px rgba(0,0,0,0.05); font-size: 14px; color: black;">
                        <div style="flex-grow: 1; display: flex; align-items: center;">
                            <span style="font-weight: 500; color: black; white-space: nowrap;
                                        overflow: hidden; text-overflow: ellipsis;
                                        max-width: 500px; display: inline-block;"
                                title="{filename_safe}">
                                📄 {filename_safe}
                            </span>
                        </div>
                        <div style="display: flex; gap: 6px;">
                            <a href="data:application/pdf;base64,{b64}" download="{filename_safe}" target="_blank">
                                <button style="font-size: 12px; padding: 4px 8px; background-color: #e0e0e0;
                                            color: black; border: none; border-radius: 4px;">
                                    ⬇️ Télécharger
                                </button>
                            </a>
                            <button onclick="window.location.href='/?pdf_to_view={filename_encoded}'"
                                style="font-size: 12px; padding: 4px 8px; background-color: #d0e7ff;
                                    color: black; border: none; border-radius: 4px;">
                                👁️ Voir
                            </button>
                        </div>
                    </div>
                """

            pdf_html += "</div>"

            # Renderiza todo con soporte HTML completo
            components.html(pdf_html, height=300, scrolling=False)
    else:
        st.warning("Le dossier des PDF n'existe pas.")

    if st.button("Generer un PDF"):
        st.session_state.page = "user"
        st.rerun()

    # --- Estado inicial necesario ---
    if "selected_user_type" not in st.session_state:
        st.session_state.selected_user_type = None  # "accepted" or "pending"
    if "selected_user_data" not in st.session_state:
        st.session_state.selected_user_data = None

    # --- Input de búsqueda compartido ---
    search_email = st.text_input("🔍 Rechercher un utilisateur (email)").strip().lower()

    col1, col2 = st.columns([2, 3])

    # --- Columna izquierda ---
    with col1:
        st.markdown("### ✅ Utilisateurs existants")
        accepted_users = pd.read_excel("accepted_user_information.xlsm") if os.path.exists("accepted_user_information.xlsm") else pd.DataFrame()

        if search_email:
            accepted_users = accepted_users[accepted_users['Email (username)'].str.lower().str.contains(search_email)]

        for i, (_, row) in enumerate(accepted_users.head(5).iterrows()):
            if st.button(f"{row['Email (username)']}", key=f"accepted_{i}"):
                st.session_state.selected_user_type = "accepted"
                st.session_state.selected_user_data = row.to_dict()

        st.markdown("---")
        st.markdown("### 🕒 Demandes en attente")
        requests = pd.read_excel("demandes_en_attente.xlsx") if os.path.exists("demandes_en_attente.xlsx") else pd.DataFrame()

        if search_email:
            requests = requests[requests['Email'].str.lower().str.contains(search_email)]

        for i, (_, row) in enumerate(requests.head(5).iterrows()):
            if st.button(f"{row['Email']}", key=f"pending_{i}"):
                st.session_state.selected_user_type = "pending"
                st.session_state.selected_user_data = row.to_dict()

    # --- Columna derecha ---
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







'''
    col1, col2 = st.columns([3, 5])

    # Section des demandes d'inscription
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
                        if send_account_email(row['Email'], password):
                            st.success(f"Compte créé et email envoyé à {row['Email']}.")
                        else:
                            st.warning(f"Compte créé mais échec de l'envoi d'email à {row['Email']}.")
                        st.rerun()

                    if colr.button("❌ Rejeter", key=f"reject_{index}"):
                        requests.drop(index, inplace=True)
                        requests.to_excel(request_file, index=False)
                        st.warning(f"Demande rejetée pour : {row['Email']}")
                        st.rerun()
        else:
            st.info("Aucune demande en attente.")

    # Section des PDFs générés
    with col2:
        # Gestion des utilisateurs
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

    # Navigation
    col4, col5, col6, col7 = st.columns([2,2,2,2])
    with col5:
        if st.button("pdf page"):
            st.session_state.page = "viewer"
            st.rerun()

'''