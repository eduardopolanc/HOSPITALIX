
import pandas as pd
import xlrd
import difflib
import numpy as np
import script.fonction.fonction_regle as fr

df_app = pd.read_excel(r"/data/copie_windows/version Windows alix02/Desktop/ALIX_APP/ALIX_4.0.xlsm",sheet_name='Concordance' ,engine='openpyxl')


def val_relation2(variable):
  '''
  Fonction pour récupèrer la lettre associée au critère choisi par le patient pour la section "Qualité relation/pb gestion".  
  Etant donné qu'il peut y avoir plusieurs sélections, l'output sera la première lettre de l'array pour chaque critère. 
  output: première lettre associée au critère choisi
  '''
  vrelation= df_app['Qualité relation/pb gestion'].loc[df_app['Unnamed: 9'] == variable]
  vrelation = vrelation.reset_index(drop=True)
  return vrelation[0]

def val_patrimoine2(variable): 
  '''
  Fonction pour récupèrer la lettre associée au critère choisi par le patient pour la section "patrimoine".  
  output: la lettre associée au critère choisi 
  '''
  vpatrimoine = df_app['Patrimoine'].loc[df_app['Unnamed: 7'] == variable]
  vpatrimoine = vpatrimoine.reset_index(drop=True)
  return vpatrimoine 

def val_aidant2(variable): 
  '''
  Fonction pour récupèrer la lettre associée au critère choisi par le patient pour la section "Patrimoine".  
  output: lettre associée au critère choisi
  '''
  vfamille = df_app['Famille'].loc[df_app['Unnamed: 5'] == variable]
  vfamille= vfamille.reset_index(drop=True)
  return vfamille

def val_contexte2(variable): 
  '''
  Fonction pour récupèrer la lettre associée au critère choisi par le patient pour la section "Santé/contexte".  
  Etant donné qu'il peut y avoir plusieurs sélections, l'output sera la première lettre de l'array pour chaque critère. 
  output: première lettre associée au critère choisi
  '''
  vsante = df_app['Santé/contexte'].loc[df_app['Unnamed: 3'] == variable]
  vsante= vsante.reset_index(drop=True)
  return vsante[0]
  
def val_situ_perso2(variable): 
  '''
  Fonction pour récupèrer la lettre associée au critère choisi par le patient pour la section "Situation perso".  
  output: lettre associée au critère choisi
  '''
  vsituation = df_app['Situation perso'].loc[df_app['Unnamed: 1'] == variable]
  vsituation = vsituation.reset_index(drop=True)
  return vsituation

def recup_variable_com( variable):
  '''
  fonction pour joindre toutes les lettres en fonction de chaque critère 
  output: Toutes les lettres pour chaque critère 
  '''
  variable = ''.join([str(item) for item in variable])
  return variable 


def rajout_Z (array_choisi): 
  '''
  rajout de la lettre 'Z' sur chaque liste 
  output: liste de tous les critères avec la lettre 'Z'
  '''
  if isinstance(array_choisi, list)== True:
    array_choisi.append('Z')
    liste = array_choisi
  else : 
    liste = ['Z']
    liste.append(array_choisi)
  return liste
 

def generate(array_nbr,name_file):  
  list_contexte = rajout_Z(array_nbr[0])
  list_varaibale_situ_perso = rajout_Z(array_nbr[1])
  list_aidant = rajout_Z(array_nbr[2])
  list_patrimoine = rajout_Z(array_nbr[3])
  list_relation = rajout_Z(array_nbr[4])


  df_CVv = pd.read_excel("ALIX_4.0.xlsm",sheet_name='Célibataire-Veuf variable' ,engine='openpyxl')

  #cf fonction_regle.py 
  contexte = [df_CVv['Variable B, contexte ou situations particulières'].str.contains(x) for x in list_contexte]
  situ_perso = [df_CVv['variable situation personnelle'].str.contains(x) for x in list_varaibale_situ_perso]
  aidant = [df_CVv['variable aidant'].str.contains(x) for x in list_aidant]
  patrimoine = [df_CVv['Variable Patrimoine / pb gestion'].str.contains(x) for x in list_patrimoine]
  relation = [df_CVv['Variable qualité des relations / pb gestion'].str.contains(x) for x in list_relation]
  
  #cf fonction_regle.py
  df_situ_perso = pd.DataFrame(situ_perso).transpose()
  df_contexte = pd.DataFrame(contexte).transpose()
  df_aidant = pd.DataFrame(aidant).transpose()
  df_patrimoine = pd.DataFrame(patrimoine).transpose()
  df_relation= pd.DataFrame(relation).transpose()
  
  #cf fonction_regle.py 
  df_situ_perso['somme'] = df_situ_perso.sum(axis=1) 
  df_contexte['somme'] = df_contexte.sum(axis=1) 
  df_aidant['somme'] = df_aidant.sum(axis=1) 
  df_patrimoine['somme'] = df_patrimoine.sum(axis=1) 
  df_relation['somme'] = df_relation.sum(axis=1)
  
  #cf fonction_regle.py 
  fiche = df_CVv['Unnamed: 0'].loc[(df_situ_perso['somme'] >= 1) & \
            (df_contexte['somme'] >= 1)& \
            (df_aidant['somme'] >=1) & \
            (df_patrimoine['somme']>=1) & \
            (df_relation['somme']>=1)]

  f = fiche.copy().dropna()

  f.to_csv(name_file, header = False,index= False,encoding="utf-8")


def generate_with_regle(array_nbr,name_file):

  df_CVv = fr.load_file("/data/copie_windows/version Windows alix02/Desktop/ALIX_APP/ALIX_4.0.xlsm", sheet_name = 'Célibataire-Veuf variable')
  df_substitution = fr.load_substitution("/data/copie_windows/version Windows alix02/Desktop/ALIX_APP/ALIX_4.0.xlsm", sheet_name = 'tableau_substitution')
  df_ordre = fr.load_ordre("ALIX_4.0.xlsm", sheet_name = 'tableau_ordre')

  list_contexte = rajout_Z(array_nbr[0])
  list_varaibale_situ_perso = rajout_Z(array_nbr[1])
  list_aidant = rajout_Z(array_nbr[2])
  list_patrimoine = rajout_Z(array_nbr[3])
  list_relation = rajout_Z(array_nbr[4])
  
  #cf fonction_regle.py 
  df_contexte, df_situ_perso, df_aidant, df_patrimoine, df_relation = fr.concatenation_list(df_CVv,list_varaibale_situ_perso,list_contexte,list_aidant,list_patrimoine,list_relation)
  df_contexte, df_situ_perso, df_aidant, df_patrimoine, df_relation = fr.df_transpose(df_contexte,df_situ_perso,df_aidant,df_patrimoine,df_relation)
  
  #cf fonction_regle.py 
  df_situ_perso['somme'] = df_situ_perso.sum(axis=1) 
  df_contexte['somme'] = df_contexte.sum(axis=1) 
  df_aidant['somme'] = df_aidant.sum(axis=1) 
  df_patrimoine['somme'] = df_patrimoine.sum(axis=1) 
  df_relation['somme'] = df_relation.sum(axis=1)

  #cf fonction_regle.py 
  fiche = fr.generate_fiche(df_CVv,df_contexte, df_situ_perso, df_aidant, df_patrimoine, df_relation)
  fiche = fr.regle_substitution(fiche, df_substitution,df_CVv)
  fiche = fr.regle_exclusion(fiche)
  fiche = fr.regle_ordre(fiche, df_ordre)
  fiche["Unnamed: 0"].to_csv(name_file, header = False,index= False , encoding="utf-8")
  #fr.fiche_to_csv(fiche)




