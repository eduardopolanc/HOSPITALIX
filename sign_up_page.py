import streamlit as st
import pandas as pd
import os
import re
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

# Vérifie les caractères spéciaux non autorisés dans un champ
def contient_caracteres_speciaux(texte):
    return bool(re.search(r"[^a-zA-Z0-9@._\- +]", texte))

def email_valide(email):
    return re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email) is not None

def sign_up_page():

    st.image("dq-legaltech-logo.ico", width=170)

    st.title("Demande de création de compte")
    
    # Champs du formulaire
    nom = st.text_input("Nom")
    prenom = st.text_input("Prénom")
    telephone = st.text_input("Téléphone", max_chars=10)
    role = st.text_input("Rôle / Profession")
    entreprise = st.text_input("Nom de l'entreprise")
    email = st.text_input("Email (utilisé comme identifiant)").strip().lower()

    if st.button("Soumettre la demande"):
        # Vérification des champs obligatoires
        if not (nom and prenom and telephone and role and entreprise and email):
            st.warning("Veuillez remplir tous les champs obligatoires.")
        elif not telephone.isdigit():
            st.error("🚫 Le numéro de téléphone ne doit contenir que des chiffres.")
        elif len(telephone) != 10 or not telephone.isdigit():
            st.error("🚫 Le numéro de téléphone doit contenir exactement 10 chiffres.")
        elif not email_valide(email):
            st.error("🚫 L'adresse email saisie n'est pas valide.")
        elif any(contient_caracteres_speciaux(champ) for champ in [nom, prenom, telephone, role, entreprise, email]):
            st.error("🚫 Certains champs contiennent des caractères non autorisés. Veuillez vérifier vos saisies.")
        else:
            accepted_path = "static/accepted_user_information.xlsx"
            user_exists = False
            deleted_user = False

            if os.path.exists(accepted_path):
                accepted_df = pd.read_excel(accepted_path)
                match = accepted_df[accepted_df["Email (username)"].str.lower() == email]
                if not match.empty:
                    statut = match.iloc[0].get("Statut", "actif")
                    if statut == "désactivé":
                        deleted_user = True
                    elif statut == "supprimé_def":
                        accepted_df = accepted_df[accepted_df["Email (username)"].str.lower() != email]
                        accepted_df.to_excel(accepted_path, index=False)
                    else:
                        user_exists = True

            request_path = "demandes_en_attente.xlsx"
            already_pending = False
            if os.path.exists(request_path):
                pending_df = pd.read_excel(request_path)
                already_pending = not pending_df[pending_df["Email"].str.lower() == email].empty

            if already_pending:
                st.warning("⏳ Une demande est déjà en attente pour cet email.")
            elif user_exists:
                st.info("🚫 Un compte existe déjà avec cet email.")
            elif deleted_user:
                st.error("🚫 Un compte désactivé est associé à cet email. Contactez-nous.")
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
                                <b>Téléphone :</b> {telephone}</p>
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
                st.session_state.page = "login"
                st.rerun()

    if st.button("Retour à la connexion"):
        st.session_state.page = "login"
        st.rerun()

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
