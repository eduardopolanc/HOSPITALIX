#Import des librairies
import pandas as pd
import xlrd
import difflib
import numpy as np



#Charger le fichier excel

def load_file(filename, sheet_name = 'Célibataire-Veuf variable'):
    """
    Charge le fichier excel donné 
    output : retourne un dataframe
    """
    df = pd.read_excel(filename, sheet_name=sheet_name, engine='openpyxl')
    return df
    
def load_substitution(filename, sheet_name = 'tableau_substitution'):
    """
    Charge la fiche excel contenant les règles de substitution
    output: retourne un dataframe
    """
    df_substitution = pd.read_excel(filename, sheet_name=sheet_name ,engine='openpyxl')
    return df_substitution

def load_ordre(filename, sheet_name = 'tableau_ordre'):
    """
    Charge la fiche excel contenant les règles d'ordre
    output : retourne un dataframe
    """
    df_ordre = pd.read_excel(filename, sheet_name=sheet_name, engine='openpyxl')
    return df_ordre

def concatenation_list(df_CVv,list_variable_situ_perso,list_contexte,list_aidant,list_patrimoine,list_relation):
    """
    Regarde si la variable de la situtation est dans tel ou tel ligne si la variable est contenu dans la ligne retourne True sinon False.
    output : 5 listes 
    """
    contexte = [df_CVv['Variable B, contexte ou situations particulières'].str.contains(x) for x in list_contexte]
    situ_perso = [df_CVv['variable situation personnelle'].str.contains(x) for x in list_variable_situ_perso]
    aidant = [df_CVv['variable aidant'].str.contains(x) for x in list_aidant]
    patrimoine = [df_CVv['Variable Patrimoine / pb gestion'].str.contains(x) for x in list_patrimoine]
    relation = [df_CVv['Variable qualité des relations / pb gestion'].str.contains(x) for x in list_relation]
    return contexte, situ_perso, aidant, patrimoine, relation

def df_transpose(contexte, situ_perso, aidant, patrimoine, relation):
    """
    Transpoe les différentes listes transformé en dataframe
    output : retourne 5 dataframes
    """
    df_contexte = pd.DataFrame(contexte).transpose()
    df_situ_perso = pd.DataFrame(situ_perso).transpose()
    df_aidant = pd.DataFrame(aidant).transpose()
    df_patrimoine = pd.DataFrame(patrimoine).transpose()
    df_relation= pd.DataFrame(relation).transpose()    
    return df_contexte, df_situ_perso, df_aidant, df_patrimoine, df_relation

def sum_axis(list_dataframes):
    """
    Somme les lignes entre elle true =1 false = 0
    output : liste de dataframes
    """
    for df in list_dataframes:
        df['somme'] = df.sum(axis=1) 
    return list_dataframes

def generate_fiche(df, df_contexte, df_situ_perso, df_aidant, df_patrimoine, df_relation):  
    """
    Génère la fiche correspondant à nos filtres, regarde ligne par ligne si la somme est supérieur à 1 pour chaque ligne.
    output : Dataframe 
    """
    fiche = df.loc[(df_contexte['somme'] >= 1) & \
              (df_situ_perso['somme'] >= 1)& \
              (df_aidant['somme'] >=1) & \
              (df_patrimoine['somme']>=1) & \
              (df_relation['somme']>=1),['Unnamed: 0', 'Unnamed: 1','Exclusion']].drop_duplicates(subset= ['Unnamed: 0'] ,keep = 'first')
    return fiche

def regle_exclusion(fiche):
    """
    Implémente la règle d'exclusion, recupère dans une liste toutes les variables qui doivent être exclus.
    Garde ensuite les lignes dont leurs code n'est pas affiché dans le code
    output : Dataframe 
    """
    list_ = fiche['Exclusion'].loc[fiche['Exclusion'].notnull()].reset_index(drop=True)
    str_exclu = ''
    for x in list_:
        str_exclu +=''+str(x)+','
    str_exclu =str_exclu.replace(' ','')
    str_exclu = str_exclu.split(',')
    del str_exclu[-1]
    str_exclu = list(set(str_exclu))
    sorted(str_exclu)
    
    exclusion = [fiche['Unnamed: 1'].str.contains(x) for x in str_exclu]
    
    df_exclusion = pd.DataFrame(exclusion).transpose()
    df_exclusion['somme'] = df_exclusion.sum(axis=1) 
    df_exclusion['somme']
    fiche = fiche.loc[(df_exclusion['somme'] == 0)]
    fiche = fiche.drop_duplicates(keep = 'first')
    return fiche


def letters_to_recognize(df_column):
    """
    Fonction pour mettre les lettres de l'excel sous forme de liste
    output : dataframe
    """
    to_remove=['', ',']
    str_recognize = df_column.split(",")
    if to_remove in str_recognize:
        str_recognize.remove(to_remove)
    return str_recognize

def regle_ordre(fiche, df_ordre):
    """
    Implémente la règle d'ordre. La fonction va chercher dans le tableau les lettres à afficher, les identifie dans la fiche et les met dans l'ordre désiré. 
    output : dataframe
    """
    fiche.reset_index(inplace=True, drop=True)
    for row in range(len(df_ordre)-1):
        display_letters = df_ordre['priorité_affichage'][row]
        display_letters = letters_to_recognize(display_letters)
        checking = []
        for x in display_letters:    
            checking.append(fiche.loc[(fiche['Unnamed: 1'] == x)])

        if len(checking)==2:
            try:
                fiche = pd.concat([fiche.iloc[:checking[0].index[0]+1], checking[1], fiche.iloc[checking[0].index[0]+1:]]).reset_index(drop=True)
                if fiche.loc[(fiche['Unnamed: 1'] == checking[0]['Unnamed: 1'].item())].index[0] < fiche.loc[(fiche['Unnamed: 1'] == checking[1]['Unnamed: 1'].item())].index[0]:
                    fiche.drop(checking[1].index[0]+1, inplace = True)
                    fiche.reset_index(inplace=True, drop=True)
                else:
                    fiche.drop(checking[1].index[0], inplace = True)
                    fiche.reset_index(inplace=True, drop=True)
            except:
                pass


        else:
            continue
            
    return fiche    


def regle_substitution(fiche, df_substitution,df_CVv):
    """
    Implémente la règle de substitution 
    output : Dataframe
    """
    df = df_substitution.dropna().reset_index(drop=True).drop(index=0,axis=1)
    for x in df['si_lettres']:    
        #Regarde si il y a bien les deux lignes de subsitution 
        test = fiche.loc[(fiche['Unnamed: 1'] == x.split(',')[0])|(fiche['Unnamed: 1'] == x.split(',')[1])]
        if test.shape[0]==2:
            #Va chercher la ligne qui faut remplacer
            ligne_remp = df_CVv.loc[df_CVv['Unnamed: 1'] == (df['remplace_par'].loc[df['si_lettres'] == x].reset_index(drop=True)[0]),\
                                    ['si_lettres', 'suppr_lettres','Exclusion']].drop_duplicates(subset='suppr_lettres', keep = 'first')
            #remplace la ligne
            fiche = fiche.replace(fiche['Unnamed: 1'].loc[fiche['Unnamed: 1']==(df['suppr_lettres'].loc[df['si_lettres'] == x].reset_index(drop=True)[0])].reset_index(drop=True)[0],\
                                      ligne_remp['si_lettres'].reset_index(drop=True)[0])
            fiche = fiche.replace(fiche['Unnamed: 1'].loc[fiche['Unnamed: 1']==(df['suppr_lettres'].loc[df['si_lettres'] == x].reset_index(drop=True)[0])].reset_index(drop=True)[0],\
                                      ligne_remp['suppr_lettres'].reset_index(drop=True)[0])   
        else:
            continue
            
    return fiche
    






