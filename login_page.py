import streamlit as st
import pandas as pd
import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

def login_page():
    st.image("dq-legaltech-logo.ico", width=100)
    st.markdown("<h3 style='text-align: center;'>Bienvenue sur ALIX</h3>", unsafe_allow_html=True)
    st.title("Page de Connexion")

    # Champs de saisie
    email = st.text_input("Email").strip()
    password = st.text_input("Mot de passe", type="password")

    # Chargement des variables d'environnement
    load_dotenv()
    EMAIL_SENDER = os.getenv("EMAIL_SENDER")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

    # Fichier Excel des utilisateurs
    user_file = "static/accepted_user_information.xlsx"
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

    # Chargement du fichier
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

    # Vérification email + mot de passe
    def is_valid_user(email, password, df):
        user_row = df[df["Email (username)"].str.lower() == email.lower()]
        if not user_row.empty:
            return password == str(user_row.iloc[0]["Password"])
        return False

    # Envoi d'un email si l'utilisateur a oublié son mot de passe
    def send_password_email(to_email, password):
        if not (EMAIL_SENDER and EMAIL_PASSWORD):
            st.error("Configuration email manquante.")
            return False
        try:
            msg = EmailMessage()
            msg["Subject"] = "Mot de passe oublié - ALIX"
            msg["From"] = EMAIL_SENDER
            msg["To"] = to_email
            msg.set_content(f"""
Bonjour,

Voici votre mot de passe : {password}

Si vous n'avez pas fait cette demande, merci d'ignorer ce message.

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

    # Trois boutons alignés
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("Connexion"):
            if email.lower() == ADMIN_EMAIL.lower() and password == ADMIN_PASSWORD:
                st.session_state.page = "admin"
                st.session_state.user_email = email
                st.rerun()
            elif df_users is not None and is_valid_user(email, password, df_users):
                st.session_state.page = "user"
                st.session_state.user_email = email
                st.rerun()
            else:
                st.error("Email ou mot de passe incorrect.")

    with col2:
        if st.button("S'inscrire"):
            st.session_state.page = "signup"
            st.rerun()

    with col3:
        if st.button("Mot de passe oublié ?"):
            if not email:
                st.warning("Veuillez entrer votre adresse email ci-dessus.")
            elif df_users is not None:
                user_row = df_users[df_users["Email (username)"].str.lower() == email.lower()]
                if not user_row.empty:
                    statut = user_row.iloc[0].get("Statut", "actif")
                    if statut == "supprimé":
                        st.error("🚫 Ce compte a été supprimé. Pour plus d'informations, contactez contact@droitsquotidiens.fr")
                    else:
                        user_password = str(user_row.iloc[0]["Password"])
                        if send_password_email(email, user_password):
                            st.success("Email de récupération envoyé.")
                else:
                    st.error("Aucun compte associé à cet email.")
            else:
                st.error("Impossible de charger les utilisateurs.")

    # Pied de page
    st.markdown(
        """
        <div style="background-color:#b04587;padding:15px 0;margin-top:40px;">
            <p style="text-align:center; color:white; font-size:0.9em; margin:0;">
                Droits Quotidiens Legal Tech<br>
                📧 Pour toute question, contactez-nous à <a href='mailto:contact@droitsquotidiens.fr' style='color:white;text-decoration:underline;'>contact@droitsquotidiens.fr</a>
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
