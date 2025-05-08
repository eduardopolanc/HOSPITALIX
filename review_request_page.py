import streamlit as st
import pandas as pd
import os
import secrets
import string

# 🔐 Function to generate a random password (default length: 10 characters)
def generate_password(length=10):
    alphabet = string.ascii_letters + string.digits  # Includes uppercase, lowercase letters and digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))  # Randomly select characters

# 🌐 Main admin review page
def review_request_page():
    st.title("User Sign-Up Requests Validation")

    # Define file paths
    demandes_file = "demandes_en_attente.xlsx"  # Contains pending user registration requests
    comptes_file = "ALIX_4.0.xlsm"              # Will store only accepted users' email and password

    # Check if there are pending requests
    if os.path.exists(demandes_file):
        demandes = pd.read_excel(demandes_file)

        # If there are no requests
        if demandes.empty:
            st.info("No registration requests to review.")
        else:
            # Loop through each pending request
            for index, row in demandes.iterrows():
                with st.expander(f"{row['Prénom']} {row['Nom']} - {row['Email']}"):
                    # Show the user's submitted information for admin to review
                    st.write(f"**Last name:** {row['Nom']}")
                    st.write(f"**First name:** {row['Prénom']}")
                    st.write(f"**Phone:** {row['Téléphone']}")
                    st.write(f"**Role / Profession:** {row['Rôle']}")
                    st.write(f"**Company name:** {row['Entreprise']}")
                    st.write(f"**Email (used as login):** {row['Email']}")

                    # Display Accept and Reject buttons side by side
                    col1, col2 = st.columns(2)

                    # ✅ If the admin clicks "Accept"
                    if col1.button(f"✅ Accept - {index}"):
                        # Generate a random password
                        mot_de_passe = generate_password()

                        # Create a new account record with email and password only
                        nouveau_compte = {
                            "Email (username)": row['Email'],
                            "Password": mot_de_passe
                        }

                        # Save this new account to the final Excel file
                        if os.path.exists(comptes_file):
                            anciens = pd.read_excel(comptes_file)
                            comptes = pd.concat([anciens, pd.DataFrame([nouveau_compte])], ignore_index=True)
                        else:
                            comptes = pd.DataFrame([nouveau_compte])

                        comptes.to_excel(comptes_file, index=False)  # Save accepted user credentials

                        # Remove the accepted request from pending list
                        demandes.drop(index, inplace=True)
                        demandes.to_excel(demandes_file, index=False)

                        # Show success message with password (admin can send it to user)
                        st.success(f"✅ Account created for {row['Email']}, password: {mot_de_passe}")
                        st.rerun()  # Refresh the page to update list

                    # ❌ If the admin clicks "Reject"
                    if col2.button(f"❌ Reject - {index}"):
                        demandes.drop(index, inplace=True)  # Just remove the request
                        demandes.to_excel(demandes_file, index=False)
                        st.warning(f"❌ Request rejected for {row['Email']}")
                        st.rerun()
    else:
        st.info("No pending registration request file found.")
