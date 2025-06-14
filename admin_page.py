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
    accepted_users_file = "accepted_user_information.xlsx"
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

    # Filtrado por búsqueda
    if search_term:
        filtered_pdfs = [f for f in all_pdfs if search_term in f.lower()]
    else:
        filtered_pdfs = all_pdfs[:25]  # Limitar a 25 si no se está buscando

    # Mostrar PDFs
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

            # Mostrar mensaje si hay más de 25 y no hay búsqueda activa
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

        if search_email:
            filtered_requests = requests[requests['Email'].str.lower().str.contains(search_email)]
        else:
            filtered_requests = requests.head(25)
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
                        colA, colB, colC = st.columns([1, 1, 2])  # ✅ 定义三列
                        with colC:
                            if st.button("🟢 Commencer validation", key=f"start_confirm_{i}"):
                                st.session_state.selected_user_idx = i
                                st.rerun()
                        if st.session_state.selected_user_idx == i:            
                            with colA:
                                if st.checkbox("Confirmez l'acceptation", key=f"confirm_accept_{i}"):               
                                    if st.button("✅ Accepter", key=f"accept_{i}"):
                                        password = generate_password()
                                        send_account_email(row["Email"], password)
                                        new_account = pd.DataFrame([{
                                            "Nom": row.get("Nom", ""),
                                            "Prénom": row.get("Prénom", ""),
                                            "Téléphone": row.get("Téléphone", ""),
                                            "Entreprise": row.get("Entreprise", ""),
                                            "Rôle": row.get("Rôle", ""),
                                            "Email (username)": row["Email"],
                                            "Password": password,
                                            "Statut": "actif"
                                        }])
                                        if os.path.exists(accepted_users_file):
                                            existing = pd.read_excel(accepted_users_file)
                                            all_accounts = pd.concat([existing, new_account], ignore_index=True)
                                        else:
                                            all_accounts = new_account
                                        all_accounts.to_excel(accepted_users_file, index=False, engine="openpyxl")
  
                                        requests = requests[requests['Email'] != row['Email']]
                                        requests.to_excel("demandes_en_attente.xlsx", index=False)
                                        st.session_state.selected_user_idx = None                                        
                                        st.success("Utilisateur accepté.")
                                        st.rerun()
                                with colB:
                                    if st.button("❌ Rejeter", key=f"reject_{i}"):
                                        requests = requests[requests['Email'] != row['Email']]
                                        requests.to_excel("demandes_en_attente.xlsx", index=False)
                                        st.session_state.selected_user_idx = None             
                                        st.warning("Demande rejetée.")
                                        st.rerun()
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
                    with st.expander(f"{row['Email (username)']}"):
                        for field in ["Nom", "Prénom", "Téléphone", "Entreprise", "Rôle", "Email (username)", "Statut"]:
                            if field in row and pd.notna(row[field]):
                                st.write(f"**{field} :** {row[field]}")
                        if st.button("🗑️ Supprimer", key=f"delete_user_{i}"):
                            accepted_users.loc[accepted_users['Email (username)'] == row['Email (username)'], 'Statut'] = 'supprimé'
                            accepted_users.to_excel(accepted_users_file, index=False, engine="openpyxl")
                            st.success("Utilisateur marqué comme supprimé.")
                            st.rerun()
                if not search_email and len(actifs) > 25:
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.info("🔎 Utilisez la barre de recherche pour voir les suivants…")

    # ---- Utilisateurs supprimés ----
    with col_s:
        st.markdown("#### 🗑️ Utilisateurs supprimés")
        supprimes = accepted_users[accepted_users["Statut"] == "supprimé"]
        if search_email:
            supprimes = supprimes[supprimes['Email (username)'].str.lower().str.contains(search_email)]

        def confirmer_reactivation(email):
            @st.dialog("Confirmer la réactivation")
            def dialog():
                st.write(f"Souhaitez-vous vraiment réactiver l'utilisateur {email} ?")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Oui, réactiver"):
                        accepted_users.loc[accepted_users['Email (username)'] == email, 'Statut'] = 'actif'
                        accepted_users.to_excel(accepted_users_file, index=False, engine="openpyxl")
                        st.success("Utilisateur réactivé.")
                        st.rerun()
                with col2:
                    if st.button("❌ Annuler"):
                        st.rerun()
            dialog()

        def confirmer_suppression_definitive(email):
            @st.dialog("Confirmer la suppression définitive")
            def dialog():
                st.write(f"Voulez-vous vraiment supprimer définitivement {email} ? (Cela le rendra invisible mais restera dans le fichier Excel.)")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🗑️ Oui, supprimer définitivement"):
                        # Remplacer le statut par "supprimé_def"
                        accepted_users.loc[accepted_users['Email (username)'] == email, 'Statut'] = 'supprimé_def'
                        accepted_users.to_excel(accepted_users_file, index=False, engine="openpyxl")
                        st.success("Utilisateur supprimé définitivement.")
                        st.rerun()
                with col2:
                    if st.button("❌ Annuler"):
                        st.rerun()
            dialog()

        with st.container(height=300):
            if supprimes.empty:
                st.info("Aucun utilisateur supprimé.")
            else:
                for i, (_, row) in enumerate(supprimes.iterrows()):
                    email = row["Email (username)"]
                    with st.expander(f"{email}"):
                        for field in ["Nom", "Prénom", "Téléphone", "Entreprise", "Rôle", "Email (username)", "Statut"]:
                            if field in row and pd.notna(row[field]):
                                st.write(f"**{field} :** {row[field]}")
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("✅ Réactiver", key=f"reactiver_{i}"):
                                confirmer_reactivation(email)
                        with col2:
                            if st.button("❌ Supprimer définitivement", key=f"delete_final_{i}"):
                                confirmer_suppression_definitive(email)

    url_encoded = f"/app/{urllib.parse.quote(accepted_users_file)}"
    st.markdown(
        f"<a href='{url_encoded}' download='{accepted_users_file}' style='font-size: 16px;'>📥 Télécharger le fichier Excel</a>",
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
