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
    colq, colw = st.columns([2, 2])
    with colq:
        st.image("dq-legaltech-logo.ico", width=100)
    with colw:
        st.markdown("<h3 style='text-align: center;'>Générateur de fiches</h3>", unsafe_allow_html=True)

    FILE_NAME1 = "script/fonction/Fiche1.txt"
    FILE_NAME2 = "script/fonction/Fiche2.txt"
    USER_FILE = "accepted_user_information.xlsm"

    def load_users():
        if not os.path.exists(USER_FILE):
            return None
        try:
            df = pd.read_excel(USER_FILE, engine="openpyxl")
            if not all(col in df.columns for col in ["Email (username)", "Password"]):
                return None
            return df
        except:
            return None

    df_users = load_users()
    if df_users is None:
        st.error("Erreur de chargement des utilisateurs. Veuillez contacter l'administrateur.")
        st.stop()

    if "user_email" in st.session_state:
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

        if "show_form" not in st.session_state:
            st.session_state.show_form = False

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

        st.write('Commentaire')
        title = st.text_input('Commentaire', '')

        v1 = fonction.recup_variable_com(array_vchoisi[0])
        v2 = fonction.recup_variable_com(array_vchoisi[1])
        v3 = fonction.recup_variable_com(array_vchoisi[2])
        v4 = fonction.recup_variable_com(array_vchoisi[3])
        v5 = fonction.recup_variable_com(array_vchoisi[4])

        if st.button("ajouter le commentaire"):
            com = [dt.now(), 'Code fiche :', v1, v2, v3, v4, v5, title]
            try:
                wb = load_workbook("Commentaire.xlsx")
                ws = wb["Com"]
                ws.append(com)
                wb.save("Commentaire.xlsx")
                st.success("Commentaire ajouté avec succès.")
            except Exception as e:
                st.error(f"Erreur lors de l'ajout du commentaire : {e}")

        show_pdf_section = False

        if st.button("Exporter le rapport"):
            pdf = Make_pdf(FILE_NAME2, context)
            date_str = dt.now().strftime("%Y-%m-%d_%H%M%S")
            user_name = st.session_state.user_email.split("@")[0].replace(".", "").replace(" ", "")
            filename = f"{date_str}_{user_name}.pdf"
            output_path = os.path.join("static", filename)
            pdf.output(name=output_path, dest="F")
            st.session_state["pdf_to_view"] = filename
            show_pdf_section = True
            st.session_state["last_generated_pdf"] = filename
            st.session_state["last_context"] = context

        if "pdf_to_view" in st.session_state:
            file_to_display = st.session_state["pdf_to_view"]
            file_path = os.path.join("static", file_to_display)
            if os.path.exists(file_path):
                with open(file_path, "rb") as f:
                    st.download_button("Télécharger le PDF", f, file_name=file_to_display, mime="application/pdf")
                pdf_url = f"/app/static/{urllib.parse.quote(file_to_display)}"
                st.link_button("Voir le PDF", url=pdf_url)

        if st.session_state.user_email.lower() == ADMIN_EMAIL.lower():
            if st.button("Retour vers l'administrateur"):
                st.session_state.page = "admin"
                st.rerun()

        st.markdown("### 💬 Commentaire sur votre PDF généré")
        pdf_name = st.session_state.get("last_generated_pdf", None)
        user_email = st.session_state.get("user_email", "anyone")

        if not pdf_name:
            st.info("Aucun PDF généré pour le moment. La zone de commentaire apparaîtra après la génération.")
        else:
            #Zone de texte
            if "comment_text" not in st.session_state:
                st.session_state.comment_text = ""
            
            st.session_state.comment_text = st.text_area("Votre commentaire: ", value=st.session_state.comment_text)

            confirm = st.checkbox("Je confirme vouloir envoyer ce commentaire.")

            if st.button("Envoyer le commentaire"):
                if confirm and st.session_state.comment_text.strip():
                    commentaire_path = "Commentaire.xlsx"
                    context_used = st.session_state.get("last_context", [])

                    new_comment = {
                        "Horodatage": dt.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Utilisateur": user_email,
                        "PDF": pdf_name,
                        "Commentaire": st.session_state.comment_text.strip(),
                        "Variables utilisées": ", ".join(str(v) for v in context_used)
                    }

                    if os.path.exists(commentaire_path):
                        df = pd.read_excel(commentaire_path, engine="openpyxl")
                        df = pd.concat([df, pd.DataFrame([new_comment])], ignore_index=True)

                    else:
                        df = pd.DataFrame([new_comment])
                    
                    df.to_excel(commentaire_path, index=False, engine="openpyxl")

                    st.success("✅ Commentaire envoyé avec succès.")
                    st.session_state.comment_text = "" # Réinitialise le champ texte

                elif not confirm:
                    st.warning("Veuillez confirmer l'envoi en cochant la case.")
                else:
                    st.warning("Le commentaire ne peut pas être vide.")

    st.markdown("""
        <div style="background-color:#b04587;padding:15px 0;margin-top:40px;">
            <p style="text-align:center; color:white; font-size:0.9em; margin:0;">
                Droits Quotidiens Legal Tech<br>
                Pour toute question, contactez-nous à
                <a href='mailto:contact@droitsquotidiens.fr' style='color:white;text-decoration:underline;'>contact@droitsquotidiens.fr</a>
            </p>
        </div>
    """, unsafe_allow_html=True)


