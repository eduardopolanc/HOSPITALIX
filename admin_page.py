import streamlit as st
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
    
    st.subheader("📄 PDF générés")

    pdf_folder = "pdf_reports"
    if os.path.exists(pdf_folder):
        pdf_files = sorted(
            [f for f in os.listdir(pdf_folder) if f.endswith(".pdf")],
            reverse=True
        )

        if not pdf_files:
            st.info("Aucun PDF trouvé.")
        else:
            with st.container():
                st.markdown("""
                    <style>
                        #scroll-pdf-zone {
                            max-height: 200px;
                            overflow-y: auto;
                            padding-right: 8px;
                        }
                    </style>
                    <div id="scroll-pdf-zone">
                """, unsafe_allow_html=True)

                for filename in pdf_files:
                    file_path = os.path.join(pdf_folder, filename)
                    with open(file_path, "rb") as f:
                        b64 = base64.b64encode(f.read()).decode()

                    # URL encoding du nom de fichier pour éviter des problèmes d'URL
                    filename_encoded = urllib.parse.quote(filename)

                    st.markdown(f"""
                        <div style="display: flex; align-items: center; justify-content: space-between;
                                    background-color: #ffffff; border: 1px solid #ccc;
                                    padding: 6px 12px; border-radius: 6px; margin-bottom: 8px;
                                    box-shadow: 0 1px 3px rgba(0,0,0,0.05); font-size: 14px; color: black;">
                            <div style="flex-grow: 1; display: flex; align-items: center;">
                                <span style="font-weight: 500; color: black; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 220px; display: inline-block;" title="{filename}">
                                    📄 {filename}
                                </span>
                            </div>
                            <div style="display: flex; gap: 6px;">
                                <a href="data:application/pdf;base64,{b64}" download="{filename}" target="_blank">
                                    <button style="font-size: 12px; padding: 4px 8px; background-color: #e0e0e0; color: black; border: none; border-radius: 4px;">
                                        ⬇️ Télécharger
                                    </button>
                                </a>
                                <button onclick="window.location.href='/pdf_viewer_page?pdf_to_view={filename_encoded}'"
                                    style="font-size: 12px; padding: 4px 8px; background-color: #d0e7ff; color: black; border: none; border-radius: 4px;">
                                    👁️ Voir
                                </button>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                # Cierre du div scroll
                st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.warning("Le dossier des PDF n'existe pas.")

    if st.button("Generer un PDF"):
        st.session_state.page = "user"
        st.rerun()

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
