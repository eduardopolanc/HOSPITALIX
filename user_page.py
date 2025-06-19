import os
import re
import xlrd
import difflib
import streamlit as st
import logging
import time
from pytrends.request import TrendReq
import script.fonction.fonction as fonction
from openpyxl import load_workbook
from fpdf import FPDF
import base64
from script.pdf.pdf_generator import Make_pdf
from datetime import datetime as dt
import hashlib
import pandas as pd
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import urllib.parse
import streamlit.components.v1 as components
import bcrypt

st.markdown("""
    <style>
    [data-testid="collapsedControl"] {
        display: none;
    }
    section[data-testid="stSidebar"] {
        min-width: 300px !important;
        max-width: 300px !important;
        background-color: #f4f5f7 !important;
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
    }
    .block-container {
        padding-top: 1rem !important;
    }
    [class^="css-"][class*="e1fqkh3o3"] {
        min-height: 0px !important;
    }
    </style>
""", unsafe_allow_html=True)

load_dotenv()
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
def contient_caracteres_speciaux(texte):
    return not re.match(r"^[\wÀ-ÿ@.\-_\s]*$", texte)


def send_password_change_email(user_email):
    msg = EmailMessage()
    msg["Subject"] = "Changement de mot de passe"
    msg["From"] = EMAIL_SENDER
    msg["To"] = user_email

    html_content = f"""
    <html>
        <body>
            <p>Bonjour,</p>
            <p>Votre mot de passe a été modifié avec succès.</p>
            <p>Si vous n'êtes pas à l'origine de cette modification, veuillez contacter notre équipe :
            <a href='mailto:contact@droitsquotidiens.fr'>contact@droitsquotidiens.fr</a>.</p>
            <p>Merci,<br>L'équipe Droits Quotidiens</p>
        </body>
    </html>
    """

    msg.set_content("Votre mot de passe a été modifié.")
    msg.add_alternative(html_content, subtype='html')

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        logging.error(f"Erreur lors de l'envoi de l'email : {e}")


def user_page():
    FILE_NAME1 = "script/fonction/Fiche1.txt"
    FILE_NAME2 = "script/fonction/Fiche2.txt"
    USER_FILE = "static/accepted_user_information.xlsx"

    def load_users():
        if not os.path.exists(USER_FILE):
            return None
        try:
            df = pd.read_excel(USER_FILE, engine="openpyxl")
            if not all(col in df.columns for col in ["Email (username)", "Hashed Password"]):
                return None
            return df
        except:
            return None

    df_users = load_users()
    if df_users is None:
        if st.session_state.user_email.lower() != ADMIN_EMAIL.lower():
            st.error("Erreur de chargement des utilisateurs. Veuillez contacter l'administrateur.")
            st.stop()

    # Barre du haut avec logo, titre et menu Options
    col1, col2, col3 = st.columns([1, 4, 2])
    with col1:
        st.image("dq-legaltech-logo.ico", width=170)
    with col2:
        st.markdown("<h1 style='text-align: center;'>Générateur de fiches</h1>", unsafe_allow_html=True)
    with col3:
        if "user_email" in st.session_state:
            menu_options = ["Profil", "Déconnexion"]
            if st.session_state.user_email.lower() != ADMIN_EMAIL.lower():
                menu_options.insert(1, "Changer mot de passe")

            menu_option = st.selectbox("Options", menu_options, key="user_menu")

            if menu_option == "Changer mot de passe":
                st.subheader("Changer le mot de passe")

                if "show_pwd_form" not in st.session_state:
                    st.session_state["show_pwd_form"] = True

                if not st.session_state["show_pwd_form"]:
                    st.session_state["show_pwd_form"] = True
                    for key in ["current_pwd", "new_pwd", "confirm_pwd"]:
                        st.session_state.pop(key, None)
                    st.rerun()

                if st.session_state["show_pwd_form"]:
                    st.text_input("Mot de passe actuel", type="password", key="current_pwd")
                    st.text_input("Nouveau mot de passe", type="password", key="new_pwd")
                    st.text_input("Confirmez le nouveau mot de passe", type="password", key="confirm_pwd")


                    if st.button("Mettre à jour"):
                        current = st.session_state.get("current_pwd", "")
                        new_pwd = st.session_state.get("new_pwd", "")
                        confirm_pwd = st.session_state.get("confirm_pwd", "")
                        if contient_caracteres_speciaux(new_pwd) or contient_caracteres_speciaux(confirm_pwd):
                            st.error("❌ Le mot de passe ne doit pas contenir de caractères spéciaux (autorisés : lettres, chiffres, @ . - _ ).")
                        else:
                            row = df_users[df_users["Email (username)"].str.lower() == st.session_state.user_email.lower()]
                            if not row.empty and bcrypt.checkpw(current.encode(), str(row.iloc[0]["Password"]).encode()):
                                if new_pwd == confirm_pwd:
                                    new_hash = bcrypt.hashpw(new_pwd.encode(), bcrypt.gensalt()).decode()
                                    df_users.loc[row.index, "Hashed Password"] = new_hash
                                    df_users.to_excel(USER_FILE, index=False, engine="openpyxl")
                                    send_password_change_email(st.session_state.user_email)
                                    st.success("Mot de passe mis à jour.")
                                    st.session_state["show_pwd_form"] = False
                                else:
                                    st.error("Les mots de passe ne correspondent pas.")
                            else:
                                st.error("Mot de passe actuel incorrect.")


            elif menu_option == "Déconnexion":
                st.session_state.clear()
                st.success("Déconnecté avec succès.")
                st.rerun()

    if "user_email" not in st.session_state:
        st.error("Veuillez vous connecter.")
        st.stop()


    st.sidebar.title('Choix')
    list_contexte = st.sidebar.multiselect('Santé /contexte', (
        'mémoire', 'santé', 'surendettement', 'maltraitance', 'internet',
        'tuteur', 'rien', 'plus disponible', 'pas habitude papier', 'indifférent'))
    situation_perso = st.sidebar.selectbox('Situation perso', (
        'Seule', 'Veuf', 'Divorce', 'Conjoint pas autonome', 'Conjoint autonome', 'indifférent'))
    aidant = st.sidebar.selectbox('Famille', (
        'famille proche', 'famille éloignée', 'autre', 'aucun', 'plus disponible', 'indifférent'))
    patrimoine = st.sidebar.selectbox('Patrimoine', (
        'Faible', 'moyen', 'important', 'gestion pat', 'indifférent'))
    relation = st.sidebar.multiselect('Qualité relation/pb gestion', (
        'bonnes relations', 'relation tendues', 'admin', 'budget', 'suivi med', 'aucun pb', 'gestion pat', 'indifférent'))

    context = [list_contexte, situation_perso, aidant, patrimoine, relation]
    array_vchoisi = [
        [fonction.val_contexte2(x) for x in list_contexte],
        fonction.val_situ_perso2(situation_perso)[0],
        fonction.val_aidant2(aidant)[0],
        fonction.val_patrimoine2(patrimoine)[0],
        [fonction.val_relation2(x) for x in relation]
    ]

    st.toggle("Afficher le formulaire", key="show_form")
    if st.session_state.show_form:
        st.subheader('Code fiche :')
        st.write(*array_vchoisi)

        if len(array_vchoisi[0]) > 1 or len(array_vchoisi[4]) > 1:
            fonction.generate(array_vchoisi, FILE_NAME1)
            fonction.generate_with_regle(array_vchoisi, FILE_NAME2)
            fiche1 = open(FILE_NAME1, encoding='utf-8').readlines()
            fiche2 = open(FILE_NAME2, encoding='utf-8').readlines()
            st.title('Fiche sans règle:')
            st.write(fiche1)
            st.title('Fiche avec règle:')
            st.write(fiche2)
        else:
            fonction.generate(array_vchoisi, FILE_NAME2)
            fiche2 = open(FILE_NAME2, encoding='utf-8').readlines()
            st.title('Fiche simple:')
            st.write(fiche2)

    v1 = fonction.recup_variable_com(array_vchoisi[0])
    v2 = fonction.recup_variable_com(array_vchoisi[1])
    v3 = fonction.recup_variable_com(array_vchoisi[2])
    v4 = fonction.recup_variable_com(array_vchoisi[3])
    v5 = fonction.recup_variable_com(array_vchoisi[4])

    st.session_state["last_context_labeled"] = {
        "Santé/contexte": v1,
        "Situation perso": v2,
        "Famille": v3,
        "Patrimoine": v4,
        "Qualité relation/pb gestion": v5
    }

    col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
    with col1:
        if st.button("Exporter le rapport"):
            pdf = Make_pdf(FILE_NAME2, context)
            date_str = dt.now().strftime("%Y-%m-%d_%H%M%S")
            user_name = st.session_state.user_email.split("@")[0].replace(".", "").replace(" ", "")
            filename = f"{date_str}_{user_name}.pdf"
            output_path = os.path.join("static", filename)
            pdf.output(name=output_path, dest="F")
            st.session_state["pdf_to_view"] = filename
            st.session_state["last_generated_pdf"] = filename
            st.session_state["last_context"] = context

    with col2:
        if "pdf_to_view" in st.session_state:
            file_to_display = st.session_state["pdf_to_view"]
            file_path = os.path.join("static", file_to_display)
            if os.path.exists(file_path):
                with open(file_path, "rb") as f:
                    st.download_button("Télécharger le PDF", f, file_name=file_to_display, mime="application/pdf")
                pdf_url = f"/app/static/{urllib.parse.quote(file_to_display)}"
                with col3:
                    st.link_button("Voir le PDF", url=pdf_url)

    with col4:
        if st.session_state.user_email.lower() == ADMIN_EMAIL.lower():
            if st.button("Retour vers l'administrateur"):
                st.session_state.page = "admin"
                st.rerun()

    # Bloc Commentaire
    commentaire_path = "Commentaire.xlsx"

    def enregistrer_commentaire(texte):
        user_email = st.session_state.get("user_email", "anonyme")
        pdf_name = st.session_state.get("last_generated_pdf", "inconnu")
        context_labeled = st.session_state.get("last_context_labeled", {})

        if os.path.exists(commentaire_path):
            df = pd.read_excel(commentaire_path, engine="openpyxl")
            duplicate = df[
                (df["Utilisateur"] == user_email) &
                (df["PDF"] == pdf_name)
            ]
            if not duplicate.empty:
                st.warning("⚠️ Un commentaire a déjà été envoyé pour ce PDF.")
                return

        new_comment = {
            "Horodatage": dt.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Utilisateur": user_email,
            "PDF": pdf_name,
            "Commentaire": texte.strip(),
            "Santé/contexte": context_labeled.get("Santé/contexte", ""),
            "Situation perso": context_labeled.get("Situation perso", ""),
            "Famille": context_labeled.get("Famille", ""),
            "Patrimoine": context_labeled.get("Patrimoine", ""),
            "Qualité relation/pb gestion": context_labeled.get("Qualité relation/pb gestion", "")
        }

        if os.path.exists(commentaire_path):
            df = pd.concat([df, pd.DataFrame([new_comment])], ignore_index=True)
        else:
            df = pd.DataFrame([new_comment])

        df.to_excel(commentaire_path, index=False, engine="openpyxl")
        st.success("✅ Commentaire envoyé avec succès.")
        st.session_state.comment_text = ""
        st.rerun()

    @st.dialog("Confirmation d'envoi")
    def confirmer_envoi_commentaire(texte):
        st.write("Souhaitez-vous vraiment envoyer ce commentaire ?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Oui, envoyer", key="confirm_envoyer"):
                enregistrer_commentaire(texte)
        with col2:
            if st.button("❌ Annuler", key="cancel_envoyer"):
                st.rerun()

    st.markdown("### 💬 Commentaire sur votre PDF généré")
    pdf_name = st.session_state.get("last_generated_pdf", None)

    if not pdf_name:
        st.info("Aucun PDF généré pour le moment. La zone de commentaire apparaîtra après la génération.")
    else:
        if "comment_text" not in st.session_state:
            st.session_state.comment_text = ""

        txt = st.text_area(
            "Votre commentaire :",
            value=st.session_state.comment_text,
            max_chars=1000,
            height=150)


        if st.button("Envoyer le commentaire"):
            if not txt.strip():
                st.warning("Le commentaire ne peut pas être vide.")
                return
            elif contient_caracteres_speciaux(txt):
                st.error("❌ Le commentaire contient des caractères spéciaux non autorisés (autorisés : lettres, chiffres, @ . - _ ).")
                return
            else:
                confirmer_envoi_commentaire(txt)

    st.markdown("""
        <div style="background-color:#b04587;padding:15px 0;margin-top:40px;">
            <p style="text-align:center; color:white; font-size:0.9em; margin:0;">
                Droits Quotidiens Legal Tech<br>
                📧 Pour toute question, contactez-nous à
                <a href='mailto:contact@droitsquotidiens.fr' style='color:white;text-decoration:underline;'>contact@droitsquotidiens.fr</a>
            </p>
        </div>
    """, unsafe_allow_html=True)
