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

_Func_Name_List = ["CMD_help","CMD_exec_known_device","CMD_exec_new_device","CMDEX_ball_calibr","CMDEX_init",
                   "CMDEX_evol_profils","CMDEX_frontiere","CMDEX_grid","CMDEX_calibration","JSON_print_devices",
                   "JSON_add_device","JSON_remove_device","JSON_modify_device","DAT_change_date","DAT_pop_and_dec",
                   "DAT_switch_cols","DAT_remove_cols","DAT_remove_data","DAT_stats","DAT_light_format",
                   "DAT_change_sep","DAT_no_gps_pos","DAT_fuse_data","DAT_fuse_bases","TRANS_df_to_matrix",
                   "TRANS_matrix_to_df","TRANS_matrix_to_grd","TRANS_grd_to_matrix","FIG_display_fig","FIG_plot_data",
                   "FIG_plot_grid","FIG_plot_pos","EXEC"]

def main(app_data,file_list,file_list_rev,sep,output_file,output_file_base,light_restr,split,sup_na,regr,corr_base,no_base,choice):
    """ [TA]\n
    As its name would suggest, is the main function for the global CMD process.\n
    Can be called from ``CMD_exec_known_device`` or ``CMD_exec_new_device``.
    
    Notes
    -----
    Cannot be called from cmd directly.
    
    Parameters
    ----------
    app_data : dict
        Device dictionary. See function ``JSON_add_device``.
    file_list : ``None`` or list of str
        List of files to process. If ``None``, takes all .dat in the current ``CONFIG.data_path`` folder.
    file_list_rev : ``None`` or list of str
        List of files to not process, while taking the others (inverse of ``file_list``). Is ignored if ``file_list != None``.
    sep : str
        Dataframe separator.
    output_file : ``None`` or str
        Output file name for all profiles, If ``None``, is called ``"res.dat"``.
    output_file_base : ``None`` or str
        Output file name for all bases, If ``None``, is called ``"res_B.dat"``.
    light_restr : ``None`` or list of str
        Applying ``DAT_light_format`` to output with exclusion strings : any data including one of the specified strings will be ignored.
    split : bool
        Files are not fused into a single output.
    sup_na : bool
        Whether ``NaN`` values should be deleted. Otherwise, apply ``NaN`` completion in the ``EM_CMD.CMD_init`` function.
    regr : bool
        Whether profiles should be linearized in the ``EM_CMD.CMD_init`` function.
    corr_base : bool
        Whether profiles should be adjusted from bases values in the ``EM_CMD.CMD_init`` function.
    no_base : bool
        If no file contains bases, while having clear profiles. Will only consider profiles.    
    choice : bool
        Enables manual acceptance of each adjustment in the ``EM_CMD.CMD_frontiere_loop`` function.
    
    Returns
    -------
    none, but save output dataframe in multiple .dat.
    
    Warns
    -----
    * There is more than 8 files, which is not recommended.
    
    Raises
    ------
    * File not found.
    
    See also
    --------
    ``EM_CMD.CMD_init, EM_CMD.CMD_frontiere_loop, EM_CMD.DAT_light_format``
    """
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
                EM_CMD.MESS_err_mess('Le fichier "{}" est introuvable'.format(f_rev))
    else:
        for f in file_list:
            ls_nomfich.append(f.replace('"',''))
    
    nb_fich = len(ls_nomfich)
    if nb_fich > 8:
        EM_CMD.MESS_warn_mess('Le nombre de fichiers est élevé ({}) : il est conseillé de fractionner le traitement pour obtenir de meilleurs résultats'.format(nb_fich))
        
    # concaténation si nécessaire avant traitement
    ls_base, ls_mes, ncx, ncy, col_T, nb_res, ls_pd_done_before = EM_CMD.CMD_init(app_data,ls_nomfich,sep,sup_na,regr,corr_base,no_base,not_in_file=True,full_infos=True)
            
    cpt = 0
    if ls_mes:
        for ic,df in enumerate(ls_mes):
            #EM_CMD.MESS_warn_mess(ls_nomfich[ic])
            if df.empty:
                ls_mes[ic] = ls_pd_done_before[cpt]
                cpt += 1
    else:
        ls_mes = ls_pd_done_before
    
    if nb_fich > 1:
        ls_mes = EM_CMD.CMD_frontiere_loop(ls_mes,ncx,ncy,col_T,nb_fich,app_data["nb_ecarts"],nb_res,choice,not_in_file=True)
    
    os.chdir(CONFIG.script_path)
    if split:
        for ic,p in enumerate(ls_mes):
            if light_restr != None:
                p = EM_CMD.DAT_light_format(p,nb_ecarts=app_data["nb_ecarts"],restr=light_restr)
            p.to_csv(CONFIG.data_path+ls_nomfich[ic][:-4]+"_P.dat", header=True, index=False, sep=sep, mode='w')
        for ic,b in enumerate(ls_base):
            if not b.empty:
                b.to_csv(CONFIG.data_path+ls_nomfich[ic][:-4]+"_B.dat", header=True, index=False, sep=sep, mode='w')
    
    don_mes = pd.concat(ls_mes)
    if light_restr != None: # Mise en format uniforme
        don_mes = EM_CMD.DAT_light_format(don_mes,nb_ecarts=app_data["nb_ecarts"],restr=light_restr)
    don_mes.to_csv(CONFIG.data_path+output_file, header=True, index=False, sep=sep, mode='w')
    if ls_base:
        don_base = pd.concat(ls_base)
        if not don_base.empty:
            don_base.to_csv(CONFIG.data_path+output_file_base, header=True, index=False, sep=sep, mode='w')
    #print(don_mes)
    
    # on affiche les points de mesure apres repositionnement, interpolation et redressement
    for e in range(app_data["nb_ecarts"]):
        fig,ax=plt.subplots(nrows=1,ncols=nb_res,figsize=(CONFIG.fig_width,CONFIG.fig_height))
        X = don_mes[ncx[e]]
        Y = don_mes[ncy[e]]
        for r in range(nb_res):
            Z = don_mes[col_T[e]]
            Q5,Q95 = Z.quantile([0.05,0.95])
            col = ax[r].scatter(X,Y,marker='s',c=Z,cmap='cividis',s=6,vmin=Q5,vmax=Q95)
            plt.colorbar(col,ax=ax[r],shrink=0.7)
            ax[r].title.set_text(col_T[e*nb_res+r])
            ax[r].set_xlabel(ncx[e])
            ax[r].set_ylabel(ncy[e])
            ax[r].set_aspect('equal')
        plt.show(block=False)
        plt.pause(CONFIG.fig_render_time) # À augmenter si la figure ne s'affiche pas, sinon on pourra le baisser pour accélérer la vitesse de l'input
        plt.savefig(CONFIG.script_path+"Output/CMD_" +str(e)+'.png')
        pickle.dump(fig, open("Output/CMD_" +str(e)+'.pickle', 'wb'))
        
        
    #fin de lecture du fichier
    EM_CMD.keep_plt_for_cmd()
    os.chdir(CONFIG.script_path)

# Suite ct à la ligne ligne 403

# Sert à remplir la base avec les appareils utiles au fichiers en local [pour les tests]

def init_app_dat():
    app_data = EM_CMD.JSON_add_device('mini3L','HCP',3,[30000],gps=True,gps_dec=[0.25,-0.2],TR_l=[0.32,0.71,1.18],\
                                      TR_t=[0,0,0],height=0.1,bucking_coil=0,coeff_c_ph=[0.5982,0.9839,0.7074],coeff_c_qu=[0.00591,0.0281,0.0745],autosave=True)
    # EM_CMD.JSON_add_coeff(app_data)
    app_data = EM_CMD.JSON_add_device('mini3L','VCP',3,[30000],gps=True,gps_dec=[0.25,-0.2],TR_l=[0.32,0.71,1.18],\
                                      TR_t=[0,0,0],height=0.1,bucking_coil=0,coeff_c_ph=[1,1,1],coeff_c_qu=[0.00599,0.0290,0.0785],autosave=True)
    # EM_CMD.JSON_add_coeff(app_data)
    app_data = EM_CMD.JSON_add_device('mini3L','VCP',3,[10000,20000,30000],gps=True,gps_dec=[0.25,-0.2],TR_l=[0.32,0.71,1.18],\
                                      TR_t=[0,0,0],height=0.1,bucking_coil=0,coeff_c_ph=[1,1,1],coeff_c_qu=[0.00599,0.0290,0.0785],autosave=True)
    # EM_CMD.JSON_add_coeff(app_data)
    app_data = EM_CMD.JSON_add_device('mini6L','HCP',6,[10000,10000,20000,10000,1,30000,20000],gps=True,gps_dec=[0.25,-0.2],TR_l=[0.2,0.33,0.5,0.72,1.03,1.5],\
                                      TR_t=[0,0,0,0,0,0],height=0.1,bucking_coil=0,coeff_c_ph=[1,1,1,1,1,1],coeff_c_qu=[0.00194,0.00524,0.0119,0.0242,0.0484,0.0986],autosave=True)
    # EM_CMD.JSON_add_coeff(app_data)
    app_data = EM_CMD.JSON_add_device('mini6L','VCP',6,[10000,10000,20000,10000,1,30000,20000],gps=True,gps_dec=[0.25,-0.2],TR_l=[0.2,0.33,0.5,0.72,1.03,1.5],\
                                      TR_t=[0,0,0,0,0,0],height=0.1,bucking_coil=0,coeff_c_ph=[1,1,1,1,1,1],coeff_c_qu=[0.00194,0.00525,0.012,0.0246,0.0498,0.1037],autosave=True)
    # EM_CMD.JSON_add_coeff(app_data)
    app_data = EM_CMD.JSON_add_device('mini6L','PRP_CS',6,[10000,10000,20000,10000,1,30000,20000],gps=True,gps_dec=[0.25,-0.2],TR_l=[0.2,0.33,0.5,0.72,1.03,1.5],\
                                      TR_t=[0,0,0,0,0,0],height=0.1,bucking_coil=0,coeff_c_ph=[1,1,1,1,1,1],coeff_c_qu=[0.00194,0.00525,0.012,0.0246,0.0498,0.1037],autosave=True)
    # EM_CMD.JSON_add_coeff(app_data)
    app_data = EM_CMD.JSON_add_device('expl3L','HCP',3,[10000,20000,30000],gps=True,gps_dec=[0.25,-0.2],TR_l=[0,0,0],\
                                      TR_t=[1.5,2.4,4.6],height=0.1,bucking_coil=0,coeff_c_ph=[1,1,1],coeff_c_qu=[0.0402,0.1366,0.3144],autosave=True)
    # EM_CMD.JSON_add_coeff(app_data)
    app_data = EM_CMD.JSON_add_device('expl3L','VCP',3,[10000,20000,30000],gps=True,gps_dec=[0.25,-0.2],TR_l=[0,0,0],\
                                      TR_t=[1.5,2.4,4.6],height=0.1,bucking_coil=0,coeff_c_ph=[1,1,1],coeff_c_qu=[0.0417,0.1463,0.3558],autosave=True)
    # EM_CMD.JSON_add_coeff(app_data)
    app_data = EM_CMD.JSON_add_device('mini3L','HCP',3,[30000],gps=False,gps_dec=[0,0],TR_l=[0.32,0.71,1.18],\
                                      TR_t=[0,0,0],height=0.1,bucking_coil=0,coeff_c_ph=[1,1,1],coeff_c_qu=[0.00591,0.0281,0.0745],autosave=True)
    # EM_CMD.JSON_add_coeff(app_data)

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



def CMD_help(help_id=None):
    """ [TA]\n
    Print custom function description for requested function.\n
    
    Parameters
    ----------
    ``[opt]`` help_id : ``None`` or int, default : ``None``
        Function index in ``_Func_Name_List`` (global array).
    
    Notes
    -----
    If ``help_id = -1``, user will select function with requested input.
    If ``help_id = None``, every function will be displayed.\n
    Every function description should be ordered as in the ``_Title_list`` constant array, which correspond to the ``_Func_Name_List`` global constant array order.
    """
    _Title_list = ["Aide","Traitement CMD (appareil enregistré)","Traitement CMD (nouvel appareil)","Calibration à la boule","Interpolation, décalage et complétion",
                   "Etalonnage par base et/ou manuel","Étalonnage des frontières","Mise en grille des données",
                   "Étalonnage final des données par calibration (loi physique)","Liste des appareils enregistrés","Ajouter un appareil","Supprimer un appareil enregistré",
                   "Modifier un appareil enregistré","Changement de la date d'un fichier .dat","Suppression d'une colonne surnuméraire dans un fichier .dat",
                   "Inversion de deux colonnes dans un fichier .dat","Suppression de colonnes dans un fichier .dat","Suppression de données (valeurs) dans un fichier .dat",
                   "Statistiques sur fichier.dat","Mise en format standard d'un fichier .dat","Changement du séparateur dans un fichier .dat",
                   "Correction des positions sans GPS d'un fichier .dat","Fusion de données dans un même fichier .dat","Fusion de bases B1 et B2 dans un même fichier .dat",
                   "Changement de format, de dataframe (.dat) à matrice (.json)","Changement de format, de matrice (.json) à dataframe (.dat)",
                   "Changement de format, de matrice (.json) à Surfer (.grd)","Changement de format, de Surfer (.grd) à matrice (.json)",
                   "Affichage interactif de figures en .pickle","Affichage et enregistrement de figures (nuage de points)",
                   "Affichage et enregistrement de figures (grille)","Affichage des positions pour chaque bobine","Lancement de fonction via fichier .txt"]
    if help_id == -1:
        aff = ["Fonction à afficher :","",EM_CMD.warning_color+"[y]"+EM_CMD.error_color+" TOUT",EM_CMD.warning_color+"[c]"+EM_CMD.type_color+" Catégories de fonctions"]
        for ic,func_name in enumerate(_Func_Name_List):
            aff.append(EM_CMD.warning_color+"[{}] ".format(ic)+EM_CMD.success_color+func_name+EM_CMD.code_color+" ({})".format(_Title_list[ic]))
        correct = False
        while correct == False:
            EM_CMD.MESS_input_mess(aff)
            inp = input()
            try:
                if inp == "y":
                    help_id = None
                    correct = True
                elif inp == "c":
                    help_id = "c"
                    correct = True
                else:
                    help_id = int(inp)
                    if help_id >= 0 and help_id < len(_Title_list):
                        correct = True
                    else:
                        EM_CMD.MESS_warn_mess("Aucune fonction n'a cet indice")
            except ValueError:
                EM_CMD.MESS_warn_mess("Réponse non reconnue !")
                
    print(EM_CMD.success_color)
    nc = os.get_terminal_size().columns
    print("~"*nc)
    print("")
    print(" "*((nc-55)//2),"-------------------------------------------------------")
    print(" "*((nc-55)//2),"-----  Programme de traîtement des donneées CMD   -----")
    print(" "*((nc-55)//2),"-------------------------------------------------------")
    if help_id == None or help_id == "c":
        print(EM_CMD.title_color)
        curr_title = "[c] Catégories de fonctions :"
        print(curr_title+EM_CMD.title_next_color+"."*(nc-len(curr_title)))
        print(EM_CMD.bold_und_color)
        print("DESCRIPTION :"+EM_CMD.bold_color+" Cette section présente la classification des différentes fonctions de l'interface.")
        print("")
        print(EM_CMD.bold_und_color+EM_CMD.type_color+"[CMD] Traitement principal"+EM_CMD.base_color)
        print("   Ces fonctions lancent un traîtement général depuis un ou plusieurs fichiers bruts afin de réaliser automatiquement la complétion ou délétion NaN, la séparation base/profil, \
le décalage des positions par voies et l'étalonnage aux frontières. On peut aussi réaliser la linéarisation des profils, l'étalonnage par base.")
        print("")
        print(EM_CMD.bold_und_color+EM_CMD.type_color+"[CMDEX] Traitement réduit à une seule étape"+EM_CMD.base_color)
        print("   Ces fonctions permettent de fractionner le traîtement en différentes tâches, afin d'avoir la main mise sur le déroulé. En plus des tâches proposées par la boucle principale, \
on y trouve des ajustements qui impérativement être faits séparément. Par exemple, l'ajustement manuel sur profil, la mise en grille (interpolation, kriging), la calibration via les constantes \
de l'appareil.")
        print("")
        print(EM_CMD.bold_und_color+EM_CMD.type_color+"[JSON] Manipulation des fichiers .json"+EM_CMD.base_color)
        print("   Ces fonctions gèrent la base des appareils de mesure. Toute fonction nécessitant d'utiliser des informations extérieures au jeu de donnée (configuration des bobines, position/\
fréquences des bobines, hauteur de prospection...) référencent un appareil en paramètre. Cet appareil doit être ajouté au préalable dans le fichier \"Appareil.dat\", puis appelé selon un \
identifiant (nombre) unique. Il existe donc une procédure qui ajoute un appareil avec tous ces paramètres propres, ou les afficher/retirer.")
        print("")
        print(EM_CMD.bold_und_color+EM_CMD.type_color+"[DAT] Manipulation des fichiers .dat"+EM_CMD.base_color)
        print("   Ces fonctions proposent diverses procédures utilitaires qui peuvent être appliquées sur des jeux de données, en général avant quelconque traitement. Elles servent à rectifier \
toutes sortes de biais ou d'erreurs (données divergentes, colonnes inversées, mauvais séparateur...) ou à mieux les ordonner (supprimer des colonnes, fusionner des fichiers...).")
        print("")
        print(EM_CMD.bold_und_color+EM_CMD.type_color+"[TRANS] Changement de format"+EM_CMD.base_color)
        print("   Ces fonctions servent à passer d'un format de stockage de données à un autre, en fonction de ses besoins. Cela concerne en particulier les grilles.")
        print("")
        print(EM_CMD.bold_und_color+EM_CMD.type_color+"[FIG] Affichage"+EM_CMD.base_color)
        print("   Ces fonctions mettent en figure les données, sans effectuer d'opérations sur le jeu en lui-même.")
        print(EM_CMD.base_color)
    ic = 0
    if help_id == None or help_id == ic:
        print(EM_CMD.title_color)
        curr_title = "[{}] ".format(ic)+_Title_list[ic]+" :"
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
        print("          CMDEX -> Traitement réduit à une seule étape")
        print("          JSON -> Manipulation des fichiers .json")
        print("          DAT -> Manipulation des fichiers .dat")
        print("")
        print("exemples : "+EM_CMD.code_color+'python3 Traitement_CMD_v7.py CMD_help')
        print("           "+EM_CMD.code_color+'python3 Traitement_CMD_v7.py CMD_help 1')
        print("           "+EM_CMD.code_color+'python3 Traitement_CMD_v7.py CMD_help CMD_exec_known_device')
        print(EM_CMD.base_color)
    ic += 1
    if help_id == None or help_id == ic:
        print(EM_CMD.title_color)
        curr_title = "[{}] ".format(ic)+_Title_list[ic]+" :"
        print(curr_title+EM_CMD.title_next_color+"."*(nc-len(curr_title)))
        print(EM_CMD.bold_und_color)
        print("DESCRIPTION :"+EM_CMD.bold_color+" Effectue le traitement de données CMD mesurées avec un appareil et des réglages connus (présents dans la base 'Appareils.json').")
        print("Les fichiers .dat sont récoltés dans le dossier pointé par la variable globale 'CONFIG.data_path'.")
        print("Les fichiers .json sont récoltés dans le dossier pointé par la variable globale 'CONFIG.json_path'.")
        print(EM_CMD.code_color)
        print(">>> CMD_exec_known_device("+EM_CMD.success_color+"uid"+EM_CMD.code_color+","+EM_CMD.success_low_color+"[file_list"+EM_CMD.code_color+","+
              EM_CMD.success_low_color+"file_list_rev"+EM_CMD.code_color+","+EM_CMD.success_low_color+"sep"+EM_CMD.code_color+","+EM_CMD.success_low_color+"output_file"+EM_CMD.code_color+","+
              EM_CMD.success_low_color+"output_file_base"+EM_CMD.code_color+","+EM_CMD.success_low_color+"light_restr"+EM_CMD.code_color+","+EM_CMD.success_low_color+"split"+EM_CMD.code_color+","+
              EM_CMD.success_low_color+"sup_na"+EM_CMD.code_color+","+EM_CMD.success_low_color+"regr"+EM_CMD.code_color+","+EM_CMD.success_low_color+"corr_base"+EM_CMD.code_color+","+
              EM_CMD.success_low_color+"no_base"+EM_CMD.code_color+","+EM_CMD.success_low_color+"choice]"+EM_CMD.code_color+")")
        print(EM_CMD.base_color)
        print("avec : "+EM_CMD.success_color+"uid"+EM_CMD.type_color+" : int "+EM_CMD.base_color+"= indentifiant de l'appareil dans la base JSON")
        print("       "+EM_CMD.success_low_color+"file_list = None"+EM_CMD.type_color+" : str[] "+EM_CMD.base_color+"= liste des fichiers à traiter, le premier est celui servant pour le redressement (laisser vide pour traiter tous les fichiers du dossier)")
        print("       "+EM_CMD.success_low_color+"file_list_rev = None"+EM_CMD.type_color+" : str[] "+EM_CMD.base_color+"= liste des fichiers à ne pas traiter (n'est pris en compte que si le champ précédent est laissé vide)")
        print("       "+EM_CMD.success_low_color+"sep = '\\t'"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= caractère de séparation du .dat (par défaut '\\t')")
        print("       "+EM_CMD.success_low_color+'output_file = "res.dat"'+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= nom du fichier de sortie (profils)")
        print("       "+EM_CMD.success_low_color+'output_file_base = "res_B.dat"'+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= nom du fichier de sortie (base), seulement si des bases ont été détectées")
        print("       "+EM_CMD.success_low_color+'light_restr = None'+EM_CMD.type_color+" : str[] "+EM_CMD.base_color+"= si on uniforme le résultat avec cette restriction, sinon on ne fait rien (voir la fonction 'DAT_light_format')")
        print("       "+EM_CMD.success_low_color+"split = False"+EM_CMD.type_color+" : bool "+EM_CMD.base_color+"= si on sépare le résultat pour chaque fichier d'entrée (on ajoutera les suffixes '_P' pour profils et '_B' pour base), ignore les deux paramètres précédents")
        print("       "+EM_CMD.success_low_color+"sup_na = True"+EM_CMD.type_color+" : bool "+EM_CMD.base_color+"= suppression des données incomplètes (sinon redressage)")
        print("       "+EM_CMD.success_low_color+"regr = False"+EM_CMD.type_color+" : bool "+EM_CMD.base_color+"= propose d'appliquer ou non une régression linéaire sur les profils, si certains ne sont pas droits (par défaut, ne le fait pas)")
        print("       "+EM_CMD.success_low_color+"corr_base = True"+EM_CMD.type_color+" : bool "+EM_CMD.base_color+"= si activé, applique une correction par base sur les données d'un même fichier (voir CMDEX_evol_profils pour plus d'options)")
        print("       "+EM_CMD.success_low_color+"no_base = False"+EM_CMD.type_color+" : bool "+EM_CMD.base_color+"= si activé, ne considère que des profils (si le jeu ne contient pas de base)")
        print("       "+EM_CMD.success_low_color+"choice = False"+EM_CMD.type_color+" : bool "+EM_CMD.base_color+"= si activé, permet de valider ou non chaque ajustement proposé entre les jeux de données (attention, cette procédure peut être longue)")
        print("")
        print("exemples : "+EM_CMD.code_color+'python3 Traitement_CMD_v7.py CMD_exec_known_device 1')
        print("           "+EM_CMD.code_color+'python3 Traitement_CMD_v7.py CMD_exec_known_device 4 "sup_na=False" "file_list=["d1.dat",d2.dat]"')
        print(EM_CMD.base_color)
    ic += 1
    if help_id == None or help_id == ic:
        print(EM_CMD.title_color)
        curr_title = "[{}] ".format(ic)+_Title_list[ic]+" :"
        print(curr_title+EM_CMD.title_next_color+"."*(nc-len(curr_title)))
        print(EM_CMD.bold_und_color)
        print("DESCRIPTION :"+EM_CMD.bold_color+" Effectue le traitement de données CMD mesurées avec un nouvel appareil, donc les paramètres doivent être spécifiés.")
        print("Les fichiers .dat sont récoltés dans le dossier pointé par la variable globale 'CONFIG.data_path'.")
        print("Les fichiers .json sont récoltés dans le dossier pointé par la variable globale 'CONFIG.json_path'.")
        print(EM_CMD.code_color)
        print(">>> CMD_exec_new_device("+EM_CMD.success_color+"app_name"+EM_CMD.code_color+","+EM_CMD.success_color+"config"+EM_CMD.code_color+","+EM_CMD.success_color+"nb_ecarts"+EM_CMD.code_color+","+
              EM_CMD.success_color+"nb_ecarts"+EM_CMD.code_color+","+EM_CMD.success_color+"freq_list"+EM_CMD.code_color+","+EM_CMD.success_low_color+"[GPS"+EM_CMD.code_color+","+
              EM_CMD.success_low_color+"GPS_dec"+EM_CMD.code_color+","+EM_CMD.success_low_color+"TR_l"+EM_CMD.code_color+","+EM_CMD.success_low_color+"TR_t"+EM_CMD.code_color+","+
              EM_CMD.success_low_color+"height"+EM_CMD.code_color+","+EM_CMD.success_low_color+"bucking_coil"+EM_CMD.code_color+","+EM_CMD.success_low_color+"coeff_c_ph"+EM_CMD.code_color+","+
              EM_CMD.success_low_color+"coeff_c_qu"+EM_CMD.code_color+","+EM_CMD.success_low_color+"file_list"+EM_CMD.code_color+","+EM_CMD.success_low_color+"file_list_rev"+EM_CMD.code_color+","+
              EM_CMD.success_low_color+"sep"+EM_CMD.code_color+","+EM_CMD.success_low_color+"output_file"+EM_CMD.code_color+","+EM_CMD.success_low_color+"output_file_base"+EM_CMD.code_color+","+
              EM_CMD.success_low_color+"light_restr"+EM_CMD.code_color+","+EM_CMD.success_low_color+"split"+EM_CMD.code_color+","+EM_CMD.success_low_color+"sup_na"+EM_CMD.code_color+","+
              EM_CMD.success_low_color+"regr"+EM_CMD.code_color+","+EM_CMD.success_low_color+"corr_base"+EM_CMD.code_color+","+EM_CMD.success_low_color+"no_base"+EM_CMD.code_color+","+
              EM_CMD.success_low_color+"choice]"+EM_CMD.code_color+")")
        print(EM_CMD.base_color)
        print("avec : "+EM_CMD.success_color+"app_name"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= nom de l'appareil")
        print("       "+EM_CMD.success_color+"config"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= configuration des bobines (HCP,VCP,VVCP,PRP_CS,PRP_DEM,PAR,COAX_H,COAX_P,CUS)")
        print("       "+EM_CMD.success_color+"nb_ecarts"+EM_CMD.type_color+" : int "+EM_CMD.base_color+"= nombre de bobines")
        print("       "+EM_CMD.success_color+"freq_list"+EM_CMD.type_color+" : float[] "+EM_CMD.base_color+"= fréquences du signal (en ???)")
        print("       "+EM_CMD.success_low_color+"GPS = True"+EM_CMD.type_color+" : bool "+EM_CMD.base_color+"= présence ou non de données GPS")
        print("       "+EM_CMD.success_low_color+"GPS_dec = [0.0,0.0]"+EM_CMD.type_color+" : float[] "+EM_CMD.base_color+"= décalage de l'antenne GPS par rapport au centre, 2 coos (en m) (inutile si GPS=False)")
        print("       "+EM_CMD.success_low_color+"TR_l = array of 0.0"+EM_CMD.type_color+" : float[] "+EM_CMD.base_color+"= positions des bobines receptrices (en m) sur l'axe latéral")
        print("       "+EM_CMD.success_low_color+"TR_t = array of 0.0"+EM_CMD.type_color+" : float[] "+EM_CMD.base_color+"= positions des bobines receptrices (en m) sur l'axe transversal")
        print("       "+EM_CMD.success_low_color+"height = 0.1"+EM_CMD.type_color+" : float "+EM_CMD.base_color+"= hauteur de l'appareil par rapport au sol (en m)")
        print("       "+EM_CMD.success_low_color+"bucking_coil = 0"+EM_CMD.type_color+" : int "+EM_CMD.base_color+"= numéro de la bucking coil parmi les bobines (0 si inexistante)")
        print("       "+EM_CMD.success_low_color+"coeff_c_ph = None"+EM_CMD.type_color+" : float[] "+EM_CMD.base_color+"= coefficient de l'appareil en phase (calculé avec 'CMDEX_ball_calibr')")
        print("       "+EM_CMD.success_low_color+"coeff_c_qu = None"+EM_CMD.type_color+" : float[] "+EM_CMD.base_color+"= coefficient de l'appareil en quadrature (donné par le constructeur)")
        print("       "+EM_CMD.success_low_color+"file_list = None"+EM_CMD.type_color+" : str[] "+EM_CMD.base_color+"= liste des fichiers à traiter, le premier est celui servant pour le redressement (laisser vide pour traiter tous les fichiers du dossier)")
        print("       "+EM_CMD.success_low_color+"file_list_rev = None"+EM_CMD.type_color+" : str[] "+EM_CMD.base_color+"= liste des fichiers à ne pas traiter (n'est pris en compte que si le champ précédent est laissé vide)")
        print("       "+EM_CMD.success_low_color+"sep = '\\t'"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= caractère de séparation du .dat (par défaut '\\t')")
        print("       "+EM_CMD.success_low_color+'output_file = "res.dat"'+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= nom du fichier de sortie (profils)")
        print("       "+EM_CMD.success_low_color+'output_file_base = "res_B.dat"'+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= nom du fichier de sortie (base), seulement si des bases ont été détectées")
        print("       "+EM_CMD.success_low_color+'light_restr = None'+EM_CMD.type_color+" : str[] "+EM_CMD.base_color+"= si on uniforme le résultat avec cette restriction, sinon on ne fait rien (voir la fonction 'DAT_light_format')")
        print("       "+EM_CMD.success_low_color+"split = False"+EM_CMD.type_color+" : bool "+EM_CMD.base_color+"= si on sépare le résultat pour chaque fichier d'entrée (on ajoutera les suffixes '_P' pour profils et '_B' pour base), ignore les deux paramètres précédents")
        print("       "+EM_CMD.success_low_color+"sup_na = True"+EM_CMD.type_color+" : bool "+EM_CMD.base_color+"= suppression des données incomplètes (sinon redressage)")
        print("       "+EM_CMD.success_low_color+"regr = False"+EM_CMD.type_color+" : bool "+EM_CMD.base_color+"= propose d'appliquer ou non une régression linéaire sur les profils, si certains ne sont pas droits (par défaut, ne le fait pas)")
        print("       "+EM_CMD.success_low_color+"corr_base = True"+EM_CMD.type_color+" : bool "+EM_CMD.base_color+"= si activé, applique une correction par base sur les données d'un même fichier (voir CMDEX_evol_profils pour plus d'options)")
        print("       "+EM_CMD.success_low_color+"no_base = False"+EM_CMD.type_color+" : bool "+EM_CMD.base_color+"= si activé, ne considère que des profils (si le jeu ne contient pas de base)")
        print("       "+EM_CMD.success_low_color+"choice = False"+EM_CMD.type_color+" : bool "+EM_CMD.base_color+"= si activé, permet de valider ou non chaque ajustement proposé entre les jeux de données (attention, cette procédure peut être longue)")
        print("")
        print("exemples : "+EM_CMD.code_color+'python3 Traitement_CMD_v7.py CMD_exec_new_device "dummy" "PAR" 5 40000 TR_l="[0.24,0.52,0.91,1.2,1.45]" "file_list=["d1.dat",d2.dat]"')
        print("           "+EM_CMD.code_color+'python3 Traitement_CMD_v7.py CMD_exec_new_device "mini3L" "VCP" 3 [30000] TR_t="0.32 0.71 1.18 " height=0.2 "GPS = False" sup_na=False')
        print(EM_CMD.base_color)
    ic += 1
    if help_id == None or help_id == ic:
        print(EM_CMD.title_color)
        curr_title = "[{}] ".format(ic)+_Title_list[ic]+" :"
        print(curr_title+EM_CMD.title_next_color+"."*(nc-len(curr_title)))
        print(EM_CMD.bold_und_color)
        print("DESCRIPTION :"+EM_CMD.bold_color+" Calcule le coefficient de l'appareil à partir d'un fichier de calibration à la boule.")
        print("Une fois la valeur obtenue, on pourra créer l'appareil dans la base en spécifiant le champ 'coeff_construct'.")
        print("Si l'appareil est en VVCP, il faut indiquer si le calibrage a été réalisé à la manière d'un HCP ou d'un VCP (et remplir le champ 'config' en conséquence).")
        print(EM_CMD.code_color)
        print(">>> CMDEX_ball_calibr("+EM_CMD.success_color+"ball_file"+EM_CMD.code_color+","+EM_CMD.success_color+"config"+EM_CMD.code_color+","+EM_CMD.success_color+"TR"+EM_CMD.code_color+","+
              EM_CMD.success_color+"radius"+EM_CMD.code_color+","+EM_CMD.success_color+"z"+EM_CMD.code_color+","+EM_CMD.success_color+"x_min"+EM_CMD.code_color+","+
              EM_CMD.success_color+"x_max"+EM_CMD.code_color+","+EM_CMD.success_low_color+"[y"+EM_CMD.code_color+","+EM_CMD.success_low_color+"step"+EM_CMD.code_color+","+
              EM_CMD.success_low_color+"bucking_coil]"+EM_CMD.code_color+")")
        print(EM_CMD.base_color)
        print("avec : "+EM_CMD.success_color+"ball_file"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= chemin et nom du fichier de calibrage à la boule")
        print("       "+EM_CMD.success_color+"config"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= configuration des bobines (HCP,VCP,PRP_CS,PRP_DEM)")
        print("       "+EM_CMD.success_color+"TR"+EM_CMD.type_color+" : int[] "+EM_CMD.base_color+"= écarts des bobines receptrices (en cm)")
        print("       "+EM_CMD.success_color+"radius"+EM_CMD.type_color+" : int "+EM_CMD.base_color+"= rayon de la boule (en cm)")
        print("       "+EM_CMD.success_color+"z"+EM_CMD.type_color+" : int "+EM_CMD.base_color+"= décalage en z (en cm)")
        print("       "+EM_CMD.success_color+"x_min"+EM_CMD.type_color+" : int "+EM_CMD.base_color+"= position de départ en x (en cm)")
        print("       "+EM_CMD.success_color+"x_max"+EM_CMD.type_color+" : int "+EM_CMD.base_color+"= position d'arrivée en x (en cm)")
        print("       "+EM_CMD.success_low_color+"y = 0"+EM_CMD.type_color+" : int "+EM_CMD.base_color+"= décalage en y (en cm)")
        print("       "+EM_CMD.success_low_color+"step = 5"+EM_CMD.type_color+" : int "+EM_CMD.base_color+"= pas en x (en cm)")
        print("       "+EM_CMD.success_low_color+"bucking_coil = 0"+EM_CMD.type_color+" : int "+EM_CMD.base_color+"= numéro de la bucking coil parmi les bobines (0 si inexistante)")
        print("")
        print("exemples : "+EM_CMD.code_color+'python3 Traitement_CMD_v7.py CMDEX_ball_calibr path/to/file/ball.dat HCP 0.32,0.71,1.18 2 15 -25 125')
        print("           "+EM_CMD.code_color+'python3 Traitement_CMD_v7.py CMDEX_ball_calibr path/to/file/football.dat "VCP" 0.2,0.4,0.6,0.8,1.0,1.2 5 17 0 200 step=10 bucking_coil=1')
        print(EM_CMD.base_color)
    ic += 1
    if help_id == None or help_id == ic:
        print(EM_CMD.title_color)
        curr_title = "[{}] ".format(ic)+_Title_list[ic]+" :"
        print(curr_title+EM_CMD.title_next_color+"."*(nc-len(curr_title)))
        print(EM_CMD.bold_und_color)
        print("DESCRIPTION :"+EM_CMD.bold_color+" À partir d'une liste fichier de données, effectue les étapes initiales du traitement.")
        print("1) Mise à jour du temps, si GPS.")
        print("2) Détection profils/bases.")
        print("3) Interpolation des position.")
        print("4) [Optionnel] Complétion des NaN et linéarisation des profils")
        print("5) Décalage GPS et bobines en n voies.")
        print(EM_CMD.code_color)
        print(">>> CMDEX_init("+EM_CMD.success_color+"uid"+EM_CMD.code_color+","+EM_CMD.success_low_color+"[file_list"+EM_CMD.code_color+","+EM_CMD.success_low_color+"sep"+EM_CMD.code_color+","+
              EM_CMD.success_low_color+"sup_na"+EM_CMD.code_color+","+EM_CMD.success_low_color+"regr"+EM_CMD.code_color+","+EM_CMD.success_low_color+"l_r"+EM_CMD.code_color+","+
              EM_CMD.success_low_color+"corr_base"+EM_CMD.code_color+","+EM_CMD.success_low_color+"no_base"+EM_CMD.code_color+","+EM_CMD.success_low_color+"pseudo_prof"+EM_CMD.code_color+","+
              EM_CMD.success_low_color+"l_p]"+EM_CMD.code_color+")")
        print(EM_CMD.base_color)
        print("avec : "+EM_CMD.success_color+"uid"+EM_CMD.type_color+" : int "+EM_CMD.base_color+"= indentifiant de l'appareil dans la base JSON")
        print("       "+EM_CMD.success_low_color+"file_list = None"+EM_CMD.type_color+" : str[] "+EM_CMD.base_color+"= liste des fichiers à traiter (laisser vide pour traiter tous les fichiers du dossier)")
        print("       "+EM_CMD.success_low_color+"sep = '\\t'"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= caractère de séparation du .dat (par défaut '\\t')")
        print("       "+EM_CMD.success_low_color+"sup_na = True"+EM_CMD.type_color+" : bool "+EM_CMD.base_color+"= suppression des données incomplètes (sinon redressage)")
        print("       "+EM_CMD.success_low_color+"regr = False"+EM_CMD.type_color+" : bool "+EM_CMD.base_color+"= propose d'appliquer ou non une régression linéaire sur les profils, si certains ne sont pas droits (par défaut, ne le fait pas)")
        print("       "+EM_CMD.success_low_color+"l_r = None"+EM_CMD.type_color+" : int/str[] "+EM_CMD.base_color+"= définit la liste des choix pour la régression des profils (inutile si 'regr = False')")
        print("       "+EM_CMD.success_low_color+"corr_base = True"+EM_CMD.type_color+" : bool "+EM_CMD.base_color+"= si activé, applique une correction par base sur les données d'un même fichier (voir CMDEX_evol_profils pour plus d'options)")
        print("       "+EM_CMD.success_low_color+"no_base = False"+EM_CMD.type_color+" : bool "+EM_CMD.base_color+"= si activé, ne considère que des profils (si le jeu ne contient pas de base)")
        print("       "+EM_CMD.success_low_color+"pseudo_prof = False"+EM_CMD.type_color+" : bool "+EM_CMD.base_color+"= si activé, force l'utilisation d'un algorithme plus souple mais moins précis pour la détection de profils")
        print("       "+EM_CMD.success_low_color+"l_p = None"+EM_CMD.type_color+" : float[] "+EM_CMD.base_color+"= définit les n points servant à construire les n-1 segments pour les pseudo profils, sinon fait une régression linéaire (inutile si 'pseudo_prof = False')")
        print("")
        print("exemples : "+EM_CMD.code_color+'python3 Traitement_CMD_v7.py CMDEX_init 0 sup_na=False')
        print("           "+EM_CMD.code_color+'python3 Traitement_CMD_v7.py CMDEX_init 8 file_list="[sq1.dat,sq2.dat,sq3.dat,sq4.dat]" sep=, regr=True')
        print(EM_CMD.base_color)
    ic += 1
    if help_id == None or help_id == ic:
        print(EM_CMD.title_color)
        curr_title = "[{}] ".format(ic)+_Title_list[ic]+" :"
        print(curr_title+EM_CMD.title_next_color+"."*(nc-len(curr_title)))
        print(EM_CMD.bold_und_color)
        print("DESCRIPTION :"+EM_CMD.bold_color+" À partir d'un fichier de profils et d'un fichier de bases associées, propose un étalonnage des profils par alignement des bases.")
        print("L'opération se fait par différence, mais il est possible de faire par multiplication. Il est possible de traiter plusieurs coupes de fichiers (profil,base), mais l'ordre doit correspondre.")
        print("La sortie est par graphe et par fichier (pour le résultat).")
        print("Il est possible de demander la rectification de blocs de profils, si d'autres imperfections sont visibles, avec le paramètre "+'"man_adjust"'+".")
        print("Si on souhaite uniquement effectuer cette opération, on peut désactiver l'opération avec bases, avec le paramètre "+'"auto_adjust"'+".")
        print(EM_CMD.code_color)
        print(">>> CMDEX_evol_profils("+EM_CMD.success_color+"file_prof_list"+EM_CMD.code_color+","+EM_CMD.success_color+"file_base_list"+EM_CMD.code_color+","+
              EM_CMD.success_color+"col_z"+EM_CMD.code_color+","+EM_CMD.success_low_color+"[sep"+EM_CMD.code_color+","+EM_CMD.success_low_color+"replace"+EM_CMD.code_color+","+
              EM_CMD.success_low_color+"output_file_list"+EM_CMD.code_color+","+EM_CMD.success_low_color+"nb_ecarts"+EM_CMD.code_color+","+EM_CMD.success_low_color+"diff"+EM_CMD.code_color+","+
              EM_CMD.success_low_color+"auto_adjust"+EM_CMD.code_color+","+EM_CMD.success_low_color+"man_adjust"+EM_CMD.code_color+","+EM_CMD.success_low_color+"line]"+EM_CMD.code_color+")")
        print(EM_CMD.base_color)
        print("avec : "+EM_CMD.success_color+"file_prof_list"+EM_CMD.type_color+" : str[] "+EM_CMD.base_color+"= liste des fichiers profils à traiter")
        print("       "+EM_CMD.success_color+"file_base_list"+EM_CMD.type_color+" : str[] "+EM_CMD.base_color+"= liste des fichiers bases à traiter, col_x='X_int', col_y='Y_int'")
        print("       "+EM_CMD.success_color+"col_z"+EM_CMD.type_color+" : int[] "+EM_CMD.base_color+"= position des colonnes données, la première est 0")
        print("       "+EM_CMD.success_low_color+"sep = '\\t'"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= caractère de séparation du .dat (par défaut '\\t')")
        print("       "+EM_CMD.success_low_color+"replace = False"+EM_CMD.type_color+" : bool "+EM_CMD.base_color+"= si le résultat est mis dans le fichier profils de départ (sinon, un nouveau est créé avec le suffixe '_ep')")
        print("       "+EM_CMD.success_low_color+"output_file_list = None"+EM_CMD.type_color+" : str[] "+EM_CMD.base_color+"= nom des fichier de sortie pour les bases, n'est pas pris en compte si replace=True")
        print("       "+EM_CMD.success_low_color+"nb_ecarts = 1"+EM_CMD.type_color+" : int "+EM_CMD.base_color+"= nombres de voies/bobines")
        print("       "+EM_CMD.success_low_color+"diff = True"+EM_CMD.type_color+" : bool "+EM_CMD.base_color+"= si le repositionnement se fait par addition/soustraction ou multiplication/division.")
        print("       "+EM_CMD.success_low_color+"auto_adjust = True"+EM_CMD.type_color+" : bool "+EM_CMD.base_color+"= permet d'activer la rectification automatique des profils par base")
        print("       "+EM_CMD.success_low_color+"man_adjust = False"+EM_CMD.type_color+" : bool "+EM_CMD.base_color+"= permet d'activer la rectification manuelle de blocs de profils")
        print("       "+EM_CMD.success_low_color+"line = False"+EM_CMD.type_color+" : bool "+EM_CMD.base_color+"= si on trace la courbe des profils (sinon juste les points)")
        print("")
        print("exemples : "+EM_CMD.code_color+'python3 Traitement_CMD_v7.py CMDEX_evol_profils "prof_1.dat" "base_1.dat" 2,3 line=True')
        print("           "+EM_CMD.code_color+'python3 Traitement_CMD_v7.py CMDEX_evol_profils "[prof_1.dat,prof_2.dat,prof_3.dat]" "[base_1.dat,base_2.dat,base_3.dat]" "2,3,6,7,10,11" "nb_ecarts=3" "sep=," "output_file_list=[o1.dat,o2.dat,o3.dat]"')
        print(EM_CMD.base_color)
    ic += 1
    if help_id == None or help_id == ic:
        print(EM_CMD.title_color)
        curr_title = "[{}] ".format(ic)+_Title_list[ic]+" :"
        print(curr_title+EM_CMD.title_next_color+"."*(nc-len(curr_title)))
        print(EM_CMD.bold_und_color)
        print("DESCRIPTION :"+EM_CMD.bold_color+" À partir d'une liste fichier de données, propose de corriger les décalages entre les jeux frontaliers.")
        print("Si l'ensemble des données n'est pas connexe (c'est-à-dire que tous les jeux ne se \"touchent pas\", à une tolérence près), seul une partie sera traitée.")
        print("Les jeux peuvent avoir plusieurs colonnes x et y (pour les voies), mais elles doivent être de même noms entre eux.")
        print("Si \"choice=True\", l'utilisateur pourra choisir ou nom de garder la transformation proposée pour chaque donnée.")
        print("Le résultat correspond à la concaténation de tous les jeux.")
        print(EM_CMD.code_color)
        print(">>> CMDEX_frontiere("+EM_CMD.success_color+"col_x"+EM_CMD.code_color+","+EM_CMD.success_color+"col_y"+EM_CMD.code_color+","+EM_CMD.success_color+"col_z"+EM_CMD.code_color+","+
              EM_CMD.success_low_color+"[file_list"+EM_CMD.code_color+","+EM_CMD.success_low_color+"sep"+EM_CMD.code_color+","+EM_CMD.success_low_color+"output_file"+EM_CMD.code_color+","+
              EM_CMD.success_low_color+"choice]"+EM_CMD.code_color+")")
        print(EM_CMD.base_color)
        print("avec : "+EM_CMD.success_color+"col_x"+EM_CMD.type_color+" : int[] "+EM_CMD.base_color+"= position des colonnes des coordonnées x (une par voie), la première est 0")
        print("       "+EM_CMD.success_color+"col_y"+EM_CMD.type_color+" : int[] "+EM_CMD.base_color+"= position des colonnes des coordonnées y (une par voie), la première est 0")
        print("       "+EM_CMD.success_color+"col_z"+EM_CMD.type_color+" : int[] "+EM_CMD.base_color+"= position des colonnes données, la première est 0 (sa taille doit être un multiple de la taille des vecteurs positions)")
        print("       "+EM_CMD.success_low_color+"file_list = None"+EM_CMD.type_color+" : str[] "+EM_CMD.base_color+"= liste des fichiers à traiter, le premier est celui servant pour le redressement (laisser vide pour traiter tous les fichiers du dossier)")
        print("       "+EM_CMD.success_low_color+"sep = '\\t'"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= caractère de séparation du .dat (par défaut '\\t')")
        print("       "+EM_CMD.success_low_color+'output_file = "frt.dat"'+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= nom du fichier de sortie")
        print("       "+EM_CMD.success_low_color+"choice = False"+EM_CMD.type_color+" : bool "+EM_CMD.base_color+"= si activé, permet de valider ou non chaque ajustement proposé entre les jeux de données (attention, cette procédure peut être longue)")
        print("")
        print("exemples : "+EM_CMD.code_color+'python3 Traitement_CMD_v7.py CMDEX_frontiere 0 1 7,8 output_file=treeway.dat')
        print("           "+EM_CMD.code_color+'python3 Traitement_CMD_v7.py CMDEX_frontiere "0,4,8" "1,5,9" "2,3,6,7,10,11" file_list="[sq1.dat,sq2.dat,sq3.dat,sq4.dat]" sep=, choice=True')
        print(EM_CMD.base_color)
    ic += 1
    if help_id == None or help_id == ic:
        print(EM_CMD.title_color)
        curr_title = "[{}] ".format(ic)+_Title_list[ic]+" :"
        print(curr_title+EM_CMD.title_next_color+"."*(nc-len(curr_title)))
        print(EM_CMD.bold_und_color)
        print("DESCRIPTION :"+EM_CMD.bold_color+" À partir d'un fichier de données, propose la mise en grille selon la méthode utilisée.")
        print("Si \"m_type='h\", alors on procède à l'élaboration d'une heatmap de densité des points. Utile pour déterminer le seuil.")
        print("Si \"m_type='i\", on interpole sur grille selon un des algorithmes suivants : 'nearest', 'linear', 'cubic'.")
        print("Si \"m_type='k\", un processus de choix de variogramme permettra ensuite de choisir les paramètres kriging. Seule les cases détectées par l'agorithme précédent seront considérées.")
        print("Afin de définir les dimensions de la grille, on peut soit fixer sa taille (prec), soit son pas (step).")
        print("Attention à ne pas lancer de kriging sur un grand jeu de données ou une trop grande grille au risque de ne jamais le terminer !")
        print(EM_CMD.code_color)
        print(">>> CMDEX_grid("+EM_CMD.success_color+"col_x"+EM_CMD.code_color+","+EM_CMD.success_color+"col_y"+EM_CMD.code_color+","+EM_CMD.success_color+"col_z"+EM_CMD.code_color+","+
              EM_CMD.success_low_color+"[file_list"+EM_CMD.code_color+","+EM_CMD.success_low_color+"sep"+EM_CMD.code_color+","+EM_CMD.success_low_color+"output_file"+EM_CMD.code_color+","+
              EM_CMD.success_low_color+"m_type"+EM_CMD.code_color+","+EM_CMD.success_low_color+"radius"+EM_CMD.code_color+","+EM_CMD.success_low_color+"prec"+EM_CMD.code_color+","+
              EM_CMD.success_low_color+"step"+EM_CMD.code_color+","+EM_CMD.success_low_color+"seuil"+EM_CMD.code_color+","+EM_CMD.success_low_color+"i_method"+EM_CMD.code_color+","+
              EM_CMD.success_low_color+"only_nan"+EM_CMD.code_color+","+EM_CMD.success_low_color+"no_crop"+EM_CMD.code_color+","+EM_CMD.success_low_color+"all_models"+EM_CMD.code_color+","+
              EM_CMD.success_low_color+"plot_pts"+EM_CMD.code_color+","+EM_CMD.success_low_color+"matrix]"+EM_CMD.code_color+")")
        print(EM_CMD.base_color)
        print("avec : "+EM_CMD.success_color+"col_x"+EM_CMD.type_color+" : int[] "+EM_CMD.base_color+"= position des colonnes des coordonnées x (une par voie), la première est 0")
        print("       "+EM_CMD.success_color+"col_y"+EM_CMD.type_color+" : int[] "+EM_CMD.base_color+"= position des colonnes des coordonnées y (une par voie), la première est 0")
        print("       "+EM_CMD.success_color+"col_z"+EM_CMD.type_color+" : int[] "+EM_CMD.base_color+"= position des colonnes données, la première est 0 (sa taille doit être un multiple de la taille des vecteurs positions)")
        print("       "+EM_CMD.success_low_color+"file_list = None"+EM_CMD.type_color+" : str[] "+EM_CMD.base_color+"= liste des fichiers à traiter (ils seront fusionnés)")
        print("       "+EM_CMD.success_low_color+"sep = '\\t'"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= caractère de séparation du .dat (par défaut '\\t')")
        print("       "+EM_CMD.success_low_color+'output_file = None'+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= nom du fichier de sortie, sinon n'en crée pas")
        print("       "+EM_CMD.success_low_color+"m_type = None"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= 'h' -> heatmap, 'i' -> interpolation, 'k' -> kriging (sinon, le choix se fera pendant l'exécution)")
        print("       "+EM_CMD.success_low_color+"radius = 0"+EM_CMD.type_color+" : int "+EM_CMD.base_color+"= distance au-delà de laquelle une case sans point est considérée comme vide (dans le cas contraire, on l'estime par son voisinage)")
        print("       "+EM_CMD.success_low_color+"prec = 100"+EM_CMD.type_color+" : int "+EM_CMD.base_color+"= nombre maximal de cases sur une ligne/colonne de la grille de sortie (s'adapte avec la forme du jeu)")
        print("       "+EM_CMD.success_low_color+"step = None"+EM_CMD.type_color+" : float "+EM_CMD.base_color+"= pas entre chaque case, selon l'unité utilisée par les colonnes positions (ignore prec si utilisé)")
        print("       "+EM_CMD.success_low_color+"seuil = 0.0"+EM_CMD.type_color+" : float "+EM_CMD.base_color+"= seuil d'acceptation d'un point en périphérie, varie souvent de -1 à 2 (plus il est grand, plus on retire de cases des la grille)")
        print("       "+EM_CMD.success_low_color+"i_method = None"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= 'nearest', 'linear', 'cubic', 'RBF_linear', 'RBF_thin_plate_spline', 'RBF_cubic', 'RBF_quintic', 'RBF_multiquadric',\
              'RBF_inverse_multiquadric', 'RBF_inverse_quadratic', 'RBF_gaussian' (sinon, le choix se fera pendant l'exécution, inutile si m_type!='i')")
        print("       "+EM_CMD.success_low_color+"only_nan = False"+EM_CMD.type_color+" : bool "+EM_CMD.base_color+"= si True, garde toujours les cases contenant au moins un point de mesure. Sinon on effectue le même test d'eccentricité que pour les cases vides.")
        print("       "+EM_CMD.success_low_color+"no_crop = False"+EM_CMD.type_color+" : bool "+EM_CMD.base_color+"= si False, ne sélectionne qu'au maximum 1000 points de l'ensemble (activer cette option augmente grandement le temps de calcul, inutile si m_type!='k')")
        print("       "+EM_CMD.success_low_color+"all_models = False"+EM_CMD.type_color+" : bool "+EM_CMD.base_color+"= propose les modèles de variogramme avancés (inutile si m_type!='k')")
        print("       "+EM_CMD.success_low_color+"plot_pts = False"+EM_CMD.type_color+" : bool "+EM_CMD.base_color+"= afficher ou non les points initiaux, avec une couleur par fichier (inutile si m_type='h')")
        print("       "+EM_CMD.success_low_color+"matrix = False"+EM_CMD.type_color+" : bool "+EM_CMD.base_color+"= enregistrer sous forme matricielle (tableau 3D), ou sous forme dataframe")
        print("")
        print("exemples : "+EM_CMD.code_color+'python3 Traitement_CMD_v7.py CMDEX_grid 0 1 7,8')
        print("           "+EM_CMD.code_color+'python3 Traitement_CMD_v7.py CMDEX_grid "0,4,8" "1,5,9" "2,3,6,7,10,11" file_list="[res.dat]" m_type=k radius=5 seuil=1 prec=100 all_models=True plot_pts=True')
        print(EM_CMD.base_color)
    ic += 1
    if help_id == None or help_id == ic:
        print(EM_CMD.title_color)
        curr_title = "[{}] ".format(ic)+_Title_list[ic]+" :"
        print(curr_title+EM_CMD.title_next_color+"."*(nc-len(curr_title)))
        print(EM_CMD.bold_und_color)
        print("DESCRIPTION :"+EM_CMD.bold_color+" Effectue le calibrage des données en ppm.")
        print("La procédure nécessite de calculer les coefficients de passage entre différents paramètres physiques (condictivité, résistivité). Ils sont stockés dans le fichier 'Constantes.json'.")
        print(EM_CMD.code_color)
        print(">>> CMDEX_calibration("+EM_CMD.success_color+"uid"+EM_CMD.code_color+","+EM_CMD.success_color+"col_ph"+EM_CMD.code_color+","+EM_CMD.success_color+"col_qu"+EM_CMD.code_color+","+
              EM_CMD.success_low_color+"[file_list"+EM_CMD.code_color+EM_CMD.success_low_color+"sep"+EM_CMD.code_color+EM_CMD.success_low_color+"output_file_list]"+EM_CMD.code_color+")")
        print(EM_CMD.base_color)
        print("avec : "+EM_CMD.success_color+"uid"+EM_CMD.type_color+" : int "+EM_CMD.base_color+"= indentifiant de l'appareil dans la base JSON")
        print("       "+EM_CMD.success_color+"col_ph"+EM_CMD.type_color+" : str[] "+EM_CMD.base_color+"= position des colonnes en phase, la première est 0")
        print("       "+EM_CMD.success_color+"col_qu"+EM_CMD.type_color+" : str[] "+EM_CMD.base_color+"= position des colonnes en quadrature, la première est 0")
        print("       "+EM_CMD.success_low_color+"file_list = None"+EM_CMD.type_color+" : str[] "+EM_CMD.base_color+"= liste des fichiers à traiter (laisser vide pour traiter tous les fichiers du dossier)")
        print("       "+EM_CMD.success_low_color+"sep = '\\t'"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= caractère de séparation du .dat (par défaut '\\t')")
        print("       "+EM_CMD.success_low_color+"output_file_list = None"+EM_CMD.type_color+" : str[] "+EM_CMD.base_color+"= nom des fichier de sortie (sinon, un nouveau est créé avec le suffixe '_calibr')")
        print("")
        print("exemples : "+EM_CMD.code_color+'python3 Traitement_CMD_v7.py CMDEX_calibration 0 1,5,9 0,4,8')
        print("           "+EM_CMD.code_color+'python3 Traitement_CMD_v7.py CMDEX_calibration 1 8,10,12 7,9,11 file_list="[rachida_dat_i.dat,date_the_fruit.dat] sep=,"')
        print(EM_CMD.base_color)
    ic += 1
    if help_id == None or help_id == ic:
        print(EM_CMD.title_color)
        curr_title = "[{}] ".format(ic)+_Title_list[ic]+" :"
        print(curr_title+EM_CMD.title_next_color+"."*(nc-len(curr_title)))
        print(EM_CMD.bold_und_color)
        print("DESCRIPTION :"+EM_CMD.bold_color+" Affiche l'ensemble des appareils de la base 'Appareils.json'.")
        print("Chaque appareil est associé à un identifiant, qui peut être utilisé par la fonction CMD_exec_known_device pour lancer le traîtement des données .dat.")
        print(EM_CMD.code_color)
        print(">>> JSON_print_devices("+EM_CMD.success_low_color+"[uid]"+EM_CMD.code_color+")")
        print(EM_CMD.base_color)
        print("avec : "+EM_CMD.success_low_color+"uid = None"+EM_CMD.type_color+" : int "+EM_CMD.base_color+"= indentifiant de l'appareil dans la base JSON (laisser vide pour tout afficher)")
        print("")
        print("exemples : "+EM_CMD.code_color+'python3 Traitement_CMD_v7.py JSON_print_devices')
        print("           "+EM_CMD.code_color+'python3 Traitement_CMD_v7.py JSON_print_devices 4')
        print(EM_CMD.base_color)
    ic += 1
    if help_id == None or help_id == ic:
        print(EM_CMD.title_color)
        curr_title = "[{}] ".format(ic)+_Title_list[ic]+" :"
        print(curr_title+EM_CMD.title_next_color+"."*(nc-len(curr_title)))
        print(EM_CMD.bold_und_color)
        print("DESCRIPTION :"+EM_CMD.bold_color+" Ajoute un appareil la base 'Appareils.json' avec les paramètres spécifiés.")
        print(EM_CMD.code_color)
        print(">>> JSON_add_device("+EM_CMD.success_color+"app_name"+EM_CMD.code_color+","+EM_CMD.success_color+"config"+EM_CMD.code_color+","+EM_CMD.success_color+"nb_ecarts"+EM_CMD.code_color+","+
              EM_CMD.success_color+"nb_ecarts"+EM_CMD.code_color+","+EM_CMD.success_color+"freq_list"+EM_CMD.code_color+","+EM_CMD.success_low_color+"[GPS"+EM_CMD.code_color+","+
              EM_CMD.success_low_color+"GPS_dec"+EM_CMD.code_color+","+EM_CMD.success_low_color+"TR_l"+EM_CMD.code_color+","+EM_CMD.success_low_color+"TR_t"+EM_CMD.code_color+","+
              EM_CMD.success_low_color+"height"+EM_CMD.code_color+","+EM_CMD.success_low_color+"bucking_coil"+EM_CMD.code_color+","+EM_CMD.success_low_color+"coeff_c_ph"+EM_CMD.code_color+","+
              EM_CMD.success_low_color+"coeff_c_qu]"+EM_CMD.code_color+","+")")
        print(EM_CMD.base_color)
        print("avec : "+EM_CMD.success_color+"app_name"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= nom de l'appareil")
        print("       "+EM_CMD.success_color+"config"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= configuration des bobines (HCP,VCP,VVCP,PRP_CS,PRP_DEM,PAR,COAX_H,COAX_P,CUS)")
        print("       "+EM_CMD.success_color+"nb_ecarts"+EM_CMD.type_color+" : int "+EM_CMD.base_color+"= nombre de bobines")
        print("       "+EM_CMD.success_color+"freq_list"+EM_CMD.type_color+" : float[] "+EM_CMD.base_color+"= fréquences du signal (en ???)")
        print("       "+EM_CMD.success_low_color+"GPS = True"+EM_CMD.type_color+" : bool "+EM_CMD.base_color+"= présence ou non de données GPS")
        print("       "+EM_CMD.success_low_color+"GPS_dec = [0.0,0.0]"+EM_CMD.type_color+" : float[] "+EM_CMD.base_color+"= décalage de l'antenne GPS par rapport au centre, 2 coos (en m) (inutile si GPS=False)")
        print("       "+EM_CMD.success_low_color+"TR_l = array of 0.0"+EM_CMD.type_color+" : float[] "+EM_CMD.base_color+"= positions des bobines receptrices (en m) sur l'axe latéral")
        print("       "+EM_CMD.success_low_color+"TR_t = array of 0.0"+EM_CMD.type_color+" : float[] "+EM_CMD.base_color+"= positions des bobines receptrices (en m) sur l'axe transversal")
        print("       "+EM_CMD.success_low_color+"height = 0.1"+EM_CMD.type_color+" : float "+EM_CMD.base_color+"= hauteur de l'appareil par rapport au sol (en m)")
        print("       "+EM_CMD.success_low_color+"bucking_coil = 0"+EM_CMD.type_color+" : int "+EM_CMD.base_color+"= numéro de la bucking coil parmi les bobines (0 si inexistante)")
        print("       "+EM_CMD.success_low_color+"coeff_c_ph = None"+EM_CMD.type_color+" : float[] "+EM_CMD.base_color+"= coefficient de l'appareil en phase (calculé avec 'CMDEX_ball_calibr')")
        print("       "+EM_CMD.success_low_color+"coeff_c_qu = None"+EM_CMD.type_color+" : float[] "+EM_CMD.base_color+"= coefficient de l'appareil en quadrature (donné par le constructeur)")
        print("")
        print("exemples : "+EM_CMD.code_color+'python3 Traitement_CMD_v7.py JSON_add_device "dummy" "PAR" 5 40000 TR_l="[0.24,0.52,0.91,1.2,1.45]"')
        print("           "+EM_CMD.code_color+'python3 Traitement_CMD_v7.py JSON_add_device "mini3L" "VCP" 3 [30000] TR_t="0.32 0.71 1.18 " height=0.2 "GPS = False"')
    ic += 1
    if help_id == None or help_id == ic:
        print(EM_CMD.title_color)
        curr_title = "[{}] ".format(ic)+_Title_list[ic]+" :"
        print(curr_title+EM_CMD.title_next_color+"."*(nc-len(curr_title)))
        print(EM_CMD.bold_und_color)
        print("DESCRIPTION :"+EM_CMD.bold_color+" Supprime l'appareil associé à l'identifiant choisi de la base 'Appareils.json'.")
        print(EM_CMD.code_color)
        print(">>> JSON_remove_device("+EM_CMD.success_low_color+"[uid]"+EM_CMD.code_color+")")
        print(EM_CMD.base_color)
        print("avec : "+EM_CMD.success_low_color+"uid = None"+EM_CMD.type_color+" : int "+EM_CMD.base_color+"= indentifiant de l'appareil dans la base JSON (laisser vide pour supprimer le dernier)")
        print("")
        print("exemples : "+EM_CMD.code_color+'python3 Traitement_CMD_v7.py JSON_remove_device')
        print("           "+EM_CMD.code_color+'python3 Traitement_CMD_v7.py JSON_remove_device 0')
        print(EM_CMD.base_color)
    ic += 1
    if help_id == None or help_id == ic:
        print(EM_CMD.title_color)
        curr_title = "[{}] ".format(ic)+_Title_list[ic]+" :"
        print(curr_title+EM_CMD.title_next_color+"."*(nc-len(curr_title)))
        print(EM_CMD.bold_und_color)
        print("DESCRIPTION :"+EM_CMD.bold_color+" Modifie certains champs de l'appareil associé à l'identifiant choisi de la base 'Appareils.json'.")
        print("Si certains champs créent des incohérences entre eux (par exemple les écartements et le nombre de bobines), ils devront tous être changés.")
        print("Cette fonction ne crée pas de copie de l'ancien appareil, se contente de le remplacer.")
        print(EM_CMD.code_color)
        print(">>> JSON_modify_device("+EM_CMD.success_color+"uid"+EM_CMD.code_color+","+EM_CMD.success_low_color+"**kwargs"+EM_CMD.code_color+")")
        print(EM_CMD.base_color)
        print("avec : "+EM_CMD.success_color+"uid"+EM_CMD.type_color+" : int "+EM_CMD.base_color+"= indentifiant de l'appareil dans la base JSON (laisser vide pour supprimer le dernier)")
        print("       "+EM_CMD.success_low_color+"**kwargs"+EM_CMD.base_color+" : champs à modifier (se référer aux champs existants de la fonction 'JSON_add_device')")
        print("")
        print("exemples : "+EM_CMD.code_color+'python3 Traitement_CMD_v7.py JSON_modify_device 0 config="HCP" GPS=True')
        print("           "+EM_CMD.code_color+'python3 Traitement_CMD_v7.py JSON_modify_device 4 nb_ecarts=6 TR_l=[0.35,0.78,1.29,1.54,1.81,2.08] TR_t="[0,0,0,0,0,0]" ')
        print(EM_CMD.base_color)
    ic += 1
    if help_id == None or help_id == ic:
        print(EM_CMD.title_color)
        curr_title = "[{}] ".format(ic)+_Title_list[ic]+" :"
        print(curr_title+EM_CMD.title_next_color+"."*(nc-len(curr_title)))
        print(EM_CMD.bold_und_color)
        print("DESCRIPTION :"+EM_CMD.bold_color+" Permet de corriger toutes les lignes d'un fichier avec la date spécifiée si celle-ci est incorrecte.")
        print(EM_CMD.code_color)
        print(">>> DAT_change_date("+EM_CMD.success_color+"file_list"+EM_CMD.code_color+","+EM_CMD.success_color+"date_str"+EM_CMD.code_color+","+EM_CMD.success_low_color+"[sep"+EM_CMD.code_color+","+
              EM_CMD.success_low_color+"replace"+EM_CMD.code_color+","+EM_CMD.success_low_color+"output_file_list]"+EM_CMD.code_color+")")
        print(EM_CMD.base_color)
        print("avec : "+EM_CMD.success_color+"file_list"+EM_CMD.type_color+" : str[] "+EM_CMD.base_color+"= liste des fichiers à traiter")
        print("       "+EM_CMD.success_color+"date_str"+EM_CMD.type_color+" : str "+EM_CMD.base_color+'= nouvelle date (format "mois/jour/année")')
        print("       "+EM_CMD.success_low_color+"sep = '\\t'"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= caractère de séparation du .dat (par défaut '\\t')")
        print("       "+EM_CMD.success_low_color+"replace = False"+EM_CMD.type_color+" : bool "+EM_CMD.base_color+"= si le résultat est mis dans le fichier de départ (sinon, un nouveau est créé avec le suffixe '_corr')")
        print("       "+EM_CMD.success_low_color+"output_file_list = None"+EM_CMD.type_color+" : str[] "+EM_CMD.base_color+"= nom des fichier de sortie, n'est pas pris en compte si replace=True")
        print("")
        print("exemples : "+EM_CMD.code_color+'python3 Traitement_CMD_v7.py DAT_change_date "path/to/file/very_nice_data.dat" "12/24/2020"')
        print("           "+EM_CMD.code_color+'python3 Traitement_CMD_v7.py DAT_change_date "[wrong_date.dat,we_r_not_in_2000.dat]" "02/29/2024" "sep=,"')
        print(EM_CMD.base_color)
    ic += 1
    if help_id == None or help_id == ic:
        print(EM_CMD.title_color)
        curr_title = "[{}] ".format(ic)+_Title_list[ic]+" :"
        print(curr_title+EM_CMD.title_next_color+"."*(nc-len(curr_title)))
        print(EM_CMD.bold_und_color)
        print("DESCRIPTION :"+EM_CMD.bold_color+" Permet de retirer une entête de colonne si aucune donnée ne lui est associé, pour éviter de décaler le reste du jeu de données.")
        print(EM_CMD.code_color)
        print(">>> DAT_pop_and_dec("+EM_CMD.success_color+"file_list"+EM_CMD.code_color+","+EM_CMD.success_color+"colsup"+EM_CMD.code_color+","+EM_CMD.success_low_color+"[sep"+EM_CMD.code_color+","+
              EM_CMD.success_low_color+"replace"+EM_CMD.code_color+","+EM_CMD.success_low_color+"output_file_list]"+EM_CMD.code_color+")")
        print(EM_CMD.base_color)
        print("avec : "+EM_CMD.success_color+"file_list"+EM_CMD.type_color+" : str[] "+EM_CMD.base_color+"= liste des fichiers à traiter")
        print("       "+EM_CMD.success_color+"colsup"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= nom de colonne à supprimer")
        print("       "+EM_CMD.success_low_color+"sep = '\\t'"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= caractère de séparation du .dat (par défaut '\\t')")
        print("       "+EM_CMD.success_low_color+"replace = False"+EM_CMD.type_color+" : bool "+EM_CMD.base_color+"= si le résultat est mis dans le fichier de départ (sinon, un nouveau est créé avec le suffixe '_corr')")
        print("       "+EM_CMD.success_low_color+"output_file_list = None"+EM_CMD.type_color+" : str[] "+EM_CMD.base_color+"= nom des fichier de sortie, n'est pas pris en compte si replace=True")
        print("")
        print("exemples : "+EM_CMD.code_color+'python3 Traitement_CMD_v7.py DAT_pop_and_dec "path/to/file/very_nice_data.dat" Note')
        print("           "+EM_CMD.code_color+'python3 Traitement_CMD_v7.py DAT_pop_and_dec "[2muchnames.dat,y_zer_is_no_time.dat]" "Time" "sep=," replace=True')
        print(EM_CMD.base_color)
    ic += 1
    if help_id == None or help_id == ic:
        print(EM_CMD.title_color)
        curr_title = "[{}] ".format(ic)+_Title_list[ic]+" :"
        print(curr_title+EM_CMD.title_next_color+"."*(nc-len(curr_title)))
        print(EM_CMD.bold_und_color)
        print("DESCRIPTION :"+EM_CMD.bold_color+" Permet d'échanger les valeurs de deux colonnes, tout en conservant leur position.")
        print(EM_CMD.code_color)
        print(">>> DAT_switch_cols("+EM_CMD.success_color+"file_list"+EM_CMD.code_color+","+EM_CMD.success_color+"col_a"+EM_CMD.code_color+","+EM_CMD.success_color+"col_b"+EM_CMD.code_color+","+
              EM_CMD.success_low_color+"[sep"+EM_CMD.code_color+","+EM_CMD.success_low_color+"replace"+EM_CMD.code_color+","+EM_CMD.success_low_color+"output_file_list]"+EM_CMD.code_color+")")
        print(EM_CMD.base_color)
        print("avec : "+EM_CMD.success_color+"file_list"+EM_CMD.type_color+" : str[] "+EM_CMD.base_color+"= liste des fichiers à traiter")
        print("       "+EM_CMD.success_color+"col_a"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= nom de la première colonne")
        print("       "+EM_CMD.success_color+"col_b"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= nom de la deuxième colonne")
        print("       "+EM_CMD.success_low_color+"sep = '\\t'"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= caractère de séparation du .dat (par défaut '\\t')")
        print("       "+EM_CMD.success_low_color+"replace = False"+EM_CMD.type_color+" : bool "+EM_CMD.base_color+"= si le résultat est mis dans le fichier de départ (sinon, un nouveau est créé avec le suffixe '_corr')")
        print("       "+EM_CMD.success_low_color+"output_file_list = None"+EM_CMD.type_color+" : str[] "+EM_CMD.base_color+"= nom des fichier de sortie, n'est pas pris en compte si replace=True")
        print("")
        print("exemples : "+EM_CMD.code_color+'python3 Traitement_CMD_v7.py DAT_switch_cols "path/to/file/very_nice_data.dat" "Easting" "Northing"')
        print("           "+EM_CMD.code_color+'python3 Traitement_CMD_v7.py DAT_switch_cols "[east_is_not_north.dat,very_mean_file_not_working.dat]" "Cond.1[mS/m]" "Inph.1[ppt]" "sep=," replace=True')
        print(EM_CMD.base_color)
    ic += 1
    if help_id == None or help_id == ic:
        print(EM_CMD.title_color)
        curr_title = "[{}] ".format(ic)+_Title_list[ic]+" :"
        print(curr_title+EM_CMD.title_next_color+"."*(nc-len(curr_title)))
        print(EM_CMD.bold_und_color)
        print("DESCRIPTION :"+EM_CMD.bold_color+" Permet de supprimer les colonnes inutiles. Utile pour faire le tri ou pour réduire l'utilisation mémoire.")
        print('Si "keep=True", alors ne garde que les colonnes spécifiées (fonction inverse).')
        print("Pour uniformiser l'opération de manière automatique, voir la fonction 'DAT_light_format'")
        print(EM_CMD.code_color)
        print(">>> DAT_remove_cols("+EM_CMD.success_color+"file_list"+EM_CMD.code_color+","+EM_CMD.success_color+"colsup_list"+EM_CMD.code_color+","+EM_CMD.success_color+"[keep"+EM_CMD.code_color+","+
              EM_CMD.success_low_color+"sep"+EM_CMD.code_color+","+EM_CMD.success_low_color+"replace"+EM_CMD.code_color+","+EM_CMD.success_low_color+"output_file_list]"+EM_CMD.code_color+")")
        print(EM_CMD.base_color)
        print("avec : "+EM_CMD.success_color+"file_list"+EM_CMD.type_color+" : str[] "+EM_CMD.base_color+"= liste des fichiers à traiter")
        print("       "+EM_CMD.success_color+"colsup_list"+EM_CMD.type_color+" : str[] "+EM_CMD.base_color+"= nom des colonnes concernées (ne pas mettre de crochets pour délimiter la liste)")
        print("       "+EM_CMD.success_low_color+"keep = False"+EM_CMD.type_color+" : bool "+EM_CMD.base_color+"= si True, on ne garde que les colonnes spécifiées (sinon ce sont celles qu'on supprime)")
        print("       "+EM_CMD.success_low_color+"sep = '\\t'"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= caractère de séparation du .dat (par défaut '\\t')")
        print("       "+EM_CMD.success_low_color+"replace = False"+EM_CMD.type_color+" : bool "+EM_CMD.base_color+"= si le résultat est mis dans le fichier de départ (sinon, un nouveau est créé avec le suffixe '_corr')")
        print("       "+EM_CMD.success_low_color+"output_file_list = None"+EM_CMD.type_color+" : str[] "+EM_CMD.base_color+"= nom des fichier de sortie, n'est pas pris en compte si replace=True")
        print("")
        print("exemples : "+EM_CMD.code_color+'python3 Traitement_CMD_v7.py DAT_remove_cols "path/to/file/very_nice_data.dat" "Error1[%],Error2[%],Error3[%]"')
        print("           "+EM_CMD.code_color+'python3 Traitement_CMD_v7.py DAT_remove_cols "[Error[%]_was_an_error.dat,where_is_the_Note_anyways.dat]" "x[m],y[m],Cond.1[mS/m],Inph.1[ppt],Cond.2[mS/m],Inph.2[ppt],Cond.3[mS/m],Inph.3[ppt]" keep=True')
        print(EM_CMD.base_color)
    ic += 1
    if help_id == None or help_id == ic:
        print(EM_CMD.title_color)
        curr_title = "[{}] ".format(ic)+_Title_list[ic]+" :"
        print(curr_title+EM_CMD.title_next_color+"."*(nc-len(curr_title)))
        print(EM_CMD.bold_und_color)
        print("DESCRIPTION :"+EM_CMD.bold_color+" Permet d'effacer les valeurs sur un bloc de lignes, sur des colonnes spécifiques. Sert à pouvoir traiter les données défectueuses non vides comme des données manquantes.")
        print("Pour faciliter la détection des lignes problématiques, on pourra utiliser la fonction 'DAT_min_max_col'.")
        print(EM_CMD.code_color)
        print(">>> DAT_remove_data("+EM_CMD.success_color+"file_list"+EM_CMD.code_color+","+EM_CMD.success_color+"colsup_list"+EM_CMD.code_color+","+EM_CMD.success_color+"i_min"+EM_CMD.code_color+","+
              EM_CMD.success_color+"i_max"+EM_CMD.code_color+","+EM_CMD.success_low_color+"[sep"+EM_CMD.code_color+","+EM_CMD.success_low_color+"replace"+EM_CMD.code_color+","+
              EM_CMD.success_low_color+"output_file_list]"+EM_CMD.code_color+")")
        print(EM_CMD.base_color)
        print("avec : "+EM_CMD.success_color+"file_list"+EM_CMD.type_color+" : str[] "+EM_CMD.base_color+"= liste des fichiers à traiter")
        print("       "+EM_CMD.success_color+"colsup_list"+EM_CMD.type_color+" : str[] "+EM_CMD.base_color+"= nom des colonnes concernées (ne pas mettre de crochets pour délimiter la liste)")
        print("       "+EM_CMD.success_color+"i_min"+EM_CMD.type_color+" : int "+EM_CMD.base_color+"= première ligne concernée (indiquée dans le fichier)")
        print("       "+EM_CMD.success_color+"i_max"+EM_CMD.type_color+" : int "+EM_CMD.base_color+"= dernière ligne concernée (indiquée dans le fichier)")
        print("       "+EM_CMD.success_low_color+"sep = '\\t'"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= caractère de séparation du .dat (par défaut '\\t')")
        print("       "+EM_CMD.success_low_color+"replace = False"+EM_CMD.type_color+" : bool "+EM_CMD.base_color+"= si le résultat est mis dans le fichier de départ (sinon, un nouveau est créé avec le suffixe '_corr')")
        print("       "+EM_CMD.success_low_color+"output_file_list = None"+EM_CMD.type_color+" : str[] "+EM_CMD.base_color+"= nom des fichier de sortie, n'est pas pris en compte si replace=True")
        print("")
        print("exemples : "+EM_CMD.code_color+'python3 Traitement_CMD_v7.py DAT_remove_data "path/to/file/very_nice_data.dat" x[m],y[m] 1234 1324')
        print("           "+EM_CMD.code_color+'python3 Traitement_CMD_v7.py DAT_remove_data "[begone_failure.dat,thanos_snap.dat]" Easting,Northing 42 69 "sep=," replace=True')
        print(EM_CMD.base_color)
    ic += 1
    if help_id == None or help_id == ic:
        print(EM_CMD.title_color)
        curr_title = "[{}] ".format(ic)+_Title_list[ic]+" :"
        print(curr_title+EM_CMD.title_next_color+"."*(nc-len(curr_title)))
        print(EM_CMD.bold_und_color)
        print("DESCRIPTION :"+EM_CMD.bold_color+" Génère des histogrammes sur les colonnes spécifiées.")
        print("Permet également d'obtenir l'index des lignes contenant des valeurs extrêmes sur les données recherchées. Sert à identifier de potentielles valeurs défectueuses.")
        print("Pour les supprimer, on pourra utiliser la fonction 'DAT_remove_data'.")
        print(EM_CMD.code_color)
        print(">>> DAT_stats("+EM_CMD.success_color+"file_list"+EM_CMD.code_color+","+EM_CMD.success_color+"col_list"+EM_CMD.code_color+","+EM_CMD.success_low_color+"[sep"+EM_CMD.code_color+","+
              EM_CMD.success_low_color+"n]"+EM_CMD.code_color+","+EM_CMD.success_low_color+"**kwargs"+EM_CMD.code_color+")")
        print(EM_CMD.base_color)
        print("avec : "+EM_CMD.success_color+"file_list"+EM_CMD.type_color+" : str[] "+EM_CMD.base_color+"= liste des fichiers à traiter")
        print("       "+EM_CMD.success_color+"col_list"+EM_CMD.type_color+" : str[] "+EM_CMD.base_color+"= nom des colonnes concernées (ne pas mettre de crochets pour délimiter la liste)")
        print("       "+EM_CMD.success_low_color+"sep = '\\t'"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= caractère de séparation du .dat (par défaut '\\t')")
        print("       "+EM_CMD.success_low_color+"n = 10"+EM_CMD.type_color+" : int "+EM_CMD.base_color+"= nombre de valeurs à afficher")
        print("       "+EM_CMD.success_low_color+"**kwargs"+EM_CMD.base_color+" : arguments optionels de la fonction 'hist' de pandas (UNIQUEMENT via appel dans le shell/script)")
        print("")
        print("exemples : "+EM_CMD.code_color+'python3 Traitement_CMD_v7.py DAT_stats "path/to/file/very_nice_data.dat" Cond.1[mS/m],Inph.1[ppt]')
        print("           "+EM_CMD.code_color+'python3 Traitement_CMD_v7.py DAT_stats "[there_is_an_imposter.dat,among_us.dat]" Easting,Northing "sep=," n=20')
        print(EM_CMD.base_color)
    ic += 1
    if help_id == None or help_id == ic:
        print(EM_CMD.title_color)
        curr_title = "[{}] ".format(ic)+_Title_list[ic]+" :"
        print(curr_title+EM_CMD.title_next_color+"."*(nc-len(curr_title)))
        print(EM_CMD.bold_und_color)
        print("DESCRIPTION :"+EM_CMD.bold_color+" Permet d'ordonner les colonnes dans un format plus lisible et uniforme.")
        print("En l'occurence, on gardera les colonnes suivantes dans cet ordre : <X_int_1|Y_int_1|Donnée1|Donnée2|...|X_int_2|...|Num fich|b et p|Base|Profil> .")
        print("Toutes les autres colonnes sont supprimées. Nécessite au moins l'interpolation + séparation base/profil + décalage par GPS.")
        print("Nécessite de préciser le nombre de voies des fichiers.")
        print("Pour une procédure de suppression plus libre, voir la fonction 'DAT_remove_cols'.")
        print(EM_CMD.code_color)
        print(">>> DAT_light_format("+EM_CMD.success_color+"file_list"+EM_CMD.code_color+","+EM_CMD.success_low_color+"[sep"+EM_CMD.code_color+","+EM_CMD.success_low_color+"replace"+EM_CMD.code_color+","+
              EM_CMD.success_low_color+"output_file_list"+EM_CMD.code_color+","+EM_CMD.success_low_color+"nb_ecarts"+EM_CMD.code_color+","+EM_CMD.success_low_color+"restr]"+EM_CMD.code_color+")")
        print(EM_CMD.base_color)
        print("avec : "+EM_CMD.success_color+"file_list"+EM_CMD.type_color+" : str[] "+EM_CMD.base_color+"= liste des fichiers à traiter")
        print("       "+EM_CMD.success_low_color+"sep = '\\t'"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= caractère de séparation du .dat (par défaut '\\t')")
        print("       "+EM_CMD.success_low_color+"replace = False"+EM_CMD.type_color+" : bool "+EM_CMD.base_color+"= si le résultat est mis dans le fichier de départ (sinon, un nouveau est créé avec le suffixe '_clean')")
        print("       "+EM_CMD.success_low_color+"output_file_list = None"+EM_CMD.type_color+" : str[] "+EM_CMD.base_color+"= nom des fichier de sortie, n'est pas pris en compte si replace=True")
        print("       "+EM_CMD.success_low_color+"nb_ecarts = 3"+EM_CMD.type_color+" : int "+EM_CMD.base_color+"= nombres de voies/bobines")
        print("       "+EM_CMD.success_low_color+"restr = []"+EM_CMD.type_color+" : str[] "+EM_CMD.base_color+"= strings d'exclusions : toute donnée comprenant l'une des chaînes spécifiées sera ignorée")
        print("")
        print("exemples : "+EM_CMD.code_color+'python3 Traitement_CMD_v7.py DAT_light_format "path/to/file/very_nice_data.dat" nb_ecarts=3')
        print("           "+EM_CMD.code_color+'python3 Traitement_CMD_v7.py DAT_light_format "[order_and_discipline.dat,uniform_like_the_law.dat]" restr=["Inv,Error"] replace=True')
        print(EM_CMD.base_color)
    ic += 1
    if help_id == None or help_id == ic:
        print(EM_CMD.title_color)
        curr_title = "[{}] ".format(ic)+_Title_list[ic]+" :"
        print(curr_title+EM_CMD.title_next_color+"."*(nc-len(curr_title)))
        print(EM_CMD.bold_und_color)
        print("DESCRIPTION :"+EM_CMD.bold_color+" Permet de modifier le séparateur utilisé dans certains fichiers .dat. Utile dans le cas où on souhaite utiliser plusieurs fichiers dans un même traitement.")
        print(EM_CMD.code_color)
        print(">>> DAT_change_sep("+EM_CMD.success_color+"file_list"+EM_CMD.code_color+","+EM_CMD.success_color+"sep"+EM_CMD.code_color+","+EM_CMD.success_color+"new_sep"+EM_CMD.code_color+","+
              EM_CMD.success_low_color+"[replace"+EM_CMD.code_color+","+EM_CMD.success_low_color+"output_file_list]"+EM_CMD.code_color+")")
        print(EM_CMD.base_color)
        print("avec : "+EM_CMD.success_color+"file_list"+EM_CMD.type_color+" : str[] "+EM_CMD.base_color+"= liste des fichiers à traiter")
        print("       "+EM_CMD.success_color+"sep"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= caractère de séparation d'origine du .dat")
        print("       "+EM_CMD.success_color+"new_sep"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= caractère de séparation souhaité pour le .dat")
        print("       "+EM_CMD.success_low_color+"replace = False"+EM_CMD.type_color+" : bool "+EM_CMD.base_color+"= si le résultat est mis dans le fichier de départ (sinon, un nouveau est créé avec le suffixe '_corr')")
        print("       "+EM_CMD.success_low_color+"output_file_list = None"+EM_CMD.type_color+" : str[] "+EM_CMD.base_color+"= nom des fichier de sortie, n'est pas pris en compte si replace=True")
        print("")
        print("exemples : "+EM_CMD.code_color+'python3 Traitement_CMD_v7.py DAT_change_sep "path/to/file/very_nice_data.dat" "\\t" ","')
        print("           "+EM_CMD.code_color+'python3 Traitement_CMD_v7.py DAT_change_sep "[comma_put_me_in_coma.dat,super_NaNny.dat]" "," "!" replace=True "output_file=very_surprised.dat"')
        print(EM_CMD.base_color)
    ic += 1
    if help_id == None or help_id == ic:
        print(EM_CMD.title_color)
        curr_title = "[{}] ".format(ic)+_Title_list[ic]+" :"
        print(curr_title+EM_CMD.title_next_color+"."*(nc-len(curr_title)))
        print(EM_CMD.bold_und_color)
        print("DESCRIPTION :"+EM_CMD.bold_color+" Attribue à chaque point de prospection sans GPS sa vraie position, si celle-ci est répétée sur un même profil.")
        print(EM_CMD.code_color)
        print(">>> DAT_no_gps_pos("+EM_CMD.success_color+"file_list"+EM_CMD.code_color+","+EM_CMD.success_low_color+"[sep"+EM_CMD.code_color+","+EM_CMD.success_low_color+"replace"+EM_CMD.code_color+","+
              EM_CMD.success_low_color+"output_file_list"+EM_CMD.code_color+","+")")
        print(EM_CMD.base_color)
        print("avec : "+EM_CMD.success_color+"file_list"+EM_CMD.type_color+" : str[] "+EM_CMD.base_color+"= liste des fichiers à traiter")
        print("       "+EM_CMD.success_low_color+"sep = '\\t'"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= caractère de séparation du .dat (par défaut '\\t')")
        print("       "+EM_CMD.success_low_color+"replace = False"+EM_CMD.type_color+" : bool "+EM_CMD.base_color+"= si le résultat est mis dans le fichier de départ (sinon, un nouveau est créé avec le suffixe '_pos')")
        print("       "+EM_CMD.success_low_color+"output_file_list = None"+EM_CMD.type_color+" : str[] "+EM_CMD.base_color+"= nom des fichier de sortie, n'est pas pris en compte si replace=True")
        print("")
        print("exemples : "+EM_CMD.code_color+'python3 Traitement_CMD_v7.py DAT_no_gps_pos "path/to/file/very_nice_data.dat"')
        print("           "+EM_CMD.code_color+'python3 Traitement_CMD_v7.py DAT_no_gps_pos "[0and0and0and0and0.dat,from_line_to_square.dat]" sep=, replace=True')
        print(EM_CMD.base_color)
    ic += 1
    if help_id == None or help_id == ic:
        print(EM_CMD.title_color)
        curr_title = "[{}] ".format(ic)+_Title_list[ic]+" :"
        print(curr_title+EM_CMD.title_next_color+"."*(nc-len(curr_title)))
        print(EM_CMD.bold_und_color)
        print("DESCRIPTION :"+EM_CMD.bold_color+" Fusionne une liste de fichiers, en les mettant les uns à la suite des autres dans un autre fichier.")
        print("Nécessite que tous les fichiers aient les mêmes colonnes, l'ordre n'importe pas. L'ordre suit celui de 'file_list'.")
        print(EM_CMD.code_color)
        print(">>> DAT_fuse_data("+EM_CMD.success_color+"file_list"+EM_CMD.success_low_color+"[sep"+EM_CMD.code_color+","+EM_CMD.success_low_color+"output_file]"+EM_CMD.code_color+")")
        print(EM_CMD.base_color)
        print("avec : "+EM_CMD.success_color+"file_list"+EM_CMD.type_color+" : str[] "+EM_CMD.base_color+"= liste des fichiers à traiter")
        print("       "+EM_CMD.success_low_color+"sep = '\\t'"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= caractère de séparation du .dat (par défaut '\\t')")
        print("       "+EM_CMD.success_low_color+"output_file = \"fused.dat\""+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= nom du fichier de sortie.")
        print("")
        print("exemples : "+EM_CMD.code_color+'python3 Traitement_CMD_v7.py DAT_fuse_data "path/to/file/very_nice_data.dat","path/to/otherfile/very_nice_data_two.dat"')
        print("           "+EM_CMD.code_color+'python3 Traitement_CMD_v7.py DAT_fuse_data ["is_the_leader.dat","will_follow.dat","am_your_slave.dat"] "sep=," "output_file=stronger_together.dat"')
        print(EM_CMD.base_color)
    ic += 1
    if help_id == None or help_id == ic:
        print(EM_CMD.title_color)
        curr_title = "[{}] ".format(ic)+_Title_list[ic]+" :"
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
        print("exemples : "+EM_CMD.code_color+'python3 Traitement_CMD_v7.py DAT_fuse_bases "path/to/file/B1.dat" "path/to/file/B2.dat" "path/to/file/very_nice_data.dat"')
        print("           "+EM_CMD.code_color+'python3 Traitement_CMD_v7.py DAT_fuse_bases "I_am_before.dat" "I_am_after.dat" "I_am_the_night.dat" "sep=," "output_file=pI_am_eternal.dat"')
        print(EM_CMD.base_color)
    ic += 1
    if help_id == None or help_id == ic:
        print(EM_CMD.title_color)
        curr_title = "[{}] ".format(ic)+_Title_list[ic]+" :"
        print(curr_title+EM_CMD.title_next_color+"."*(nc-len(curr_title)))
        print(EM_CMD.bold_und_color)
        print("DESCRIPTION :"+EM_CMD.bold_color+" Permet de passer un fichier sortie de 'CMDEX_grid' au format matrice.")
        print("Utile pour utiliser la fonction 'FIG_plot_grid'.")
        print(EM_CMD.code_color)
        print(">>> TRANS_df_to_matrix("+EM_CMD.success_color+"file"+EM_CMD.code_color+","+EM_CMD.success_low_color+"[sep"+EM_CMD.code_color+","+EM_CMD.success_low_color+"output_file]"+EM_CMD.code_color+")")
        print(EM_CMD.base_color)
        print("avec : "+EM_CMD.success_color+"file"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= nom du fichier")
        print("       "+EM_CMD.success_low_color+"sep = '\\t'"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= caractère de séparation du .dat (par défaut '\\t')")
        print("       "+EM_CMD.success_low_color+"output_file = \"mtd.dat\""+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= nom du fichier de sortie")
        print("")
        print("exemples : "+EM_CMD.code_color+'python3 Traitement_CMD_v7.py TRANS_df_to_matrix "path/to/file/very_nice_data_grid.dat"')
        print("           "+EM_CMD.code_color+'python3 Traitement_CMD_v7.py TRANS_df_to_matrix "frame_perfect.dat" output_file="matrixed.json" "sep=,"')
        print(EM_CMD.base_color)
    ic += 1
    if help_id == None or help_id == ic:
        print(EM_CMD.title_color)
        curr_title = "[{}] ".format(ic)+_Title_list[ic]+" :"
        print(curr_title+EM_CMD.title_next_color+"."*(nc-len(curr_title)))
        print(EM_CMD.bold_und_color)
        print("DESCRIPTION :"+EM_CMD.bold_color+" Permet de passer un fichier sortie de 'CMDEX_grid' au format dataframe.")
        print("Utile pour utiliser les données pour des traitements futurs.")
        print(EM_CMD.code_color)
        print(">>> TRANS_matrix_to_df("+EM_CMD.success_color+"file"+EM_CMD.code_color+","+EM_CMD.success_low_color+"[sep"+EM_CMD.code_color+","+EM_CMD.success_low_color+"output_file]"+EM_CMD.code_color+")")
        print(EM_CMD.base_color)
        print("avec : "+EM_CMD.success_color+"file"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= nom du fichier")
        print("       "+EM_CMD.success_low_color+"sep = '\\t'"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= caractère de séparation du .dat de sortie (par défaut '\\t')")
        print("       "+EM_CMD.success_low_color+"output_file = \"dtm.json\""+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= nom du fichier de sortie")
        print("")
        print("exemples : "+EM_CMD.code_color+'python3 Traitement_CMD_v7.py TRANS_matrix_to_df "path/to/file/very_nice_dict.json"')
        print("           "+EM_CMD.code_color+'python3 Traitement_CMD_v7.py TRANS_matrix_to_df "matrix_reloaded.json" output_file="framed.dat" "sep=,"')
        print(EM_CMD.base_color)
    ic += 1
    if help_id == None or help_id == ic:
        print(EM_CMD.title_color)
        curr_title = "[{}] ".format(ic)+_Title_list[ic]+" :"
        print(curr_title+EM_CMD.title_next_color+"."*(nc-len(curr_title)))
        print(EM_CMD.bold_und_color)
        print("DESCRIPTION :"+EM_CMD.bold_color+" Permet de passer un fichier sortie de 'CMDEX_grid' au format matrix à un fichier Surfer.")
        print("Utile pour utiliser les données via le logiciel Golden Software Surfer.")
        print("Un fichier différent est créé pour chaque donnée, ils seront marqués par leur index.")
        print(EM_CMD.code_color)
        print(">>> TRANS_matrix_to_grd("+EM_CMD.success_color+"file"+EM_CMD.code_color+","+EM_CMD.success_color+"fmt"+EM_CMD.code_color+","+EM_CMD.success_low_color+"[output_file]"+EM_CMD.code_color+")")
        print(EM_CMD.base_color)
        print("avec : "+EM_CMD.success_color+"file"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= nom du fichier")
        print("       "+EM_CMD.success_color+"fmt"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= type de format Surfer ('surfer6bin', 'surfer6ascii', 'surfer7bin')")
        print("       "+EM_CMD.success_low_color+"output_file = None"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= nom du fichier de sortie (sinon, un nouveau est créé avec le suffixe '_grd')")
        print("")
        print("exemples : "+EM_CMD.code_color+'python3 Traitement_CMD_v7.py TRANS_matrix_to_grd "path/to/file/very_nice_dict.json" "surfer6bin"')
        print("           "+EM_CMD.code_color+'python3 Traitement_CMD_v7.py TRANS_matrix_to_grd "about_to_surf.json" surfer6ascii output_file="tidal_wave.grd" ')
        print(EM_CMD.base_color)
    ic += 1
    if help_id == None or help_id == ic:
        print(EM_CMD.title_color)
        curr_title = "[{}] ".format(ic)+_Title_list[ic]+" :"
        print(curr_title+EM_CMD.title_next_color+"."*(nc-len(curr_title)))
        print(EM_CMD.bold_und_color)
        print("DESCRIPTION :"+EM_CMD.bold_color+" Permet de passer un fichier Surfer à un fichier au format matrix.")
        print("Utile pour utiliser les données via le logiciel Golden Software Surfer.")
        print("On pourra considérer plusieurs fichiers en même temps, mais les paramètres de la grille doivent être identiques et doivent être au même format.")
        print(EM_CMD.code_color)
        print(">>> TRANS_grd_to_matrix("+EM_CMD.success_color+"file_list"+EM_CMD.code_color+","+EM_CMD.success_color+"fmt"+EM_CMD.code_color+","+EM_CMD.success_low_color+"[output_file]"+EM_CMD.code_color+")")
        print(EM_CMD.base_color)
        print("avec : "+EM_CMD.success_color+"file_list"+EM_CMD.type_color+" : str[] "+EM_CMD.base_color+"= noms des fichiers à rassembler")
        print("       "+EM_CMD.success_color+"fmt"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= type de format Surfer ('surfer6bin', 'surfer6ascii', 'surfer7bin')")
        print("       "+EM_CMD.success_low_color+"output_file = None"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= nom du fichier de sortie (sinon, un nouveau est créé avec le suffixe '_grd')")
        print("")
        print("exemples : "+EM_CMD.code_color+'python3 Traitement_CMD_v7.py TRANS_grd_to_matrix "path/to/file/very_nice_grid.grd" "surfer6bin"')
        print("           "+EM_CMD.code_color+'python3 Traitement_CMD_v7.py TRANS_grd_to_matrix ["end_of_summer.grd",mountain_is_better.grd] surfer6ascii output_file="september.json" ')
        print(EM_CMD.base_color)
    ic += 1
    if help_id == None or help_id == ic:
        print(EM_CMD.title_color)
        curr_title = "[{}] ".format(ic)+_Title_list[ic]+" :"
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
        print("exemples : "+EM_CMD.code_color+'python3 Traitement_CMD_v7.py FIG_display_fig')
        print("           "+EM_CMD.code_color+'python3 Traitement_CMD_v7.py FIG_display_fig "0.pickle,1.pickle,2.pickle,3.pickle,4.pickle,5.pickle"')
        print(EM_CMD.base_color)
    ic += 1
    if help_id == None or help_id == ic:
        print(EM_CMD.title_color)
        curr_title = "[{}] ".format(ic)+_Title_list[ic]+" :"
        print(curr_title+EM_CMD.title_next_color+"."*(nc-len(curr_title)))
        print(EM_CMD.bold_und_color)
        print("DESCRIPTION :"+EM_CMD.bold_color+" Permet d'obtenir les nuages de points des données brutes.")
        print("Les figures sont automatiquement enregistrées dans le dossier 'Output' avec le préfixe 'FIG_'.")
        print(EM_CMD.code_color)
        print(">>> FIG_plot_data("+EM_CMD.success_color+"file"+EM_CMD.code_color+","+EM_CMD.success_low_color+"[sep"+EM_CMD.code_color+","+EM_CMD.success_low_color+"col_x"+EM_CMD.code_color+","+
              EM_CMD.success_low_color+"col_y"+EM_CMD.code_color+","+EM_CMD.success_low_color+"col_z]"+EM_CMD.code_color+")")
        print(EM_CMD.base_color)
        print("avec : "+EM_CMD.success_color+"file"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= nom du fichier")
        print("       "+EM_CMD.success_low_color+"sep = '\\t'"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= caractère de séparation du .dat (par défaut '\\t')")
        print("       "+EM_CMD.success_low_color+"col_x = [0]"+EM_CMD.type_color+" : int[] "+EM_CMD.base_color+"= position des colonnes des coordonnées x (une par voie), la première est 0 (sinon, prend la première)")
        print("       "+EM_CMD.success_low_color+"col_y = [1]"+EM_CMD.type_color+" : int[] "+EM_CMD.base_color+"= position des colonnes des coordonnées y (une par voie), la première est 0 (sinon, prend la seconde)")
        print("       "+EM_CMD.success_low_color+"col_z = None"+EM_CMD.type_color+" : int[] "+EM_CMD.base_color+"= position des colonnes données, la première est 0 (sa taille doit être un multiple de la taille des vecteurs positions) (sinon, prend toutes les autres)")
        print("")
        print("exemples : "+EM_CMD.code_color+'python3 Traitement_CMD_v7.py FIG_plot_data "path/to/file/very_nice_data.dat"')
        print("           "+EM_CMD.code_color+'python3 Traitement_CMD_v7.py FIG_plot_data "day_ta.dat" col_x=0,4,8 col_y=1,5,9 col_z=2,3,6,7,10,11')
        print(EM_CMD.base_color)
    ic += 1
    if help_id == None or help_id == ic:
        print(EM_CMD.title_color)
        curr_title = "[{}] ".format(ic)+_Title_list[ic]+" :"
        print(curr_title+EM_CMD.title_next_color+"."*(nc-len(curr_title)))
        print(EM_CMD.bold_und_color)
        print("DESCRIPTION :"+EM_CMD.bold_color+" Permet d'obtenir les grilles de données à partir du format 'matrix' en .json.")
        print("Les figures sont automatiquement enregistrées dans le dossier 'Output' avec le préfixe 'FIG_'.")
        print(EM_CMD.code_color)
        print(">>> FIG_plot_grid("+EM_CMD.success_color+"file"+EM_CMD.code_color+")")
        print(EM_CMD.base_color)
        print("avec : "+EM_CMD.success_color+"file"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= nom du fichier")
        print("")
        print("exemples : "+EM_CMD.code_color+'python3 Traitement_CMD_v7.py FIG_plot_grid "path/to/file/very_nice_MATRIX.json"')
        print(EM_CMD.base_color)
    ic += 1
    if help_id == None or help_id == ic:
        print(EM_CMD.title_color)
        curr_title = "[{}] ".format(ic)+_Title_list[ic]+" :"
        print(curr_title+EM_CMD.title_next_color+"."*(nc-len(curr_title)))
        print(EM_CMD.bold_und_color)
        print("DESCRIPTION :"+EM_CMD.bold_color+" Permet de comparer les positions des bobines sur l'ensemble de la prospection.")
        print("Chaque couleur correspond à une bobine différente. Pour un même point de prospection, on les relient par un trait noir.")
        print("Attention, cette image peut être relativement lourde à générer si le nombre de points totaux est élevé.")
        print(EM_CMD.code_color)
        print(">>> FIG_plot_pos("+EM_CMD.success_color+"file"+EM_CMD.code_color+","+EM_CMD.success_low_color+"[sep]"+EM_CMD.code_color+")")
        print(EM_CMD.base_color)
        print("avec : "+EM_CMD.success_color+"file"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= nom du fichier")
        print("       "+EM_CMD.success_low_color+"sep = '\\t'"+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= caractère de séparation du .dat (par défaut '\\t')")
        print("")
        print("exemples : "+EM_CMD.code_color+'python3 Traitement_CMD_v7.py FIG_plot_pos "path/to/file/very_nice_data.dat"')
        print("exemples : "+EM_CMD.code_color+'python3 Traitement_CMD_v7.py FIG_plot_pos "points_invasion.dat" sep=,')
        print(EM_CMD.base_color)
    ic += 1
    if help_id == None or help_id == ic:
        print(EM_CMD.title_color)
        curr_title = "[{}] ".format(ic)+_Title_list[ic]+" :"
        print(curr_title+EM_CMD.title_next_color+"."*(nc-len(curr_title)))
        print(EM_CMD.bold_und_color)
        print("DESCRIPTION :"+EM_CMD.bold_color+" Permet d'exécuter n'importe quelle fonction avec ses arguments spécifiés depuis un fichier .txt")
        print("Chaque paramètre (y compris le nom de la fonction) doit être spécifié dans son ordre d'apparition dans la commande.")
        print("Après chaque exécution de fonction réussie, les données permettant de la relancer par cette voie sont mises dans le fichier '_cmd_.txt' du dossier 'EXEC'.")
        print("L'exécution de cette fonction copie également les données du fichier d'entrée dans le fichier '_cmd_.txt'.")
        print(EM_CMD.code_color)
        print(">>> EXEC("+EM_CMD.success_low_color+"[file]"+EM_CMD.code_color+")")
        print(EM_CMD.base_color)
        print("avec : "+EM_CMD.success_low_color+'file = "_cmd_.txt"'+EM_CMD.type_color+" : str "+EM_CMD.base_color+"= nom du fichier contenant la commande (doit être dans le dossier 'EXEC')")
        print("")
        print("exemples : "+EM_CMD.code_color+'python3 Traitement_CMD_v7.py EXEC')
        print("exemples : "+EM_CMD.code_color+'python3 Traitement_CMD_v7.py EXEC file="my_best_memories.txt"')
        print(EM_CMD.base_color)
    print(EM_CMD.success_color+"~"*nc)
    print(EM_CMD.base_color)
    #EM_CMD.shutdown(0)
    
"""
Les fonctions suivantes ne seront pas explicitées car elles reprennent la description de leur équivalent du fichier ``EM_CMD``.
"""
def CMD_exec_known_device(uid,file_list=None,file_list_rev=None,sep='\t',output_file="res.dat",output_file_base="res_B.dat",\
                          light_restr=None,split=False,sup_na=True,regr=False,corr_base=True,no_base=False,choice=False):
    """
    See also
    --------
    ``main, EM_CMD.JSON_find_device``
    """
    app_data = EM_CMD.JSON_find_device(uid)
    print(app_data)
    main(app_data,file_list,file_list_rev,sep,output_file,output_file_base,light_restr,split,sup_na,regr,corr_base,no_base,choice)
    EM_CMD.MESS_succ_mess("Fin de l'exécution !")
    EM_CMD.keep_plt_for_cmd()

def CMD_exec_new_device(app_name,config,nb_ecarts,freq_list,gps=True,gps_dec=[0.0,0.0],TR_l=None,TR_t=None,height=0.1,\
                        bucking_coil=0,coeff_c_ph=None,coeff_c_qu=None,file_list=None,file_list_rev=None,sep='\t',\
                        output_file="res.dat",output_file_base="res_B.dat",light_restr=None,split=False,sup_na=True,\
                        regr=False,corr_base=True,no_base=False,choice=False):
    """
    See also
    --------
    ``main, EM_CMD.JSON_add_device``
    """
    app_data = EM_CMD.JSON_add_device(app_name,config,nb_ecarts,freq_list,gps,gps_dec,TR_l,TR_t,height,bucking_coil,\
                                      coeff_c_ph,coeff_c_qu,autosave=False)
    print(app_data)
    main(app_data,file_list,file_list_rev,sep,output_file,output_file_base,light_restr,split,sup_na,regr,corr_base,no_base,choice)
    EM_CMD.MESS_succ_mess("Fin de l'exécution !")
    EM_CMD.keep_plt_for_cmd()

def CMDEX_ball_calibr(ball_file,config,TR,radius,z,x_min,x_max,sep='\t',y=0,step=5,bucking_coil=0):
    """
    See also
    --------
    ``EM_CMD.FORTRAN_ball_calibr``
    """
    EM_CMD.FORTRAN_ball_calibr(ball_file,config,TR,radius,z,x_min,x_max,sep,y,step,bucking_coil,plot=True)
    EM_CMD.MESS_succ_mess("Fin de l'exécution !")
    EM_CMD.keep_plt_for_cmd()

def CMDEX_init(uid,file_list=None,sep='\t',sup_na=True,regr=False,l_r=None,corr_base=True,no_base=False,pseudo_prof=False,l_p=None):
    """
    See also
    --------
    ``main, EM_CMD.JSON_add_device``
    """
    EM_CMD.CMD_init(uid,file_list,sep,sup_na,regr,l_r,corr_base,no_base,pseudo_prof,l_p,in_file=True)
    EM_CMD.MESS_succ_mess("Fin de l'exécution !")
    EM_CMD.keep_plt_for_cmd()

def CMDEX_evol_profils(file_prof_list,file_base_list,col_z,sep='\t',replace=False,output_file_list=None,nb_ecarts=1,\
                       diff=True,auto_adjust=True,man_adjust=False,line=False):
    """
    See also
    --------
    ``EM_CMD.CMD_evol_profils``
    """
    EM_CMD.CMD_evol_profils(file_prof_list,file_base_list,col_z,sep,replace,output_file_list,nb_ecarts,diff,auto_adjust,\
                            man_adjust,None,line,verif=True,in_file=True)
    EM_CMD.MESS_succ_mess("Fin de l'exécution !")
    EM_CMD.keep_plt_for_cmd()

def CMDEX_frontiere(col_x,col_y,col_z,file_list=None,sep='\t',output_file="frt.dat",choice=False):
    """
    See also
    --------
    ``EM_CMD.CMD_frontiere``
    """
    EM_CMD.CMD_frontiere(col_x,col_y,col_z,file_list,sep,output_file,choice)
    EM_CMD.MESS_succ_mess("Fin de l'exécution !")
    EM_CMD.keep_plt_for_cmd()

def CMDEX_grid(col_x,col_y,col_z,file_list=None,sep='\t',output_file=None,m_type=None,radius=0,prec=100,step=None,\
               seuil=0.0,i_method=None,only_nan=True,no_crop=False,all_models=False,plot_pts=False,matrix=False):
    """
    See also
    --------
    ``EM_CMD.CMD_grid``
    """
    EM_CMD.CMD_grid(col_x,col_y,col_z,file_list,sep,output_file,m_type,radius,prec,step,seuil,i_method,only_nan,\
                    no_crop,all_models,plot_pts=plot_pts,matrix=matrix)
    EM_CMD.MESS_succ_mess("Fin de l'exécution !")
    EM_CMD.keep_plt_for_cmd()

def CMDEX_calibration(uid,col_ph,col_qu,file_list=None,sep='\t',output_file_list=None):
    """
    See also
    --------
    ``EM_CMD.CMD_calibration``
    """
    EM_CMD.CMD_calibration(uid,col_ph,col_qu,file_list,sep,output_file_list)
    EM_CMD.MESS_succ_mess("Fin de l'exécution !")
    EM_CMD.keep_plt_for_cmd()

def JSON_print_devices(uid=None):
    """
    See also
    --------
    ``EM_CMD.JSON_print_devices``
    """
    EM_CMD.JSON_print_devices(uid=uid)


def JSON_add_device(app_name,config,nb_ecarts,freq_list,gps=True,gps_dec=[0.0,0.0],TR_l=None,TR_t=None,height=0.1,\
                    bucking_coil=0,coeff_c_ph=None,coeff_c_qu=None):
    """
    See also
    --------
    ``EM_CMD.JSON_add_device``
    """
    error = EM_CMD.JSON_add_device(app_name,config,nb_ecarts,freq_list,gps,gps_dec,TR_l,TR_t,height,bucking_coil,\
                                   coeff_c_ph,coeff_c_qu,autosave=True,error_code=True)
    if not error:
        EM_CMD.MESS_succ_mess("Appareil ajouté avec succès !")

def JSON_remove_device(uid=None):
    """
    See also
    --------
    ``EM_CMD.JSON_remove_device``
    """
    EM_CMD.JSON_remove_device(uid=uid)
    EM_CMD.MESS_succ_mess("Appareil supprimé avec succès !")

def JSON_modify_device(uid,new_values_dict):
    """
    See also
    --------
    ``EM_CMD.JSON_modify_device``
    """
    EM_CMD.JSON_modify_device(uid,new_values_dict)
    EM_CMD.MESS_succ_mess("Appareil modifié avec succès !")

def DAT_change_date(file_list,date_str,sep='\t',replace=False,output_file_list=None):
    """
    See also
    --------
    ``EM_CMD.DAT_change_date``
    """
    EM_CMD.DAT_change_date(file_list,date_str,sep,replace,output_file_list,in_file=True)
    EM_CMD.MESS_succ_mess("Date modifiée avec succès !")

def DAT_pop_and_dec(file_list,colsup,sep='\t',replace=False,output_file_list=None):
    """
    See also
    --------
    ``EM_CMD.DAT_pop_and_dec``
    """
    EM_CMD.DAT_pop_and_dec(file_list,colsup,sep,replace,output_file_list,in_file=True)
    EM_CMD.MESS_succ_mess("Nom de colonne supprimé avec succès !")

def DAT_switch_cols(file_list,col_a,col_b,sep='\t',replace=False,output_file_list=None):
    """
    See also
    --------
    ``EM_CMD.DAT_switch_cols``
    """
    EM_CMD.DAT_switch_cols(file_list,col_a,col_b,sep,replace,output_file_list,in_file=True)
    EM_CMD.MESS_succ_mess("Colonnes échangées avec succès !")

def DAT_remove_cols(file_list,colsup_list,keep=False,sep='\t',replace=False,output_file_list=None):
    """
    See also
    --------
    ``EM_CMD.DAT_remove_cols``
    """
    EM_CMD.DAT_remove_cols(file_list,colsup_list,keep,sep,replace,output_file_list,in_file=True)
    EM_CMD.MESS_succ_mess("Colonnes supprimées avec succès !")

def DAT_remove_data(file_list,colsup_list,i_min,i_max,sep='\t',replace=False,output_file_list=None):
    """
    See also
    --------
    ``EM_CMD.DAT_remove_data``
    """
    EM_CMD.DAT_remove_data(file_list,colsup_list,i_min,i_max,sep,replace,output_file_list,in_file=True)
    EM_CMD.MESS_succ_mess("Données supprimées avec succès !")

def DAT_stats(file_list,col_list,sep='\t',bins=25,n=10,**kwargs):
    """
    See also
    --------
    ``EM_CMD.DAT_stats``
    """
    EM_CMD.DAT_stats(file_list,col_list,sep,bins,n,**kwargs)

def DAT_light_format(file_list,sep='\t',replace=False,output_file_list=None,nb_ecarts=3,restr=[]):
    """
    See also
    --------
    ``EM_CMD.DAT_light_format``
    """
    EM_CMD.DAT_light_format(file_list,sep,replace,output_file_list,nb_ecarts,restr,in_file=True)
    EM_CMD.MESS_succ_mess("Colonnes ordonnées avec succès !")

def DAT_change_sep(file_list,sep,new_sep,replace=False,output_file_list=None):
    """
    See also
    --------
    ``EM_CMD.DAT_change_sep``
    """
    EM_CMD.DAT_change_sep(file_list,sep,new_sep,replace,output_file_list,in_file=True)
    EM_CMD.MESS_succ_mess("Séparateur modifié avec succès !")

def DAT_no_gps_pos(file_list,sep='\t',replace=False,output_file_list=None):
    """
    See also
    --------
    ``EM_CMD.DAT_no_gps_pos``
    """
    EM_CMD.DAT_no_gps_pos(file_list,sep,replace,output_file_list,in_file=True)
    EM_CMD.MESS_succ_mess("Position ajustée avec succès !")

def DAT_fuse_data(file_list,sep='\t',output_file="fused.dat"):
    """
    See also
    --------
    ``EM_CMD.DAT_fuse_data``
    """
    EM_CMD.DAT_fuse_data(file_list,sep,output_file,in_file=True)
    EM_CMD.MESS_succ_mess("Fichiers fusionnés avec succès !")

def DAT_fuse_bases(file_B1,file_B2,file_prof,sep='\t',output_file=None):
    """
    See also
    --------
    ``EM_CMD.DAT_fuse_bases``
    """
    EM_CMD.DAT_fuse_bases(file_B1,file_B2,file_prof,sep,output_file,in_file=True)
    EM_CMD.MESS_succ_mess("Bases fusionnées avec succès !")

def TRANS_df_to_matrix(file,sep='\t',output_file="mtd.dat"):
    """
    See also
    --------
    ``EM_CMD.TRANS_df_to_matrix``
    """
    EM_CMD.TRANS_df_to_matrix(file,sep,output_file)
    EM_CMD.MESS_succ_mess("Changement de format avec succès !")

def TRANS_matrix_to_df(file,sep='\t',output_file="dtm.json"):
    """
    See also
    --------
    ``EM_CMD.TRANS_matrix_to_df``
    """
    EM_CMD.TRANS_matrix_to_df(file,sep,output_file)
    EM_CMD.MESS_succ_mess("Changement de format avec succès !")

def TRANS_matrix_to_grd(file,fmt,output_file=None):
    """
    See also
    --------
    ``EM_CMD.TRANS_matrix_to_grd``
    """
    EM_CMD.TRANS_matrix_to_grd(file,fmt,output_file)
    EM_CMD.MESS_succ_mess("Changement de format avec succès !")

def TRANS_grd_to_matrix(file_list,fmt,output_file=None):
    """
    See also
    --------
    ``EM_CMD.TRANS_grd_to_matrix``
    """
    EM_CMD.TRANS_grd_to_matrix(file_list,fmt,output_file)
    EM_CMD.MESS_succ_mess("Changement de format avec succès !")

def FIG_display_fig(file_list=None):
    """
    See also
    --------
    ``EM_CMD.FIG_display_fig``
    """
    EM_CMD.FIG_display_fig(file_list)

def FIG_plot_data(file,sep='\t',col_x=[0],col_y=[1],col_z=None):
    """
    See also
    --------
    ``EM_CMD.FIG_plot_data``
    """
    EM_CMD.FIG_plot_data(file,sep,col_x,col_y,col_z)

def FIG_plot_grid(file):
    """
    See also
    --------
    ``EM_CMD.FIG_plot_grid``
    """
    EM_CMD.FIG_plot_grid(file)

def FIG_plot_pos(file,sep='\t'):
    """
    See also
    --------
    ``EM_CMD.FIG_plot_pos``
    """
    EM_CMD.FIG_plot_pos(file,sep)

def EXEC(file="_cmd_.txt"):
    """ [TA]\n
    Load function call parameters from text file.
    Can be used to create call templates and skip the classic procedure.
    
    Notes
    -----
    If a function call successfully terminate, call parameters are automatically saved in ``EXEC/_cmd_.txt``.
    Files must be in the ``EXEC`` folder.
    
    Parameters
    ----------
    file : str
        File containing function call parameters. No path is expected.
    
    Returns
    -------
    none, but directly update ``sys.argv``.
    
    Raises
    ------
    * File not found.
    """
    sys.argv = sys.argv[:1]
    try:
        with open("EXEC/"+file, 'r') as cmd_file:
            for ic,var in enumerate(cmd_file):
                sys.argv.append(var[:-1])
    except FileNotFoundError:
        EM_CMD.MESS_err_mess('Le fichier "{}" est introuvable'.format(file))

# lecture de la commande utilisateur

def function_call():
    """ [TA]\n
    Handles ``sys.argv`` to call the right function with the right parameters.\n
    
    Notes
    -----
    ``CMD_help(-1)`` is called by default if no parameter is specified.\n
    To execute a 'void' call, use ``0``. It's an empty code block that can be used for testing.\n
    If a function call is successful, saves parameters in ``EXEC/_cmd_.txt``.\n
    Using ``globals()[sys.argv[1]] == [function_name]`` helps to identificate if the requested function is protected or does not exists.\n
    Remarks regarding how to correctly assign mandatory parameters to variables :\n
    * If parameter is a file path, use ``EM_CMD.TOOL_str_clean`` with ``path = True``.
    * If parameter is a file path list, use ``EM_CMD.TOOL_split_str_list`` with ``path = True``.
    * If parameter is a column label, use ``EM_CMD.TOOL_str_clean`` with ``noclean = True``.
    * If parameter is a column label list, use ``EM_CMD.TOOL_split_str_list`` with ``noclean = True``.
    * If parameter is a regular list, use ``EM_CMD.TOOL_split_str_list`` with default parameters.
    * If parameter is a regular string, simply assign the corresponding ``sys.argv`` element.
    * If parameter is a boolean, use ``EM_CMD.TOOL_str_to_bool``.
    * If parameter is a numeric, simply convert the corresponding ``sys.argv`` element to right type.
    Remarks regarding how to correctly assign optional parameters to variables :\n
    * Assign default value to parameter below mandatory parameters.
    * Check if length of ``sys.argv`` surpasses the number of mandatory parameters + 2 (this file name + function name).
    * If yes, call ``EM_CMD.TOOL_optargs_list`` with only the optional parameters from ``sys.argv`` on first argument.\
    Second argument is the list of all optional variable names as string.\
    Third argument is the list of their type. Lists of type *t* should be written as such : ``[t]``.\
    Order of second and third parameters must match.\
    Output of the function is a dictionary.
    * You can then retrieve the parameters' value by using the ``.get()`` procedure for each variable, where parameters are \
    the variable string label and their default value. That way, only parameters that were specified by user are modified.
    After every parameter is set, you call finally call the corresponding function as normal.
    
    Parameters
    ----------
    none, but uses ``sys.argv`` which are the python command parameters.
    
    Raises
    ------
    * Function is protected (cannot be called as standalone).
    * Function does not exists.
    * Function got wrong number of parameters.
    * Function mandatory parameter is of wrong type.
    * Function call with ``CMD_help`` got unknown function.
    * Function call with ``CMD_help`` got protected function.
    
    See also
    --------
    ``CMD_help, EM_CMD.TOOL_optargs_list, EM_CMD.TOOL_str_clean, EM_CMD.TOOL_split_str_list, EM_CMD.TOOL_str_to_bool``
    """
    # tekst = matplotlib.get_backend()
    # print("Backend = ", tekst)
    # plt.switch_backend('Agg')
    # plt.switch_backend('TkAgg')
    # tekst = matplotlib.get_backend()
    # print("Backend = ", tekst)
    try:
        if len(sys.argv) > 1 and sys.argv[1] == "EXEC":
            file = "_cmd_.txt"
            if len(sys.argv) > 2:
                opt_params = EM_CMD.TOOL_optargs_list(sys.argv[2:], ["file"], [str])
                file = opt_params.get("file", "_cmd_.txt")
            EXEC(file)
        os.chdir(CONFIG.data_path)
        if len(sys.argv) == 1:
            CMD_help(-1)
        elif sys.argv[1] == "0":
            print("Appel passif")
            init_app_dat()
        elif globals()[sys.argv[1]] == CMD_help:
            if len(sys.argv) > 2:
                if sys.argv[2] == "c":
                    CMD_help("c")
                else:
                    found = False
                    for ic, func_name in enumerate(_Func_Name_List):
                        if sys.argv[2] == func_name or sys.argv[2] == str(ic):
                            CMD_help(ic)
                            found = True
                    if not found:
                        if sys.argv[2] in globals():
                            EM_CMD.MESS_err_mess("La fonction est protégée : aucune aide")
                        else:
                            EM_CMD.MESS_err_mess("La fonction ou l'indice ne correspond à aucune fonction connue")
            else:
                CMD_help()
        elif globals()[sys.argv[1]] == CMD_exec_known_device:
            uid = int(sys.argv[2])
            file_list = None
            file_list_rev = None
            sep = '\t'
            output_file = "res.dat"
            output_file_base = "res_B.dat"
            light_restr = None
            split = False
            sup_na = True
            regr = False
            corr_base = True
            no_base = False
            choice = False
            if len(sys.argv) > 3:
                opt_params = EM_CMD.TOOL_optargs_list(sys.argv[3:], ["file_list","file_list_rev","sep","output_file","output_file_base","light_restr",\
                                                                     "split","sup_na","regr","corr_base","no_base","choice"],
                                                                     [[str],[str],str,str,str,[str],bool,bool,bool,bool,bool,bool])
                file_list = opt_params.get("file_list", None)
                file_list_rev = opt_params.get("file_list_rev", None)
                sep = opt_params.get("sep", '\t')
                output_file = opt_params.get("output_file", "res.dat")
                output_file_base = opt_params.get("output_file_base", "res_B.dat")
                light_restr = opt_params.get("light_restr", None)
                split = opt_params.get("split", False)
                sup_na = opt_params.get("sup_na", True)
                regr = opt_params.get("regr", False)
                corr_base = opt_params.get("corr_base", True)
                no_base = opt_params.get("no_base", False)
                choice = opt_params.get("choice", False)
            CMD_exec_known_device(uid,file_list,file_list_rev,sep,output_file,output_file_base,light_restr,split,sup_na,regr,corr_base,no_base,choice)
        elif globals()[sys.argv[1]] == CMD_exec_new_device:
            app_name = EM_CMD.TOOL_str_clean(sys.argv[2])
            config = EM_CMD.TOOL_str_clean(sys.argv[3])
            nb_ecarts = int(sys.argv[4])
            freq_list = EM_CMD.TOOL_split_str_list(sys.argv[5], float)
            gps = True
            gps_dec = [0.0,0.0]
            TR_l = None
            TR_t = None
            height = 0.1
            bucking_coil = 0
            coeff_c_ph = None
            coeff_c_qu = None
            file_list = None
            file_list_rev = None
            sep = '\t'
            output_file = "res.dat"
            output_file_base = "res_B.dat"
            light_restr = None
            split = False
            sup_na = True
            regr = False
            corr_base = True
            no_base = False
            choice  = False
            if len(sys.argv) > 6:
                opt_params = EM_CMD.TOOL_optargs_list(sys.argv[6:], ["GPS","GPS_dec","TR_l","TR_t","height","bucking_coil","coeff_c_ph","coeff_c_qu","file_list",\
                                                                     "file_list_rev","sep","output_file","output_file_base","light_restr","split","sup_na",\
                                                                     "regr","corr_base","no_base","choice"],\
                                                                     [bool,[float],[float],[float],float,int,[float],[float],[str],[str],str,str,[str],bool,bool,bool,bool,bool,bool])
                gps = opt_params.get("GPS", True)
                gps_dec = opt_params.get("GPS_dec", [0.0,0.0])
                TR_l = opt_params.get("TR_l", None)
                TR_t = opt_params.get("TR_t", None)
                height = opt_params.get("height", 0.1)
                bucking_coil = opt_params.get("bucking_coil", 0)
                coeff_c_ph = opt_params.get("coeff_c_ph", None)
                coeff_c_qu = opt_params.get("coeff_c_qu", None)
                file_list = opt_params.get("file_list", None)
                file_list_rev = opt_params.get("file_list_rev", None)
                sep = opt_params.get("sep", '\t')
                output_file = opt_params.get("output_file", "res.dat")
                output_file_base = opt_params.get("output_file_base", "res_B.dat")
                light_restr = opt_params.get("light_restr", None)
                split = opt_params.get("split", False)
                sup_na = opt_params.get("sup_na", True)
                regr = opt_params.get("regr", False)
                corr_base = opt_params.get("corr_base", True)
                no_base = opt_params.get("no_base", False)
                choice = opt_params.get("choice", False)
            CMD_exec_new_device(app_name,config,nb_ecarts,freq_list,gps,gps_dec,TR_l,TR_t,height,bucking_coil,coeff_c_ph,coeff_c_qu,file_list,file_list_rev,\
                                sep,output_file,output_file_base,light_restr,split,sup_na,regr,corr_base,no_base,choice)
        elif globals()[sys.argv[1]] == CMDEX_ball_calibr:
            ball_file = EM_CMD.TOOL_str_clean(sys.argv[2], path=True)
            config = EM_CMD.TOOL_str_clean(sys.argv[3])
            TR = EM_CMD.TOOL_split_str_list(sys.argv[4], int)
            radius = int(sys.argv[5])
            z = int(sys.argv[6])
            x_min = int(sys.argv[7])
            x_max = int(sys.argv[8])
            sep = '\t'
            y = 0
            step = 5
            bucking_coil = 0
            if len(sys.argv) > 9:
                opt_params = EM_CMD.TOOL_optargs_list(sys.argv[9:], ["sep","y","step","bucking_coil"], [str,int,int,int])
                sep = opt_params.get("sep", '\t')
                y = opt_params.get("y", 0)
                step = opt_params.get("step", 5)
                bucking_coil = opt_params.get("bucking_coil", 0)
            CMDEX_ball_calibr(ball_file,config,TR,radius,z,x_min,x_max,sep,y,step,bucking_coil)
        elif globals()[sys.argv[1]] == CMDEX_init:
            uid = int(sys.argv[2])
            file_list = None
            sep = '\t'
            sup_na = True
            regr = False
            l_r = None
            corr_base = True
            no_base = False
            pseudo_prof = False
            l_p = None
            if len(sys.argv) > 3:
                opt_params = EM_CMD.TOOL_optargs_list(sys.argv[3:], ["file_list","sep","sup_na","regr","l_r","corr_base","no_base","pseudo_prof","l_p"], [[str],str,bool,bool,[int],bool,bool,bool,[float]])
                file_list = opt_params.get("file_list", None)
                sep = opt_params.get("sep", '\t')
                sup_na = opt_params.get("sup_na", True)
                regr = opt_params.get("regr", False)
                l_r = opt_params.get("l_r", None)
                corr_base = opt_params.get("corr_base", True)
                no_base = opt_params.get("no_base", False)
                pseudo_prof = opt_params.get("pseudo_prof", False)
                l_p = opt_params.get("l_p", False)
            CMDEX_init(uid,file_list,sep,sup_na,regr,l_r,corr_base,no_base,pseudo_prof,l_p)
        elif globals()[sys.argv[1]] == CMDEX_evol_profils:
            file_prof_list = EM_CMD.TOOL_split_str_list(sys.argv[2], str, path=True)
            file_base_list = EM_CMD.TOOL_split_str_list(sys.argv[3], str, path=True)
            col_z = EM_CMD.TOOL_split_str_list(sys.argv[4], int)
            sep = '\t'
            replace = False
            output_file_list = None
            nb_ecarts = 1
            diff = True
            auto_adjust = True
            man_adjust = False
            line = False
            if len(sys.argv) > 5:
                opt_params = EM_CMD.TOOL_optargs_list(sys.argv[5:], ["sep","replace","output_file_list","nb_ecarts","diff","auto_adjust","man_adjust","line"],\
                                                                    [str,bool,[str],int,bool,bool,bool,bool])
                sep = opt_params.get("sep", '\t')
                replace = opt_params.get("replace", False)
                output_file_list = opt_params.get("output_file_list", None)
                nb_ecarts = opt_params.get("nb_ecarts", 1)
                diff = opt_params.get("diff", True)
                auto_adjust = opt_params.get("auto_adjust", True)
                man_adjust = opt_params.get("man_adjust", False)
                line = opt_params.get("line", False)
            CMDEX_evol_profils(file_prof_list,file_base_list,col_z,sep,replace,output_file_list,nb_ecarts,diff,auto_adjust,man_adjust,line)
        elif globals()[sys.argv[1]] == CMDEX_frontiere:
            col_x = EM_CMD.TOOL_split_str_list(sys.argv[2], int)
            col_y = EM_CMD.TOOL_split_str_list(sys.argv[3], int)
            col_z = EM_CMD.TOOL_split_str_list(sys.argv[4], int)
            file_list = None
            sep = '\t'
            output_file = None
            choice = False
            if len(sys.argv) > 5:
                opt_params = EM_CMD.TOOL_optargs_list(sys.argv[5:], ["file_list","sep","output_file","choice"], [[str],str,str,bool])
                file_list = opt_params.get("file_list", None)
                sep = opt_params.get("sep", '\t')
                output_file = opt_params.get("output_file", None)
                choice = opt_params.get("choice", False)
            CMDEX_frontiere(col_x,col_y,col_z,file_list,sep,output_file,choice)
        elif globals()[sys.argv[1]] == CMDEX_grid:
            col_x = EM_CMD.TOOL_split_str_list(sys.argv[2], int)
            col_y = EM_CMD.TOOL_split_str_list(sys.argv[3], int)
            col_z = EM_CMD.TOOL_split_str_list(sys.argv[4], int)
            file_list = None
            sep = '\t'
            output_file = None
            m_type = None
            radius = 0
            prec = 100
            step = None
            seuil = 0
            i_method = None
            only_nan = True
            no_crop = False
            all_models = False
            plot_pts = False
            matrix = False
            if len(sys.argv) > 5:
                opt_params = EM_CMD.TOOL_optargs_list(sys.argv[5:], ["file_list","sep","output_file","m_type","radius","prec","step","seuil","i_method",\
                                                                     "only_nan","no_crop","all_models","plot_pts","matrix"],\
                                                                    [[str],str,str,str,int,int,float,float,str,bool,bool,bool,bool,bool])
                file_list = opt_params.get("file_list", None)
                sep = opt_params.get("sep", '\t')
                output_file = opt_params.get("output_file", None)
                m_type = opt_params.get("m_type", None)
                radius = opt_params.get("radius", 0)
                prec = opt_params.get("prec", 100)
                step = opt_params.get("step", None)
                seuil = opt_params.get("seuil", 0)
                i_method = opt_params.get("i_method", None)
                only_nan = opt_params.get("only_nan", True)
                no_crop = opt_params.get("no_crop", False)
                all_models = opt_params.get("all_models", False)
                plot_pts = opt_params.get("plot_pts", False)
                matrix = opt_params.get("matrix", False)
            CMDEX_grid(col_x,col_y,col_z,file_list,sep,output_file,m_type,radius,prec,step,seuil,i_method,only_nan,no_crop,all_models,plot_pts,matrix)
        elif globals()[sys.argv[1]] == CMDEX_calibration:
            uid = int(sys.argv[2])
            col_ph = EM_CMD.TOOL_split_str_list(sys.argv[3], int)
            col_qu = EM_CMD.TOOL_split_str_list(sys.argv[4], int)
            file_list = None
            sep = '\t'
            output_file_list = None
            if len(sys.argv) > 5:
                opt_params = EM_CMD.TOOL_optargs_list(sys.argv[5:], ["file_list","sep","output_file_list"],[[str],str,str])
                file_list = opt_params.get("file_list", None)
                sep = opt_params.get("sep", '\t')
                output_file_list = opt_params.get("output_file_list", None)
            CMDEX_calibration(uid,col_ph,col_qu,file_list,sep,output_file_list)
        elif globals()[sys.argv[1]] == JSON_print_devices:
            uid = None
            if len(sys.argv) > 2:
                opt_params = EM_CMD.TOOL_optargs_list(sys.argv[2:], ["uid"], [int])
                uid = opt_params.get("uid", None)
            JSON_print_devices(uid)
        elif globals()[sys.argv[1]] == JSON_add_device:
            app_name = EM_CMD.TOOL_str_clean(sys.argv[2])
            config = EM_CMD.TOOL_str_clean(sys.argv[3])
            nb_ecarts = int(sys.argv[4])
            freq_list = EM_CMD.TOOL_split_str_list(sys.argv[5], float)
            gps = True
            gps_dec = [0.0,0.0]
            TR_l = None
            TR_t = None
            height = 0.1
            bucking_coil = 0
            coeff_c_ph = None
            coeff_c_qu = None
            if len(sys.argv) > 6:
                opt_params = EM_CMD.TOOL_optargs_list(sys.argv[6:], ["GPS","GPS_dec","TR_l","TR_t","height","bucking_coil","coeff_c_ph","coeff_c_qu"],\
                                                                    [bool,[float],[float],[float],float,float,[float],[float]])
                gps = opt_params.get("GPS", True)
                gps_dec = opt_params.get("GPS_dec", [0.0,0.0])
                TR_l = opt_params.get("TR_l", None)
                TR_t = opt_params.get("TR_t", None)
                height = opt_params.get("height", 0.1)
                bucking_coil = opt_params.get("bucking_coil", 0)
                coeff_c_ph = opt_params.get("coeff_c_ph", None)
                coeff_c_qu = opt_params.get("coeff_c_qu", None)
            JSON_add_device(app_name,config,nb_ecarts,freq_list,gps,gps_dec,TR_l,TR_t,height,bucking_coil,coeff_c_ph,coeff_c_qu)
        elif globals()[sys.argv[1]] == JSON_remove_device:
            uid = -1
            if len(sys.argv) > 2:
                opt_params = EM_CMD.TOOL_optargs_list(sys.argv[2:], ["uid"], [int])
                uid = opt_params.get("uid", -1)
            JSON_remove_device(uid)
        elif globals()[sys.argv[1]] == JSON_modify_device:
            uid = int(sys.argv[2])
            if len(sys.argv) > 3:
                opt_params = EM_CMD.TOOL_optargs_list(sys.argv[3:], ["app_name","config","nb_ecarts","freq_list","GPS","GPS_dec","TR_l","TR_t","height","bucking_coil","coeff_c_ph","coeff_c_qu","config_angles"],\
                                                                    [str,str,int,[float],bool,[float],[float],[float],float,float,[float],[float],[float]])
            JSON_modify_device(uid,opt_params)
        elif globals()[sys.argv[1]] == DAT_change_date:
            file_list = EM_CMD.TOOL_split_str_list(sys.argv[2], str, path=True)
            date_str = sys.argv[3]
            sep = '\t'
            replace = False
            output_file_list = None
            if len(sys.argv) > 4:
                opt_params = EM_CMD.TOOL_optargs_list(sys.argv[4:], ["sep","replace","output_file_list"], [str,bool,[str]])
                sep = opt_params.get("sep", '\t')
                replace = opt_params.get("replace", False)
                output_file_list = opt_params.get("output_file_list", None)
            DAT_change_date(file_list,date_str,sep,replace,output_file_list)
        elif globals()[sys.argv[1]] == DAT_pop_and_dec:
            file_list = EM_CMD.TOOL_split_str_list(sys.argv[2], str, path=True)
            colsup = sys.argv[3]
            sep = '\t'
            replace = False
            output_file_list = None
            if len(sys.argv) > 4:
                opt_params = EM_CMD.TOOL_optargs_list(sys.argv[4:], ["sep","replace","output_file_list"], [str,bool,[str]])
                sep = opt_params.get("sep", '\t')
                replace = opt_params.get("replace", False)
                output_file_list = opt_params.get("output_file_list", None)
            DAT_pop_and_dec(file_list,colsup,sep,replace,output_file_list)
        elif globals()[sys.argv[1]] == DAT_switch_cols:
            file_list = EM_CMD.TOOL_split_str_list(sys.argv[2], str, path=True)
            col_a = sys.argv[3]
            col_b = sys.argv[4]
            sep = '\t'
            replace = False
            output_file_list = None
            if len(sys.argv) > 5:
                opt_params = EM_CMD.TOOL_optargs_list(sys.argv[5:], ["sep","replace","output_file_list"], [str,bool,[str]])
                sep = opt_params.get("sep", '\t')
                replace = opt_params.get("replace", False)
                output_file_list = opt_params.get("output_file_list", None)
            DAT_switch_cols(file_list,col_a,col_b,sep,replace,output_file_list)
        elif globals()[sys.argv[1]] == DAT_remove_cols:
            file_list = EM_CMD.TOOL_split_str_list(sys.argv[2], str, path=True)
            colsup_list = EM_CMD.TOOL_split_str_list(sys.argv[3], str, noclean=True)
            keep = False
            sep = '\t'
            replace = False
            output_file_list = None
            if len(sys.argv) > 4:
                opt_params = EM_CMD.TOOL_optargs_list(sys.argv[4:], ["keep","sep","replace","output_file_list"], [bool,str,bool,[str]])
                keep = opt_params.get("keep", False)
                sep = opt_params.get("sep", '\t')
                replace = opt_params.get("replace", False)
                output_file_list = opt_params.get("output_file_list", None)
            DAT_remove_cols(file_list,colsup_list,keep,sep,replace,output_file_list)
        elif globals()[sys.argv[1]] == DAT_remove_data:
            file_list = EM_CMD.TOOL_split_str_list(sys.argv[2], str, path=True)
            colsup_list = EM_CMD.TOOL_split_str_list(sys.argv[3], str, noclean=True)
            i_min = int(sys.argv[4])
            i_max = int(sys.argv[5])
            sep = '\t'
            replace = False
            output_file_list = None
            if len(sys.argv) > 6:
                opt_params = EM_CMD.TOOL_optargs_list(sys.argv[6:], ["sep","replace","output_file_list"], [str,bool,[str]])
                sep = opt_params.get("sep", '\t')
                replace = opt_params.get("replace", False)
                output_file_list = opt_params.get("output_file_list", None)
            DAT_remove_data(file_list,colsup_list,i_min,i_max,sep,replace,output_file_list)
        elif globals()[sys.argv[1]] == DAT_stats:
            file_list = EM_CMD.TOOL_split_str_list(sys.argv[2], str, path=True)
            col_list = EM_CMD.TOOL_split_str_list(sys.argv[3], str, noclean=True)
            sep = '\t'
            bins = 25
            n = 10
            if len(sys.argv) > 4:
                opt_params = EM_CMD.TOOL_optargs_list(sys.argv[4:], ["sep","bins","n"], [str,int,int])
                sep = opt_params.get("sep", '\t')
                bins = opt_params.get("bins", 25)
                n = opt_params.get("n", 10)
            DAT_stats(file_list,col_list,sep,bins,n)
        elif globals()[sys.argv[1]] == DAT_light_format:
            file_list = EM_CMD.TOOL_split_str_list(sys.argv[2], str, path=True)
            sep = '\t'
            replace = False
            output_file_list = None
            nb_ecarts = 3
            restr = []
            if len(sys.argv) > 3:
                opt_params = EM_CMD.TOOL_optargs_list(sys.argv[3:], ["sep","replace","output_file_list","nb_ecarts","restr"], [str,bool,[str],int,[str]])
                sep = opt_params.get("sep", '\t')
                replace = opt_params.get("replace", False)
                output_file_list = opt_params.get("output_file_list", None)
                nb_ecarts = opt_params.get("nb_ecarts", 3)
                restr = opt_params.get("restr", [])
            DAT_light_format(file_list,sep,replace,output_file_list,nb_ecarts,restr)
        elif globals()[sys.argv[1]] == DAT_change_sep:
            file_list = EM_CMD.TOOL_split_str_list(sys.argv[2], str, path=True)
            sep = EM_CMD.TOOL_str_clean(sys.argv[3])
            new_sep = EM_CMD.TOOL_str_clean(sys.argv[4])
            replace = False
            output_file_list = None
            if len(sys.argv) > 5:
                opt_params = EM_CMD.TOOL_optargs_list(sys.argv[5:], ["replace","output_file_list"], [bool,[str]])
                replace = opt_params.get("replace", False)
                output_file_list = opt_params.get("output_file_list", None)
            DAT_change_sep(file_list,sep,new_sep,replace,output_file_list)
        elif globals()[sys.argv[1]] == DAT_no_gps_pos:
            file_list = EM_CMD.TOOL_split_str_list(sys.argv[2], str, path=True)
            sep = '\t'
            replace = False
            output_file_list = None
            if len(sys.argv) > 3:
                opt_params = EM_CMD.TOOL_optargs_list(sys.argv[3:], ["sep","replace","output_file_list"], [str,bool,[str]])
                sep = opt_params.get("sep", '\t')
                replace = opt_params.get("replace", False)
                output_file_list = opt_params.get("output_file_list", None)
            DAT_no_gps_pos(file_list,sep,replace,output_file_list)
        elif globals()[sys.argv[1]] == DAT_fuse_data:
            file_list = EM_CMD.TOOL_split_str_list(sys.argv[2], str, path=True)
            sep = '\t'
            output_file = "fused.dat"
            if len(sys.argv) > 3:
                opt_params = EM_CMD.TOOL_optargs_list(sys.argv[3:], ["sep","output_file"], [str,str])
                sep = opt_params.get("sep", '\t')
                output_file = opt_params.get("output_file", "fused.dat")
            DAT_fuse_data(file_list,sep,output_file)
        elif globals()[sys.argv[1]] == DAT_fuse_bases:
            file_B1 = EM_CMD.TOOL_str_clean(sys.argv[2], path=True)
            file_B2 = EM_CMD.TOOL_str_clean(sys.argv[3], path=True)
            file_prof = EM_CMD.TOOL_str_clean(sys.argv[4], path=True)
            sep = '\t'
            output_file = None
            if len(sys.argv) > 5:
                opt_params = EM_CMD.TOOL_optargs_list(sys.argv[5:], ["sep","output_file"], [str,str])
                sep = opt_params.get("sep", '\t')
                output_file = opt_params.get("output_file", None)
            DAT_fuse_bases(file_B1,file_B2,file_prof,sep,output_file)
        elif globals()[sys.argv[1]] == TRANS_df_to_matrix:
            file = EM_CMD.TOOL_str_clean(sys.argv[2], path=True)
            sep = '\t'
            output_file = "dtm.json"
            if len(sys.argv) > 3:
                opt_params = EM_CMD.TOOL_optargs_list(sys.argv[3:], ["sep","output_file"], [str,str])
                sep = opt_params.get("sep", '\t')
                output_file = opt_params.get("output_file", "dtm.json")
            TRANS_df_to_matrix(file,sep,output_file)
        elif globals()[sys.argv[1]] == TRANS_matrix_to_df:
            file = EM_CMD.TOOL_str_clean(sys.argv[2], path=True)
            sep = '\t'
            output_file = "mtd.dat"
            if len(sys.argv) > 3:
                opt_params = EM_CMD.TOOL_optargs_list(sys.argv[3:], ["sep","output_file"], [str,str])
                sep = opt_params.get("sep", '\t')
                output_file = opt_params.get("output_file", "mtd.dat")
            TRANS_matrix_to_df(file,sep,output_file)
        elif globals()[sys.argv[1]] == TRANS_matrix_to_grd:
            file = EM_CMD.TOOL_str_clean(sys.argv[2], path=True)
            fmt = EM_CMD.TOOL_str_clean(sys.argv[3])
            output_file = None
            if len(sys.argv) > 4:
                opt_params = EM_CMD.TOOL_optargs_list(sys.argv[4:], ["output_file"], [str])
                output_file = opt_params.get("output_file", None)
            TRANS_matrix_to_grd(file,fmt,output_file)
        elif globals()[sys.argv[1]] == TRANS_grd_to_matrix:
            file_list = EM_CMD.TOOL_split_str_list(sys.argv[2], str, path=True)
            fmt = EM_CMD.TOOL_str_clean(sys.argv[3])
            output_file = None
            if len(sys.argv) > 4:
                opt_params = EM_CMD.TOOL_optargs_list(sys.argv[4:], ["output_file"], [str])
                output_file = opt_params.get("output_file", None)
            TRANS_grd_to_matrix(file_list,fmt,output_file)
        elif globals()[sys.argv[1]] == FIG_display_fig:
            file_list = None
            if len(sys.argv) > 2:
                opt_params = EM_CMD.TOOL_optargs_list(sys.argv[2:], ["file_list"], [[str]])
                file_list = opt_params.get("file_list", None)
            FIG_display_fig(file_list)
        elif globals()[sys.argv[1]] == FIG_plot_data:
            file = EM_CMD.TOOL_str_clean(sys.argv[2], path=True)
            sep = '\t'
            col_x = [0]
            col_y = [1]
            col_z = None
            if len(sys.argv) > 3:
                opt_params = EM_CMD.TOOL_optargs_list(sys.argv[3:], ["sep","col_x","col_y","col_z"], [str,[int],[int],[int]])
                sep = opt_params.get("sep", '\t')
                col_x = opt_params.get("col_x", [0])
                col_y = opt_params.get("col_y", [1])
                col_z = opt_params.get("col_z", None)
            FIG_plot_data(file,sep,col_x,col_y,col_z)
        elif globals()[sys.argv[1]] == FIG_plot_pos:
            file = EM_CMD.TOOL_str_clean(sys.argv[2], path=True)
            sep = '\t'
            if len(sys.argv) > 3:
                opt_params = EM_CMD.TOOL_optargs_list(sys.argv[3:], ["sep"], [str])
                sep = opt_params.get("sep", '\t')
            FIG_plot_pos(file,sep)
        elif globals()[sys.argv[1]] == FIG_plot_grid:
            file = EM_CMD.TOOL_str_clean(sys.argv[2], path=True)
            if len(sys.argv) > 3:
                EM_CMD.TOOL_optargs_list(sys.argv[3:], [], [])
            FIG_plot_grid(file,sep)
        else:
            EM_CMD.MESS_err_mess("La fonction choisie est protégée")
    except KeyError:
        EM_CMD.MESS_err_mess("La fonction choisie n'existe pas (voir aide)")
    # except IndexError:
    #     EM_CMD.MESS_err_mess("Le nombre de paramètres est insuffisant (voir aide)")
    # except ValueError:
    #     EM_CMD.MESS_err_mess("Un des paramètres n'est pas du bon type")
    
    os.chdir(CONFIG.script_path)
    with open("EXEC/_cmd_.txt", 'w') as cmd_file:
        for v in sys.argv[1:]:
            if v not in ["GraphicUI","GraphicUIn't","GraphicUI_ignore"]:
                cmd_file.write(v + '\n')

if __name__ == '__main__':
    function_call()


