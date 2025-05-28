import streamlit as st
import pandas as pd
import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

# Cette fonction définit la page d'inscription utilisateur
def sign_up_page():
    st.title("Demande de création de compte")  # Titre de la page

    # Champs du formulaire
    nom = st.text_input("Nom")
    prenom = st.text_input("Prénom")
    telephone = st.text_input("Téléphone (optionnel)")
    role = st.text_input("Rôle / Profession")
    entreprise = st.text_input("Nom de l'entreprise")
import streamlit as st
import pandas as pd
import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

# Cette fonction définit la page d'inscription utilisateur
def sign_up_page():
    st.title("Demande de création de compte")  # Titre de la page

    # Champs du formulaire
    nom = st.text_input("Nom")
    prenom = st.text_input("Prénom")
    telephone = st.text_input("Téléphone (optionnel)")
    role = st.text_input("Rôle / Profession")
    entreprise = st.text_input("Nom de l'entreprise")
    email = st.text_input("Email (utilisé comme identifiant)")

    # Quand l'utilisateur clique sur "Soumettre"
    if st.button("Soumettre la demande"):
        if not (nom and prenom and email and role and entreprise):
            st.warning("Veuillez remplir tous les champs obligatoires.")
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

            request_file = "demandes_en_attente.xlsx"

            # Ajouter ou créer le fichier
            if os.path.exists(request_file):
                existing = pd.read_excel(request_file, engine="openpyxl")
                all_requests = pd.concat([existing, new_request], ignore_index=True)
            else:
                all_requests = new_request

            # Sauvegarde du fichier
            all_requests.to_excel(request_file, index=False, engine="openpyxl")

            # Chargement des variables d'environnement
            load_dotenv()
            EMAIL_SENDER = os.getenv("EMAIL_SENDER")
            EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
            EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")

            if all([EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECEIVER]):
                # Email à l'admin
                msg_admin = EmailMessage()
                msg_admin["Subject"] = "Nouvelle demande de création de compte"
                msg_admin["From"] = EMAIL_SENDER
                msg_admin["To"] = EMAIL_RECEIVER

                html_admin = f"""
                <html>
                    <body>
                        <p>Une nouvelle demande de création de compte a été reçue :</p>
                        <p><b>Nom :</b> {nom} <br>
                        <b>Prénom :</b> {prenom} <br>
                        <b>Email :</b> {email}<br>
                        <b>Entreprise :</b> {entreprise}<br>
                        <b>Rôle :</b> {role}<br>
                        <b>Téléphone :</b> {telephone or 'Non fourni'}</p>
                        <p><a href="http://alix.iparme.com/">Accéder à l'application</a></p>
                    </body>
                </html>
                """

                msg_admin.set_content("Une nouvelle demande a été reçue.")
                msg_admin.add_alternative(html_admin, subtype='html')

                # Email de confirmation utilisateur
                msg_user = EmailMessage()
                msg_user["Subject"] = "Confirmation de votre demande"
                msg_user["From"] = EMAIL_SENDER
                msg_user["To"] = email

                html_user = f"""
                <html>
                    <body>
                        <p>Bonjour {prenom},</p>
                        <p>Votre demande de création de compte a bien été reçue.</p>
                        <p>Nous la traiterons dans les plus brefs délais.</p>
                        <p>Merci,<br>L'équipe Hospitalix</p>
                    </body>
                </html>
                """

                msg_user.set_content("Votre demande a bien été reçue.")
                msg_user.add_alternative(html_user, subtype='html')

                try:
                    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
                        server.send_message(msg_admin)
                        server.send_message(msg_user)
                except:
                    pass

            st.success("Votre demande a été soumise avec succès.")

    # Bouton retour
    if st.button("Retour à la connexion"):
        st.session_state.page = "login"
        st.rerun()
