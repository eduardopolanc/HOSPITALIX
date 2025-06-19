import streamlit as st
st.set_page_config(layout="wide")
from admin_page import admin_page
from login_page import login_page
from sign_up_page import sign_up_page
from user_page import user_page

# ➕ Appliquer le style global pour enlever le header/padding Streamlit
st.markdown("""
    <style>
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container {
        padding-top: 1rem !important;
    }
    </style>
""", unsafe_allow_html=True)

# Session state defaults
if 'page' not in st.session_state:
    st.session_state.page = "login"
if "autentication" not in st.session_state:
    st.session_state.autentication = False

page = st.session_state.page

# Navigation
if page == "login":
    login_page()
elif page == "admin":
    admin_page()
elif page == "signup":
    sign_up_page()
elif page == "user":
    user_page()
else:
    st.warning("Page non autorisée. Redirection vers la connexion...")
    st.session_state.page = 'login'
