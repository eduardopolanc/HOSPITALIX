import streamlit as st
import pandas as pd
import os

# Fonction principale de la page d'inscription
def sign_up_page():
    st.title("Demande de création de compte")

    # Champs du formulaire
    nom = st.text_input("Nom")
    prenom = st.text_input("Prénom")
    telephone = st.text_input("Téléphone (optionnel)")
    role = st.text_input("Rôle / Profession")
    entreprise = st.text_input("Nom de l'entreprise")
    email = st.text_input("Email (utilisé comme identifiant)")

    # Quand l'utilisateur soumet le formulaire
    if st.button("Envoyer la demande"):
        if not (nom and prenom and email and role and entreprise):
            st.warning("Veuillez remplir tous les champs obligatoires.")
        else:
            # Créer une ligne avec les infos saisies
            nouvelle_demande = pd.DataFrame([{
                "Nom": nom,
                "Prenom": prenom,
                "Téléphone": telephone,
                "Rôle": role,
                "Entreprise": entreprise,
                "Email": email
            }])

            fichier_demandes = "demandes_en_attente.xlsx"

            # Ajouter à l'existant ou créer un nouveau fichier
            if os.path.exists(fichier_demandes):
                existant = pd.read_excel(fichier_demandes)
                toutes_les_demandes = pd.concat([existant, nouvelle_demande], ignore_index=True)
            else:
                toutes_les_demandes = nouvelle_demande

            toutes_les_demandes.to_excel(fichier_demandes, index=False)
            st.success("Votre demande a été envoyée avec succès.")

    # Bouton de retour à la page de connexion
    if st.button("⬅ Retour à la connexion"):
        st.session_state.page = "login"
        st.rerun()
