import os
import smtplib
import pandas as pd
from email.message import EmailMessage
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Chemin principal – à modifier si le dossier est déplacé sur le serveur
BASE_DIR = "/data/copie_windows/version Windows alix02/Desktop/ALIX_APP_DEV"

# Charger les variables d'environnement
load_dotenv(os.path.join(BASE_DIR, ".env"))
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_DEST = os.getenv("ADMIN_EMAIL")

# Définir les chemins des fichiers
STATIC_FOLDER = os.path.join(BASE_DIR, "static")
COMMENT_FILE = os.path.join(BASE_DIR, "Commentaire.xlsx")
DEMANDE_FILE = os.path.join(BASE_DIR, "demandes_en_attente.xlsx")
ACCEPTED_USERS_FILE = os.path.join(BASE_DIR, "static/accepted_user_information.xlsx")

# Dates de référence
today = datetime.today()
last_week = today - timedelta(days=7)
first_day_month = today.replace(day=1)
last_day_previous_month = first_day_month - timedelta(days=1)
first_day_previous_month = last_day_previous_month.replace(day=1)

# PDFs générés cette semaine
pdfs = []
all_pdfs = []
pdfs_to_delete = []
pdfs_this_month = 0

if os.path.exists(STATIC_FOLDER):
    for file in os.listdir(STATIC_FOLDER):
        if file.endswith(".pdf"):
            full_path = os.path.join(STATIC_FOLDER, file)
            mod_time = datetime.fromtimestamp(os.path.getmtime(full_path))
            all_pdfs.append(file)
            if mod_time >= last_week:
                pdfs.append(file)
            if mod_time <= today - timedelta(days=30):
                pdfs_to_delete.append(file)
            if mod_time >= first_day_month:
                pdfs_this_month += 1

# Commentaires de la semaine
nb_comments = 0
if os.path.exists(COMMENT_FILE):
    df_comments = pd.read_excel(COMMENT_FILE)
    df_comments["Horodatage"] = pd.to_datetime(df_comments["Horodatage"], errors="coerce")
    recent_comments = df_comments[df_comments["Horodatage"] >= last_week]
    nb_comments = len(recent_comments)

# Demandes en attente
nb_demandes = 0
if os.path.exists(DEMANDE_FILE):
    df_demandes = pd.read_excel(DEMANDE_FILE)
    nb_demandes = len(df_demandes)

# Utilisateurs actifs et statistiques
nb_users = 0
users_current_month = []
users_prev_month = []
if os.path.exists(ACCEPTED_USERS_FILE):
    df_users = pd.read_excel(ACCEPTED_USERS_FILE)
    if "Statut" in df_users.columns and "Date Création" in df_users.columns:
        actifs = df_users[df_users["Statut"] == "actif"]
        nb_users = len(actifs)

        df_users["Date Création"] = pd.to_datetime(df_users["Date Création"], errors="coerce")
        users_current_month = df_users[(df_users["Statut"] == "actif") & (df_users["Date Création"] >= first_day_month)]
        users_prev_month = df_users[(df_users["Statut"] == "actif") & (df_users["Date Création"] >= first_day_month) & (df_users["Date Création"] < first_day_month)]

# Création du message
msg = EmailMessage()
msg["Subject"] = f"Rapport hebdomadaire ALIX - Semaine du {last_week.strftime('%d/%m/%Y')} au {today.strftime('%d/%m/%Y')}"
msg["From"] = EMAIL_SENDER
msg["To"] = EMAIL_DEST

# Corps de l'email

body = f"""
Bonjour,

Veuillez consulter ci-dessous le rapport hebdomadaire de l’application Alix :

📊 Statistiques globales :

- 👤 Utilisateurs actifs : {nb_users}
- 📄 PDFs totaux sur le site : {len(all_pdfs)}
- ⏳ Demandes en attente : {nb_demandes}
  {chr(10).join(pdfs_to_delete[:5])}
  ...

- 📄 Total de PDFs générés cette semaine : {len(pdfs)}
- 💬 Nouveaux commentaires : {nb_comments}
- 🗑️ PDFs à supprimer cette semaine : {len(pdfs_to_delete)}



🔗 Consultez la plateforme pour plus d’infos : http://alix.iparme.com/

Cordialement,
L'équipe ALIX
"""
msg.set_content(body)

# Envoi de l'email

try:
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
        smtp.send_message(msg)
    print("✅ Rapport envoyé avec succès.")
except Exception as e:
    print("❌ Erreur lors de l'envoi :", e)