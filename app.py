import streamlit as st
from admin_page import admin_page
from login_page import login_page
from pdf_viewer_page import pdf_viewer_page
from sign_up_page import sign_up_page
from user_page import user_page
from review_request_page import review_request_page

# Redirigir automáticamente a la URL con embed=true si no está presente
if "embed" not in st.query_params:
    js = """
    <script>
    const currentUrl = window.location.href;
    if (!currentUrl.includes("?embed=true")) {
        const cleanUrl = currentUrl.split("?")[0];  // remove any existing query
        window.location.replace(cleanUrl + "?embed=true");
    }
    </script>
    """
    st.markdown(js, unsafe_allow_html=True)
    st.stop()



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
elif page == "viewer":
    pdf_viewer_page()
elif page == "signup":
    sign_up_page()
elif page == "user":
    user_page()
elif page in ["review", "request"]:
    review_request_page()
else:
    st.warning("Page not authorized. Redirecting to Login...")
    st.session_state.page = 'login'
