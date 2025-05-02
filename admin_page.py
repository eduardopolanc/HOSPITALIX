import streamlit as st

def admin_page():
    button_user = st.button("user page")
    button_pdf = st.button("pdf page")
    button_out = st.button("log out")

    if button_user:
        st.session_state.page = "user"
    if button_pdf:
        st.session_state.page = "viewer"
    if button_out:
        st.session_state.page = "login"