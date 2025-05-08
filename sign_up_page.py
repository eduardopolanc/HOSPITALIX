import streamlit as st
import pandas as pd
import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

# This function defines the user sign-up page
def sign_up_page():
    st.title("Account Creation Request")  # Page title

    # Input form fields
    nom = st.text_input("Nom")
    prenom = st.text_input("Prenom")
    telephone = st.text_input("Téléphone (optionnel)")
    role = st.text_input("Rôle / Profession")
    entreprise = st.text_input("Nom de l'entreprise")
    email = st.text_input("Email (utilisé comme identifiant)")

    # When the user submits the form
    if st.button("Submit Request"):
        # Check if required fields are filled
        if not (nom and prenom and email and role and entreprise):
            st.warning("Veuillez remplir tous les champs obligatoires.")
        else:
            # Create a DataFrame containing the user info
            new_request = pd.DataFrame([{
                "Nom": nom,
                "Prenom": prenom,
                "Téléphone": telephone,
                "Rôle": role,
                "entreprise": entreprise,
                "Email": email
            }])

            # Define where the requests will be stored
            request_file = "demandes_en_attente.xlsx"

            # Append to existing file or create a new one
            if os.path.exists(request_file):
                existing = pd.read_excel(request_file)
                all_requests = pd.concat([existing, new_request], ignore_index=True)
            else:
                all_requests = new_request

            # Save the updated table to Excel
            all_requests.to_excel(request_file, index=False)
            load_dotenv()
            EMAIL_SENDER = os.getenv("EMAIL_SENDER")
            EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
            EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")

            if all([EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECEIVER]):
                # -------------------- email to admin --------------------
                msg_admin = EmailMessage()
                msg_admin["Subject"] = "Nouvelle demande de création de compte"
                msg_admin["From"] = EMAIL_SENDER
                msg_admin["To"] = EMAIL_RECEIVER

                html_admin = f"""
                <html>
                    <body>
                        <p>Une nouvelle demande de création de compte a été reçue :</p>
                        <p><b>Nom :</b> {prenom} {nom}<br>
                        <b>Email :</b> {email}<br>
                        <b>Entreprise :</b> {entreprise}<br>
                        <b>Rôle :</b> {role}<br>
                        <b>Téléphone :</b> {telephone or 'Non fourni'}</p>
                        <p>Vous pouvez consulter la demande sur la page suivante :</p>
                        <p><a href="http://alix.iparme.com/">Accéder à l'application</a></p>
                    </body>
                </html>
                """

                msg_admin.set_content("Une nouvelle demande a été reçue (version texte).")
                msg_admin.add_alternative(html_admin, subtype='html')


                # -------------------- email to user --------------------
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

                msg_user.set_content("Votre demande a bien été reçue (version texte).")
                msg_user.add_alternative(html_user, subtype='html')


                # -------------------- sending --------------------
                try:
                    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
                        server.send_message(msg_admin)
                        server.send_message(msg_user)
                except:
                    pass
            
        # Notify the user of success
        st.success("Votre demande a été soumise avec succès.")

    # Button to return to login page
    if st.button("Back to Login"):
        st.session_state.page = "login"
        st.rerun()

