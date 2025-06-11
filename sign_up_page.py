import streamlit as st
import pandas as pd
import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

# Cette fonction définit la page d'inscription utilisateur
def sign_up_page():
    st.title("Demande de création de compte")

    # Champs du formulaire
    nom = st.text_input("Nom")
    prenom = st.text_input("Prénom")
    telephone = st.text_input("Téléphone (optionnel)")
    role = st.text_input("Rôle / Profession")
    entreprise = st.text_input("Nom de l'entreprise")
    email = st.text_input("Email (utilisé comme identifiant)").strip().lower()

    if st.button("Soumettre la demande"):
        if not (nom and prenom and email and role and entreprise):
            st.warning("Veuillez remplir tous les champs obligatoires.")
        else:
            # Vérification dans accepted_user_information.xlsm
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

            # Vérification dans demandes_en_attente.xlsx
            request_path = "demandes_en_attente.xlsx"
            already_pending = False
            if os.path.exists(request_path):
                pending_df = pd.read_excel(request_path)
                already_pending = not pending_df[pending_df["Email"].str.lower() == email].empty

            # Affichage des cas bloquants
            if already_pending:
                st.warning("⏳ Une demande est déjà en attente pour cette adresse.")
            elif user_exists:
                st.info("✅ Ce compte est déjà actif.")
            elif deleted_user:
                st.error("🚫 Ce compte a été supprimé. Contactez contact@droitsquotidiens.fr")
            else:
                # Création de la ligne de demande
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

                # Envoi des emails
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
                                <p>Merci,<br>L'équipe Hospitalix</p>
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

    if st.button("Retour à la connexion"):
        st.session_state.page = "login"
        st.rerun()
