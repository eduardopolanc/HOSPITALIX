import streamlit as st

def login_page():

    button_signup = st.button("sign up")
    button_user = st.button("go to user")
    button_admin = st.button("go to admin")

    if button_admin:
        st.session_state.page = "admin"
        st.rerun()

    if button_signup:
        st.session_state.page = "signup"
        st.rerun()
    if button_user:
        st.session_state.page = "user"
        st.rerun()
