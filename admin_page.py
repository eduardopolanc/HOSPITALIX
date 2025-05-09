import streamlit as st

def admin_page():
    button_user = st.button("user page")
    button_pdf = st.button("pdf page")
    button_out = st.button("log out")
    

    if button_user:
        st.session_state.page = "user"
        st.rerun()

    if button_pdf:
        st.session_state.page = "viewer"
        st.rerun()

    if button_out:
        st.session_state.page = "login"
        st.rerun()

def user_request():
    button_re = st.button("user's request")
    
    if button_re:
            st.session_state.page = "request"
            st.rerun()