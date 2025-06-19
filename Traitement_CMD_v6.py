# -*- coding: utf-8 -*-
"""
Created on Sat Feb 13 17:32:15 2021

@author: thiesson
"""

import os
import glob
import sys
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pickle

import CONFIG
import EM_CMD


os.chdir(CONFIG.data_path)

def main(app_data,file_list,file_list_rev,sep,output_file,output_file_base,split,sup_na,regr,corr_base,choice):
    
    nomrep1="CMD explorer GPS/VCP"
    nomrep2="CMD explorer GPS/HCP"
    nomrep3="CMD mini explorer 3L GPS"
    nomrep4="C:/Data_equivalent/prospection/Tournoisis_Amelie_Laurent/\
    2024/cmd explorer/VCP"
    nomrep5="C:/Data_equivalent/prospection/Tournoisis_Amelie_Laurent/\
    2024/CMD miniexplorer/VVCP"

    nomrep = CONFIG.data_path

    os.chdir(nomrep)
    ls_nomfich = []
    if file_list == None:
        ls_nomfich = glob.glob("*.dat")
        if file_list_rev != None:
            try:
                for f_rev in file_list_rev:
                    ls_nomfich.remove(f_rev)
            except:
                EM_CMD.CMD_err_mess('Le fichier "{}" est introuvable'.format(f_rev))
    else:
        for f in file_list:
            ls_nomfich.append(f.replace('"',''))
    
    nb_fich = len(ls_nomfich)
    if nb_fich > 8:
        EM_CMD.CMD_warn_mess('Le nombre de fichiers est élevé ({}) : il est conseillé de fractionner le traitement pour obtenir de meilleurs résultats'.format(nb_fich))

    # il faut gérer différentes choses comme la recherche de base ou la présence
    # d'un GPS. C'est le rôle des booléens suivants
    # qu'on pourra traduire sous forme d'interface si nécessaire
    Base=True
    # init_geom=False


    # ici on a les différents paramètre des différentes géométries
    # on pourrait utiliser un dictionnaire

    # decal6L=np.round(TxRx6L/2.-0.75,3)
    # decal3L=np.round(TxRx3L/2.-0.59,3)
    # decalex=np.round(TxRxex/2.-2.3,3)
    
    dec_para = np.round(np.array(app_data["TxRx"])/2.-0.59,3)

        
    #à modifier en fonction de la configuration de prospection 
    #décalage entre antenne GPS et centre de l'appareil    
    dec_tete_app=np.array((0.4,))

    if app_data["GPS"] : 
        dec_perp=dec_tete_app
        if len(dec_perp)==1 :
            dec_perp=np.tile(dec_perp,app_data["nb_ecarts"])
        else:
            if len(dec_perp)!=app_data["nb_ecarts"] :
                EM_CMD.CMD_err_mess("Attention,la taille du décalage doit être 1 ou {} : on prend la première valeur du tableau fourni".format(app_data["nb_ecarts"]))
                dec_perp=np.tile(dec_perp[0],app_data["nb_ecarts"])

    # init_geom=True
    
    # if not(init_geom) :
    #     EM_CMD.CMD_err_mess("Pas d'initialisation, arrêt du script")
    # pass
        
    # concaténation si nécessaire avant traitement
    ls_pd=[]
    ls_pd_done_before = []
    
    for ic,f in enumerate(ls_nomfich) :
        data = EM_CMD.CMD_check_time_date(f,sep)
        
        data['Num fich']=ic+1
        #print(data.columns)
        try:
            testouh = data["X_int"]
            ls_pd_done_before.append(data)
        except KeyError:
            ls_pd.append(data)
        
    if app_data["GPS"] :
        i_GPS = 2
        const_GPS = 7
        nom_colX='Northing'
        nom_colY='Easting'
    else :
        # i_GPS = 3
        # const_GPS = 4
        i_GPS = 2
        const_GPS = 2
        nom_colX='x[m]'
        nom_colY='y[m]'
    
    ls_base = []
    ls_mes = []
    
    for ic,don_c in enumerate(ls_pd) :
        print("Fichier de données n°{} : '{}'".format(ic+1,ls_nomfich[ic]))
      
    if len(ls_pd) != 0:
        don_raw = pd.concat(ls_pd)
        don_raw.index=np.arange(don_raw.shape[0])
    
        # Si le fichier contient des données temporelles
        try:
            don_raw['temps (s)']=EM_CMD.CMD_time(don_raw)
            # On gère les prospections faites des jours différents
            for ic,date_c in enumerate(don_raw['Date'].unique()) :
                if ic>0 :
                    ind_d =don_raw.index[don_raw['Date']==date_c]
                    don_raw.loc[ind_d,'temps (s)']=don_raw.loc[ind_d,'temps (s)']+ic*86400
                #print(don_raw.dtypes)
                don_d=EM_CMD.CMD_detect_chgt(don_raw)
                #EM_CMD.CMD_warn_mess("uno")
                don_i=EM_CMD.CMD_intrp_prof(don_d)
                #EM_CMD.CMD_warn_mess("dos")
                don_i=EM_CMD.CMD_detect_base_pos(don_i,2)
                #EM_CMD.CMD_warn_mess("tres")
        except KeyError:
            don_raw["X_int"] = don_raw.iloc[:,0]
            don_raw["Y_int"] = don_raw.iloc[:,1]
            
            don_i = EM_CMD.CMD_detec_profil_carre(don_raw)
    
        if sup_na:
            don_i.dropna(subset = [nom_colX,nom_colY],inplace=True)
            don_i.reset_index(drop=True,inplace=True)
        else:
            EM_CMD.CMD_warn_mess("Les données NaN seront redressées")
            don_i = EM_CMD.CMD_XY_Nan_completion(don_i)
        don_base,don_mes=EM_CMD.CMD_sep_BM(don_i)
        #EM_CMD.CMD_warn_mess("quatro")
        
        # print(don_i)
        # print(don_mes)
        
        for i in range(nb_fich):
            i_fich_mes = don_mes[don_mes["Num fich"] == i+1]
            i_fich_base = don_base[don_base["Num fich"] == i+1]
            ls_base.append(i_fich_base)
            
            if regr:
                fig,ax=plt.subplots(nrows=1,ncols=1,figsize=(CONFIG.fig_height,CONFIG.fig_height))
                ax.plot(i_fich_mes["X_int"],i_fich_mes["Y_int"],'+r')
                ax.plot(i_fich_mes[i_fich_mes["Profil"] == i_fich_mes.iloc[0]["Profil"]]["X_int"],i_fich_mes["Y_int"][i_fich_mes["Profil"] == i_fich_mes.iloc[0]["Profil"]],'+b')
                ax.set_xlabel(nom_colX)
                ax.set_ylabel(nom_colY)
                ax.set_aspect('equal')
                ax.set_title(ls_nomfich[i])
                plt.show(block=False)
                plt.pause(0.25)
                
                correct = False
                while correct == False:
                    if EM_CMD.GUI:
                        EM_CMD.CMD_input_GUI(["fichier {} : redressement ?".format(ls_nomfich[i]),"","~r~ Oui (tous les profils)","~r~ Non","","Oui, à partir du profil k, ou jusqu'au profil -k (-1 est le dernier profil)","Ignore le choix précédent si non vide","~t~","","Le premier profil est indiqué en bleu"])
                        try:
                            fin, inp = EM_CMD.GUI_VAR_LIST
                            if inp == "":
                                inp = ["y","n"][fin]
                                print("rrr")
                        except:
                            EM_CMD.CMD_warn_mess("Veuillez sélectionner un réponse")
                            continue
                        print("iii")
                    else:
                        EM_CMD.CMD_input_mess(["fichier {} : redressement ?".format(ls_nomfich[i]),"","y : Oui (tous les profils)","k >= 0 : Oui, à partir du profil k","k < 0 : Oui, jusqu'au profil -k (-1 est le dernier profil)","n : Non","","Le premier profil est indiqué en bleu"])
                        inp = input()
                    try:
                        print(inp)
                        print("uuu")
                        if inp == "n":
                            pass
                        elif inp == "y":
                            i_fich_mes = EM_CMD.CMD_pts_rectif(i_fich_mes)
                        elif int(inp) >= 0:
                            i_fich_mes = EM_CMD.CMD_pts_rectif(i_fich_mes,ind_deb=int(inp))
                        else:
                            i_fich_mes = EM_CMD.CMD_pts_rectif(i_fich_mes,ind_fin=int(inp))
                        correct = True
                    except ValueError:
                        EM_CMD.CMD_warn_mess("Réponse non reconnue !")
                    except IndexError:
                        EM_CMD.CMD_warn_mess("Le profil {} n'existe pas !".format(inp))
                
            if corr_base:
                try:
                    i_fich_mes = EM_CMD.CMD_evol_profils(i_fich_mes,i_fich_base,ls_nomfich[i],const_GPS,i_GPS*app_data["nb_ecarts"],app_data["nb_ecarts"],verif=False)
                except IndexError:
                    EM_CMD.CMD_warn_mess("Base externe au fichier {}, pas d'ajustement".format(ls_nomfich[i]))
            ls_mes.append(i_fich_mes)
            
    cpt = 0
    if ls_mes:
        for ic,df in enumerate(ls_mes):
            #EM_CMD.CMD_warn_mess(ls_nomfich[ic])
            if df.empty:
                ls_mes[ic] = ls_pd_done_before[cpt]
                cpt += 1
    else:
        ls_mes = ls_pd_done_before
    
    if nb_fich > 1:
        #EM_CMD.CMD_warn_mess("cinco")
        don_to_corr = [i for i in range(1,nb_fich)]
        don_corr = [0]
        is_corr_done = False
        while is_corr_done == False:
            don_corr_copy = don_corr.copy()
            for i in don_corr_copy:
                don_to_corr_copy = don_to_corr.copy()
                for j in don_to_corr_copy:
                    EM_CMD.CMD_warn_mess("{} , {}".format(i+1,j+1))
                    # print(ls_mes[i])
                    # print("---------------------------")
                    # print(ls_mes[j])
                    ls_mes[j], done = EM_CMD.CMD_corr_data(ls_mes[i], ls_mes[j], nom_colX, nom_colY, const_GPS, i_GPS*app_data["nb_ecarts"], m_size=40, verif=False, verif_pts=False, choice=choice)
                    if done:
                        don_to_corr.remove(j)
                        don_corr.append(j)
                don_corr.remove(i)
                if len(don_to_corr) == 0:
                    is_corr_done = True
            if len(don_corr) == 0:
                EM_CMD.CMD_warn_mess("Certains jeux de données n'ont pas pu être ajustés. Sont-ils tous frontaliers ?")
                is_corr_done = True
              
    os.chdir(CONFIG.script_path)
    if split:
        for ic,p in enumerate(ls_mes):
            p.to_csv(CONFIG.data_path+ls_nomfich[ic][:-4]+"_P.dat", header=True, index=False, sep=sep, mode='w')
        for ic,b in enumerate(ls_base):
            if not b.empty:
                b.to_csv(CONFIG.data_path+ls_nomfich[ic][:-4]+"_B.dat", header=True, index=False, sep=sep, mode='w')
    don_mes = pd.concat(ls_mes)
    don_mes.to_csv(CONFIG.data_path+output_file, header=True, index=False, sep=sep, mode='w')
    if ls_base:
        don_base = pd.concat(ls_base)
        if not don_base.empty:
            don_base.to_csv(CONFIG.data_path+output_file_base, header=True, index=False, sep=sep, mode='w')
    #print(don_mes)
    
    # on affiche les points de mesure apres repositionnement, interpolation et redressement
    ls_C=[const_GPS+i*i_GPS for i in range(app_data["nb_ecarts"])]
    ls_I=[1 + const_GPS+i*i_GPS for i in range(app_data["nb_ecarts"])]
    col_C=don_mes.columns[ls_C]
    col_I=don_mes.columns[ls_I]
    # print(don_mes)
    # print("const_GPS = ",const_GPS)
    # print("i_GPS = ",i_GPS)
    # print("ls_C = ",ls_C)
    # print("ls_I = ",ls_I)
    # print("col_C = ",col_C)
    # print("col_I = ",col_I)
    
    for i in range(app_data["nb_ecarts"]):
        fig,ax=plt.subplots(nrows=1,ncols=2,figsize=(CONFIG.fig_width,CONFIG.fig_height))
        X = don_mes['X_int']
        Y = don_mes['Y_int']
        Z1 = don_mes[col_C[i]]
        Z2 = don_mes[col_I[i]]
        Q5,Q95 = Z1.quantile([0.05,0.95])
        col1 = ax[0].scatter(X,Y,marker='s',c=Z1,cmap='cividis',s=6,vmin=Q5,vmax=Q95)
        plt.colorbar(col1,ax=ax[0],shrink=0.7)
        ax[0].title.set_text(col_C[i])
        Q5,Q95 = Z2.quantile([0.05,0.95])
        col2 = ax[1].scatter(X,Y,marker='s',c=Z2,cmap='cividis',s=6,vmin=Q5,vmax=Q95)
        plt.colorbar(col2,ax=ax[1],shrink=0.7)
        ax[1].title.set_text(col_I[i])
        for axc in ax :
            axc.set_xlabel(nom_colX)
            axc.set_ylabel(nom_colY)
            axc.set_aspect('equal')
        plt.show(block=False)
        plt.pause(0.25)
        plt.savefig(CONFIG.script_path+"Output/CMD_" +str(i)+'.png')
        pickle.dump(fig, open("Output/CMD_" +str(i)+'.pickle', 'wb'))
        
        
    #fin de lecture du fichier
    EM_CMD.CMD_input_mess(["Fin de l'execution, appuyer sur 'Entree' pour fermer"])
    #input()
    os.chdir(CONFIG.script_path)

# Suite ct à la ligne ligne 403

# Sert à remplir la base avec les appareils utiles au fichiers en local [pour les tests]

def init_app_dat():
    JSON_add_device('mini3L','HCP',3,[0.32,0.71,1.18],[30000],True,0.1,0,1)
    JSON_add_device('mini3L','VCP',3,[0.32,0.71,1.18],[30000],True,0.1,0,1)
    JSON_add_device('mini3L','VCP',3,[0.32,0.71,1.18],[0.00591,0.0281,0.0745],True,0.1,0,1)
    JSON_add_device('mini6L','HCP',6,[0.2,0.33,0.5,0.72,1.03,1.5],[0.00194,0.00524,0.0119,0.0242,0.0484,0.0986],True,0.1,0,1)
    JSON_add_device('mini6L','VCP',6,[0.2,0.33,0.5,0.72,1.03,1.5],[0.00194,0.00525,0.012,0.0246,0.0498,0.1037],True,0.1,0,1)
    JSON_add_device('mini6L','PRP_CS',6,[0.2,0.33,0.5,0.72,1.03,1.5],[0.00194,0.00525,0.012,0.0246,0.0498,0.1037],True,0.1,0,1)
    JSON_add_device('expl3L','HCP',3,[1.5,2.4,4.6],[0.0402,0.1366,0.3144],True,0.1,0,1)
    JSON_add_device('expl3L','VCP',3,[1.5,2.4,4.6],[0.0417,0.1463,0.3558],True,0.1,0,1)
    JSON_add_device('mini3L','HCP',3,[0.32,0.71,1.18],[30000],False,0.1,0,1)

# EM_CMD.JSON_print_devices(CONFIG.json_path)

# EM_CMD.JSON_add_coeff('VCP',[0.32,0.71,1.18],0.1,[0.00591,0.0281,0.0745])
# EM_CMD.JSON_add_coeff('HCP',[0.32,0.71,1.18],0.2,[0.00591,0.0281,0.0745])
# EM_CMD.JSON_add_coeff('HCP',[0.32,0.71,1.18],0.1,[0.00591,0.0281,0.0745])
# EM_CMD.JSON_add_coeff('HCP',[0.32,0.71,1.18],0.3,[0.00591,0.0281,0.0745])
# EM_CMD.JSON_add_coeff('HCP',[0.32,0.70,1.18],0.1,[0.00591,0.0281,0.0745])


# EM_CMD.JSON_print_devices(uid=4)
# app_data = EM_CMD.JSON_find_device( 5)
# print(app_data)
# app_data = EM_CMD.JSON_find_device( 11)
# print(app_data)

# Attend une réponse utilisateur si l'exécution provient du cmd (matplotlib est fermé automatiquement sinon)

def CMD_help(help_id=None):
    print(EM_CMD.success_color)
    nc = os.get_terminal_size().columns
    print("~"*nc)
    print("")
    print(" "*((nc-55)//2),"-------------------------------------------------------")
    print(" "*((nc-55)//2),"-----  Programme de traîtement des donneées CMD   -----")
    print(" "*((nc-55)//2),"-------------------------------------------------------")
    if help_id == None or help_id == 0:
        print(EM_CMD.title_color)
        curr_title = "[0] Aide :"
        print(curr_title+EM_CMD.title_next_color+"."*(nc-len(curr_title)))
        print(EM_CMD.bold_und_color)
        print("DESCRIPTION :"+EM_CMD.bold_color+" Permet d'afficher la description des fonctions disponibles.")
        print(EM_CMD.code_color)
        print(">>> CMD_help("+EM_CMD.success_low_color+"[help_id]"+EM_CMD.code_color+")")
        print(EM_CMD.base_color)
        print("avec : "+EM_CMD.success_low_color+"help_id = None"+EM_CMD.type_color+" : string/int "+EM_CMD.base_color+"= fonction sélectionnée ou son indice (laisser vide pour tout afficher)")
        print("")
        print("indice : indiqué à côté du nom de la fonction")
        print("")
        print("préfixe : CMD -> Traitement principal")
        print("          CMDEX -> Traitement réduit à une seule tâche")
        print("          JSON -> Manipulation des fichiers .json")
        print("          DAT -> Manipulation des fichiers .dat")
        print("")
        print("exemples : "+EM_CMD.code_color+'python3 Traitement_CMD_v6.py CMD_help')
        print("           "+EM_CMD.code_color+'python3 Traitement_CMD_v6.py CMD_help 1')
        print("           "+EM_CMD.code_color+'python3 Traitement_CMD_v6.py CMD_help CMD_exec_known_device')
        print(EM_CMD.base_color)
    if help_id == None or help_id == 1:
        print(EM_CMD.title_color)
        curr_title = "[1] Traitement CMD (appareil enregistré) :"
        print(curr_title+EM_CMD.title_next_color+"."*(nc-len(curr_title)))
        print(EM_CMD.bold_und_color)
        print("DESCRIPTION :"+EM_CMD.bold_color+" Effectue le traitement de données CMD mesurées avec un appareil et des réglages connus (présents dans la base 'Appareil.json').")
        print("Les fichiers .dat sont récoltés dans le dossier pointé par la variable globale 'CONFIG.data_path'.")
        print("Les fichiers .json sont récoltés dans le dossier pointé par la variable globale 'CONFIG.json_path'.")
        print(EM_CMD.code_color)
        print(">>> CMD_exec_known_device("+EM_CMD.success_color+"uid"+EM_CMD.code_color+","+EM_CMD.success_low_color+"[file_list"+EM_CMD.code_color+","+
              EM_CMD.success_low_color+"file_list_rev"+EM_CMD.code_color+","+EM_CMD.success_low_color+"sep"+EM_CMD.code_color+","+EM_CMD.success_low_color+"output_file"+EM_CMD.code_color+","+
              EM_CMD.success_low_color+"output_file_base"+EM_CMD.code_color+","+EM_CMD.success_low_color+"split"+EM_CMD.code_color+","+EM_CMD.success_low_color+"sup_na"+EM_CMD.code_color+","+
              EM_CMD.success_low_color+"regr"+EM_CMD.code_color+","+EM_CMD.success_low_color+"corr_base"+EM_CMD.code_color+","+EM_CMD.success_low_color+"choice]"+EM_CMD.code_color+")")
        print(EM_CMD.base_color)
        print("avec : "+EM_CMD.success_color+"uid"+EM_CMD.type_color+" : int "+EM_CMD.base_color+"= indentifiant de l'appareil dans la base JSON")
        print("       "+EM_CMD.success_low_color+"file_list = None"+EM_CMD.type_color+" : str[] "+EM_CMD.base_color+"= liste des fichiers à traiter, le premier est celui servant pour le redressement (laisser vide pour traiter tous les fichiers du dossier)")
        print("       "+EM_CMD.success_low_color+"file_list_rev = None"+EM_CMD.type_color+" : str[] "+EM_CMD.base_color+"= liste des fichiers à ne pas traiter (n'est pris en compte que si le champ précédent est laissé vide)")
        print("       "+EM_CMD.success_low_color+"sep = '\\t'"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= caractère de séparation du .dat (par défaut '\\t')")
        print("       "+EM_CMD.success_low_color+'output_file = "res.dat"'+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= nom du fichier de sortie (profils)")
        print("       "+EM_CMD.success_low_color+'output_file_base = "res_B.dat"'+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= nom du fichier de sortie (base), seulement si des bases ont été détectées")
        print("       "+EM_CMD.success_low_color+"split = False"+EM_CMD.type_color+" : bool "+EM_CMD.base_color+"= si on sépare le résultat pour chaque fichier d'entrée (on ajoutera les suffixes '_P' pour profils et '_B' pour base), ignore les deux paramètres précédents")
        print("       "+EM_CMD.success_low_color+"sup_na = True"+EM_CMD.type_color+" : bool "+EM_CMD.base_color+"= suppression des données incomplètes (sinon redressage)")
        print("       "+EM_CMD.success_low_color+"regr = False"+EM_CMD.type_color+" : bool "+EM_CMD.base_color+"= propose d'appliquer ou non une régression linéaire sur les profils, si certains ne sont pas droits (par défaut, ne le fait pas)")
        print("       "+EM_CMD.success_low_color+"corr_base = True"+EM_CMD.type_color+" : bool "+EM_CMD.base_color+"= si activé, applique une correction par base sur les données d'un même fichier (voir CMDEX_evol_profils pour plus d'options)")
        print("       "+EM_CMD.success_low_color+"choice = False"+EM_CMD.type_color+" : bool "+EM_CMD.base_color+"= si activé, permet de valider ou non chaque ajustement proposé entre les jeux de données (attention, cette procédure peut être longue)")
        print("")
        print("exemples : "+EM_CMD.code_color+'python3 Traitement_CMD_v6.py CMD_exec_known_device 1')
        print("           "+EM_CMD.code_color+'python3 Traitement_CMD_v6.py CMD_exec_known_device 4 "sup_na=False" "file_list=["d1.dat",d2.dat]"')
        print(EM_CMD.base_color)
    if help_id == None or help_id == 2:
        print(EM_CMD.title_color)
        curr_title = "[2] Traitement CMD (nouvel appareil) :"
        print(curr_title+EM_CMD.title_next_color+"."*(nc-len(curr_title)))
        print(EM_CMD.bold_und_color)
        print("DESCRIPTION :"+EM_CMD.bold_color+" Effectue le traitement de données CMD mesurées avec un nouvel appareil, donc les paramètres doivent être spécifiés.")
        print("Les fichiers .dat sont récoltés dans le dossier pointé par la variable globale 'CONFIG.data_path'.")
        print("Les fichiers .json sont récoltés dans le dossier pointé par la variable globale 'CONFIG.json_path'.")
        print(EM_CMD.code_color)
        print(">>> CMD_exec_new_device("+EM_CMD.success_color+"app_name"+EM_CMD.code_color+","+EM_CMD.success_color+"config"+EM_CMD.code_color+","+EM_CMD.success_color+"nb_ecarts"+EM_CMD.code_color+","+
              EM_CMD.success_color+"nb_ecarts"+EM_CMD.code_color+","+EM_CMD.success_color+"TxRx"+EM_CMD.code_color+","+EM_CMD.success_color+"freq_list"+EM_CMD.code_color+","+
              EM_CMD.success_low_color+"[GPS"+EM_CMD.code_color+","+EM_CMD.success_low_color+"height"+EM_CMD.code_color+","+EM_CMD.success_low_color+"bucking_coil"+EM_CMD.code_color+","+
              EM_CMD.success_low_color+"coeff_construct"+EM_CMD.code_color+","+EM_CMD.success_low_color+"file_list"+EM_CMD.code_color+","+EM_CMD.success_low_color+"file_list_rev"+EM_CMD.code_color+","+
              EM_CMD.success_low_color+"sep"+EM_CMD.code_color+","+EM_CMD.success_low_color+"output_file"+EM_CMD.code_color+","+EM_CMD.success_low_color+"output_file_base"+EM_CMD.code_color+","+
              EM_CMD.success_low_color+"split"+EM_CMD.code_color+","+EM_CMD.success_low_color+"sup_na"+EM_CMD.code_color+","+EM_CMD.success_low_color+"regr"+EM_CMD.code_color+","+
              EM_CMD.success_low_color+"corr_base"+EM_CMD.code_color+","+EM_CMD.success_low_color+"choice]"+EM_CMD.code_color+")")
        print(EM_CMD.base_color)
        print("avec : "+EM_CMD.success_color+"app_name"+EM_CMD.type_color+" : string "+EM_CMD.base_color+"= nom de l'appareil")
        print("       "+EM_CMD.success_color+"config"+EM_CMD.type_color+" : string "+EM_CMD.base_color+"= configuration des bobines (HCP,VCP,PRP_CS,PRP_DEM,PAR,CUS)")
        print("       "+EM_CMD.success_color+"nb_ecarts"+EM_CMD.type_color+" : int "+EM_CMD.base_color+"= nombre de bobines")
        print("       "+EM_CMD.success_color+"TxRx"+EM_CMD.type_color+" : float[] "+EM_CMD.base_color+"= positions des bobines recepteurs (en m)")
        print("       "+EM_CMD.success_color+"freq_list"+EM_CMD.type_color+" : float[] "+EM_CMD.base_color+"= fréquences du signal (en ???)")
        print("       "+EM_CMD.success_low_color+"GPS = True"+EM_CMD.type_color+" : bool "+EM_CMD.base_color+"= présence ou non de données GPS")
        print("       "+EM_CMD.success_low_color+"height = 0.1"+EM_CMD.type_color+" : float "+EM_CMD.base_color+"= hauteur de l'appareil par rapport au sol (en m)")
        print("       "+EM_CMD.success_low_color+"bucking_coil = 0"+EM_CMD.type_color+" : int "+EM_CMD.base_color+"= numéro de la bucking coil parmi les bobines (0 si inexistante)")
        print("       "+EM_CMD.success_low_color+"coeff_construct = 1.0"+EM_CMD.type_color+" : float "+EM_CMD.base_color+"= coefficient de l'appareil (fourni par le constructeur)")
        print("       "+EM_CMD.success_low_color+"file_list = None"+EM_CMD.type_color+" : str[] "+EM_CMD.base_color+"= liste des fichiers à traiter, le premier est celui servant pour le redressement (laisser vide pour traiter tous les fichiers du dossier)")
        print("       "+EM_CMD.success_low_color+"file_list_rev = None"+EM_CMD.type_color+" : str[] "+EM_CMD.base_color+"= liste des fichiers à ne pas traiter (n'est pris en compte que si le champ précédent est laissé vide)")
        print("       "+EM_CMD.success_low_color+"sep = '\\t'"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= caractère de séparation du .dat (par défaut '\\t')")
        print("       "+EM_CMD.success_low_color+'output_file = "res.dat"'+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= nom du fichier de sortie (profils)")
        print("       "+EM_CMD.success_low_color+'output_file_base = "res_B.dat"'+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= nom du fichier de sortie (base), seulement si des bases ont été détectées")
        print("       "+EM_CMD.success_low_color+"split = False"+EM_CMD.type_color+" : bool "+EM_CMD.base_color+"= si on sépare le résultat pour chaque fichier d'entrée (on ajoutera les suffixes '_P' pour profils et '_B' pour base), ignore les deux paramètres précédents")
        print("       "+EM_CMD.success_low_color+"sup_na = True"+EM_CMD.type_color+" : bool "+EM_CMD.base_color+"= suppression des données incomplètes (sinon redressage)")
        print("       "+EM_CMD.success_low_color+"regr = False"+EM_CMD.type_color+" : bool "+EM_CMD.base_color+"= propose d'appliquer ou non une régression linéaire sur les profils, si certains ne sont pas droits (par défaut, ne le fait pas)")
        print("       "+EM_CMD.success_low_color+"corr_base = True"+EM_CMD.type_color+" : bool "+EM_CMD.base_color+"= si activé, applique une correction par base sur les données d'un même fichier (voir CMDEX_evol_profils pour plus d'options)")
        print("       "+EM_CMD.success_low_color+"choice = False"+EM_CMD.type_color+" : bool "+EM_CMD.base_color+"= si activé, permet de valider ou non chaque ajustement proposé entre les jeux de données (attention, cette procédure peut être longue)")
        print("")
        print("exemples : "+EM_CMD.code_color+'python3 Traitement_CMD_v6.py CMD_exec_new_device "dummy" "PAR" 5 "[0.24,0.52,0.91,1.2,1.45]" 40000 "file_list=["d1.dat",d2.dat]"')
        print("           "+EM_CMD.code_color+'python3 Traitement_CMD_v6.py CMD_exec_new_device "mini3L" "VCP" 3 "0.32 0.71 1.18 " [30000] height=0.2 "GPS = False" sup_na=False')
        print(EM_CMD.base_color)
    if help_id == None or help_id == 3:
        print(EM_CMD.title_color)
        curr_title = "[3] Etalonnage par base et/ou manuel :"
        print(curr_title+EM_CMD.title_next_color+"."*(nc-len(curr_title)))
        print(EM_CMD.bold_und_color)
        print("DESCRIPTION :"+EM_CMD.bold_color+" À partir d'un fichier de profils et d'un fichier de bases associées, propose un étalonnage des profils par alignement des bases.")
        print("L'opération se fait par différence, mais il est possible de faire par multiplication. Il est possible de traiter plusieurs coupes de fichiers (profil,base), mais l'ordre doit correspondre.")
        print("La sortie est par graphe et par fichier (pour le résultat).")
        print("Il est possible de demander la rectification de blocs de profils, si d'autres imperfections sont visibles visuellement, avec le paramètre "+'"man_adjust"'+".")
        print("Si on souhaite uniquement effectuer cette opération, on peut désactiver l'opération avec bases, avec le paramètre "+'"auto_adjust"'+".")
        print(EM_CMD.code_color)
        print(">>> CMDEX_evol_profils("+EM_CMD.success_color+"file_prof_list"+EM_CMD.code_color+","+EM_CMD.success_color+"file_base_list"+EM_CMD.code_color+","+
              EM_CMD.success_low_color+"[sep"+EM_CMD.code_color+","+EM_CMD.success_low_color+"replace"+EM_CMD.code_color+","+EM_CMD.success_low_color+"output_file_list"+EM_CMD.code_color+","+
              EM_CMD.success_low_color+"start"+EM_CMD.code_color+","+EM_CMD.success_low_color+"nb_data"+EM_CMD.code_color+","+EM_CMD.success_low_color+"nb_ecarts"+EM_CMD.code_color+","+
              EM_CMD.success_low_color+"diff"+EM_CMD.code_color+","+EM_CMD.success_low_color+"auto_adjust"+EM_CMD.code_color+","+EM_CMD.success_low_color+"man_adjust"+EM_CMD.code_color+","+
              EM_CMD.success_low_color+"line]"+EM_CMD.code_color+")")
        print(EM_CMD.base_color)
        print("avec : "+EM_CMD.success_color+"file_prof_list"+EM_CMD.type_color+" : str[] "+EM_CMD.base_color+"= liste des fichiers profils à traiter")
        print("       "+EM_CMD.success_color+"file_base_list"+EM_CMD.type_color+" : str[] "+EM_CMD.base_color+"= liste des fichiers bases à traiter")
        print("       "+EM_CMD.success_low_color+"sep = '\\t'"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= caractère de séparation du .dat (par défaut '\\t')")
        print("       "+EM_CMD.success_low_color+"replace = False"+EM_CMD.type_color+" : bool "+EM_CMD.base_color+"= si le résultat est mis dans le fichier profils de départ (sinon, un nouveau est créé avec le suffixe '_corr')")
        print("       "+EM_CMD.success_low_color+"output_file_list = None"+EM_CMD.type_color+" : str[] "+EM_CMD.base_color+"= nom des fichier de sortie, n'est pas pris en compte si replace=True (si None, alors le résultat n'est pas enregistré)")
        print("       "+EM_CMD.success_low_color+"start = 7"+EM_CMD.type_color+" : int "+EM_CMD.base_color+"= indice de la première colonne de données à traiter (sans compter les colonnes surnuméraires)")
        print("       "+EM_CMD.success_low_color+"nb_data = 6"+EM_CMD.type_color+" : int "+EM_CMD.base_color+"= nombres de données à traiter")
        print("       "+EM_CMD.success_low_color+"nb_ecarts = nb_data/2"+EM_CMD.type_color+" : int "+EM_CMD.base_color+"= nombres de données par voies/bobines")
        print("       "+EM_CMD.success_low_color+"auto_adjust = True"+EM_CMD.type_color+" : bool "+EM_CMD.base_color+"= permet d'activer la rectification automatique des profils par base")
        print("       "+EM_CMD.success_low_color+"man_adjust = False"+EM_CMD.type_color+" : bool "+EM_CMD.base_color+"= permet d'activer la rectification manuelle de blocs de profils")
        print("       "+EM_CMD.success_low_color+"line = False"+EM_CMD.type_color+" : bool "+EM_CMD.base_color+"= si on trace la courbe des profils (sinon juste les points)")
        print("")
        print("exemples : "+EM_CMD.code_color+'python3 Traitement_CMD_v6.py CMDEX_evol_profils "prof_1.dat" "base_1.dat" line=True')
        print("           "+EM_CMD.code_color+'python3 Traitement_CMD_v6.py CMDEX_evol_profils "[prof_1.dat,prof_2.dat,prof_3.dat]" "[base_1.dat,base_2.dat,base_3.dat]" "sep=," "output_file_list=[o1.dat,o2.dat,o3.dat]" start=2')
        print(EM_CMD.base_color)
    if help_id == None or help_id == 4:
        print(EM_CMD.title_color)
        curr_title = "[4] Mise en grille des données:"
        print(curr_title+EM_CMD.title_next_color+"."*(nc-len(curr_title)))
        print(EM_CMD.bold_und_color)
        print("DESCRIPTION :"+EM_CMD.bold_color+" À partir d'un fichier de données, propose la mise en grille selon la méthode utilisée.")
        print("Si \"m_type='h\", alors on procède à l'élaboration d'une heatmap de densité des points. Utile pour déterminer le seuil.")
        print("Si \"m_type='i\", on interpole sur grille selon un des algorithmes suivants : 'nearest', 'linear', 'cubic'.")
        print("Si \"m_type='k\", un processus de choix de variogramme permettra ensuite de choisir les paramètres kriging. Seule les cases détectées par l'agorithme précédent seront considérées.")
        print("Attention à ne pas lancer de kriging sur un grand jeu de données ou une trop grande grille au risque de ne jamais le terminer !")
        print(EM_CMD.code_color)
        print(">>> CMDEX_grid("+EM_CMD.success_color+"col_x"+EM_CMD.code_color+","+EM_CMD.success_color+"col_y"+EM_CMD.code_color+","+EM_CMD.success_low_color+"[file_list"+EM_CMD.code_color+","+
              EM_CMD.success_low_color+"sep"+EM_CMD.code_color+","+EM_CMD.success_low_color+"output_file"+EM_CMD.code_color+","+EM_CMD.success_low_color+"m_type"+EM_CMD.code_color+","+
              EM_CMD.success_low_color+"radius"+EM_CMD.code_color+","+EM_CMD.success_low_color+"start"+EM_CMD.code_color+","+EM_CMD.success_low_color+"nb_data"+EM_CMD.code_color+","+
              EM_CMD.success_low_color+"nb_ecarts"+EM_CMD.code_color+","+EM_CMD.success_low_color+"prec"+EM_CMD.code_color+","+EM_CMD.success_low_color+"seuil"+EM_CMD.code_color+","+
              EM_CMD.success_low_color+"i_method"+EM_CMD.code_color+","+EM_CMD.success_low_color+"no_crop"+EM_CMD.code_color+","+EM_CMD.success_low_color+"all_models"+EM_CMD.code_color+","+
              EM_CMD.success_low_color+"plot_pts]"+EM_CMD.code_color+")")
        print(EM_CMD.base_color)
        print("avec : "+EM_CMD.success_color+"col_x"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= nom de la colonne des coordonnées x")
        print("       "+EM_CMD.success_color+"col_y"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= nom de la colonne des coordonnées y")
        print("       "+EM_CMD.success_low_color+"file_list = None"+EM_CMD.type_color+" : str[] "+EM_CMD.base_color+"= liste des fichiers à traiter, le premier est celui servant pour le redressement (laisser vide pour traiter tous les fichiers du dossier)")
        print("       "+EM_CMD.success_low_color+"sep = '\\t'"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= caractère de séparation du .dat (par défaut '\\t')")
        print("       "+EM_CMD.success_low_color+'output_file = None'+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= nom du fichier de sortie, sinon n'en crée pas")
        print("       "+EM_CMD.success_low_color+"m_type = None"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= 'h' -> heatmap, 'i' -> interpolation, 'k' -> kriging (sinon, le choix se fera pendant l'exécution)")
        print("       "+EM_CMD.success_low_color+"radius = 0"+EM_CMD.type_color+" : int "+EM_CMD.base_color+"= distance au-delà de laquelle une case sans point est considérée comme vide (dans le cas contraire, on l'estime par son voisinage).")
        print("       "+EM_CMD.success_low_color+"start = 7"+EM_CMD.type_color+" : int "+EM_CMD.base_color+"= indice de la première colonne de données à traiter (sans compter les colonnes surnuméraires)")
        print("       "+EM_CMD.success_low_color+"nb_data = 6"+EM_CMD.type_color+" : int "+EM_CMD.base_color+"= nombres de données à traiter")
        print("       "+EM_CMD.success_low_color+"nb_ecarts = nb_data/2"+EM_CMD.type_color+" : int "+EM_CMD.base_color+"= nombres de données par voies/bobines")
        print("       "+EM_CMD.success_low_color+"prec = 100"+EM_CMD.type_color+" : int "+EM_CMD.base_color+"= taille de la grille de sortie (s'adapte avec la forme du jeu)")
        print("       "+EM_CMD.success_low_color+"seuil = 0.0"+EM_CMD.type_color+" : float "+EM_CMD.base_color+"= seuil d'acceptation d'un point en périphérie (0 = toujours, varie généralement entre 0 et 4)")
        print("       "+EM_CMD.success_low_color+"i_method = None"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= 'nearest', 'linear', 'cubic'  (sinon, le choix se fera pendant l'exécution, inutile si m_type!='i')")
        print("       "+EM_CMD.success_low_color+"no_crop = False"+EM_CMD.type_color+" : bool "+EM_CMD.base_color+"= si False, ne sélectionne qu'au maximum 1000 points de l'ensemble (activer cette option augmente grandement le temps de calcul, inutile si m_type!='k')")
        print("       "+EM_CMD.success_low_color+"all_models = False"+EM_CMD.type_color+" : bool "+EM_CMD.base_color+"= propose les modèles de variogramme avancés (inutile si m_type!='k')")
        print("       "+EM_CMD.success_low_color+"plot_pts = False"+EM_CMD.type_color+" : bool "+EM_CMD.base_color+"= afficher ou non les points initiaux, avec une couleur par fichier (inutile si m_type='h')")
        print("")
        print("exemples : "+EM_CMD.code_color+'python3 Traitement_CMD_v6.py CMDEX_grid "Easting" "Northing" ')
        print("           "+EM_CMD.code_color+'python3 Traitement_CMD_v6.py CMDEX_grid "X_int" "Y_int" file_list="[res.dat]" m_type=k radius=5 seuil=4 prec=100 all_models=True plot_pts=True nb_data=1')
        print(EM_CMD.base_color)
    if help_id == None or help_id == 5:
        print(EM_CMD.title_color)
        curr_title = "[5] Liste des appareils enregistrés :"
        print(curr_title+EM_CMD.title_next_color+"."*(nc-len(curr_title)))
        print(EM_CMD.bold_und_color)
        print("DESCRIPTION :"+EM_CMD.bold_color+" Affiche l'ensemble des appareils de la base 'Appareil.json'.")
        print("Chaque appareil est associé à un identifiant, qui peut être utilisé par la fonction CMD_exec_known_device pour lancer le traîtement des données .dat.")
        print(EM_CMD.code_color)
        print(">>> JSON_print_devices("+EM_CMD.success_low_color+"[uid]"+EM_CMD.code_color+")")
        print(EM_CMD.base_color)
        print("avec : "+EM_CMD.success_low_color+"uid"+EM_CMD.type_color+" : int "+EM_CMD.base_color+"= indentifiant de l'appareil dans la base JSON (laisser vide pour tout afficher)")
        print("")
        print("exemples : "+EM_CMD.code_color+'python3 Traitement_CMD_v6.py JSON_print_devices')
        print("           "+EM_CMD.code_color+'python3 Traitement_CMD_v6.py JSON_print_devices 4')
        print(EM_CMD.base_color)
    if help_id == None or help_id == 6:
        print(EM_CMD.title_color)
        curr_title = "[6] Ajouter un appareil :"
        print(curr_title+EM_CMD.title_next_color+"."*(nc-len(curr_title)))
        print(EM_CMD.bold_und_color)
        print("DESCRIPTION :"+EM_CMD.bold_color+" Ajoute un appareil la base 'Appareil.json' avec les paramètres spécifiés.")
        print(EM_CMD.code_color)
        print(">>> JSON_add_device("+EM_CMD.success_color+"app_name"+EM_CMD.code_color+","+EM_CMD.success_color+"config"+EM_CMD.code_color+","+EM_CMD.success_color+"nb_ecarts"+EM_CMD.code_color+","+
              EM_CMD.success_color+"nb_ecarts"+EM_CMD.code_color+","+EM_CMD.success_color+"TxRx"+EM_CMD.code_color+","+EM_CMD.success_color+"freq_list"+EM_CMD.code_color+","+
              EM_CMD.success_low_color+"[GPS"+EM_CMD.code_color+","+EM_CMD.success_low_color+"height"+EM_CMD.code_color+","+EM_CMD.success_low_color+"bucking_coil"+EM_CMD.code_color+","+
              EM_CMD.success_low_color+"coeff_construct]"+")")
        print(EM_CMD.base_color)
        print("avec : "+EM_CMD.success_color+"app_name"+EM_CMD.type_color+" : string "+EM_CMD.base_color+"= nom de l'appareil")
        print("       "+EM_CMD.success_color+"config"+EM_CMD.type_color+" : string "+EM_CMD.base_color+"= configuration des bobines (HCP,VCP,VVCP,PRP,PAR,CUS)")
        print("       "+EM_CMD.success_color+"nb_ecarts"+EM_CMD.type_color+" : int "+EM_CMD.base_color+"= nombre de bobines")
        print("       "+EM_CMD.success_color+"TxRx"+EM_CMD.type_color+" : float[] "+EM_CMD.base_color+"= positions des bobines recepteurs (en m)")
        print("       "+EM_CMD.success_color+"freq_list"+EM_CMD.type_color+" : float[] "+EM_CMD.base_color+"= fréquences du signal (en ???)")
        print("       "+EM_CMD.success_low_color+"GPS = True"+EM_CMD.type_color+" : bool "+EM_CMD.base_color+"= présence ou non de données GPS")
        print("       "+EM_CMD.success_low_color+"height = 0.1"+EM_CMD.type_color+" : float "+EM_CMD.base_color+"= hauteur de l'appareil par rapport au sol (en m)")
        print("       "+EM_CMD.success_low_color+"bucking_coil = 0"+EM_CMD.type_color+" : int "+EM_CMD.base_color+"= numéro de la bucking coil parmi les bobines (0 si inexistante)")
        print("       "+EM_CMD.success_low_color+"coeff_construct = 1.0"+EM_CMD.type_color+" : float "+EM_CMD.base_color+"= coefficient de l'appareil (fourni par le constructeur)")
        print("")
        print("exemples : "+EM_CMD.code_color+'python3 Traitement_CMD_v6.py JSON_add_device "dummy" "PAR" 5 "[0.24,0.52,0.91,1.2,1.45]" 40000')
        print("           "+EM_CMD.code_color+'python3 Traitement_CMD_v6.py JSON_add_device "mini3L" "VCP" 3 "0.32 0.71 1.18 " [30000] height=0.2 "GPS = False"')
    if help_id == None or help_id == 7:
        print(EM_CMD.title_color)
        curr_title = "[7] Supprimer un appareil enregistré :"
        print(curr_title+EM_CMD.title_next_color+"."*(nc-len(curr_title)))
        print(EM_CMD.bold_und_color)
        print("DESCRIPTION :"+EM_CMD.bold_color+" Supprime l'appareil associé à l'identifiant choisi de la base 'Appareil.json'.")
        print(EM_CMD.code_color)
        print(">>> JSON_remove_device("+EM_CMD.success_low_color+"[uid]"+EM_CMD.code_color+")")
        print(EM_CMD.base_color)
        print("avec : "+EM_CMD.success_low_color+"uid"+EM_CMD.type_color+" : int "+EM_CMD.base_color+"= indentifiant de l'appareil dans la base JSON (laisser vide pour supprimer le dernier)")
        print("")
        print("exemples : "+EM_CMD.code_color+'python3 Traitement_CMD_v6.py JSON_remove_device')
        print("           "+EM_CMD.code_color+'python3 Traitement_CMD_v6.py JSON_remove_device 0')
        print(EM_CMD.base_color)
    if help_id == None or help_id == 8:
        print(EM_CMD.title_color)
        curr_title = "[8] Changement de la date d'un fichier .dat :"
        print(curr_title+EM_CMD.title_next_color+"."*(nc-len(curr_title)))
        print(EM_CMD.bold_und_color)
        print("DESCRIPTION :"+EM_CMD.bold_color+" Permet de corriger toutes les lignes d'un fichier avec la date spécifiée si celle-ci est incorrecte.")
        print(EM_CMD.code_color)
        print(">>> DAT_change_date("+EM_CMD.success_color+"file_list"+EM_CMD.code_color+","+EM_CMD.success_color+"date_str"+EM_CMD.code_color+","+EM_CMD.success_low_color+"[sep"+EM_CMD.code_color+","+
              EM_CMD.success_low_color+"replace"+EM_CMD.code_color+","+EM_CMD.success_low_color+"output_file]"+EM_CMD.code_color+")")
        print(EM_CMD.base_color)
        print("avec : "+EM_CMD.success_color+"file_list"+EM_CMD.type_color+" : str[] "+EM_CMD.base_color+"= liste des fichiers à traiter")
        print("       "+EM_CMD.success_color+"date_str"+EM_CMD.type_color+" : str "+EM_CMD.base_color+'= nouvelle date (format "mois/jour/année")')
        print("       "+EM_CMD.success_low_color+"sep = '\\t'"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= caractère de séparation du .dat (par défaut '\\t')")
        print("       "+EM_CMD.success_low_color+"replace = False"+EM_CMD.type_color+" : bool "+EM_CMD.base_color+"= si le résultat est mis dans le fichier de départ (sinon, un nouveau est créé avec le suffixe '_corr')")
        print("       "+EM_CMD.success_low_color+"output_file_list = None"+EM_CMD.type_color+" : str[] "+EM_CMD.base_color+"= nom des fichier de sortie, n'est pas pris en compte si replace=True")
        print("")
        print("exemples : "+EM_CMD.code_color+'python3 Traitement_CMD_v6.py DAT_change_date "path/to/file/very_nice_data.dat" "12/24/2020"')
        print("           "+EM_CMD.code_color+'python3 Traitement_CMD_v6.py DAT_change_date "[path/to/file/wrong_date.dat,path/to/otherfile/we_r_not_in_2000.dat]" "02/29/2024" "sep=,"')
        print(EM_CMD.base_color)
    if help_id == None or help_id == 9:
        print(EM_CMD.title_color)
        curr_title = "[9] Suppression d'une colonne surnuméraire dans un fichier .dat :"
        print(curr_title+EM_CMD.title_next_color+"."*(nc-len(curr_title)))
        print(EM_CMD.bold_und_color)
        print("DESCRIPTION :"+EM_CMD.bold_color+" Permet de retirer une entête de colonne si aucune donnée ne lui est associé, pour éviter de décaler le reste du jeu de données.")
        print(EM_CMD.code_color)
        print(">>> DAT_pop_and_dec("+EM_CMD.success_color+"file_list"+EM_CMD.code_color+","+EM_CMD.success_color+"colsup"+EM_CMD.code_color+","+EM_CMD.success_low_color+"[sep"+EM_CMD.code_color+","+
              EM_CMD.success_low_color+"replace"+EM_CMD.code_color+","+EM_CMD.success_low_color+"output_file]"+EM_CMD.code_color+")")
        print(EM_CMD.base_color)
        print("avec : "+EM_CMD.success_color+"file_list"+EM_CMD.type_color+" : str[] "+EM_CMD.base_color+"= liste des fichiers à traiter")
        print("       "+EM_CMD.success_color+"colsup"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= nom de colonne à supprimer")
        print("       "+EM_CMD.success_low_color+"sep = '\\t'"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= caractère de séparation du .dat (par défaut '\\t')")
        print("       "+EM_CMD.success_low_color+"replace = False"+EM_CMD.type_color+" : bool "+EM_CMD.base_color+"= si le résultat est mis dans le fichier de départ (sinon, un nouveau est créé avec le suffixe '_corr')")
        print("       "+EM_CMD.success_low_color+"output_file_list = None"+EM_CMD.type_color+" : str[] "+EM_CMD.base_color+"= nom des fichier de sortie, n'est pas pris en compte si replace=True")
        print("")
        print("exemples : "+EM_CMD.code_color+'python3 Traitement_CMD_v6.py DAT_pop_and_dec "path/to/file/very_nice_data.dat" Note')
        print("           "+EM_CMD.code_color+'python3 Traitement_CMD_v6.py DAT_pop_and_dec "[path/to/file/2muchnames.dat,path/to/otherfile/y_zer_is_no_time.dat]" "Time" "sep=," replace=True')
        print(EM_CMD.base_color)
    if help_id == None or help_id == 10:
        print(EM_CMD.title_color)
        curr_title = "[10] Inversion de deux colonnes dans un fichier .dat :"
        print(curr_title+EM_CMD.title_next_color+"."*(nc-len(curr_title)))
        print(EM_CMD.bold_und_color)
        print("DESCRIPTION :"+EM_CMD.bold_color+" Permet d'échanger les valeurs de deux colonnes, tout en conservant leur position.")
        print(EM_CMD.code_color)
        print(">>> DAT_switch_cols("+EM_CMD.success_color+"file_list"+EM_CMD.code_color+","+EM_CMD.success_color+"col_a"+EM_CMD.code_color+","+EM_CMD.success_color+"col_b"+EM_CMD.code_color+","+
              EM_CMD.success_low_color+"[sep"+EM_CMD.code_color+","+EM_CMD.success_low_color+"replace"+EM_CMD.code_color+","+EM_CMD.success_low_color+"output_file]"+EM_CMD.code_color+")")
        print(EM_CMD.base_color)
        print("avec : "+EM_CMD.success_color+"file_list"+EM_CMD.type_color+" : str[] "+EM_CMD.base_color+"= liste des fichiers à traiter")
        print("       "+EM_CMD.success_color+"col_a"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= nom de la première colonne")
        print("       "+EM_CMD.success_color+"col_b"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= nom de la deuxième colonne")
        print("       "+EM_CMD.success_low_color+"sep = '\\t'"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= caractère de séparation du .dat (par défaut '\\t')")
        print("       "+EM_CMD.success_low_color+"replace = False"+EM_CMD.type_color+" : bool "+EM_CMD.base_color+"= si le résultat est mis dans le fichier de départ (sinon, un nouveau est créé avec le suffixe '_corr')")
        print("       "+EM_CMD.success_low_color+"output_file_list = None"+EM_CMD.type_color+" : str[] "+EM_CMD.base_color+"= nom des fichier de sortie, n'est pas pris en compte si replace=True")
        print("")
        print("exemples : "+EM_CMD.code_color+'python3 Traitement_CMD_v6.py DAT_switch_cols "path/to/file/very_nice_data.dat" "Easting" "Northing"')
        print("           "+EM_CMD.code_color+'python3 Traitement_CMD_v6.py DAT_switch_cols "[path/to/file/east_is_not_north.dat,path/to/otherfile/very_mean_file_not_working.dat]" "Cond.1[mS/m]" "Inph.1[ppt]" "sep=," replace=True')
        print(EM_CMD.base_color)
    if help_id == None or help_id == 11:
        print(EM_CMD.title_color)
        curr_title = "[11] Suppression de colonnes dans un fichier .dat :"
        print(curr_title+EM_CMD.title_next_color+"."*(nc-len(curr_title)))
        print(EM_CMD.bold_und_color)
        print("DESCRIPTION :"+EM_CMD.bold_color+" Permet de supprimer les colonnes inutiles. Utile pour faire le tri ou pour réduire l'utilisation mémoire.")
        print('Si "keep=True", alors ne garde que les colonnes spécifiées (fonction inverse).')
        print(EM_CMD.code_color)
        print(">>> DAT_remove_cols("+EM_CMD.success_color+"file_list"+EM_CMD.code_color+","+EM_CMD.success_color+"colsup_list"+EM_CMD.code_color+","+EM_CMD.success_color+"[keep"+EM_CMD.code_color+","+
              EM_CMD.success_low_color+"sep"+EM_CMD.code_color+","+EM_CMD.success_low_color+"replace"+EM_CMD.code_color+","+EM_CMD.success_low_color+"output_file]"+EM_CMD.code_color+")")
        print(EM_CMD.base_color)
        print("avec : "+EM_CMD.success_color+"file_list"+EM_CMD.type_color+" : str[] "+EM_CMD.base_color+"= liste des fichiers à traiter")
        print("       "+EM_CMD.success_color+"colsup_list"+EM_CMD.type_color+" : str[] "+EM_CMD.base_color+"= nom des colonnes concernées (ne pas mettre de crochets pour délimiter la liste)")
        print("       "+EM_CMD.success_low_color+"keep = False"+EM_CMD.type_color+" : bool "+EM_CMD.base_color+"= si True, on ne garde que les colonnes spécifiées (sinon ce sont celles qu'on supprime)")
        print("       "+EM_CMD.success_low_color+"sep = '\\t'"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= caractère de séparation du .dat (par défaut '\\t')")
        print("       "+EM_CMD.success_low_color+"replace = False"+EM_CMD.type_color+" : bool "+EM_CMD.base_color+"= si le résultat est mis dans le fichier de départ (sinon, un nouveau est créé avec le suffixe '_corr')")
        print("       "+EM_CMD.success_low_color+"output_file_list = None"+EM_CMD.type_color+" : str[] "+EM_CMD.base_color+"= nom des fichier de sortie, n'est pas pris en compte si replace=True")
        print("")
        print("exemples : "+EM_CMD.code_color+'python3 Traitement_CMD_v6.py DAT_remove_cols "path/to/file/very_nice_data.dat" "Error1[%],Error2[%],Error3[%]"')
        print("           "+EM_CMD.code_color+'python3 Traitement_CMD_v6.py DAT_remove_cols "[path/to/file/Error[%]_was_an_error.dat,path/to/otherfile/where_is_the_Note_anyways.dat]" "x[m],y[m],Cond.1[mS/m],Inph.1[ppt],Cond.2[mS/m],Inph.2[ppt],Cond.3[mS/m]" keep=True')
        print(EM_CMD.base_color)
    if help_id == None or help_id == 12:
        print(EM_CMD.title_color)
        curr_title = "[12] Suppression de données (valeurs) dans un fichier .dat :"
        print(curr_title+EM_CMD.title_next_color+"."*(nc-len(curr_title)))
        print(EM_CMD.bold_und_color)
        print("DESCRIPTION :"+EM_CMD.bold_color+" Permet d'effacer les valeurs sur un bloc de lignes, sur des colonnes spécifiques. Sert à pouvoir traiter les données défectueuses non vides comme des données manquantes.")
        print(EM_CMD.code_color)
        print(">>> DAT_remove_data("+EM_CMD.success_color+"file_list"+EM_CMD.code_color+","+EM_CMD.success_color+"colsup_list"+EM_CMD.code_color+","+EM_CMD.success_color+"i_min"+EM_CMD.code_color+","+
              EM_CMD.success_color+"i_max"+EM_CMD.code_color+","+EM_CMD.success_low_color+"[sep"+EM_CMD.code_color+","+EM_CMD.success_low_color+"replace"+EM_CMD.code_color+","+
              EM_CMD.success_low_color+"output_file]"+EM_CMD.code_color+")")
        print(EM_CMD.base_color)
        print("avec : "+EM_CMD.success_color+"file_list"+EM_CMD.type_color+" : str[] "+EM_CMD.base_color+"= liste des fichiers à traiter")
        print("       "+EM_CMD.success_color+"colsup_list"+EM_CMD.type_color+" : str[] "+EM_CMD.base_color+"= nom des colonnes concernées (ne pas mettre de crochets pour délimiter la liste)")
        print("       "+EM_CMD.success_color+"i_min"+EM_CMD.type_color+" : int "+EM_CMD.base_color+"= première ligne concernée")
        print("       "+EM_CMD.success_color+"i_max"+EM_CMD.type_color+" : int "+EM_CMD.base_color+"= dernière ligne concernée")
        print("       "+EM_CMD.success_low_color+"sep = '\\t'"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= caractère de séparation du .dat (par défaut '\\t')")
        print("       "+EM_CMD.success_low_color+"replace = False"+EM_CMD.type_color+" : bool "+EM_CMD.base_color+"= si le résultat est mis dans le fichier de départ (sinon, un nouveau est créé avec le suffixe '_corr')")
        print("       "+EM_CMD.success_low_color+"output_file_list = None"+EM_CMD.type_color+" : str[] "+EM_CMD.base_color+"= nom des fichier de sortie, n'est pas pris en compte si replace=True")
        print("")
        print("exemples : "+EM_CMD.code_color+'python3 Traitement_CMD_v6.py DAT_remove_data "path/to/file/very_nice_data.dat" "x[m],y[m]" 1234 1324')
        print("           "+EM_CMD.code_color+'python3 Traitement_CMD_v6.py DAT_remove_data "[path/to/file/begone_failure.dat,path/to/otherfile/thanos_snapping_data.dat]" "Easting,Northing" 42 69 "sep=," replace=True')
        print(EM_CMD.base_color)
    if help_id == None or help_id == 13:
        print(EM_CMD.title_color)
        curr_title = "[13] Changement du séparateur dans un fichier .dat :"
        print(curr_title+EM_CMD.title_next_color+"."*(nc-len(curr_title)))
        print(EM_CMD.bold_und_color)
        print("DESCRIPTION :"+EM_CMD.bold_color+" Permet de modifier le séparateur utilisé dans certains fichiers .dat. Utile dans le cas où on souhaite utiliser plusieurs fichiers dans un même traitement.")
        print(EM_CMD.code_color)
        print(">>> DAT_change_sep("+EM_CMD.success_color+"file_list"+EM_CMD.code_color+","+EM_CMD.success_color+"sep"+EM_CMD.code_color+","+EM_CMD.success_color+"new_sep"+EM_CMD.code_color+","+
              EM_CMD.success_low_color+"[replace"+EM_CMD.code_color+","+EM_CMD.success_low_color+"output_file]"+EM_CMD.code_color+")")
        print(EM_CMD.base_color)
        print("avec : "+EM_CMD.success_color+"file_list"+EM_CMD.type_color+" : str[] "+EM_CMD.base_color+"= liste des fichiers à traiter")
        print("       "+EM_CMD.success_color+"sep"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= caractère de séparation d'origine du .dat")
        print("       "+EM_CMD.success_color+"new_sep"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= caractère de séparation souhaité pour le .dat")
        print("       "+EM_CMD.success_low_color+"replace = False"+EM_CMD.type_color+" : bool "+EM_CMD.base_color+"= si le résultat est mis dans le fichier de départ (sinon, un nouveau est créé avec le suffixe '_corr')")
        print("       "+EM_CMD.success_low_color+"output_file_list = None"+EM_CMD.type_color+" : str[] "+EM_CMD.base_color+"= nom des fichier de sortie, n'est pas pris en compte si replace=True")
        print("")
        print("exemples : "+EM_CMD.code_color+'python3 Traitement_CMD_v6.py DAT_change_sep "path/to/file/very_nice_data.dat" "\\t" ","')
        print("           "+EM_CMD.code_color+'python3 Traitement_CMD_v6.py DAT_change_sep "[path/to/file/comma_put_me_in_coma.dat,path/to/otherfile/i_dont_have_NaN.dat]" "," "!" replace=True "output_file=path/to/res_file/very_surprised.dat"')
        print(EM_CMD.base_color)
    if help_id == None or help_id == 14:
        print(EM_CMD.title_color)
        curr_title = "[14] Fusion de bases B1 et B2 dans un même fichier .dat :"
        print(curr_title+EM_CMD.title_next_color+"."*(nc-len(curr_title)))
        print(EM_CMD.bold_und_color)
        print("DESCRIPTION :"+EM_CMD.bold_color+" Dans le cas de deux bases (avant et après prospection) dans deux fichiers à part, permet de rassembler les données en un même fichier.")
        print("Actualise l'index des bases par rapport au profils du fichier de même prospection, B1 est placé avant et B2 après. Procédure essentielle pour l'ajustement par base.")
        print(EM_CMD.code_color)
        print(">>> DAT_fuse_bases("+EM_CMD.success_color+"file_B1"+EM_CMD.code_color+","+EM_CMD.success_color+"file_B2"+EM_CMD.code_color+","+EM_CMD.success_color+"file_prof"+EM_CMD.code_color+","+
              EM_CMD.success_low_color+"[sep"+EM_CMD.code_color+","+EM_CMD.success_low_color+"output_file]"+EM_CMD.code_color+")")
        print(EM_CMD.base_color)
        print("avec : "+EM_CMD.success_color+"file_B1"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= fichier de la première base B1")
        print("       "+EM_CMD.success_color+"file_B2"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= fichier de la seconde base B2")
        print("       "+EM_CMD.success_color+"file_prof"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= fichier des profils (doit avoir déjà été interpolé)")
        print("       "+EM_CMD.success_low_color+"sep = '\\t'"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= caractère de séparation du .dat (par défaut '\\t')")
        print("       "+EM_CMD.success_low_color+"output_file = None"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= nom du fichier de sortie (sinon, un nouveau est créé avec le suffixe '_B')")
        print("")
        print("exemples : "+EM_CMD.code_color+'python3 Traitement_CMD_v6.py DAT_fuse_bases "path/to/file/B1.dat" "path/to/file/B2.dat" "path/to/file/very_nice_data.dat"')
        print("           "+EM_CMD.code_color+'python3 Traitement_CMD_v6.py DAT_fuse_bases "path/to/file/I_am_before.dat" "path/to/file/I_am_after.dat" "path/to/file/I_am_the_night.dat" "sep=," "output_file=path/to/res_file/I_am_eternal.dat"')
        print(EM_CMD.base_color)
    if help_id == None or help_id == 15:
        print(EM_CMD.title_color)
        curr_title = "[15] Affichage interactif de figures en .pickle :"
        print(curr_title+EM_CMD.title_next_color+"."*(nc-len(curr_title)))
        print(EM_CMD.bold_und_color)
        print("DESCRIPTION :"+EM_CMD.bold_color+" Il est possible d'enregistrer les figures sous format image avec l'interface de matplotlib, mais on y pert toute possibilité d'interaction (zoom, translation, bordures...).")
        print("Les figures importantes (en général celles créées en fin d'exécution) sont automatiquement enregistrées sous format .pickle dans le dossier 'Output'.")
        print("Cette fonction permet de les ouvrir de nouveau avec toutes les fonctionalités. Il n'est pas nécessaire de spécifier le chemin entier si elles sont dans le dossier 'Output'.")
        print("Attention, le dossier est entièrement vidé avant chaque nouvelle exécution. Pensez à déplacer les figures qui vous intéresse.")
        print(EM_CMD.code_color)
        print(">>> FIG_display_fig("+EM_CMD.success_low_color+"[file_list]"+EM_CMD.code_color+")")
        print(EM_CMD.base_color)
        print("avec : "+EM_CMD.success_low_color+"file_list = None"+EM_CMD.type_color+" : str[] "+EM_CMD.base_color+"= liste des fichiers à traiter (laisser vide pour traiter tous les fichiers du dossier 'Output')")
        print("")
        print("exemples : "+EM_CMD.code_color+'python3 Traitement_CMD_v6.py FIG_display_fig')
        print("           "+EM_CMD.code_color+'python3 Traitement_CMD_v6.py FIG_display_fig "0.pickle,1.pickle,2.pickle,3.pickle,4.pickle,5.pickle"')
        print(EM_CMD.base_color)
    if help_id == None or help_id == 16:
        print(EM_CMD.title_color)
        curr_title = "[16] Affichage et enregistrement de figures (nuage de points) :"
        print(curr_title+EM_CMD.title_next_color+"."*(nc-len(curr_title)))
        print(EM_CMD.bold_und_color)
        print("DESCRIPTION :"+EM_CMD.bold_color+" Permet d'obtenir les nuages de points des données brutes.")
        print("Les figures sont automatiquement enregistrées dans le dossier 'Output' avec le préfixe 'FIG_'.")
        print(EM_CMD.code_color)
        print(">>> FIG_plot_data("+EM_CMD.success_color+"file"+EM_CMD.code_color+","+EM_CMD.success_low_color+"[sep"+EM_CMD.code_color+","+EM_CMD.success_low_color+"col_x"+EM_CMD.code_color+","+
              EM_CMD.success_low_color+"col_y"+EM_CMD.code_color+","+EM_CMD.success_low_color+"start"+EM_CMD.code_color+","+EM_CMD.success_low_color+"nb_data]"+EM_CMD.code_color+")")
        print(EM_CMD.base_color)
        print("avec : "+EM_CMD.success_color+"file"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= nom du fichier")
        print("       "+EM_CMD.success_low_color+"sep = '\\t'"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= caractère de séparation du .dat (par défaut '\\t')")
        print("       "+EM_CMD.success_low_color+"col_x = None"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= nom de la colonne des coordonnées x (par défaut la première)")
        print("       "+EM_CMD.success_low_color+"col_y = None"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= nom de la colonne des coordonnées y (par défaut la deuxième)")
        print("       "+EM_CMD.success_low_color+"start = 2"+EM_CMD.type_color+" : int "+EM_CMD.base_color+"= indice de la première colonne de données à traiter (sans compter les colonnes surnuméraires)")
        print("       "+EM_CMD.success_low_color+"nb_data = None"+EM_CMD.type_color+" : int "+EM_CMD.base_color+"= nombres de données à traiter (par défaut, prend toutes les colonnes à partir de 'start')")
        print("")
        print("exemples : "+EM_CMD.code_color+'python3 Traitement_CMD_v6.py FIG_plot_data "path/to/file/very_nice_data.dat"')
        print("           "+EM_CMD.code_color+'python3 Traitement_CMD_v6.py FIG_plot_data "path/to/file/day_ta.dat" col_x=X_int col_y=Y_int nb_data=1')
        print(EM_CMD.base_color)
    print(EM_CMD.success_color+"~"*nc)
    print(EM_CMD.base_color)

def CMD_exec_known_device(uid,file_list,file_list_rev,sep,output_file,output_file_base,split,sup_na,regr,corr_base,choice):
    app_data = EM_CMD.JSON_find_device(uid)
    print(app_data)
    main(app_data,file_list,file_list_rev,sep,output_file,output_file_base,split,sup_na,regr,corr_base,choice)
    os.chdir(CONFIG.script_path)
    EM_CMD.CMD_succ_mess("Fin de l'exécution !")
    EM_CMD.keep_plt_for_cmd()

def CMD_exec_new_device(app_name,config,nb_ecarts,TxRx,freq_list,gps,height,bucking_coil,coeff_construct,file_list,file_list_rev,sep,output_file,output_file_base,split,sup_na,regr,corr_base,choice):
    app_data = EM_CMD.JSON_add_device(app_name,config,nb_ecarts,TxRx,freq_list,gps,height,bucking_coil,coeff_construct,autosave=False)
    print(app_data)
    main(app_data,file_list,file_list_rev,sep,sup_na,output_file,output_file_base,split,regr,corr_base,choice)
    os.chdir(CONFIG.script_path)
    EM_CMD.CMD_succ_mess("Fin de l'exécution !")
    EM_CMD.keep_plt_for_cmd()

def CMDEX_evol_profils(file_prof_list,file_base_list,sep,output_file_list,replace,start,nb_data,nb_ecarts,diff,auto_adjust,man_adjust,line):
    if len(file_prof_list) != len(file_base_list):
        EM_CMD.CMD_err_mess("Le nombre de fichiers profil ({}) et base ({}) ne correspondent pas".format(len(file_prof_list),len(file_base_list)))
    if not replace and len(file_prof_list) != len(output_file_list):
        EM_CMD.CMD_err_mess("Le nombre de fichiers profil ({}) et résultat ({}) ne correspondent pas".format(len(file_prof_list),len(output_file_list)))
    for i in range(len(file_prof_list)):
        data_prof = EM_CMD.CMD_check_time_date(file_prof_list[i],sep)
        data_base = EM_CMD.CMD_check_time_date(file_base_list[i],sep)
        res = EM_CMD.CMD_evol_profils(data_prof,data_base,file_prof_list[i],start,nb_data,nb_ecarts,diff=diff,auto_adjust=auto_adjust,man_adjust=man_adjust,verif=True,line=line)
        if replace:
            res.to_csv(file_prof_list[i], index=False, sep=sep)
        elif output_file_list == None:
            continue
        else:
            res.to_csv(output_file_list[i], index=False, sep=sep)
    os.chdir(CONFIG.script_path)
    EM_CMD.CMD_succ_mess("Fin de l'exécution !")
    EM_CMD.keep_plt_for_cmd()

def CMDEX_grid(col_x,col_y,file_list,sep,output_file,m_type,radius,start,nb_data,nb_ecarts,prec,seuil,i_method,no_crop,all_models,plot_pts):
    EM_CMD.CMD_grid(col_x,col_y,file_list,sep,output_file,m_type,radius,start,nb_data,nb_ecarts,prec,seuil,i_method,no_crop,all_models,plot_pts)
    os.chdir(CONFIG.script_path)
    EM_CMD.CMD_succ_mess("Fin de l'exécution !")
    EM_CMD.keep_plt_for_cmd()

def JSON_print_devices(uid):
    EM_CMD.JSON_print_devices(uid=uid)

def JSON_add_device(app_name,config,nb_ecarts,TxRx,freq_list,gps,height,bucking_coil,coeff_construct):
    EM_CMD.JSON_add_device(app_name,config,nb_ecarts,TxRx,freq_list,gps,height,bucking_coil,coeff_construct,autosave=True)
    os.chdir(CONFIG.script_path)
    EM_CMD.CMD_succ_mess("Appareil ajouté avec succès !")

def JSON_remove_device(uid):
    EM_CMD.JSON_remove_device(uid)
    os.chdir(CONFIG.script_path)
    EM_CMD.CMD_succ_mess("Appareil supprimé avec succès !")

def DAT_change_date(file_list,date_str,sep,replace,output_file_list):
    EM_CMD.DAT_change_date(file_list,date_str,sep,replace,output_file_list)
    os.chdir(CONFIG.script_path)
    EM_CMD.CMD_succ_mess("Date modifiée avec succès !")

def DAT_pop_and_dec(file_list,colsup,sep,replace,output_file_list):
    EM_CMD.DAT_pop_and_dec(file_list,colsup,sep,replace,output_file_list)
    os.chdir(CONFIG.script_path)
    EM_CMD.CMD_succ_mess("Nom de colonne supprimé avec succès !")

def DAT_switch_cols(file_list,col_a,col_b,sep,replace,output_file_list):
    EM_CMD.DAT_switch_cols(file_list,col_a,col_b,sep,replace,output_file_list)
    os.chdir(CONFIG.script_path)
    EM_CMD.CMD_succ_mess("Colonnes échangées avec succès !")

def DAT_remove_cols(file_list,colsup_list,keep,sep,replace,output_file_list):
    EM_CMD.DAT_remove_cols(file_list,colsup_list,keep,sep,replace,output_file_list)
    os.chdir(CONFIG.script_path)
    EM_CMD.CMD_succ_mess("Colonnes supprimées avec succès !")

def DAT_remove_data(file_list,colsup_list,i_min,i_max,sep,replace,output_file_list):
    EM_CMD.DAT_remove_data(file_list,colsup_list,i_min,i_max,sep,replace,output_file_list)
    os.chdir(CONFIG.script_path)
    EM_CMD.CMD_succ_mess("Données supprimées avec succès !")

def DAT_change_sep(file_list,sep,new_sep,replace,output_file_list):
    EM_CMD.DAT_change_sep(file_list,sep,new_sep,replace,output_file_list)
    os.chdir(CONFIG.script_path)
    EM_CMD.CMD_succ_mess("Séparateur modifié avec succès !")

def DAT_fuse_bases(file_B1,file_B2,file_prof,sep,output_file):
    EM_CMD.DAT_fuse_bases(file_B1,file_B2,file_prof,sep,output_file)
    os.chdir(CONFIG.script_path)
    EM_CMD.CMD_succ_mess("Bases fusionnées avec succès !")

def FIG_display_fig(file_list):
    EM_CMD.FIG_display_fig(file_list)
    os.chdir(CONFIG.script_path)

def FIG_plot_data(file,sep,col_x,col_y,start,nb_data):
    EM_CMD.FIG_plot_data(file,sep,col_x,col_y,start,nb_data)
    os.chdir(CONFIG.script_path)

# lecture de la commande utilisateur

if __name__ == '__main__':
    # tekst = matplotlib.get_backend()
    # print("Backend = ", tekst)
    # plt.switch_backend('Agg')
    # plt.switch_backend('TkAgg')
    # tekst = matplotlib.get_backend()
    # print("Backend = ", tekst)
    try:
        if len(sys.argv) == 1:
            CMD_help()
        elif sys.argv[1] == "0":
            print("Appel passif")
        elif globals()[sys.argv[1]] == CMD_help:
            if len(sys.argv) > 2:
                if sys.argv[2] == "CMD_help" or sys.argv[2] == "0":
                    CMD_help(0)
                elif sys.argv[2] == "CMD_exec_known_device" or sys.argv[2] == "1":
                    CMD_help(1)
                elif sys.argv[2] == "CMD_exec_new_device" or sys.argv[2] == "2":
                    CMD_help(2)
                elif sys.argv[2] == "CMDEX_evol_profils" or sys.argv[2] == "3":
                    CMD_help(3)
                elif sys.argv[2] == "CMDEX_grid" or sys.argv[2] == "4":
                    CMD_help(4)
                elif sys.argv[2] == "JSON_print_devices" or sys.argv[2] == "5":
                    CMD_help(5)
                elif sys.argv[2] == "JSON_add_device" or sys.argv[2] == "6":
                    CMD_help(6)
                elif sys.argv[2] == "JSON_remove_device" or sys.argv[2] == "7":
                    CMD_help(7)
                elif sys.argv[2] == "DAT_change_date" or sys.argv[2] == "8":
                    CMD_help(8)
                elif sys.argv[2] == "DAT_pop_and_dec" or sys.argv[2] == "9":
                    CMD_help(9)
                elif sys.argv[2] == "DAT_switch_cols" or sys.argv[2] == "10":
                    CMD_help(10)
                elif sys.argv[2] == "DAT_remove_cols" or sys.argv[2] == "11":
                    CMD_help(11)
                elif sys.argv[2] == "DAT_remove_data" or sys.argv[2] == "12":
                    CMD_help(12)
                elif sys.argv[2] == "DAT_change_sep" or sys.argv[2] == "13":
                    CMD_help(13)
                elif sys.argv[2] == "DAT_fuse_bases" or sys.argv[2] == "14":
                    CMD_help(14)
                elif sys.argv[2] == "FIG_display_fig" or sys.argv[2] == "15":
                    CMD_help(15)
                elif sys.argv[2] == "FIG_plot_data" or sys.argv[2] == "16":
                    CMD_help(16)
                else:
                    if sys.argv[2] in globals():
                        EM_CMD.CMD_err_mess("La fonction est protégée : aucune aide")
                    else:
                        EM_CMD.CMD_err_mess("La fonction ou l'indice ne correspond à aucune fonction connue")
            else:
                CMD_help()
        elif globals()[sys.argv[1]] == CMD_exec_known_device:
            uid = int(sys.argv[2])
            file_list = None
            file_list_rev = None
            sep = '\t'
            output_file = "res.dat"
            output_file_base = "res_B.dat"
            split = False
            sup_na = True
            regr = False
            corr_base = True
            choice = False
            if len(sys.argv) > 3:
                opt_params = EM_CMD.CMD_optargs_list(sys.argv[3:], ["file_list","file_list_rev","sep","output_file","output_file_base","split","sup_na","regr","corr_base","choice"], [[str],[str],str,str,str,bool,bool,bool,bool,bool])
                file_list = opt_params.get("file_list", None)
                file_list_rev = opt_params.get("file_list_rev", None)
                sep = opt_params.get("sep", '\t')
                output_file = opt_params.get("output_file", "res.dat")
                output_file_base = opt_params.get("output_file_base", "res_B.dat")
                split = opt_params.get("split", False)
                sup_na = opt_params.get("sup_na", True)
                regr = opt_params.get("regr", False)
                corr_base = opt_params.get("corr_base", True)
                choice = opt_params.get("choice", False)
            CMD_exec_known_device(uid,file_list,file_list_rev,sep,output_file,output_file_base,split,sup_na,regr,corr_base,choice)
        elif globals()[sys.argv[1]] == CMD_exec_new_device:
            app_name = sys.argv[2]
            config = sys.argv[3]
            nb_ecarts = int(sys.argv[4])
            TxRx = EM_CMD.CMD_split_list(sys.argv[5], float)
            freq_list = EM_CMD.CMD_split_list(sys.argv[6], float)
            gps = True
            height = 0.1
            bucking_coil = 0
            coeff_construct = 1.0
            file_list = None
            file_list_rev = None
            sep = '\t'
            output_file = "res.dat"
            output_file_base = "res_B.dat"
            split = False
            sup_na = True
            regr = False
            corr_base = True
            choice  = False
            if len(sys.argv) > 7:
                opt_params = EM_CMD.CMD_optargs_list(sys.argv[7:], ["GPS","height","bucking_coil","coeff_construct","file_list","file_list_rev","sep","output_file","output_file_base","split","sup_na","regr","corr_base","choice"], [bool,float,int,float,[str],[str],str,str,bool,bool,bool,bool,bool])
                gps = opt_params.get("GPS", True)
                height = opt_params.get("height", 0.1)
                bucking_coil = opt_params.get("bucking_coil", 0)
                coeff_construct = opt_params.get("coeff_construct", 1.0)
                file_list = opt_params.get("file_list", None)
                file_list_rev = opt_params.get("file_list_rev", None)
                sep = opt_params.get("sep", '\t')
                output_file = opt_params.get("output_file", "res.dat")
                output_file_base = opt_params.get("output_file_base", "res_B.dat")
                split = opt_params.get("split", False)
                sup_na = opt_params.get("sup_na", True)
                regr = opt_params.get("regr", False)
                corr_base = opt_params.get("corr_base", True)
                choice = opt_params.get("choice", False)
            CMD_exec_new_device(app_name,config,nb_ecarts,TxRx,freq_list,gps,height,bucking_coil,coeff_construct,file_list,file_list_rev,sep,output_file,output_file_base,split,sup_na,regr,corr_base,choice)
        elif globals()[sys.argv[1]] == CMDEX_evol_profils:
            file_prof_list = EM_CMD.CMD_split_list(sys.argv[2], str, path=True)
            file_base_list = EM_CMD.CMD_split_list(sys.argv[3], str, path=True)
            sep = '\t'
            replace = False
            output_file_list = None
            start = 7
            nb_data = 6
            nb_ecarts = nb_data//2
            diff = True
            auto_adjust = True
            man_adjust = False
            line = False
            if len(sys.argv) > 4:
                opt_params = EM_CMD.CMD_optargs_list(sys.argv[4:], ["sep","replace","output_file_list","start","nb_data","nb_ecarts","diff","auto_adjust","man_adjust","line"], [str,bool,[str],int,int,int,bool,bool,bool,bool])
                sep = opt_params.get("sep", '\t')
                output_file_list = opt_params.get("output_file_list", None)
                replace = opt_params.get("replace", False)
                start = opt_params.get("start", 7)
                nb_data = opt_params.get("nb_data", 6)
                nb_ecarts = opt_params.get("nb_ecarts", nb_data//2)
                diff = opt_params.get("diff", True)
                auto_adjust = opt_params.get("auto_adjust", True)
                man_adjust = opt_params.get("man_adjust", False)
                line = opt_params.get("line", False)
            CMDEX_evol_profils(file_prof_list,file_base_list,sep,output_file_list,replace,start,nb_data,nb_ecarts,diff,auto_adjust,man_adjust,line)
        elif globals()[sys.argv[1]] == CMDEX_grid:
            col_x = EM_CMD.CMD_str_clean(sys.argv[2], l=True, path=True)
            col_y = EM_CMD.CMD_str_clean(sys.argv[3], l=True, path=True)
            file_list = None
            sep = '\t'
            output_file = None
            m_type = None
            radius = 0
            start = 7
            nb_data = 6
            nb_ecarts = nb_data//2
            prec = 100
            seuil = 0
            i_method = None
            no_crop = False
            all_models = False
            plot_pts = False
            if len(sys.argv) > 4:
                opt_params = EM_CMD.CMD_optargs_list(sys.argv[4:], ["file_list","sep","output_file","m_type","radius","start","nb_data","nb_ecarts","prec","seuil","i_method","no_crop","all_models","plot_pts"], [[str],str,str,str,int,int,int,int,int,float,str,bool,bool,bool])
                file_list = opt_params.get("file_list", None)
                sep = opt_params.get("sep", '\t')
                output_file = opt_params.get("output_file", None)
                m_type = opt_params.get("m_type", None)
                radius = opt_params.get("radius", 0)
                start = opt_params.get("start", 7)
                nb_data = opt_params.get("nb_data", 6)
                nb_ecarts = opt_params.get("nb_ecarts", nb_data//2)
                prec = opt_params.get("prec", 100)
                seuil = opt_params.get("seuil", 0)
                i_method = opt_params.get("i_method", None)
                no_crop = opt_params.get("no_crop", False)
                all_models = opt_params.get("all_models", False)
                plot_pts = opt_params.get("plot_pts", False)
            CMDEX_grid(col_x,col_y,file_list,sep,output_file,m_type,radius,start,nb_data,nb_ecarts,prec,seuil,i_method,no_crop,all_models,plot_pts)
        elif globals()[sys.argv[1]] == JSON_print_devices:
            uid = None
            if len(sys.argv) > 2:
                opt_params = EM_CMD.CMD_optargs_list(sys.argv[2:], ["uid"], [int])
                uid = opt_params.get("uid", None)
            JSON_print_devices(uid)
        elif globals()[sys.argv[1]] == JSON_add_device:
            app_name = sys.argv[2]
            config = sys.argv[3]
            nb_ecarts = int(sys.argv[4])
            TxRx = EM_CMD.CMD_split_list(sys.argv[5], float)
            freq_list = EM_CMD.CMD_split_list(sys.argv[6], float)
            gps = True
            height = 0.1
            bucking_coil = 0
            coeff_construct = 1.0
            if len(sys.argv) > 7:
                opt_params = EM_CMD.CMD_optargs_list(sys.argv[7:], ["GPS","height","bucking_coil","coeff_construct"], [bool,float,float])
                #print(opt_params)
                gps = opt_params.get("GPS", True)
                height = opt_params.get("height", 0.1)
                bucking_coil = opt_params.get("bucking_coil", 0)
                coeff_construct = opt_params.get("coeff_construct", 1.0)
            JSON_add_device(app_name,config,nb_ecarts,TxRx,freq_list,gps,height,bucking_coil,coeff_construct)
        elif globals()[sys.argv[1]] == JSON_remove_device:
            uid = -1
            if len(sys.argv) > 2:
                opt_params = EM_CMD.CMD_optargs_list(sys.argv[2:], ["uid"], [int])
                uid = opt_params.get("uid", -1)
            JSON_remove_device(uid)
        elif globals()[sys.argv[1]] == DAT_change_date:
            file_list = EM_CMD.CMD_split_list(sys.argv[2], str, path=True)
            date_str = sys.argv[3]
            sep = '\t'
            replace = False
            output_file_list = None
            if len(sys.argv) > 4:
                opt_params = EM_CMD.CMD_optargs_list(sys.argv[4:], ["sep","replace","output_file_list"], [str,bool,[str]])
                sep = opt_params.get("sep", '\t')
                replace = opt_params.get("replace", False)
                output_file_list = opt_params.get("output_file_list", None)
            DAT_change_date(file_list,date_str,sep,replace,output_file_list)
        elif globals()[sys.argv[1]] == DAT_pop_and_dec:
            file_list = EM_CMD.CMD_split_list(sys.argv[2], str, path=True)
            colsup = EM_CMD.CMD_str_clean(sys.argv[3], l=True, path=True)
            sep = '\t'
            replace = False
            output_file_list = None
            if len(sys.argv) > 4:
                opt_params = EM_CMD.CMD_optargs_list(sys.argv[4:], ["sep","replace","output_file_list"], [str,bool,[str]])
                sep = opt_params.get("sep", '\t')
                replace = opt_params.get("replace", False)
                output_file_list = opt_params.get("output_file_list", None)
            DAT_pop_and_dec(file_list,colsup,sep,replace,output_file_list)
        elif globals()[sys.argv[1]] == DAT_switch_cols:
            file_list = EM_CMD.CMD_split_list(sys.argv[2], str, path=True)
            col_a = EM_CMD.CMD_str_clean(sys.argv[3], l=True, path=True)
            col_b = EM_CMD.CMD_str_clean(sys.argv[4], l=True, path=True)
            sep = '\t'
            replace = False
            output_file_list = None
            if len(sys.argv) > 5:
                opt_params = EM_CMD.CMD_optargs_list(sys.argv[5:], ["sep","replace","output_file_list"], [str,bool,[str]])
                sep = opt_params.get("sep", '\t')
                replace = opt_params.get("replace", False)
                output_file_list = opt_params.get("output_file_list", None)
            DAT_switch_cols(file_list,col_a,col_b,sep,replace,output_file_list)
        elif globals()[sys.argv[1]] == DAT_remove_cols:
            file_list = EM_CMD.CMD_split_list(sys.argv[2], str, path=True)
            colsup_list = EM_CMD.CMD_split_list(sys.argv[3], str, noclean=True)
            keep = False
            sep = '\t'
            replace = False
            output_file_list = None
            if len(sys.argv) > 4:
                opt_params = EM_CMD.CMD_optargs_list(sys.argv[4:], ["keep","sep","replace","output_file_list"], [bool,str,bool,[str]])
                keep = opt_params.get("keep", False)
                sep = opt_params.get("sep", '\t')
                replace = opt_params.get("replace", False)
                output_file_list = opt_params.get("output_file_list", None)
            DAT_remove_cols(file_list,colsup_list,keep,sep,replace,output_file_list)
        elif globals()[sys.argv[1]] == DAT_remove_data:
            file_list = EM_CMD.CMD_split_list(sys.argv[2], str, path=True)
            colsup_list = EM_CMD.CMD_split_list(sys.argv[3], str, noclean=True)
            i_min = int(sys.argv[4])
            i_max = int(sys.argv[5])
            sep = '\t'
            replace = False
            output_file_list = None
            if len(sys.argv) > 6:
                opt_params = EM_CMD.CMD_optargs_list(sys.argv[6:], ["sep","replace","output_file_list"], [str,bool,[str]])
                sep = opt_params.get("sep", '\t')
                replace = opt_params.get("replace", False)
                output_file_list = opt_params.get("output_file_list", None)
            DAT_remove_data(file_list,colsup_list,i_min,i_max,sep,replace,output_file_list)
        elif globals()[sys.argv[1]] == DAT_change_sep:
            file_list = EM_CMD.CMD_split_list(sys.argv[2], str, path=True)
            sep = EM_CMD.CMD_str_clean(sys.argv[3])
            new_sep = EM_CMD.CMD_str_clean(sys.argv[4])
            replace = False
            output_file_list = None
            if len(sys.argv) > 5:
                opt_params = EM_CMD.CMD_optargs_list(sys.argv[5:], ["replace","output_file_list"], [bool,[str]])
                replace = opt_params.get("replace", False)
                output_file_list = opt_params.get("output_file_list", None)
            DAT_change_sep(file_list,sep,new_sep,replace,output_file_list)
        elif globals()[sys.argv[1]] == DAT_fuse_bases:
            file_B1 = EM_CMD.CMD_str_clean(sys.argv[2], path=True)
            file_B2 = EM_CMD.CMD_str_clean(sys.argv[3], path=True)
            file_prof = EM_CMD.CMD_str_clean(sys.argv[4], path=True)
            sep = '\t'
            output_file = None
            if len(sys.argv) > 5:
                opt_params = EM_CMD.CMD_optargs_list(sys.argv[5:], ["sep","output_file"], [str,str])
                sep = opt_params.get("sep", '\t')
                output_file = opt_params.get("output_file", None)
            DAT_fuse_bases(file_B1,file_B2,file_prof,sep,output_file)
        elif globals()[sys.argv[1]] == FIG_display_fig:
            file_list = None
            if len(sys.argv) > 2:
                opt_params = EM_CMD.CMD_optargs_list(sys.argv[2:], ["file_list"], [[str]])
                file_list = opt_params.get("file_list", None)
            FIG_display_fig(file_list)
        elif globals()[sys.argv[1]] == FIG_plot_data:
            file = EM_CMD.CMD_str_clean(sys.argv[2], path=True)
            sep = '\t'
            col_x = None
            col_y = None
            start = 2
            nb_data = None
            if len(sys.argv) > 3:
                opt_params = EM_CMD.CMD_optargs_list(sys.argv[3:], ["sep","col_x","col_y","start","nb_data"], [str,str,str,int,int])
                sep = opt_params.get("sep", '\t')
                col_x = opt_params.get("col_x", None)
                col_y = opt_params.get("col_y", None)
                start = opt_params.get("start", 2)
                nb_data = opt_params.get("nb_data", None)
            FIG_plot_data(file,sep,col_x,col_y,start,nb_data)
        else:
            EM_CMD.CMD_err_mess("La fonction choisie est protégée")
    except KeyError:
        EM_CMD.CMD_err_mess("La fonction choisie n'existe pas (voir aide)")
    # except IndexError:
    #     EM_CMD.CMD_err_mess("Le nombre de paramètres est insuffisant (voir aide)")
    # except ValueError:
    #     EM_CMD.CMD_err_mess("Un des paramètres n'est pas du bon type")

#init_app_dat()



