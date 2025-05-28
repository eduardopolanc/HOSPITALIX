import streamlit as st
import pandas as pd
import os
import secrets
import string

# Function to generate a secure random password
def generate_password(length=10):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

# This function defines the admin review page
def review_request_page():
    st.title("Revue Admin : Demandes de création de compte")

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

                    if col1.button("✅ Accepter", key=f"accept_{index}"):
                        password = generate_password()

                        nouveau_compte = pd.DataFrame([{
                            "Nom": row["Nom"],
                            "Prenom": row["Prenom"],
                            "Téléphone": row["Téléphone"],
                            "Rôle": row["Rôle"],
                            "Entreprise": row["Entreprise"],
                            "Email": row["Email"],
                            "Mot de passe": password
                        }])

                        if os.path.exists(fichier_comptes):
                            existant = pd.read_excel(fichier_comptes)
                            tous_les_comptes = pd.concat([existant, nouveau_compte], ignore_index=True)
                        else:
                            tous_les_comptes = nouveau_compte

                        tous_les_comptes.to_excel(fichier_comptes, index=False, engine="openpyxl")

                        demandes.drop(index, inplace=True)
                        demandes.to_excel(fichier_demandes, index=False, engine="openpyxl")

                        st.success(f"Compte créé pour {row['Email']} avec mot de passe : {password}")
                        st.rerun()

                    if col2.button("❌ Rejeter", key=f"reject_{index}"):
                        demandes.drop(index, inplace=True)
                        demandes.to_excel(fichier_demandes, index=False, engine="openpyxl")
                        st.warning(f"Demande pour {row['Email']} rejetée.")
                        st.rerun()
    else:
        st.info("Fichier de demandes non trouvé.")

    if st.button("⬅️ Retour", key="back_button"):
        st.session_state.page = "admin"
        st.rerun()

