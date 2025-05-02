import streamlit as st

def sign_up_page():
    button_retur = st.button("return to login")

    if button_retur:
        st.session_state.page = "login"
        st.rerun()
