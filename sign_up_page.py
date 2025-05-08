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

            # Import emails from .env file
            load_dotenv()
            EMAIL_SENDER = os.getenv("EMAIL_SENDER")
            EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
            EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")

            if all([EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECEIVER]):
                msg = EmailMessage()
                msg["Subject"] = "Nouvelle demande de création de compte"
                msg["From"] = EMAIL_SENDER
                msg["To"] = EMAIL_RECEIVER

                html_body = f"""
                <html>
                <body>
                    <p>Se ha recibido una nueva solicitud de creación de cuenta.</p>
                    <p><b>Nombre:</b> {prenom} {nom}<br>
                    <b>Correo:</b> {email}<br>
                    <b>Empresa:</b> {entreprise}<br>
                    <b>Rol:</b> {role}<br>
                    <b>Teléfono:</b> {telephone or 'No proporcionado'}</p>
                    <p>Puedes revisar la solicitud en la siguiente página:</p>
                    <p><a href="http://tudominio.com:8501">Ir a la aplicación</a></p>
                </body>
                </html>
                """

                msg.set_content("Tu cliente de correo no soporta HTML.")
                msg.add_alternative(html_body, subtype='html')

                try:
                    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
                        server.send_message(msg)
                except:
                    pass
            
        # Notify the user of success
        st.success("Votre demande a été soumise avec succès.")

    # Button to return to login page
    if st.button("Back to Login"):
        st.session_state.page = "login"
        st.rerun()

