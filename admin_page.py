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

def render_scrollable_user_list(users, user_type, selected_email, key_prefix):
    container_html = """
    <div style="max-height: 300px; overflow-y: auto; padding-right: 6px;">
    """

    for i, (_, row) in enumerate(users.iterrows()):
        email = row['Email (username)'] if user_type == "accepted" else row['Email']
        safe_email = email.replace('"', '&quot;').replace("'", "&#39;")
        selected = (selected_email == email)

        style = f"""
            background-color: {'#ffdddd' if selected else '#222'};
            color: white;
            padding: 8px 12px;
            border: 1px solid {'#cc0000' if selected else '#555'};
            border-radius: 6px;
            margin-bottom: 6px;
            cursor: pointer;
            font-family: sans-serif;
        """

        js_callback = f"""
        <script>
        const data = {{type: '{user_type}', email: '{urllib.parse.quote(email)}'}};
        fetch(window.location.href, {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify(data)
        }}).then(() => window.location.reload());
        </script>
        """

        container_html += f"""
            <div style="{style}" onclick="document.dispatchEvent(new Event('select_{key_prefix}_{i}'))">
                {safe_email}
            </div>
            <script>
                document.addEventListener('select_{key_prefix}_{i}', function() {{
                    {js_callback}
                }});
            </script>
        """

    container_html += "</div>"
    return container_html


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
    st.set_page_config(layout="wide")
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
    account_file = "accepted_user_information.xlsm"
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


    cole, colr = st.columns([2,4])

    with cole:
        st.markdown("### 👥 Gestion des utilisateurs")
    with colr:
        search_email = st.text_input("🔍 Rechercher un utilisateur (email)").strip().lower()

    col_accepted, col_pending = st.columns(2)

    # ---- Utilisateurs acceptés ----
    with col_accepted:
        st.markdown("#### ✅ Utilisateurs acceptés")
        accepted_users = pd.read_excel("accepted_user_information.xlsm") if os.path.exists("accepted_user_information.xlsm") else pd.DataFrame()

        if search_email:
            filtered_accepted = accepted_users[accepted_users['Email (username)'].str.lower().str.contains(search_email)]
        else:
            filtered_accepted = accepted_users.head(25)

        with st.container(height=300):
            if filtered_accepted.empty:
                st.info("Aucun utilisateur trouvé.")
            else:
                for i, (_, row) in enumerate(filtered_accepted.iterrows()):
                    with st.expander(f"{row['Email (username)']}"):
                        for field in ["Nom", "Prenom", "Téléphone", "Entreprise", "Rôle", "Email (username)"]:
                            if field in row and pd.notna(row[field]):
                                st.write(f"**{field} :** {row[field]}")
                        if st.button("🗑️ Supprimer", key=f"delete_user_{i}"):
                            accepted_users = accepted_users[accepted_users['Email (username)'] != row['Email (username)']]
                            accepted_users.to_excel("accepted_user_information.xlsm", index=False)
                            st.success("Utilisateur supprimé.")
                            st.rerun()
                # Message en bas
                if not search_email and len(accepted_users) > 25:
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.info("🔎 Utilisez la barre de recherche pour voir les suivants…")

    # ---- Demandes en attente ----
    with col_pending:
        st.markdown("#### 🕒 Demandes en attente")
        requests = pd.read_excel("demandes_en_attente.xlsx") if os.path.exists("demandes_en_attente.xlsx") else pd.DataFrame()

        if search_email:
            filtered_requests = requests[requests['Email'].str.lower().str.contains(search_email)]
        else:
            filtered_requests = requests.head(2)

        with st.container(height=300):
            if filtered_requests.empty:
                st.info("Aucune demande trouvée.")
            else:
                for i, (_, row) in enumerate(filtered_requests.iterrows()):
                    with st.expander(f"{row['Email']}"):
                        for field in ["Nom", "Prenom", "Téléphone", "Entreprise", "Rôle", "Email"]:
                            if field in row and pd.notna(row[field]):
                                st.write(f"**{field} :** {row[field]}")
                        colA, colB = st.columns(2)
                        with colA:
                            if st.button("✅ Accepter", key=f"accept_{i}"):
                                password = generate_password()
                                new_account = pd.DataFrame([{
                                    "Nom": row.get("Nom", ""),
                                    "Prenom": row.get("Prenom", ""),
                                    "Téléphone": row.get("Téléphone", ""),
                                    "Entreprise": row.get("Entreprise", ""),
                                    "Rôle": row.get("Rôle", ""),
                                    "Email (username)": row["Email"],
                                    "Password": password
                                }])
                                if os.path.exists("accepted_user_information.xlsm"):
                                    existing = pd.read_excel("accepted_user_information.xlsm")
                                    all_accounts = pd.concat([existing, new_account], ignore_index=True)
                                else:
                                    all_accounts = new_account
                                all_accounts.to_excel("accepted_user_information.xlsm", index=False)

                                requests = requests[requests['Email'] != row['Email']]
                                requests.to_excel("demandes_en_attente.xlsx", index=False)
                                st.success("Utilisateur accepté.")
                                st.rerun()
                        with colB:
                            if st.button("❌ Rejeter", key=f"reject_{i}"):
                                requests = requests[requests['Email'] != row['Email']]
                                requests.to_excel("demandes_en_attente.xlsx", index=False)
                                st.warning("Demande rejetée.")
                                st.rerun()
                # Message en bas
                if not search_email and len(requests) > 25:
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.info("🔎 Utilisez la barre de recherche pour voir les suivants…")

    st.markdown("---")
    st.markdown("### 📊 Statistiques générales")

    # Charger les données
    accepted_users = pd.read_excel("accepted_user_information.xlsm") if os.path.exists("accepted_user_information.xlsm") else pd.DataFrame()
    requests = pd.read_excel("demandes_en_attente.xlsx") if os.path.exists("demandes_en_attente.xlsx") else pd.DataFrame()
    pdf_folder = "static"
    pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith(".pdf")] if os.path.exists(pdf_folder) else []

    # Compter
    nb_users = len(accepted_users)
    nb_requests = len(requests)
    nb_pdfs = len(pdf_files)

    # Affichage
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("👤 Utilisateurs enregistrés", nb_users)
    with col2:
        st.metric("⏳ Demandes en attente", nb_requests)
    with col3:
        st.metric("📄 PDFs générés", nb_pdfs)
