import os
import re
import xlrd
import difflib
import streamlit as st
import logging
import time
from pytrends.request import TrendReq
import script.fonction.fonction as fonction
from openpyxl import load_workbook
from fpdf import FPDF
import base64
from script.pdf.pdf_generator import Make_pdf
from datetime import datetime as dt

def user_page():
  File_name1 = "/data/copie_windows/version Windows alix02/Desktop/ALIX_APP/script/fonction/Fiche1.txt"
  File_name2 = "/data/copie_windows/version Windows alix02/Desktop/ALIX_APP/script/fonction/Fiche2.txt"
  v1,v2,v3,v4,v5='Z','Z','Z','Z','Z'

  memory_fiche1 = open(File_name1,encoding='utf-8').readlines()
  memory_fiche2 = open(File_name2,encoding='utf-8').readlines()

  st.sidebar.title('Choose')
  list_contexte=st.sidebar.multiselect('Santé/contexte',('mémoire','santé','surendettement','maltraitance','internet','tuteur','rien','plus disponible','pas habitude papier','indifférent'))
  list_varaibale_situ_perso=st.sidebar.selectbox('Situation perso	',('Seule','Veuf', 'Divorce','Conjoint pas autonome','Conjoint autonome','indifférent'))
  list_aidant=st.sidebar.selectbox('Famille',('famille proche','famille éloignée','autre','aucun','plus disponible','indifférent'))
  list_patrimoine=st.sidebar.selectbox('Patrimoine',('Faible','moyen','important','gestion pat','indifférent'))
  list_relation=st.sidebar.multiselect('Qualité relation/pb gestion	',('bonnes relations','relation tendues','admin','budget','suivi med','aucun pb','gestion pat','indifférent'))


  context = []
  context.append(list_contexte)
  context.append(list_varaibale_situ_perso)
  context.append(list_aidant)
  context.append(list_patrimoine)
  context.append(list_relation)

  array_vchoisi =[]
  array_contexte=[]
  array_relation=[]

  v1 = [fonction.val_contexte2(x) for x in list_contexte] 
  array_vchoisi.append(v1)

  v2 = fonction.val_situ_perso2(list_varaibale_situ_perso)
  array_vchoisi.append(v2[0])

  v3 = fonction.val_aidant2(list_aidant)
  array_vchoisi.append(v3[0])

  v4 = fonction.val_patrimoine2(list_patrimoine)
  array_vchoisi.append(v4[0])

  v5 = [fonction.val_relation2(x) for x in list_relation]
  array_vchoisi.append(v5)

  if(st.button("Click to display the form")): 
    st.title('Code fiche :')
    st.write(v1,v2,v3,v4,v5)
    if (len(v1)>1) or (len(v5)>1):
      fonction.generate(array_vchoisi,File_name1)
      fonction.generate_with_regle(array_vchoisi,File_name2)
      fiche1 = open(File_name1,encoding='utf-8').readlines()
      fiche2 = open(File_name2,encoding='utf-8').readlines()
      st.title('Fiche sans regle:')
      st.write(fiche1)
      st.title('Fiche avec regle:')
      st.write(fiche2)
      memory_fiche1 = fiche1
      memory_fiche2 = fiche2
    else:
      fonction.generate(array_vchoisi,File_name2)
      fiche2 = open(File_name2,encoding='utf-8').readlines()
      st.title('Fiche simple:')
      st.write(fiche2)

      memory_fiche2 = fiche2



  st.write('Commentaire')
  title = st.text_input('Commentaire', '')

  v1 = fonction.recup_variable_com(v1)
  v2 = fonction.recup_variable_com(v2)
  v3 = fonction.recup_variable_com(v3)
  v4 = fonction.recup_variable_com(v4)
  v5 = fonction.recup_variable_com(v5)

  if(st.button("ajouter le commentaire")):
    com =[dt.now(),'Code fiche :',v1, v2, v3, v4, v5,title]
    file = "Commentaire.xlsx"
    wb = load_workbook(file)
    ws = wb["Com"]
    ws.append(com)
    wb.save(file)


  export_as_pdf = st.button("Export Report")

  def create_download_link(val, filename):
      b64 = base64.b64encode(val)  # val looks like b'...'
      return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{filename}.pdf">Download file</a>'


  if export_as_pdf:

      pdf = Make_pdf(File_name2,context)

      html = create_download_link(pdf.output(dest='S').encode('latin-1','ignore'),filename='FICHE AUTOMATISEE D’INFORMATIONS PERSONNALISEES')

      st.markdown(html, unsafe_allow_html=True)

      if st.button("view PDF"):
         st.session_state.page = "viewer"
      if st.button("go to admin"):
         st.session_state.page = "admin"

       
