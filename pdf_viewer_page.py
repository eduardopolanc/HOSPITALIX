import streamlit as st

def pdf_viewer_page():

    button_user = st.button("return to user")
    button_admin = st.button("return to admin")

    if button_user:
        st.session_state.page = "user"
        st.rerun()

    if button_admin:
        st.session_state.page = "admin"
        st.rerun()
