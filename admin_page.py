import streamlit as st
import streamlit.components.v1 as components
import os
import pandas as pd
import base64
import secrets
import string
from email.message import EmailMessage
import smtplib
from dotenv import load_dotenv
import urllib.parse
import datetime as dt

# Fonction pour générer un mot de passe aléatoire
def generate_password(length=10):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

# Fonction pour envoyer l'email de validation à l'utilisateur
def send_account_email(to_email, password):
    load_dotenv()
    EMAIL_SENDER = os.getenv("EMAIL_SENDER")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

    if not (EMAIL_SENDER and EMAIL_PASSWORD):
        return False

    try:
        msg = EmailMessage()
        msg["Subject"] = "Votre compte ALIX a été activé"
        msg["From"] = EMAIL_SENDER
        msg["To"] = to_email
        msg.set_content(f"""
            Bonjour,

            Votre compte ALIX a été validé.

            Voici vos identifiants :
            - Email : {to_email}
            - Mot de passe : {password}

            Rendez-vous ici pour vous connecter : http://alix.iparme.com/

            Cordialement,
            L'équipe Droits Quotidiens Legal Tech
            """)
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            smtp.send_message(msg)
        return True
    except Exception as e:
        print(f"Erreur envoi email : {e}")
        return False

def enregistrer_historique_statut(email, ancien_statut, nouveau_statut):
    date_actuelle = dt.datetime.now()
    date_str = date_actuelle.strftime("%Y-%m-%d")
    heure_str = date_actuelle.strftime("%H:%M")

    historique_path = "static/historique_statuts.xlsx"
    nouvelle_ligne = pd.DataFrame([{
        "Email": email,
        "Ancien Statut": ancien_statut,
        "Nouveau Statut": nouveau_statut,
        "Date": date_str,
        "Heure": heure_str
    }])

    if os.path.exists(historique_path):
        historique_df = pd.read_excel(historique_path)
        historique_df = pd.concat([historique_df, nouvelle_ligne], ignore_index=True)
    else:
        historique_df = nouvelle_ligne

    historique_df.to_excel(historique_path, index=False, engine="openpyxl")

# Page Admin
def admin_page():
    cola, cols, cold = st.columns([2, 2, 2])

    # Titre de la page Admin
    with cols:
        st.markdown("<h1 style='text-align: center;'>Admin Page</h1>", unsafe_allow_html=True)

    with cold:
        colq, colw = st.columns([2, 2])
        with colw:
            if st.button("log out"):
                st.session_state.page = "login"
                st.rerun()

    request_file = "demandes_en_attente.xlsx"
    accepted_users_file = "static/accepted_user_information.xlsx"
    requests = pd.DataFrame()
    if os.path.exists(request_file):
        try:
            requests = pd.read_excel(request_file)
        except:
            st.error("Erreur lors du chargement du fichier de demandes.")
    
    col_Z, col_x = st.columns([1, 2])

    with col_Z:
        st.subheader("📄 PDF générés")
    with col_x:
        search_term = st.text_input("Rechercher un PDF", "")

    pdf_folder = "static"
    all_pdfs = sorted([f for f in os.listdir(pdf_folder) if f.endswith(".pdf")], reverse=True) if os.path.exists(pdf_folder) else []

    if search_term:
        filtered_pdfs = [f for f in all_pdfs if search_term in f.lower()]
    else:
        filtered_pdfs = all_pdfs[:25]

    if not filtered_pdfs:
        st.info("Aucun PDF trouvé.")
    else:
        with st.container(height=300):
            for filename in filtered_pdfs:
                st.markdown('<hr style="margin: 6px 0;">', unsafe_allow_html=True)
                col1, col2, col3 = st.columns([3, 1, 1])

                with col1:
                    st.markdown(
                        f"""
                        <div style="font-size: 25px; margin: 0; padding: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 100%; display: inline-block;" title="{filename}">
                            📄 <b>{filename}</b>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                with col2:
                    file_path = os.path.join(pdf_folder, filename)
                    with open(file_path, "rb") as f:
                        st.download_button("⬇️ Télécharger", f, file_name=filename, mime="application/pdf")

                with col3:
                    import urllib.parse
                    pdf_url = f"/app/static/{urllib.parse.quote(filename)}"
                    st.link_button("👁️ Voir", url=pdf_url)

            if not search_term and len(all_pdfs) > 25:
                st.markdown("<br>", unsafe_allow_html=True)
                st.info("🔎 Utilisez la barre de recherche pour voir les suivants…")

    if st.button("Generer un PDF"):
        st.session_state.page = "user"
        st.rerun()

    #Comments visualization part
    st.markdown("### 💬 Commentaires des utilisateurs")

    comment_file = "Commentaire.xlsx"

    search_email = st.text_input("🔍 Rechercher un commentaire par email").strip().lower()

    if os.path.exists(comment_file):
        df_comments = pd.read_excel(comment_file, engine="openpyxl")

        if not df_comments.empty:
            if search_email:
                df_comments = df_comments[df_comments["Utilisateur"].str.lower().str.contains(search_email)]
            
            df_comments = df_comments.sort_values(by="Horodatage", ascending=False)
            df_comments = df_comments.head(100)

            with st.container(height=300):
                for _, row in df_comments.iterrows():
                    with st.expander(f"Envoyé par : {row['Utilisateur']} | Nom de la fiche : {row['PDF']} | Le : {row['Horodatage']}"):
                        st.write(f"**Commentaire :** {row['Commentaire']}")

                        st.write(f"**Santé/contexte:** {row['Santé/contexte']} | **Situation perso:** {row['Situation perso']} | **Famille:** {row['Famille']} | **Patrimoine:** {row['Patrimoine']} | **Qualité relation/pb gestion:** {row['Qualité relation/pb gestion']}")
            st.info("Aucun commentaire disponible.")
    
    else:
        st.info("Aucun fichier de commentaires trouvé.")

    cole, colr = st.columns([2, 4])
    with cole:
        st.markdown("### 👥 Gestion des utilisateurs")
    with colr:
        search_email = st.text_input("🔍 Rechercher un utilisateur (email)").strip().lower()

    col_o, col_p, col_s = st.columns(3)

    # ---- Demandes en attente ----
    with col_o:
        st.markdown("#### 🕒 Demandes en attente")
        filtered_requests = requests[requests['Email'].str.lower().str.contains(search_email)] if search_email else requests.head(25)

        if "selected_user_idx" not in st.session_state:
            st.session_state.selected_user_idx = None

        with st.container(height=300):
            if filtered_requests.empty:
                st.info("Aucune demande trouvée.")
            else:
                for i, (_, row) in enumerate(filtered_requests.iterrows()):
                    with st.expander(f"{row['Email']}"):
                        for field in ["Nom", "Prénom", "Téléphone", "Entreprise", "Rôle", "Email"]:
                            if field in row and pd.notna(row[field]):
                                st.write(f"**{field} :** {row[field]}")
                        colA, colB = st.columns([2, 2])
                        with colA:
                            if st.button("✅ Accepter", key=f"accept_{i}"):
                                st.session_state["demande_email"] = row["Email"]
                                st.session_state["demande_index"] = _
                                st.session_state["trigger_accept_dialog"] = True
                                st.session_state.pop("dialog_accept_open", None)

                        with colB:
                            if st.button("❌ Rejeter", key=f"reject_{i}"):
                                st.session_state["demande_email_rejet"] = row["Email"]
                                st.session_state["demande_index_rejet"] = _
                                st.session_state["trigger_reject_dialog"] = True
                                st.session_state.pop("dialog_reject_open", None)

        if st.session_state.get("trigger_accept_dialog", False) and "dialog_accept_open" not in st.session_state:
            st.session_state["dialog_accept_open"] = True

            @st.dialog("Confirmer l'acceptation")
            def confirmer_acceptation():
                email = st.session_state["demande_email"]
                index = st.session_state["demande_index"]
                st.write(f"Souhaitez-vous vraiment accepter la demande de {email} ?")
                colX, colY = st.columns(2)
                with colX:
                    if st.button("✅ Oui"):
                        password = generate_password()
                        enregistrer_historique_statut(email, "---", "actif")
                        send_account_email(email, password)
                        date_creation = dt.datetime.now().strftime("%Y-%m-%d")
                        row_data = filtered_requests.loc[index]
                        new_account = pd.DataFrame([{
                            "Nom": row_data.get("Nom", ""),
                            "Prénom": row_data.get("Prénom", ""),
                            "Téléphone": row_data.get("Téléphone", ""),
                            "Entreprise": row_data.get("Entreprise", ""),
                            "Rôle": row_data.get("Rôle", ""),
                            "Email (username)": row_data["Email"],
                            "Password": password,
                            "Statut": "actif",
                            "Date Création": date_creation
                        }])
                        if os.path.exists(accepted_users_file):
                            existing = pd.read_excel(accepted_users_file)
                            all_accounts = pd.concat([existing, new_account], ignore_index=True)
                        else:
                            all_accounts = new_account
                        all_accounts.to_excel(accepted_users_file, index=False, engine="openpyxl")
                        requests.drop(index=index, inplace=True)
                        requests.to_excel("demandes_en_attente.xlsx", index=False)
                        st.success("Utilisateur accepté.")
                        st.session_state["trigger_accept_dialog"] = False
                        st.session_state["dialog_accept_open"] = False
                        st.session_state.selected_user_idx = None
                        st.rerun()
                with colY:
                    if st.button("❌ No"):
                        st.session_state["trigger_accept_dialog"] = False
                        st.session_state["dialog_accept_open"] = False
                        st.rerun()

            confirmer_acceptation()

        if st.session_state.get("trigger_reject_dialog", False) and "dialog_reject_open" not in st.session_state:
            st.session_state["dialog_reject_open"] = True

            @st.dialog("Confirmer le rejet")
            def confirmer_rejet():
                email = st.session_state["demande_email_rejet"]
                index = st.session_state["demande_index_rejet"]
                st.write(f"Voulez-vous vraiment rejeter la demande de {email} ?")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Oui"):
                        requests.drop(index=index, inplace=True)
                        requests.to_excel("demandes_en_attente.xlsx", index=False)
                        st.session_state["trigger_reject_dialog"] = False
                        st.session_state["dialog_reject_open"] = False
                        st.session_state.selected_user_idx = None
                        st.warning("Demande rejetée.")
                        st.rerun()
                with col2:
                    if st.button("❌ No"):
                        st.session_state["trigger_reject_dialog"] = False
                        st.session_state["dialog_reject_open"] = False
                        st.rerun()

            confirmer_rejet()

        if not search_email and len(requests) > 25:
            st.markdown("<br>", unsafe_allow_html=True)
            st.info("🔎 Utilisez la barre de recherche pour voir les suivants…")

    # ---- Utilisateurs actifs ----
    with col_p:
        st.markdown("#### ✅ Utilisateurs actifs")
        accepted_users = pd.read_excel(accepted_users_file) if os.path.exists(accepted_users_file) else pd.DataFrame()
        if "Statut" not in accepted_users.columns:
            accepted_users["Statut"] = "actif"

        actifs = accepted_users[accepted_users["Statut"] == "actif"]
        if search_email:
            actifs = actifs[actifs['Email (username)'].str.lower().str.contains(search_email)]

        with st.container(height=300):
            if actifs.empty:
                st.info("Aucun utilisateur trouvé.")
            else:
                for i, (_, row) in enumerate(actifs.iterrows()):
                    email = row['Email (username)']
                    with st.expander(f"{email}"):
                        for field in ["Nom", "Prénom", "Téléphone", "Entreprise", "Rôle", "Email (username)", "Statut", "Date Création"]:
                            if field in row and pd.notna(row[field]):
                                st.write(f"**{field} :** {row[field]}")
                        if st.button("🗑️ Supprimer", key=f"delete_user_{i}"):
                            st.session_state["email_a_supprimer"] = email
                            st.session_state["delete_user_trigger"] = True


    # ✅ Diálogo reutilizable definido una sola vez
    if st.session_state.get("trigger_conf_dialog", False) and "dialog_conf_open" not in st.session_state:
        st.session_state["dialog_conf_open"] = True

        @st.dialog("Confirmer la suppression")
        def confirmer_suppression_utilisateur():

            target_email = st.session_state.get("email_a_supprimer", "")
            st.write(f"Voulez-vous vraiment supprimer {target_email} ?")

            colX, colY = st.columns(2)
            with colX:
                if st.button("✅ Oui"):
                    old_status = accepted_users.loc[accepted_users['Email (username)'] == target_email, 'Statut'].values[0]
                    new_status = "supprimé"
                    enregistrer_historique_statut(target_email, old_status, new_status)
                    accepted_users.loc[accepted_users['Email (username)'] == target_email, 'Statut'] = new_status
                    accepted_users.to_excel(accepted_users_file, index=False, engine="openpyxl")
                    st.success("Utilisateur marqué comme supprimé.")
                    st.session_state["delete_user_trigger"] = False
                    st.rerun()

            with colY:
                if st.button("❌ Non"):
                    st.session_state["delete_user_trigger"] = False
                    st.rerun()
        confirmer_suppression_utilisateur()


    # ---- Utilisateurs supprimés ----
    with col_s:
        st.markdown("#### 🗑️ Utilisateurs supprimés")
        supprimes = accepted_users[accepted_users["Statut"] == "supprimé"]
        if search_email:
            supprimes = supprimes[supprimes['Email (username)'].str.lower().str.contains(search_email)]

        with st.container(height=300):
            if supprimes.empty:
                st.info("Aucun utilisateur supprimé.")
            else:
                for i, (_, row) in enumerate(supprimes.iterrows()):
                    email = row["Email (username)"]
                    with st.expander(f"{email}"):
                        for field in ["Nom", "Prénom", "Téléphone", "Entreprise", "Rôle", "Email (username)", "Statut", "Date Création"]:
                            if field in row and pd.notna(row[field]):
                                st.write(f"**{field} :** {row[field]}")

                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("✅ Réactiver", key=f"reactiver_{i}"):
                                st.session_state["email_reactiver"] = email
                                st.session_state["trigger_reactivation_dialog"] = True
                                st.session_state.pop("dialog_reactivation_open", None)

                        with col2:
                            if st.button("❌ Supprimer définitivement", key=f"delete_final_{i}"):
                                st.session_state["email_supprimer_def"] = email
                                st.session_state["trigger_suppression_def_dialog"] = True
                                st.session_state.pop("dialog_suppression_def_open", None)

    # ✅ Dialog: Réactivation
    if st.session_state.get("trigger_reactivation_dialog", False) and "dialog_reactivation_open" not in st.session_state:
        st.session_state["dialog_reactivation_open"] = True

        @st.dialog("Confirmer la réactivation")
        def confirmer_reactivation():
            email = st.session_state["email_reactiver"]
            st.write(f"Souhaitez-vous vraiment réactiver l'utilisateur {email} ?")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Oui"):
                    old_status = accepted_users.loc[accepted_users['Email (username)'] == email, 'Statut'].values[0]
                    new_status = "actif"
                    enregistrer_historique_statut(email, old_status, new_status)
                    accepted_users.loc[accepted_users['Email (username)'] == email, 'Statut'] = new_status
                    accepted_users.to_excel(accepted_users_file, index=False, engine="openpyxl")
                    st.success("Utilisateur réactivé.")
                    st.session_state["trigger_reactivation_dialog"] = False
                    st.session_state["dialog_reactivation_open"] = False
                    st.rerun()
            with col2:
                if st.button("❌ Non"):
                    st.session_state["trigger_reactivation_dialog"] = False
                    st.session_state["dialog_reactivation_open"] = False
                    st.rerun()

        confirmer_reactivation()

    # ✅ Dialog: Suppression définitive
    if st.session_state.get("trigger_suppression_def_dialog", False) and "dialog_suppression_def_open" not in st.session_state:
        st.session_state["dialog_suppression_def_open"] = True

        @st.dialog("Confirmer la suppression définitive")
        def confirmer_suppression_definitive():
            email = st.session_state["email_supprimer_def"]
            st.write(f"Voulez-vous vraiment supprimer définitivement {email} ? (Cela le rendra invisible mais restera dans le fichier Excel.)")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Oui, supprimer définitivement"):
                    old_status = accepted_users.loc[accepted_users['Email (username)'] == email, 'Statut'].values[0]
                    new_status = "supprimé_def"
                    enregistrer_historique_statut(email, old_status, new_status)
                    accepted_users.loc[accepted_users['Email (username)'] == email, 'Statut'] = new_status
                    accepted_users.to_excel(accepted_users_file, index=False, engine="openpyxl")
                    st.success("Utilisateur supprimé définitivement.")
                    st.session_state["trigger_suppression_def_dialog"] = False
                    st.session_state["dialog_suppression_def_open"] = False
                    st.rerun()
            with col2:
                if st.button("❌ Non"):
                    st.session_state["trigger_suppression_def_dialog"] = False
                    st.session_state["dialog_suppression_def_open"] = False
                    st.rerun()

        confirmer_suppression_definitive()


    col_h, col_d, col_j = st.columns([2, 2, 2])

    with col_h:
        users_url = f"/app/{urllib.parse.quote(accepted_users_file)}"
        st.markdown(
            f"<a href='{users_url}' download='{accepted_users_file}' style='font-size: 16px;'>📥 Télécharger le fichier Excel utilisateur</a>",
            unsafe_allow_html=True
        )
    with col_d:
        download_url = f"/app/{urllib.parse.quote('static/historique_statuts.xlsx')}"
        st.markdown(
            f"<a href='{download_url}' download style='font-size:16px;'>📥 Télécharger l'historique des statuts</a>",
            unsafe_allow_html=True
        )

    #General statistics
    st.markdown("---")
    st.markdown("### 📊 Statistiques générales")

    accepted_users = pd.read_excel(accepted_users_file) if os.path.exists(accepted_users_file) else pd.DataFrame()
    if "Statut" not in accepted_users.columns:
        accepted_users["Statut"] = "actif"
    accepted_actifs = accepted_users[accepted_users["Statut"] == "actif"]

    requests = pd.read_excel("demandes_en_attente.xlsx") if os.path.exists("demandes_en_attente.xlsx") else pd.DataFrame()
    pdf_folder = "static"
    pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith(".pdf")] if os.path.exists(pdf_folder) else []

    # Compter uniquement les utilisateurs actifs
    nb_users = len(accepted_actifs)
    nb_requests = len(requests)
    nb_pdfs = len(pdf_files)

    # Affichage
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("👤 Utilisateurs actifs", nb_users)
    with col2:
        st.metric("⏳ Demandes en attente", nb_requests)
    with col3:
        st.metric("📄 PDFs générés", nb_pdfs)
