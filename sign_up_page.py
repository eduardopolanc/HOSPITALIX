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
    nom = st.text_input("Last Name")
    prenom = st.text_input("First Name")
    telephone = st.text_input("Phone (optional)")
    role = st.text_input("Role / Profession")
    entreprise = st.text_input("Company Name")
    email = st.text_input("Email (used as login)")

    # When the user submits the form
    if st.button("Submit Request"):
        # Check if required fields are filled
        if not (nom and prenom and email and role and entreprise):
            st.warning("Please fill in all required fields.")
        else:
            # Create a DataFrame containing the user info
            new_request = pd.DataFrame([{
                "Last Name": nom,
                "First Name": prenom,
                "Phone": telephone,
                "Role": role,
                "Company": entreprise,
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

            # load email credentials (.env file)
            load_dotenv()

            EMAIL_SENDER = os.getenv("EMAIL_SENDER")
            EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
            EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")

            if not all([EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECEIVER]):
                st.error("an error has occurred, we didn't recieve your credentials by email")
            else:
                # message to be send
                msg = EmailMessage()
                msg["Subject"] = "user request"
                msg["From"] = EMAIL_SENDER
                msg["To"] = EMAIL_RECEIVER

                # email's body
                body = f"""
                New account request:

                Prenom: {prenom}
                Nom: {nom}
                e-mail: {email}
                enterprise: {entreprise}
                Role: {role}
                phone number: {telephone}
                """
                msg.set_content(body)

                with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                    server.login(EMAIL_SENDER, EMAIL_PASSWORD)
                    server.send_message(msg)
                



            # Notify the user of success
            st.success("Your request has been submitted successfully.")

    # Button to return to login page
    if st.button("Back to Login"):
        st.session_state.page = "login"
        st.rerun()

