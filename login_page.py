import streamlit as st
import pandas as pd
import os
import smtplib
import re
from email.message import EmailMessage
from dotenv import load_dotenv
import bcrypt
from admin_page import generate_password

def login_page():
    st.image("dq-legaltech-logo.ico", width=170)
    st.markdown("""
        <h1 style='text-align: center; margin-bottom: 0;'>Bienvenue sur HospitAlix</h1>
        <h3 style='text-align: left; margin-top: 0;'>Page de connexion</h3>
    """, unsafe_allow_html=True)
    # -------------------------
    # Initialisation des états
    # -------------------------
    if "hide_password" not in st.session_state:
        st.session_state.hide_password = False
    if "warning_message" not in st.session_state:
        st.session_state.warning_message = False

    # -------------------------
    # Fonction de vérification
    # -------------------------
    def contient_caracteres_speciaux(texte):
        return bool(re.search(r"[^a-zA-Z0-9@._\-]", texte))

    # -------------------------
    # Saisie email
    # -------------------------
    email = st.text_input("Email").strip()

    # Réaffichage du mot de passe si email valide saisi
    if email and st.session_state.hide_password:
        st.session_state.hide_password = False
        st.session_state.warning_message = False

    if st.session_state.hide_password and not email and st.session_state.warning_message:
        st.warning("Veuillez entrer votre adresse email ci-dessus.")

    # -------------------------
    # Champ mot de passe
    # -------------------------
    password = None
    if not st.session_state.hide_password:
        password = st.text_input("Mot de passe", type="password")

    # -------------------------
    # Chargement des variables d’environnement
    # -------------------------
    load_dotenv()
    EMAIL_SENDER = os.getenv("EMAIL_SENDER")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
    user_file = "static/accepted_user_information.xlsx"

    # -------------------------
    # Chargement des utilisateurs
    # -------------------------
    def load_users():
        if not os.path.exists(user_file):
            return None
        try:
            df = pd.read_excel(user_file, engine="openpyxl")
            if not all(col in df.columns for col in ["Email (username)", "Password"]):
                return None
            return df
        except:
            return None

    def is_valid_user(email, password, df):
        row = df[df["Email (username)"].str.lower() == email.lower()]
        if not row.empty:
            hashed = str(row.iloc[0]["Hased Password"])
            return bcrypt.checkpw(password.encode(), hashed.encode())
        return False

    def send_password_email(to_email):
        if not (EMAIL_SENDER and EMAIL_PASSWORD):
            st.error("Configuration email manquante.")
            return False

        new_password = generate_password()
        hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()

        try:
            df = pd.read_excel(user_file, engine="openpyxl")
            index = df[df["Email (username)"].str.lower() == to_email.lower()].index[0]
            df.loc[index, "Hased Password"] = hashed
            df.to_excel(user_file, index=False, engine="openpyxl")

            msg = EmailMessage()
            msg["Subject"] = "Mot de passe réinitialisé - HospitAlix"
            msg["From"] = EMAIL_SENDER
            msg["To"] = to_email
            msg.set_content(f"""
    Bonjour,

    Votre mot de passe a été réinitialisé.

    Nouveau mot de passe : {new_password}

    Cordialement,
    L'équipe Droits Quotidiens Legal Tech
    """)

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
                smtp.send_message(msg)
            return True

        except Exception as e:
            st.error(f"Erreur lors de l'envoi de l'email : {e}")
            return False

    df_users = load_users()

    # -------------------------
    # Boutons
    # -------------------------
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("Connexion"):
            st.session_state.hide_password = False
            st.session_state.warning_message = False
            if contient_caracteres_speciaux(email):
                st.error("🚫 L'adresse email contient des caractères non autorisés.")
            elif email.lower() == ADMIN_EMAIL.lower() and password == ADMIN_PASSWORD:
                st.session_state.page = "admin"
                st.session_state.user_email = email
                st.rerun()
            elif df_users is not None and is_valid_user(email, password, df_users):
                row = df_users[df_users["Email (username)"].str.lower() == email.lower()]
                if not row.empty:
                    statut = row.iloc[0].get("Statut", "inconnu")
                    if statut == "actif":
                        st.session_state.page = "user"
                        st.session_state.user_email = email
                        st.rerun()
                    elif statut == "désactivé":
                        st.error("🚫 Ce compte a été désactivé. Merci de recréer un compte ou de nous contacter.")
                    elif statut == "supprimé_def":
                        st.error("🚫 Ce compte a été définitivement supprimé.")
                    else:
                        st.error("Statut du compte inconnu.")
                else:
                    st.error("Email non trouvé.")
            else:
                st.error("Email ou mot de passe incorrect.")

    with col2:
        if st.button("S'inscrire"):
            st.session_state.page = "signup"
            st.rerun()

    with col3:
        if st.button("Mot de passe oublié ?"):
            if not email:
                st.session_state.hide_password = True
                st.session_state.warning_message = True
            elif contient_caracteres_speciaux(email):
                st.error("🚫 L'adresse email contient des caractères non autorisés.")
            else:
                st.session_state.hide_password = False
                st.session_state.warning_message = False
                if df_users is not None:
                    row = df_users[df_users["Email (username)"].str.lower() == email.lower()]
                    if not row.empty:
                        statut = row.iloc[0].get("Statut", "inconnu")
                        if statut == "actif":
                            if send_password_email(email):
                                st.success("📧 Email de récupération envoyé.")
                        elif statut == "désactivé":
                            st.error("🚫 Ce compte a été désactivé.")
                        elif statut == "supprimé_def":
                            st.error("Ce compte a été définitivement supprimé.")
                        else:
                            st.error("Statut du compte inconnu.")
                    else:
                        st.error("Aucun compte associé à cet email.")
                else:
                    st.error("Impossible de charger les utilisateurs.")

    # -------------------------
    # Pied de page
    # -------------------------
    st.markdown("""
        <div style="background-color:#b04587;padding:15px 0;margin-top:40px;">
            <p style="text-align:center; color:white; font-size:0.9em; margin:0;">
                Droits Quotidiens Legal Tech<br>
                📧 Pour toute question, contactez-nous   
                <a href='mailto:contact@droitsquotidiens.fr' style='color:white;text-decoration:underline;'>contact@droitsquotidiens.fr</a>
            </p>
        </div>
    """, unsafe_allow_html=True)

