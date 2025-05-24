import streamlit as st
import pandas as pd
import os

def login_page():
        # Gestion des clics sur les boutons de navigation
    if st.button("Sign up"):
        st.session_state.page = "signup"
        st.rerun()

    if st.button("Go to user"):
        st.session_state.page = "user"
        st.rerun()

    if st.button("Go to admin"):
        st.session_state.page = "admin"
        st.rerun()
    """
    Page de connexion utilisateur.
    L'utilisateur saisit son email et son mot de passe.
    Les identifiants sont vérifiés dans un fichier Excel.
    Possibilité de naviguer vers inscription, utilisateur ou admin via 3 boutons.
    """

    # Titre de la page
    st.title("Page de Connexion")
    # Champs de saisie
    email = st.text_input("Email")
    password = st.text_input("Mot de passe", type="password")

    # Bouton pour se connecter
    if st.button("Se connecter"):
        # Vérification que les champs ne sont pas vides
        if not email or not password:
            st.warning("Merci de remplir à la fois email et mot de passe.")
        else:
            # Vérifier que le fichier Excel existe
            user_file = "accepted_user_information.xlsm"
            if not os.path.exists(user_file):
                st.error("Le fichier des utilisateurs acceptés est introuvable.")
            else:
                # Lire le fichier Excel
                df_users = pd.read_excel(user_file)

                # Rechercher l'utilisateur dans le fichier (colonne "Email")
                user_row = df_users[df_users["Email"] == email]

                if user_row.empty:
                    st.error("Email non trouvé.")
                else:
                    # Récupérer le mot de passe stocké
                    stored_password = user_row.iloc[0]["Password"]

                    # Comparer avec le mot de passe saisi
                    if password == stored_password:
                        st.success("Connexion réussie !")
                        # Modifier la page pour rediriger l'utilisateur
                        st.session_state.page = "user"
                        st.session_state.user_email = email
                        # Recharger la page pour appliquer le changement
                        st.experimental_rerun()
                    else:
                        st.error("Mot de passe incorrect.") 
