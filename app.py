import streamlit as st
from admin_page import admin_page
from login_page import login_page
from sign_up_page import sign_up_page
from user_page import user_page

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
    st.warning("Page not authorized. Redirecting to Login...")
    st.session_state.page = 'login'
