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
    st.title("Admin Review: Account Requests")

    # Define paths to data files
    request_file = "demandes_en_attente.xlsx"
    account_file = "accepted_user_information.xlsm"

    # Check if the request file exists
    if os.path.exists(request_file):
        requests = pd.read_excel(request_file)

        if requests.empty:
            st.info("There are no pending requests.")
        else:
            # Loop through each pending request
            for index, row in requests.iterrows():
                with st.expander(f"{row['First Name']} {row['Last Name']} - {row['Email']}"):
                    # Display user-submitted information
                    st.write(f"**Last Name:** {row['Last Name']}")
                    st.write(f"**First Name:** {row['First Name']}")
                    st.write(f"**Phone:** {row['Phone']}")
                    st.write(f"**Role:** {row['Role']}")
                    st.write(f"**Company:** {row['Company']}")
                    st.write(f"**Email:** {row['Email']}")

                    col1, col2 = st.columns(2)

                    # Accept button logic
                    if col1.button(f"✅ Accept - {index}"):
                        password = generate_password()

                        new_account = pd.DataFrame([{
                            "Email (username)": row['Email'],
                            "Password": password
                        }])

                        # Save accepted account to main file
                        if os.path.exists(account_file):
                            existing = pd.read_excel(account_file)
                            all_accounts = pd.concat([existing, new_account], ignore_index=True)
                        else:
                            all_accounts = new_account

                        all_accounts.to_excel(account_file, index=False)

                        # Remove request from pending list
                        requests.drop(index, inplace=True)
                        requests.to_excel(request_file, index=False)

                        st.success(f"Account created for {row['Email']} with password: {password}")
                        st.rerun()

                    # Reject button logic
                    if col2.button(f"❌ Reject - {index}"):
                        requests.drop(index, inplace=True)
                        requests.to_excel(request_file, index=False)
                        st.warning(f"Request for {row['Email']} has been rejected.")
                        st.rerun()
    else:
        st.info("No request file found.")
