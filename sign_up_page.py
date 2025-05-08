import streamlit as st
import pandas as pd
import os

def sign_up_page():
    st.title("Demande de création de compte")

    nom = st.text_input("Nom")
    prenom = st.text_input("Prénom")
    telephone = st.text_input("Téléphone (facultatif)")
    lieu_travail = st.text_input("Nom de structure de l’entreprise")
    email = st.text_input("Email")

    if st.button("Envoyer la demande"):
        if not (nom and prenom and email and lieu_travail):
            st.warning("Veuillez remplir tous les champs obligatoires.")
        else:
            # Crée un DataFrame avec les infos saisies
            nouvelle_demande = pd.DataFrame([{
                "Nom": nom,
                "Prénom": prenom,
                "Téléphone": telephone,
                "Entreprise": lieu_travail,
                "Email": email
            }])

            # Fichier Excel des demandes (à créer s’il n’existe pas)
            fichier = "demandes_en_attente.xlsx"

            if os.path.exists(fichier):
                ancienne = pd.read_excel(fichier)
                nouvelle = pd.concat([ancienne, nouvelle_demande], ignore_index=True)
            else:
                nouvelle = nouvelle_demande

            nouvelle.to_excel(fichier, index=False)

            st.success("Votre demande a été envoyée avec succès. Vous recevrez un email une fois le compte validé.")

    # Bouton de retour
    if st.button("Retour à la connexion"):
        st.session_state.page = "login"
        st.rerun()
