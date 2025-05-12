import streamlit as st
import os
import pandas as pd
import base64

def admin_page():
    st.set_page_config(layout="wide") # Opcional: hace que la columna izquierda tenga más espacio útil
    cola, cols, cold = st.columns([2,2,2])
    with cols:
        st.markdown("<h1 style='text-align: center;'>Admin Page</h1>", unsafe_allow_html=True)
    with cold:
        colq, colw = st.columns([2,2])
        with colw:
            if st.button("log out"):
                st.session_state.page = "login"
                st.rerun()

    # Leer solicitudes pendientes
    request_file = "demandes_en_attente.xlsx"
    requests = pd.DataFrame()
    if os.path.exists(request_file):
        try:
            requests = pd.read_excel(request_file)
        except:
            st.error("Erreur lors du chargement du fichier de demandes.")

    # Crear columnas: izquierda = navegación + solicitudes, derecha vacía
    col1, col2  = st.columns([2, 6])  # más ancho el contenido, menos margen
    with col1:
        st.markdown("#### <small>Demandes d'inscription</small>", unsafe_allow_html=True)
        st.markdown("---")
        if not requests.empty:
            for index, row in requests.iterrows():
                with st.expander(f"{row['First Name']} {row['Last Name']} - {row['Email']}"):
                    st.write(f"**Last Name:** {row['Last Name']}")
                    st.write(f"**First Name:** {row['First Name']}")
                    st.write(f"**Phone:** {row['Phone']}")
                    st.write(f"**Role:** {row['Role']}")
                    st.write(f"**Company:** {row['Company']}")
                    st.write(f"**Email:** {row['Email']}")
        else:
            st.info("Aucune demande en attente.")
    with col2:
        pdf_folder = "pdf_reports"

        st.subheader("📄 PDF générés")

        if os.path.exists(pdf_folder):
            pdf_files = sorted(
                [f for f in os.listdir(pdf_folder) if f.endswith(".pdf")],
                reverse=True
            )

            if not pdf_files:
                st.info("Aucun PDF trouvé.")
            else:
                links_html = ""
                for filename in pdf_files:
                    file_path = os.path.join(pdf_folder, filename)
                    with open(file_path, "rb") as f:
                        b64 = base64.b64encode(f.read()).decode()
                        link = f'<a href="data:application/pdf;base64,{b64}" download="{filename}" target="_blank" style="color: #00CFFF;">📄 {filename}</a>'
                        links_html += f"<div style='margin-bottom: 10px;'>{link}</div>"

                # Inserta HTML con scroll interno real
                st.components.v1.html(f"""
                    <div style="
                        background-color: #2e2e2e;
                        padding: 15px;
                        border-radius: 10px;
                        max-height: 250px;
                        overflow-y: auto;
                        color: white;
                    ">
                        {links_html}
                    </div>
                """, height=270)
        else:
            st.warning("Le dossier des PDF n'existe pas.")

    col4, col5, col6, col7 = st.columns([2,2,2,2])

    with col4:
        if st.button("user page"):
            st.session_state.page = "user"
            st.rerun()
    with col5:
        if st.button("pdf page"):
            st.session_state.page = "viewer"
            st.rerun()
    with col7:
        if st.button("user's request"):
            st.session_state.page = "request"
            st.rerun()