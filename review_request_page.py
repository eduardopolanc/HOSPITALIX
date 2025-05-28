import streamlit as st
import pandas as pd
import os
import secrets
import string

# Fonction pour générer un mot de passe sécurisé aléatoire
def generate_password(length=10):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

# Fonction principale de la page d'administration
def review_request_page():
    st.title("Demandes d'inscription")

    fichier_demandes = "demandes_en_attente.xlsx"
    fichier_comptes = "accepted_user_information.xlsx"

    if os.path.exists(fichier_demandes):
        demandes = pd.read_excel(fichier_demandes)

        if demandes.empty:
            st.info("Aucune demande en attente.")
        else:
            for index, row in demandes.iterrows():
                with st.expander(f"{row['Nom']} {row['Prenom']} - {row['Email']}"):
                    st.write(f"**Nom :** {row['Nom']}")
                    st.write(f"**Prénom :** {row['Prenom']}")
                    st.write(f"**Téléphone :** {row['Téléphone']}")
                    st.write(f"**Rôle :** {row['Rôle']}")
                    st.write(f"**Entreprise :** {row['Entreprise']}")
                    st.write(f"**Email :** {row['Email']}")

                    col1, col2 = st.columns(2)

                    # Bouton Accepter
                    if col1.button("✅ Accepter", key=f"accepter_{index}"):
                        mot_de_passe = generate_password()

                        nouveau_compte = pd.DataFrame([{
                            "Nom": row["Nom"],
                            "Prenom": row["Prenom"],
                            "Entreprise": row["Entreprise"],
                            "Email": row["Email"],
                            "Mot de passe": mot_de_passe
                        }])

                        # Enregistrement du compte accepté
                        if os.path.exists(fichier_comptes):
                            existant = pd.read_excel(fichier_comptes)
                            tous_les_comptes = pd.concat([existant, nouveau_compte], ignore_index=True)
                        else:
                            tous_les_comptes = nouveau_compte

                        tous_les_comptes.to_excel(fichier_comptes, index=False)

                        # Supprimer la demande traitée
                        demandes.drop(index, inplace=True)
                        demandes.to_excel(fichier_demandes, index=False)

                        st.success(f"Compte créé pour {row['Email']} avec le mot de passe : {mot_de_passe}")
                        st.rerun()

                    # Bouton Rejeter
                    if col2.button("❌ Rejeter", key=f"rejeter_{index}"):
                        demandes.drop(index, inplace=True)
                        demandes.to_excel(fichier_demandes, index=False)
                        st.warning(f"La demande pour {row['Email']} a été rejetée.")
                        st.rerun()

    else:
        st.info("Fichier de demandes introuvable.")

    # Bouton de retour
    if st.button("⬅ Retour", key="bouton_retour"):
        st.session_state.page = "admin"
        st.rerun()
