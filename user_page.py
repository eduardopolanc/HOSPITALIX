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
            <p>Si vous n'êtes pas à l'origine de cette modification, veuillez contacter notre équipe à l'adresse suivante :
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
    st.image("dq-legaltech-logo.ico", width=100)
    st.markdown("<h3 style='text-align: center;'>Générateur de fiches</h3>", unsafe_allow_html=True)

    FILE_NAME1 = "script/fonction/Fiche1.txt"
    FILE_NAME2 = "script/fonction/Fiche2.txt"
    USER_FILE = "accepted_user_information.xlsm"
    COMMENT_FILE = "Commentaire.xlsx"

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
        with st.expander("^z^y ^o Options"):
            menu_options = ["Profil", "Déconnexion"]
            if st.session_state.user_email.lower() != ADMIN_EMAIL.lower():
                menu_options.insert(1, "Changer mot de passe")

            menu_option = st.radio("Options", menu_options, key="user_menu")

            if menu_option == "Changer mot de passe":
                st.subheader("^=^t^p Changer le mot de passe")
                current = st.text_input("Mot de passe actuel", type="password")
                new_pwd = st.text_input("Nouveau mot de passe", type="password")
                confirm_pwd = st.text_input("Confirmez le nouveau mot de passe", type="password")
                if st.button("Mettre à jour"):
                    row = df_users[df_users["Email (username)"].str.lower() == st.session_state.user_email.lower()]
                    if not row.empty and current == str(row.iloc[0]["Password"]):
                        if new_pwd == confirm_pwd:
                            df_users.loc[row.index, "Password"] = new_pwd
                            df_users.to_excel(USER_FILE, index=False, engine="openpyxl")
                            send_password_change_email(st.session_state.user_email)
                            st.success("Mot de passe mis à jour.")
                        else:
                            st.error("Les mots de passe ne correspondent pas.")
                    else:
                        st.error("Mot de passe actuel incorrect.")

            elif menu_option == "Déconnexion":
                st.session_state.clear()
                st.success("Déconnecté avec succès.")
                st.rerun()

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
        array_vchoisi = []

        v1 = [fonction.val_contexte2(x) for x in list_contexte]
        array_vchoisi.append(v1)
        v2 = fonction.val_situ_perso2(situation_perso)
        array_vchoisi.append(v2[0])
        v3 = fonction.val_aidant2(aidant)
        array_vchoisi.append(v3[0])
        v4 = fonction.val_patrimoine2(patrimoine)
        array_vchoisi.append(v4[0])
        v5 = [fonction.val_relation2(x) for x in relation]
        array_vchoisi.append(v5)

        if "show_form" not in st.session_state:
            st.session_state.show_form = False

        st.toggle("Afficher le formulaire", key="show_form")

        if st.session_state.show_form:
            st.subheader('Code fiche :')
            st.write(v1, v2, v3, v4, v5)
            if (len(v1) > 1) or (len(v5) > 1):
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

        v1 = fonction.recup_variable_com(v1)
        v2 = fonction.recup_variable_com(v2)
        v3 = fonction.recup_variable_com(v3)
        v4 = fonction.recup_variable_com(v4)
        v5 = fonction.recup_variable_com(v5)

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

        if st.button("Exporter le rapport"):
            pdf = Make_pdf(FILE_NAME2, context)

            date_str = dt.now().strftime("%Y-%m-%d")
            user_name = st.session_state.user_email.split("@")[0].replace(".", "").replace(" ", "")
            filename = f"{date_str}_{user_name}.pdf"

            b64 = base64.b64encode(pdf.output(dest='S').encode('latin-1', 'ignore'))
            html = f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{filename}">Download file</a>'
            st.markdown(html, unsafe_allow_html=True)

        if st.button("Voir le pdf"):
            st.session_state.page = "viewer"
            st.rerun()

        if st.session_state.user_email.lower() == ADMIN_EMAIL.lower():
            if st.button("Retour vers l'administrateur"):
                st.session_state.page = "admin"
                st.rerun()

    st.markdown(
        """
        <div style="background-color:#b04587;padding:15px 0;margin-top:40px;">
            <p style="text-align:center; color:white; font-size:0.9em; margin:0;">
                Droits Quotidiens Legal Tech<br>
                ^=^s  Pour toute question, contactez-nous à <a href='mailto:contact@droitsquotidiens.fr' style='color:white;text-decoration:underline;'>contact@droitsquotidiens.fr</a>
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

