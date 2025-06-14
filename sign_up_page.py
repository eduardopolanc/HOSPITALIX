import streamlit as st
import pandas as pd
import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

# Cette fonction définit la page d'inscription utilisateur
def sign_up_page():
    st.image("dq-legaltech-logo.ico", width=100)
    st.title("Demande de création de compte")

    # Champs du formulaire
    nom = st.text_input("Nom")
    prenom = st.text_input("Prénom")
    telephone = st.text_input("Téléphone")
    role = st.text_input("Rôle / Profession")
    entreprise = st.text_input("Nom de l'entreprise")
    email = st.text_input("Email (utilisé comme identifiant)").strip().lower()

    if st.button("Soumettre la demande"):
        if not (nom and prenom and telephone and role and entreprise and email):
            st.warning("Veuillez remplir tous les champs obligatoires.")
        else:
            accepted_path = "accepted_user_information.xlsm"
            user_exists = False
            deleted_user = False

            if os.path.exists(accepted_path):
                accepted_df = pd.read_excel(accepted_path)
                match = accepted_df[accepted_df["Email (username)"].str.lower() == email]
                if not match.empty:
                    statut = match.iloc[0].get("Statut", "actif")
                    if statut == "supprimé":
                        deleted_user = True
                    else:
                        user_exists = True

            request_path = "demandes_en_attente.xlsx"
            already_pending = False
            if os.path.exists(request_path):
                pending_df = pd.read_excel(request_path)
                already_pending = not pending_df[pending_df["Email"].str.lower() == email].empty

            if already_pending:
                st.warning("⏳ Une demande de création de compte a déjà été envoyée pour cette adresse email. Veuillez utiliser une autre adresse ou contacter contact@droitsquotidiens.fr.")
            elif user_exists:
                st.info("🚫 Un compte est déjà associé à cette adresse email. Veuillez utiliser une autre adresse.")
            elif deleted_user:
                st.error("🚫 Un compte associé à cette adresse email a été précédemment supprimé. Veuillez utiliser une autre adresse ou contacter contact@droitsquotidiens.fr.")
            else:
                new_request = pd.DataFrame([{
                    "Nom": nom,
                    "Prénom": prenom,
                    "Téléphone": telephone,
                    "Rôle": role,
                    "Entreprise": entreprise,
                    "Email": email
                }])

                if os.path.exists(request_path):
                    existing = pd.read_excel(request_path, engine="openpyxl")
                    all_requests = pd.concat([existing, new_request], ignore_index=True)
                else:
                    all_requests = new_request

                all_requests.to_excel(request_path, index=False, engine="openpyxl")

                load_dotenv()
                EMAIL_SENDER = os.getenv("EMAIL_SENDER")
                EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
                ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")

                if all([EMAIL_SENDER, EMAIL_PASSWORD, ADMIN_EMAIL]):
                    msg_admin = EmailMessage()
                    msg_admin["Subject"] = "Nouvelle demande de création de compte"
                    msg_admin["From"] = EMAIL_SENDER
                    msg_admin["To"] = ADMIN_EMAIL
                    msg_admin.add_alternative(f"""
                        <html>
                            <body>
                                <p>Nouvelle demande :</p>
                                <p><b>Nom :</b> {nom}<br>
                                <b>Prénom :</b> {prenom}<br>
                                <b>Email :</b> {email}<br>
                                <b>Entreprise :</b> {entreprise}<br>
                                <b>Rôle :</b> {role}<br>
                                <b>Téléphone :</b> {telephone or 'Non fourni'}</p>
                            </body>
                        </html>
                    """, subtype='html')

                    msg_user = EmailMessage()
                    msg_user["Subject"] = "Confirmation de votre demande"
                    msg_user["From"] = EMAIL_SENDER
                    msg_user["To"] = email
                    msg_user.add_alternative(f"""
                        <html>
                            <body>
                                <p>Bonjour {prenom},</p>
                                <p>Votre demande a bien été enregistrée.</p>
                                <p>Nous la traiterons dans les plus brefs délais.</p>
                                <p>Cordialement,<br>L'équipe Droits Quotidiens Legal Tech</p>
                            </body>
                        </html>
                    """, subtype='html')

                    try:
                        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
                            server.send_message(msg_admin)
                            server.send_message(msg_user)
                    except:
                        pass

                st.success("✅ Votre demande a été soumise avec succès.")

                # Nettoyage du formulaire et retour à la connexion
                st.session_state.page = "login"
                st.rerun()

    if st.button("Retour à la connexion"):
        st.session_state.page = "login"
        st.rerun()

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
