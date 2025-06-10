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
    if os.path.exists(pdf_folder):
        pdf_files = sorted([f for f in os.listdir(pdf_folder) if f.endswith(".pdf")], reverse=True)

        # Filtrar por texto si se busca algo
        if search_term:
            pdf_files = [f for f in pdf_files if search_term.lower() in f.lower()]

        if not pdf_files:
            st.info("Aucun PDF trouvé.")
        else:
            with st.container(height=300):
                for filename in pdf_files[:50]:
                    st.markdown('<hr style="margin: 6px 0;">', unsafe_allow_html=True)
                    col1, col2, col3 = st.columns([3, 1, 1])

                    with col1:
                        st.markdown(
                            f"""
                            <div style="font-size: 30px; margin: 0; padding: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 100%; display: inline-block;" title="{filename}">
                                📄 <b>{filename}</b>
                            </div>
                            """, unsafe_allow_html=True)
 
                    with col2:
                        file_path = os.path.join(pdf_folder, filename)
                        with open(file_path, "rb") as f:
                            st.download_button("⬇️ Télécharger", f, file_name=filename, mime="application/pdf")

                    with col3:
                        if st.button("👁️ Voir", key=f"voir_{filename}"):
                            pdf_url = f"/app/static/pdf_reports/{urllib.parse.quote(filename)}"
                            js = f"""
                                <script>
                                window.open("{pdf_url}", "_blank").focus();
                                </script>
                            """
                            st.markdown(js, unsafe_allow_html=True)
                    st.markdown('<hr style="margin: 6px 0;">', unsafe_allow_html=True)

    if st.button("Generer un PDF"):
        st.session_state.page = "user"
        st.rerun()

    # --- Estado inicial necesario ---
    if "selected_user_type" not in st.session_state:
        st.session_state.selected_user_type = None  # "accepted" or "pending"
    if "selected_user_data" not in st.session_state:
        st.session_state.selected_user_data = None

    # --- Input de búsqueda compartido ---
    search_email = st.text_input("🔍 Rechercher un utilisateur (email)").strip().lower()

    col1, col2 = st.columns([2, 3])

    # --- Columna izquierda ---
    with col1:
        st.markdown("### ✅ Utilisateurs existants")

        accepted_users = pd.read_excel("accepted_user_information.xlsm") if os.path.exists("accepted_user_information.xlsm") else pd.DataFrame()
        if search_email:
            accepted_users = accepted_users[accepted_users['Email (username)'].str.lower().str.contains(search_email)]

        # Scroll para usuarios aceptados
        with st.container():
            with st.expander("Afficher les utilisateurs existants", expanded=True):
                scroll_container_style = """
                <style>
                .scroll-box {
                    max-height: 300px;
                    overflow-y: auto;
                    padding-right: 8px;
                }
                </style>
                <div class="scroll-box">
                """
                st.markdown(scroll_container_style, unsafe_allow_html=True)
                for i, (_, row) in enumerate(accepted_users.iterrows()):
                    if st.button(f"{row['Email (username)']}", key=f"accepted_{i}"):
                        st.session_state.selected_user_type = "accepted"
                        st.session_state.selected_user_data = row.to_dict()
                st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### 🕒 Demandes en attente")

        requests = pd.read_excel("demandes_en_attente.xlsx") if os.path.exists("demandes_en_attente.xlsx") else pd.DataFrame()
        if search_email:
            requests = requests[requests['Email'].str.lower().str.contains(search_email)]

        with st.container():
            with st.expander("Afficher les demandes en attente", expanded=True):
                st.markdown(scroll_container_style, unsafe_allow_html=True)
                for i, (_, row) in enumerate(requests.iterrows()):
                    if st.button(f"{row['Email']}", key=f"pending_{i}"):
                        st.session_state.selected_user_type = "pending"
                        st.session_state.selected_user_data = row.to_dict()
                st.markdown("</div>", unsafe_allow_html=True)

    # --- Columna derecha ---
    with col2:
        if st.session_state.selected_user_data:
            user = st.session_state.selected_user_data
            user_type = st.session_state.selected_user_type

            if user_type == "accepted":
                st.markdown("### 👤 Détails de l'utilisateur accepté")
                st.write(f"**Email :** {user.get('Email (username)', '')}")
                st.write(f"**Mot de passe :** {user.get('Password', '')}")

                if st.button("🗑️ Supprimer l'utilisateur"):
                    accepted_users = accepted_users[accepted_users['Email (username)'] != user['Email (username)']]
                    accepted_users.to_excel("accepted_user_information.xlsm", index=False)
                    st.success("Utilisateur supprimé.")
                    st.session_state.selected_user_data = None
                    st.rerun()

            elif user_type == "pending":
                st.markdown("### ✉️ Détails de la demande d'inscription")
                st.write(f"**Nom :** {user.get('Nom')}")
                st.write(f"**Prénom :** {user.get('Prenom')}")
                st.write(f"**Téléphone :** {user.get('Téléphone')}")
                st.write(f"**Entreprise :** {user.get('Entreprise')}")
                st.write(f"**Rôle :** {user.get('Rôle')}")
                st.write(f"**Email :** {user.get('Email')}")

                colA, colB = st.columns(2)
                with colA:
                    if st.button("✅ Accepter la demande"):
                        password = generate_password()
                        new_account = pd.DataFrame([{
                            "Email (username)": user['Email'],
                            "Password": password
                        }])

                        if os.path.exists("accepted_user_information.xlsm"):
                            existing = pd.read_excel("accepted_user_information.xlsm")
                            all_accounts = pd.concat([existing, new_account], ignore_index=True)
                        else:
                            all_accounts = new_account

                        all_accounts.to_excel("accepted_user_information.xlsm", index=False)

                        requests = requests[requests['Email'] != user['Email']]
                        requests.to_excel("demandes_en_attente.xlsx", index=False)

                        st.success("Utilisateur accepté.")
                        st.session_state.selected_user_data = None
                        st.rerun()

                with colB:
                    if st.button("❌ Rejeter la demande"):
                        requests = requests[requests['Email'] != user['Email']]
                        requests.to_excel("demandes_en_attente.xlsx", index=False)
                        st.warning("Demande rejetée.")
                        st.session_state.selected_user_data = None
                        st.rerun()
        else:
            st.info("Sélectionnez un utilisateur dans la colonne de gauche pour voir les détails.")
