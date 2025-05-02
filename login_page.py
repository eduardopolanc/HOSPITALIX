import streamlit as st

def login_page():

    button_signup = st.button("sign up")
    button_user = st.button("login")

    if button_signup:
        st.session_state.page = "signup"
    
    if button_user:
        st.session_state.page = "user"