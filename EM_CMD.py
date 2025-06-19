# -*- coding: utf-8 -*-
"""
Created on Thu Jan 30 16:16:13 2025

@author: thiesson
"""

'''
module py
'''
import os
import glob
import sys
import matplotlib
import matplotlib.pyplot as plt
#plt.ion()
import numpy as np
import pandas as pd
from scipy.stats import linregress
import scipy.interpolate as scii
import gstlearn as gl
import gstlearn.plot as gp
import random
import re
import datetime
import json
import pickle
import tkinter as tk
import tkinter.ttk as ttk
from IPython import get_ipython
import warnings

import CONFIG

# plt.rcParams['figure.subplot.left'] = 0.086
# plt.rcParams['figure.subplot.right'] = 0.97
# plt.rcParams['figure.subplot.bottom'] = 0.086
# plt.rcParams['figure.subplot.top'] = 0.97
# print(matplotlib.matplotlib_fname())

# --- Constantes de DEV (à ne pas toucher pour conserver l'expérience originale) ---

# Couleurs de terminal. Elles sont persistantes entre les prints donc il faut revenir sur base_color
# si on veut annuler la modification de l'affichage.
# Documentation disponible avec la commande "man dir colors".

GUI = CONFIG.ui_popups_from_cmd # Si on utilise l'interface graphique
FROM_GI_PY = False
GUI_VAR_LIST = []
def is_from_spyder():
    return get_ipython().__class__.__name__ == 'SpyderShell'

spyder = is_from_spyder()

def keep_plt_for_cmd():
    if not spyder and not FROM_GI_PY:
        input()

if CONFIG.no_warnings:
    warnings.filterwarnings("ignore")

def shutdown(v):
    if spyder:
        warnings.filterwarnings("ignore")
        sys.exit(v)
    else:
        sys.exit(v)

base_color = '\33[0m'

bold_color = '\33[0;1m'
und_color ='\33[0;4m'
bold_und_color = '\33[0;1;4m'
if CONFIG.no_blink:
    blink_color = ''
else:
    blink_color = '\33[5m'
error_color = '\33[0;1;31m' 
warning_color = '\33[0;1;33m' 
code_color = '\33[0;1;36m'
if spyder:
    success_color = '\33[0;1;32m'
    success_low_color = '\33[0;32m'
else:
    success_color = '\33[0;1;92m'
    success_low_color = '\33[0;92m'
title_color = '\33[0;1;4;33m' 
title_next_color = '\33[0;33m' 
type_color = '\33[35m'
#true_color = '\33[0;1;32m'

# change l'indentation lors du passage en format .JSON

class MyJSONEncoder(json.JSONEncoder):

    def iterencode(self, o, _one_shot=False):
        dict_lvl = 0
        for s in super(MyJSONEncoder, self).iterencode(o, _one_shot=_one_shot):
            if s.startswith('{'):
                dict_lvl += 1
                s = s.replace('{', '{\n'+dict_lvl*"  ")
            elif s.startswith('}'):
                dict_lvl -= 1
                s = s.replace('}', '\n'+dict_lvl*"  "+'}')
            yield s

# Message d'erreur

def MESS_err_mess(mess):
    
    l = len(mess)
    print(error_color)
    print("  ^  "+l*" "+"  ^  ")
    print(" /!\\ "+mess+" /!\\ ")
    print("·---·"+l*" "+"·---·")
    print(base_color)
    os.chdir(CONFIG.script_path)
    shutdown(1)

# Message d'avertissement

def MESS_warn_mess(mess):
    
    l = len(mess)
    print(warning_color)
    print("  ^  "+l*" "+"  ^  ")
    print(" |?| "+mess+" |?| ")
    print("  v  "+l*" "+"  v  ")
    print(base_color)

# Message de succès

def MESS_succ_mess(mess):
    
    l = len(mess)
    print(success_color)
    print("\\    "+l*" "+" \\   ")
    print(" \\ / "+mess+"  \\ /")
    print("  V  "+l*" "+"   V ")
    print(base_color)

# Message pour intervention utilisateur

def MESS_input_mess(mess_list):
    
    print(code_color+blink_color)
    print("+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+")
    print(code_color)
    for mess in mess_list:
        print(mess)
    print(code_color+blink_color)
    print("+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+")
    print(base_color)

# Boîte de dialogue tkinter pour intervention utilisateur (GUI)

def MESS_input_GUI(mess_list):
    
    l_h = 40
    font_s_v = -25
    font_s_t = 30
    if len(mess_list) > 20:
        l_h = 20
        font_s_v = -13
        font_s_t = 15
    dim_width = max(1250,len(max(mess_list, key=len))*(-font_s_v//2)+100)
    dim_height = len(mess_list)*l_h+200
    
    root = tk.Tk(screenName=CONFIG.sc_name)
    root.geometry(str(dim_width)+"x"+str(dim_height))
    root.title("ACTION !")
    
    canvas = tk.Canvas(root, width = dim_width, height = dim_height)
    canvas.pack(fill = "both", expand = True)
    
    def on_submit_button_pressed():
        root.destroy()
        for v in var_list:
            GUI_VAR_LIST.append(v.get())
        print(GUI_VAR_LIST)
    
    def on_custom_button_pressed(i):
        var_list[-1].set(i)
        on_submit_button_pressed()
    
    def on_window_close():
        root.destroy() # Note to self : Surtout NE PAS enlever cette ligne ! (sinon redémarrer Spyder)
        if CONFIG.ui_popups_shutdown:
            MESS_err_mess("Fermeture : Arrêt...")
    
    root.protocol("WM_DELETE_WINDOW", on_window_close)
        
    global GUI_VAR_LIST
    GUI_VAR_LIST = []
    var_list = []
    s_b_list = []
    s_b_label_list = []
    cpt = 0
    radio_button = 0
    submit_button = 0
    
    for ic,mess in enumerate(mess_list):
        if mess == "~t~":
            v = tk.StringVar()
            var_list.append(v)
            t = tk.Entry(master = root, font=('Times', font_s_v, 'bold'), textvariable = var_list[cpt], width=50)
            canvas.create_window( 50, 50+l_h*ic, anchor = "nw", window = t)
            cpt += 1
            radio_button = 0
        elif mess == "~c~":
            v = tk.IntVar(value=0)
            var_list.append(v)
            c = tk.Checkbutton(master = root, variable = var_list[cpt])
            canvas.create_window( 50, 50+l_h*ic, anchor = "nw", window = c)
            cpt += 1
            radio_button = 0
        elif mess[:3] == "~r~":
            if radio_button == 0:
                v = tk.IntVar(value=0)
                var_list.append(v)
                cpt += 1
            if mess[-3:] == "~!~":
                mess = mess[:-4]
                var_list[cpt-1].set(radio_button)
            r = tk.Radiobutton(master = root, font=('Times', font_s_v, 'bold'), text=mess[4:], variable=var_list[cpt-1], value=radio_button, pady = 5)
            canvas.create_window( 50, 50+l_h*ic, anchor = "nw", window = r)
            radio_button += 1
        elif mess[:3] == "~b~":
            if submit_button == 0:
                v = tk.IntVar()
                var_list.append(v)
                cpt += 1
            b = tk.Button(master = root, text=mess[4:], font=('Terminal', font_s_t, 'bold'), compound="center", command=lambda i=submit_button: on_custom_button_pressed(i))
            s_b_list.append(b)
            s_b_label_list.append((len(mess[4:])+2)*25)
            submit_button += 1
        else:
            canvas.create_text( 50, 50+l_h*ic, font=('Times', font_s_v, 'bold'), text = mess, anchor = "nw", fill="black")
            radio_button = 0
    
    if submit_button > 0:
        total_l = sum(s_b_label_list)+(dim_width//20)*(submit_button-1)
        # print(s_b_label_list)
        # print(total_l)
        for ic,b in enumerate(s_b_list):
            pos = sum(s_b_label_list[:ic])+(dim_width//20)*(ic) - total_l//2
            # print(pos)
            canvas.create_window( dim_width//2 + pos,dim_height-60, anchor = "nw",window = b)
    else:
        bs = tk.Button(root, text = 'Valider', font=('Terminal', font_s_t, 'bold'), compound="center", command=on_submit_button_pressed)
        canvas.create_window( dim_width//2 - 60,dim_height-60, anchor = "nw",window = bs)
        
    root.mainloop()
    
# Retire les caractères indésirables des strings.

def TOOL_str_clean(dirty_str,l=False,path=False):
    if l == False:
        dirty_str = dirty_str.replace('[','')
        dirty_str = dirty_str.replace(']','')
    if path == False:
        dirty_str = dirty_str.replace(' ','')
    dirty_str = dirty_str.replace('"','')
    dirty_str = dirty_str.replace("'",'')
    return dirty_str

# Convertit la liste passée en paramètre d'entrée via cmd (format string) en liste de type "list_type".

def TOOL_split_list(list_string, list_type, path=False, noclean=False):
    l = []
    #print(list_string)
    if list_type in [int, float]:
        occurs = re.compile(r"[0-9.]+").findall(list_string)
        for oc in occurs:
            l.append(list_type(oc))
    if list_type in [bool]:
        occurs = list_string.split(',')
        for oc in occurs:
            l.append(TOOL_str_to_bool(oc))
    if list_type in [str]:
        if noclean:
            occurs = list_string.split(',')
        else:
            occurs = TOOL_str_clean(list_string,path=path).split(',')
        l = occurs
    print(occurs)
    if isinstance(l,list):
        return l
    return [l]

# Récolte les arguments optionels.

def TOOL_optargs_list(list_args, list_args_name, list_args_type):
    
    global GUI
    global FROM_GI_PY
    dict_args = {}
    for c_arg in list_args:
        if c_arg == "GraphicUI":      # Pour que matplotlib fonctionne avec l'interface graphique (utilisant tkinter), avec choix graphique
            plt.switch_backend('TkAgg')
            GUI = True
            FROM_GI_PY = True
            continue
        elif c_arg == "GraphicUIn't": # Pour que matplotlib fonctionne avec l'interface graphique (utilisant tkinter), avec choix sur terminal
            plt.switch_backend('TkAgg')
            GUI = False
            FROM_GI_PY = True
            continue
        elif c_arg == "GraphicUI_ignore": # Pour simuler un appel via un terminal classique avec 'interface graphique, tout en changeant le backend
            FROM_GI_PY = False
            continue
        c_arg = TOOL_str_clean(c_arg,l=True,path=True)
        occurs = re.split(r"[ ]*=[ ]*",c_arg)
        print(occurs)
        try:
            try:
                ic = list_args_name.index(occurs[0])
            except ValueError:
                MESS_err_mess("Le paramètre optionnel '{}' n'existe pas ({})".format(occurs[0],list_args_name))
            if isinstance(list_args_type[ic],list):
                if occurs[0] in ["file_list","file_list_rev","output_file_list"]:
                    path = True
                else:
                    path = False
                dict_args[list_args_name[ic]] = TOOL_split_list(occurs[1], list_args_type[ic][0], path=path)
            elif list_args_type[ic] == bool:
                dict_args[list_args_name[ic]] = TOOL_str_to_bool(occurs[1])
            elif occurs[0] in ["output_file","output_file_base"]:
                dict_args[list_args_name[ic]] = TOOL_str_clean(occurs[1],path=True)
            else:
                dict_args[list_args_name[ic]] = list_args_type[ic](occurs[1])
        except ValueError or TypeError:
            MESS_err_mess("Le paramètre optionnel '{}' n'est pas du type {} : '{}'".format(occurs[0],list_args_type[ic],occurs[1]))
    print(dict_args)
    return dict_args

# Convertis un string en bool (de manière acceptable).

def TOOL_str_to_bool(bool_str):
    if TOOL_str_clean(bool_str).lower() in ["true","t","1"]:
        return True
    elif TOOL_str_clean(bool_str).lower() not in ["false","f","0"]:
        MESS_warn_mess('La valeur "{}"'.format(bool_str)+" n'est pas reconnue, considérée comme False.")
    return False

# Gère le cas où les fichier ne sont pas spécifiés

def TOOL_true_file_list(file_list):
    ls_nomfich = []
    if file_list == None:
        ls_nomfich = glob.glob("*.dat")
    else:
        for f in file_list:
            ls_nomfich.append(f.replace('"',''))
            
    return ls_nomfich

# Renvoie les colonnes x,y,z ainsi que le nombre de données, le nombre de voies et le nombre de données par voie.
# Si il y a une incohérence, termine l'exécution.

def TOOL_manage_cols(don,col_x,col_y,col_z):
    if len(col_x) != len(col_y):
        MESS_err_mess("La taille de col_x ({}) et de col_y ({}) ne sont pas égales".format(len(col_x),len(col_y)))
    if len(col_z)%len(col_x) != 0:
        MESS_err_mess("La taille de col_x ({}) et de col_z ({}) ne sont pas multiples. Veuillez mettre autant de données par voie".format(len(col_x),len(col_z)))
    ncx = don.columns[col_x]
    ncy = don.columns[col_y]
    col_T = don.columns[col_z]
    nb_data = len(col_z)
    nb_ecarts = len(col_x)
    nb_res = nb_data//nb_ecarts
    return ncx, ncy, col_T, nb_data, nb_ecarts, nb_res

# idéalement, il faudrait faire le lien avec les programmes fortran fonctionnels
# fournir la hauteur en plus de la marque et de la géométrie pour avoir quelque
# chose qui calcule pour chaque configuration

def TOOL_check_time_date(f,sep):
    try:
        data = pd.read_csv(f,sep=sep)
        cols_to_drop = []
        if len(data.columns) == 1:
            MESS_err_mess('Le fichier "{}" ne possède pas le séparateur {}'.format(f,repr(sep)))
        try:
            if ":" not in str(data.at[0,"Time"]):
                MESS_warn_mess('Le fichier "{}" semble posséder une colonne "Time" surnuméraire. Elle sera supprimée le temps du traitement.'.format(f))
                data = DAT_pop_and_dec([f],"Time",sep,False,"",not_in_file=True)
            else:
                cols_to_drop.append("Time")
        except KeyError:
            pass
        try:
            if "/" not in str(data.at[0,"Date"]):
                MESS_warn_mess('Le fichier "{}" semble posséder une colonne "Date" surnuméraire. Dans ce cas, veuillez la retirer (DAT_pop_and_dec).'.format(f))
                data = DAT_pop_and_dec([f],"Date",sep,False,"",not_in_file=True)
            else:
                cols_to_drop.append("Date")
        except KeyError:
            pass
        num_cols = data.columns.drop(cols_to_drop)
        data[num_cols] = data[num_cols].apply(pd.to_numeric, errors='coerce')
    except FileNotFoundError:
        MESS_err_mess('Le fichier "{}" est introuvable'.format(f))
    return data

def coeff_em (dev_type,geom):

# à compléter au fur et à mesure des prospections   
# certains coeff sont à déterminer pour la hauteur de l'appareil au dessus 
# du sol
       
    if dev_type == 'mini3L' :
        TxRx=np.array((0.32,0.71,1.18))
        if geom =='HCP':
            cond2ppt=[0.00591,0.0281,0.0745]
            # coeff pour z = 0.1m
            ppmcubcond=[[0,0,0,0],[0,0,0,0],[0,0,0,0]] 
            # coeff pour z = 0.1m
            cond2ph=[0,0,0]                  
            
            ppt2ppm=[0,0,0]
            
            # coeff pour z = 0.1m
            ppm2Kph=[1e5/47901.3,1e5/347132.,1e5/438506.5]
            
        elif geom=='VCP':
            
            cond2ppt=[0.00599,0.0290,0.0785]
            # coeff pour z = 0.1m
            # conductivité en mS/m
            ppmcubcond=[[-0.10823162947354771,-0.3036479462368002,\
                         1.3280407699069232e-05,1.4301188769635517e-09]\
                        ,[-0.16618468053064167,-0.04568571367186757,\
                          5.269589591565735e-07,7.945036636189313e-12]\
                            ,[-0.22948815755106722,-0.01503288617663641,\
                              9.323438581357515e-08,3.9144243673162584e-13]]
            # coeff pour z = 0.1m
            # conductivité en mS/m
            cond2ph=[[152.79635664008586,-0.07179399570215782,\
                     -0.00035775374713942405,1.49233410401824e-07]\
                     ,[227.06313608372378,-0.7839238365448543,\
                       -0.0037275593646650985,1.615740921987211e-06]\
                         ,[258.58913601586704,-3.5919310913030476,\
                           -0.015907663333728717,7.286970307716231e-06]]                   
            ppt2ppm=[2029,1635,1400]
            #Kph en 10-5 SI
            ppm2Kph=[1e5/304122.,1e5/444741.,1e5/477922.] # coeff pour z = 0.1m
        
        elif geom=='VVCP':
            cond2ppt=[0.00591,0.0281,0.0745]
            # coeff pour z = 0.1m
            # conductivité en mS/m
            ppmcubcond=[[0.0004719308537468325,-0.4874306864824366,\
                         1.9074048803099637e-07,-2.1314964231501785e-09]\
                        ,[0.03267362262849646,-0.08556294143116905,\
                          5.063447644648263e-07,-7.47153443562091e-11]\
                            ,[0.1501480161228954,-0.028755139621820858,\
                              4.03433833892729e-07,-2.2009286432319347e-12]]
            # coeff pour z = 0.1m
            # conductivité en mS/m
            cond2ph=[[110.56613766894806,0.000530772436500501,\
                     -0.0001778160767675579,1.7425300215793262e-08]\
                     ,[168.3894842089161,-0.0013521293081108592,\
                       -0.0037785932069280244,1.6563467407734165e-06]\
                         ,[201.87285956816925,-1.0503859348708084,\
                           -0.01653453277718441,9.750741471050308e-06]] 
            ppt2ppm=[2029,1635,1400]
            #Kph en 10-5 SI
            ppm2Kph=[1e5/220638.,1e5/335967.,1e5/390824.]
            
    if dev_type=='mini6L' :
        TxRx=np.array((0.2,0.33,0.5,0.72,1.03,1.5))
        if geom =='HCP':
            cond2ppt=[0.00194,0.00524,0.0119,0.0242,0.0484,0.0986]
            ppmcubcond=[[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
            cond2ph=[0,0,0,0,0,0]
            ppt2ppm=[0,0,0,0,0,0]
            ppm2Kph=[0,0,0,0,0,0]
        elif geom=='VCP':
            cond2ppt=[0.00194,0.00525,0.012,0.0246,0.0498,0.1037]
            ppmcubcond=[[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
            cond2ph=[0,0,0,0,0,0]
            ppt2ppm=[0,0,0,0,0,0]
            ppm2Kph=[0,0,0,0,0,0]
        elif geom=='VVCP':
            cond2ppt=[0.00194,0.00525,0.012,0.0246,0.0498,0.1037]
            ppmcubcond=[[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
            cond2ph=[0,0,0,0,0,0]
            ppt2ppm=[0,0,0,0,0,0]
            ppm2Kph=[0,0,0,0,0,0]
    if dev_type=='expl3L' :
        TxRx=np.array((1.5,2.4,4.6))
        if geom =='HCP':
            cond2ppt=[0.0402,0.1366,0.3144]
            ppmcubcond=[[0,0,0,0],[0,0,0,0],[0,0,0,0]]
            cond2ph=[0,0,0]
            ppt2ppm=[0,0,0]
            ppm2Kph=[0,0,0]
        elif geom=='VCP':
            cond2ppt=[0.0417,0.1463,0.3558]
            ppmcubcond=[[0,0,0,0],[0,0,0,0],[0,0,0,0]]
            cond2ph=[0,0,0]
            ppt2ppm=[0,0,0]
            ppm2Kph=[0,0,0]
    
    return (TxRx,cond2ppt,ppmcubcond,cond2ph,ppt2ppm,ppm2Kph)

def CMD_init(app_data,file_list,sep,sup_na,regr,corr_base,not_in_file=False):
    
    # concaténation si nécessaire avant traitement
    ls_pd=[]
    ls_pd_done_before = []
    nb_file = len(file_list)
    for ic,f in enumerate(file_list) :
        data = TOOL_check_time_date(f,sep)
        
        data['Num fich']=ic+1
        #print(data.columns)
        try:
            data["X_int"]
            ls_pd_done_before.append(data)
        except KeyError:
            ls_pd.append(data)
        
    if app_data["GPS"] :
        nb_res = 2
        const_GPS = 7
        n_col_X='Northing'
        n_col_Y='Easting'
    else :
        nb_res = 2
        const_GPS = 2
        n_col_X='x[m]'
        n_col_Y='y[m]'
    
    ls_base = []
    ls_mes = []
    col_z=[const_GPS+i for i in range(app_data["nb_ecarts"]*nb_res)]
    ncx = ["X_int_"+str(e+1) for e in range(app_data["nb_ecarts"])]
    ncy = ["Y_int_"+str(e+1) for e in range(app_data["nb_ecarts"])]
    
    for ic,don_c in enumerate(ls_pd) :
        print("Fichier de données n°{} : '{}'".format(ic+1,file_list[ic]))
      
    if len(ls_pd) != 0:
        don_raw = pd.concat(ls_pd)
        don_raw.index=np.arange(don_raw.shape[0])

        # Si le fichier contient des données temporelles
        try:
            don_raw['temps (s)']=CMD_time(don_raw)
            # On gère les prospections faites des jours différents
            for ic,date_c in enumerate(don_raw['Date'].unique()) :
                if ic>0 :
                    ind_d =don_raw.index[don_raw['Date']==date_c]
                    don_raw.loc[ind_d,'temps (s)']=don_raw.loc[ind_d,'temps (s)']+ic*86400
                don_d=CMD_detect_chgt(don_raw)
                #MESS_warn_mess("uno")
                don_i=CMD_intrp_prof(don_d)
                #MESS_warn_mess("dos")
                don_i=CMD_detect_base_pos(don_i,2)
                #MESS_warn_mess("tres")
        except KeyError:
            don_raw["X_int"] = don_raw.iloc[:,0]
            don_raw["Y_int"] = don_raw.iloc[:,1]
            
            don_i = CMD_detec_profil_carre(don_raw)
    
        if sup_na:
            don_i.dropna(subset = [n_col_X,n_col_Y],inplace=True)
            don_i.reset_index(drop=True,inplace=True)
        else:
            MESS_warn_mess("Les données NaN seront redressées")
            don_i = CMD_XY_Nan_completion(don_i)
        don_base,don_mes=CMD_sep_BM(don_i)
        #MESS_warn_mess("quatro")
        
        # print(don_i)
        # print(don_mes)
        nc_data = don_raw.columns[col_z]
        print(col_z)
        print(nc_data)
        for i in range(nb_file):
            i_fich_mes = don_mes[don_mes["Num fich"] == i+1]
            i_fich_base = don_base[don_base["Num fich"] == i+1]
            
            if regr:
                fig,ax=plt.subplots(nrows=1,ncols=1,figsize=(CONFIG.fig_height,CONFIG.fig_height))
                ax.plot(i_fich_mes["X_int"],i_fich_mes["Y_int"],'+r')
                ax.plot(i_fich_mes[i_fich_mes["Profil"] == i_fich_mes.iloc[0]["Profil"]]["X_int"],i_fich_mes["Y_int"][i_fich_mes["Profil"] == i_fich_mes.iloc[0]["Profil"]],'+b')
                ax.set_xlabel(n_col_X)
                ax.set_ylabel(n_col_Y)
                ax.set_aspect('equal')
                ax.set_title(file_list[i])
                plt.show(block=False)
                plt.pause(0.25)
                
                correct = False
                while correct == False:
                    if GUI:
                        MESS_input_GUI(["fichier {} : redressement ?".format(file_list[i]),"","~r~ Oui (tous les profils)","~r~ Non ~!~","","Oui, à partir du profil k, ou jusqu'au profil -k (-1 est le dernier profil)","Ignore le choix précédent si non vide","~t~","","Le premier profil est indiqué en bleu"])
                        try:
                            fin, inp = GUI_VAR_LIST
                            if inp == "":
                                inp = ["y","n"][fin]
                        except:
                            MESS_warn_mess("Veuillez sélectionner un réponse")
                            continue
                    else:
                        MESS_input_mess(["fichier {} : redressement ?".format(file_list[i]),"","y : Oui (tous les profils)","k >= 0 : Oui, à partir du profil k","k < 0 : Oui, jusqu'au profil -k (-1 est le dernier profil)","n : Non","","Le premier profil est indiqué en bleu"])
                        inp = input()
                    try:
                        if inp == "n":
                            pass
                        elif inp == "y":
                            i_fich_mes = CMD_pts_rectif(i_fich_mes)
                        elif int(inp) >= 0:
                            i_fich_mes = CMD_pts_rectif(i_fich_mes,ind_deb=int(inp))
                        else:
                            i_fich_mes = CMD_pts_rectif(i_fich_mes,ind_fin=int(inp))
                        correct = True
                    except ValueError:
                        MESS_warn_mess("Réponse non reconnue !")
                    except IndexError:
                        MESS_warn_mess("Le profil {} n'existe pas !".format(inp))
                plt.close(fig)
                
            if corr_base:
                try:
                    i_fich_mes = CMD_evol_profils(i_fich_mes,i_fich_base,file_list[i],col_z,app_data["nb_ecarts"],verif=False)
                except IndexError:
                    MESS_warn_mess("Base externe au fichier {}, pas d'ajustement".format(file_list[i]))
            i_fich_mes = CMD_dec_voies(i_fich_mes,ncx,ncy,app_data["nb_ecarts"],app_data["TxRx"],app_data["GPS_dec"])
            if not i_fich_base.empty:
                i_fich_base = CMD_dec_voies(i_fich_base,ncx,ncy,app_data["nb_ecarts"],app_data["TxRx"],app_data["GPS_dec"])
            ls_mes.append(i_fich_mes)
            ls_base.append(i_fich_base)
            
            if not not_in_file:
                i_fich_mes.to_csv(file_list[i]+"_init_P.dat", index=False, sep=sep) 
                if not i_fich_base.empty:
                    i_fich_base.to_csv(file_list[i]+"_init_B.dat", index=False, sep=sep)
    else:
        nc_data = ls_pd_done_before[0].columns[col_z]
    if not_in_file:
        return don_base, don_mes, ls_base, ls_mes, ncx, ncy, nc_data, nb_res, ls_pd_done_before
    else:
        final_df = pd.concat(ls_mes)
        for e in range(app_data["nb_ecarts"]):
            fig,ax=plt.subplots(nrows=1,ncols=nb_res,figsize=(CONFIG.fig_width,CONFIG.fig_height))
            X = final_df[ncx[e]]
            Y = final_df[ncy[e]]
            for r in range(nb_res):
                Z = final_df[nc_data[e]]
                Q5,Q95 = Z.quantile([0.05,0.95])
                col = ax[r].scatter(X,Y,marker='s',c=Z,cmap='cividis',s=6,vmin=Q5,vmax=Q95)
                plt.colorbar(col,ax=ax[r],shrink=0.7)
                ax[r].title.set_text(nc_data[e*nb_res+r])
                ax[r].set_xlabel(ncx[e])
                ax[r].set_ylabel(ncy[e])
                ax[r].set_aspect('equal')
            plt.show(block=False)
            plt.pause(0.25)
            plt.savefig(CONFIG.script_path+"Output/CMDEX_i_" +str(e)+'.png')
            pickle.dump(fig, open(CONFIG.script_path+"Output/CMDEX_i_" +str(e)+'.pickle', 'wb'))

# fonction de conversion du temps sous forme de chaine de caractère en seconde
# en entrée, ce peut être le Dataframe complet issu du fichier CMD ou simplement
# la colonne 'Time'
# le format doit être une chaîne de caractère séparée par sep, par défaut ce
# son des ":"
 
def CMD_time(donnees,dep_0=False,sep=':'):
    ls_tps_sec=list()
    premier=0.
    if type(donnees)==type(pd.DataFrame()):
        
        for temps in donnees['Time'] :
            if type(temps)!=type('str') :
                ls_tps_sec.append(np.nan)
            else:
                Ht,Mt,St=temps.split(sep)
                h_sec=int(Ht)*3600+int(Mt)*60+float(St)
                if (dep_0 and premier==0.) :
                    premier=h_sec
                                
                ls_tps_sec.append(round(h_sec-premier,3))
            pass
        pass
    else :
        for temps in donnees:
            if type(temps)!=type('str') :
                ls_tps_sec.append(np.nan)
            else:
                Ht,Mt,St=temps.split(':')
                h_sec=int(Ht)*3600+int(Mt)*60+float(St)
                if (dep_0 and premier==0.) :
                    premier=h_sec
                                
                ls_tps_sec.append(round(h_sec-premier,3))
            pass
        pass
    pass
    return(ls_tps_sec)

# interpolation brutale qui ne marche pas bien
def CMD_interp(donnees,acq_GPS=True):
    if acq_GPS :
        colXY=['Northing','Easting']
    else:
        colXY=['x[m]','y[m]']
        
    X,Y=donnees[colXY[0]],donnees[colXY[1]]
    DX,DY=X.diff(),Y.diff()
    DX[0:-1],DY[0:-1]=DX[1:],DY[1:]
    DR=np.sqrt(DX*DX+DY*DY)
    
    donnees['X_int']=0
    donnees['Y_int']=0
    
           
    ind_a_garder=(donnees.index[DR!=0]+1)[:-1]
    ind_a_garder=ind_a_garder.insert(0,0)
    nb_pts=ind_a_garder.diff()-1
   
    ls_intrpX,ls_intrpY=[],[]
    for ic,ind_f in enumerate(ind_a_garder[1:]):
        Xdeb,Ydeb=X[ind_a_garder[ic]],Y[ind_a_garder[ic]]
        Xfin,Yfin=X[ind_f],Y[ind_f]
        nb_pt=nb_pts[ic+1]
   #    print("début : ({},{}) - fin : ({},{}),\n\
   # Nombre de points à interpoler : {}".format(Xdeb,Ydeb,Xfin,Yfin,nb_pt))
        if ic==len(ind_a_garder)-2 :
           ls_intrpX.append(np.linspace(Xdeb,Xfin,int(nb_pt)+2))
           ls_intrpY.append(np.linspace(Ydeb,Yfin,int(nb_pt)+2))
   
        else:
           ls_intrpX.append(np.linspace(Xdeb,Xfin,int(nb_pt)+2)[:-1])
           ls_intrpY.append(np.linspace(Ydeb,Yfin,int(nb_pt)+2)[:-1])
          
        try :
            donnees['X_int']=pd.Series(np.concatenate(ls_intrpX))
            donnees['Y_int']=pd.Series(np.concatenate(ls_intrpY))
            return(donnees.copy())
        except:
            X_int1=pd.Series(np.concatenate(ls_intrpX))
            Y_int1=pd.Series(np.concatenate(ls_intrpY))
            MESS_warn_mess("[DEV] Attention, l'interpolation n'a pas la même taille que les données d'entrée")
    return(X_int1,Y_int1)

#détection de base par comparaison avec les coordonnées de la base de début
#(deb=True) ou de fin (deb=False)
# ne s'applique qu'aux cartes non concaténées

def CMD_detect_baseb(donnees,acq_GPS=True,Rd=2.,deb=True):
    
    if acq_GPS :
        colXY=['Northing','Easting']
    else :
        colXY=['x[m]','y[m]']
    X,Y=donnees[colXY[0]],donnees[colXY[1]]
    DX,DY=X.diff(),Y.diff()
    DX[0:-1],DY[0:-1]=DX[1:],DY[1:]
    DR=np.sqrt(DX*DX+DY*DY)
    indbp=DR.index[DR>Rd]
    indbp=indbp.insert(0,0)
    indbp=indbp.insert(len(indbp),donnees.index[-1])
    
    if deb:
        Xmed,Ymed=donnees.loc[indbp[0]:indbp[1],colXY].median()
    else :
        Xmed,Ymed=donnees.loc[indbp[-2]:indbp[-1],colXY].median()
        
    DRb=np.sqrt((X-Xmed)*(X-Xmed)+(Y-Ymed)*(Y-Ymed))
    ind_base=DRb.index[DRb<0.5]
    
    donnees['Base']=0
    ind0=ind_base[0]
    ibase=1
    for ind in ind_base :
        if ind-ind0>1 :
            ibase+=1
        donnees.loc[ind,'Base']=ibase
        ind0=ind
    mod_i=0
    for d in donnees['Base'].unique() :
        ind_cour=donnees.index[donnees['Base']==d]
        if len(ind_cour)<4 :
            donnees.loc[ind_cour,'Base']=0
            mod_i+=1
        else:
            donnees.loc[ind_cour,'Base']-=mod_i
 
    return(donnees.copy())

# le seuil est à changer en fonction de la prospection
# on considère que les premières mesures et/ou le sdernières sont effectuées à
# la base

def CMD_detect_basec(donnees,acq_GPS=True,seuil=1.,deb=True):
    if acq_GPS :
        colXY=['Northing','Easting']
    else :
        colXY=['x[m]','y[m]']
        
    X,Y=donnees[colXY[0]],donnees[colXY[1]]
    if not('b et p' in donnees.columns) :
        donnees=CMD_detect_chgt(donnees)
        MESS_warn_mess("[DEV] Attention, création par défaut d'une colonne 'b et p'")
    
    baseD,baseF=donnees['b et p'].iloc[[0,-1]]
    if deb :
        ind_b=donnees.index[donnees['b et p']==baseD]
    else :            
        ind_b= donnees.index[donnees['b et p']==baseF]
    
    Xmed,Ymed=donnees.loc[ind_b,colXY].median()
    
    DRb=np.sqrt((X-Xmed)*(X-Xmed)+(Y-Ymed)*(Y-Ymed))
    ind_base=DRb.index[DRb<seuil]
    
    donnees['Base']=0
    ind0=ind_base[0]
    ibase=1
    for ind in ind_base :
        if ind-ind0>1 :
            ibase+=1
        donnees.loc[ind,'Base']=ibase
        ind0=ind
    
    
    mod_i=0
    for d in donnees['Base'].unique() :
        ind_cour=donnees.index[donnees['Base']==d]
        if len(ind_cour)<4 :
            donnees.loc[ind_cour,'Base']=0
            mod_i+=1
        else:
            donnees.loc[ind_cour,'Base']-=mod_i
    
    ind_base=donnees.index[donnees['Base']!=0]
    for d in donnees['Base'].unique() :
        if d!=0 :
            ind_cour=donnees.index[donnees['Base']==d]
            dt=donnees.loc[ind_cour,'temps (s)'].diff()
            ind_split=dt.index[np.abs(dt)>1.] 
            if len(ind_split)==1 :
                ind_courb=ind_base[ind_base>ind_split.array[0]-1]                
                donnees.loc[ind_courb,'Base']+=1
    
 
    return(donnees.copy())
    
def CMD_detect_base(donnees,acq_GPS=True,nbbase=[2,]):
    if acq_GPS :
        colXY=['Northing','Easting']
    else :
        colXY=['X[m]','Y[m]']
    if type(nbbase)!=type([]): nbbase=[nbbase,]
    
    # en théorie, les bases ont un écart spatial très grand avec les points
    # de prospection. On peut même dire qu'il se trouve dans le tantième
    # équivalent à 1 moins le rapport entre le double du nombre de base et 
    # le nombre de points enregistrés 
    # 
    Q=0
    for nbb in nbbase :
        Q+=(nbb-1)*2
    Q=1-Q/donnees.shape[0]
    
    X,Y=donnees[colXY[0]],donnees[colXY[1]]
    DX,DY=X.diff(),Y.diff()
    DX[0:-1],DY[0:-1]=DX[1:],DY[1:]
    DR=np.sqrt(DX*DX+DY*DY)
    
    ind_base=donnees.index[DR>DR.quantile(Q)]
    
    # on commence par une base donc le premier indice est le début de
    # la première base on l'ajoute
    ind_base=ind_base.insert(0,0)
    # on fini par une base donc le dernier indice est la fin de la dernière
    # base on l'ajoute à la fin
    ind_base=ind_base.insert(len(ind_base),donnees.index[-1])
    # si le nombre de base est une liste alors il y a plusieurs prospection
    # dans les données (concaténation en amont) il faut donc séparer les bases
    # de fin et de début de chacune des prospections. On utilise le temps
    if len(nbbase) !=1 :
        i_d=0
        for nbb in nbbase[:-1]:
            aux=i_d+(nbb-1)*2
            ind_deb=ind_base[aux]
            ind_fin=ind_base[aux+1]
            T=donnees['temps (s)'].loc[ind_deb:ind_fin]
            DT=T.diff()
            ind_d=DT.index[np.abs(DT)>60]
            ind_f=ind_d-1
            ind_base=ind_base.insert(aux+1,ind_f)
            ind_base=ind_base.insert(aux+2,ind_d)
     
    
    donnees['Base']=0
    for ic,ind_c in enumerate(zip(ind_base[::2],ind_base[1::2])):
        donnees.loc[ind_c[0]:ind_c[1],'Base']=ic+1
 
    
    return(donnees.copy())

def CMD_detect_base_pos(don_c, seuil,trace=False):
    
    don_int=don_c.copy()
    if 'X_int' in don_int.columns:
        ls_coord=['X_int','Y_int']
    else :
        ls_coord=['Northing','Easting']
        MESS_warn_mess("[DEV] Attention, la détection est plus fiable avec les données interpolées")
    if  'b et p' in don_int.columns:
        nom_col='b et p'
    else : 
        MESS_err_mess("[DEV] Veuillez faire la détection de changements et ou profils avant d'exécuter ce sous programme")
    
    don_aux=don_int.groupby(nom_col)[ls_coord].mean().round(CONFIG.prec_data)

    if trace : 
        fig, ax=plt.subplots(nrows=1,ncols=1,figsize=(CONFIG.fig_width,CONFIG.fig_height))
    
    ls_X=[]
    ls_Y=[]
    for ind_c in don_aux.index :
        X,Y=don_aux.loc[ind_c]
        if trace : 
            ax.text(X,Y,ind_c)
        ls_X.append(X)
        ls_Y.append(Y)

    if trace :
        ax.scatter(ls_X,ls_Y,marker='+',c='k')
        ax.set_aspect('equal')
    
    
    xb,yb=ls_X[0],ls_Y[0]
    ls_base,ls_prof=[1,],[]
    for ic,xyc in enumerate(zip(ls_X[1:],ls_Y[1:])):
        r=np.sqrt((xyc[0]-xb)**2+(xyc[1]-yb)**2)
        if r<=seuil :
            ls_base.append(ic+2)
        else:
            ls_prof.append(ic+2)
    
    don_int['Base']=0
    for ic,ib in enumerate(ls_base):
        ind_c=don_int.index[don_int[nom_col]==ib]
        don_int.loc[ind_c,'Base']=ic+1
    don_int['Profil']=0        
    for ic,ip in enumerate(ls_prof):
        ind_c=don_int.index[don_int[nom_col]==ip]
        don_int.loc[ind_c,'Profil']=ic+1
        
      
    return(don_int.copy())

# détection de changement basée sur le temps (un changement de profil ou un 
# déplacement à la base est plus long que l'écart entre deux mesures)
# fonctionnelle

def CMD_detect_chgt(donnees,acq_GPS=True,verif=False):
    if acq_GPS :
        colXY=['Northing','Easting']
    else:
        colXY=['x[m]','y[m]']
    
    X,Y=donnees[colXY[0]],donnees[colXY[1]]
   
    if 'temps (s)' in donnees.columns :
        pass
    else :
        donnees['temps (s)']=CMD_time(donnees)
        
        
    T=donnees['temps (s)'].copy()
    
    for indc in T.index[T.isna()]:
        T.loc[indc]=T.loc[indc-1]
        
    DT=T.diff()
    # la différence de temps donne les débuts de profils ou de base
    ind_chgtd=DT.index[DT>5*DT.median()]
    
    # la fin est l'indice avant le début donc - 1 par rapport au précédent 
    ind_chgtf=ind_chgtd-1
    
    ind_chgtd=ind_chgtd.insert(0,0)
    ind_chgtf=ind_chgtf.append(DT.index[[-1,]])
           
    donnees['b et p']=0
    for ic,(ind_d,ind_f) in enumerate(zip(ind_chgtd,ind_chgtf)):
        donnees.loc[ind_d:ind_f,'b et p']=ic+1
        
    if verif==True:    
        fig,ax=plt.subplots(nrows=1,ncols=1,figsize=(7,7))
        ax.scatter(X.loc[ind_chgtd],Y.loc[ind_chgtd],marker='s',color='green')
        ax.scatter(X.loc[ind_chgtf],Y.loc[ind_chgtf],marker='s',color='red')
        
        ax.scatter(X,Y,marker='+',c=donnees['b et p'],cmap='cividis')
        ax.set_aspect('equal')
    
    return(donnees.copy())
    
def CMD_num_prof(donnees, acq_GPS=True):
    if not('Base' in donnees.columns) :
        donnees=CMD_detect_basec(donnees)
        MESS_warn_mess("[DEV] Attention, création automatique d'une colonne 'base'")
        
    ind_mes=donnees.index[donnees['Base']==0]
    donnees['Profil']=0
    num_Pent=donnees.loc[ind_mes,'b et p'].unique()
    for ic,val in enumerate(num_Pent) :
        ind_c=donnees.index[donnees['b et p']==val]
        donnees.loc[ind_c,'Profil']=ic+1
    return(donnees.copy())
    
# semble fonctionner le 14/11/2024
  
def CMD_synthBase(donnees,col_calc,CMDmini=True):
    if not('Base' in donnees.columns) :
        MESS_err_mess("[DEV] Veuillez créer une colonne des numéro de base avec CMD_detect_base")
    if not('temps (s)' in donnees.columns) :
        donnees['temps (s)']=CMD_time(donnees)
    num_base=donnees['Base'].unique()
    num_base=num_base[num_base>0]    
    ls_tps,ls_val=[],[]
    for n_base in num_base :
        ind_c=donnees.index[donnees['Base']==n_base]
        tps_c=donnees.loc[ind_c,'temps (s)'].median()
        Q5=donnees.loc[ind_c,col_calc].quantile(0.05)
        Q95=donnees.loc[ind_c,col_calc].quantile(0.95)
        valb_c=(Q95+Q5)/2.
        ls_tps.append(tps_c),ls_val.append(valb_c)
     
        
    pd_valmd=pd.concat(ls_val,axis=1)
    ls_sup,ls_inf=[],[]
    
    
          
    for n_base in num_base :
        ind_c=donnees.index[donnees['Base']==n_base]
        seuil=pd_valmd[n_base-1]
        bas='ND'
        ls_s,ls_i=[],[]
        for ic,sc in enumerate(seuil) :
            dat_c=donnees.loc[ind_c,col_calc[ic]].copy()
            prem=dat_c.index[0]
            ind1=dat_c.index[dat_c>sc]
            ind2=dat_c.index[dat_c<sc]
            ls_s.append(dat_c.loc[ind1].median())     
            ls_i.append(dat_c.loc[ind2].median())
        
        ls_sup.append(pd.Series(ls_s))
        ls_inf.append(pd.Series(ls_i))
    
    pd_sup=pd.concat(ls_sup,axis=1)
    pd_inf=pd.concat(ls_inf,axis=1)
    pd_sup.index=seuil.index
    pd_inf.index=seuil.index        
    pd_tps=pd.Series(ls_tps)
    
    if CMDmini :
        return(pd_tps,pd_sup,pd_inf)
    else :
        return(pd_tps,pd_valmd,None)
    
                
def CMD_sep_BM(donnees)   :
    if not('Profil' in donnees.columns) :
        MESS_err_mess("[DEV] Veuillez créer une colonne des numéro de profil avec CMD_num_prof")
    else :
        ind_p=donnees.index[donnees['Profil']!=0]
        ind_b=donnees.index[donnees['Base']!=0]
        return(donnees.loc[ind_b],donnees.loc[ind_p])

# Dans le cas d'une prospection sur un carré, on peut identifier les profils par la première coordonnée

def CMD_detec_profil_carre(don):
    don["Profil"] = 0
    don["Base"] = 0
    don["b et p"] = 0
    don["temps (s)"] = -1
    colname = don.columns[0]
    x = don[colname].iloc[0]
    prof_nb = 1
    for index, row in don.iterrows():
        x_l = don[colname].iloc[index]
        if x != x_l and x_l == x_l:
            x = x_l
            prof_nb += 1
        don.loc[index, "Profil"] = prof_nb
        don.loc[index, "b et p"] = prof_nb
    
    return don.copy()

#interpolation fine et intelligente se basant sur les profils détectés
# fonctionne le 01/01/2025
# doit être testé avec des données sans GPS et sur plusieurs cas

def CMD_intrp_prof(don_mes,acq_GPS=True):
    if acq_GPS :
        colXY=['Northing','Easting']
    else:
        colXY=['x[m]','y[m]']
        
    don_mes['X_int']=0.
    don_mes['Y_int']=0.
    if  'b et p' in don_mes.columns:
        num_profs=don_mes['b et p'].unique()
        nom_col='b et p'
    elif 'Profil' in don_mes.columns :
        num_profs=don_mes['Profil'].unique()
        nom_col='Profil'
    else : 
        MESS_err_mess("[DEV] Veuillez faire la détection de changements et/ou profils avant d'exécuter ce sous programme")
    
# on parcours chaque profil
    for num_p in num_profs :
        ind_prof=don_mes.index[don_mes[nom_col]==num_p]
        prof_c=don_mes.loc[ind_prof,colXY]
        prof_c.columns=['X','Y']
  
        dxdy=prof_c.diff()
        dxdy['dr']=np.sqrt((dxdy**2).sum(axis=1))
        dxdy.loc[:,'dr']=np.round(dxdy.loc[:,'dr'],CONFIG.prec_data)
        # pour récupérer le premier index sous forme d'index (et pas d'entier)
        # il faut indiquer .index[0:1]CMD_intrp
        ind_ancre=dxdy.index[0:1].append(dxdy.index[dxdy['dr']!=0])
        if ind_ancre[-1]!=dxdy.index[-1] :
            ind_ancre=ind_ancre.append(dxdy.index[-1:])
        ind_ancd=ind_ancre[0:-1]
        ind_ancf=ind_ancre[1:]
        nbpts=(ind_ancf-ind_ancd).array
        ls_dX,ls_dY=[],[]
    # On crée les listes de décalage à appliquer à chaque points en X et Y
    # la fin du profil est gérée en prenant les décalages précédents et en faisant
    #    
        for ic,nbp in enumerate(nbpts):
           dernier=len(nbpts)
           fin=dxdy.loc[ind_ancf[ic:ic+1],['X','Y']].to_numpy().flatten()
           
           if np.array_equal(fin,np.array([0.,0.])):
               fin=dxdy.loc[ind_ancf[ic-1:ic],['X','Y']].to_numpy().flatten()
               int_c=np.linspace([0,0],fin,nbp+1)
               # if nbpts[ic-1]>nbp :
               #     int_c=np.linspace([0,0],fin,nbpts[ic-1]+1)[:nbp+1,:]
               # else:
               #     #int_c=np.linspace([0,0],fin,nbpts[ic-1]+1)
               #     int_c=np.linspace([0,0],fin,nbp+1)
               #     #int_c2=int_c+int_c[-1,:]+int_c[1,:]
               #     #int_c=np.concatenate([int_c,int_c2])[:nbp+1,:]
           else:
               int_c=np.linspace([0,0],fin,nbp+1)
               int_c[-1,:]=np.array([0.,0.])
                  
           if ic>0 :
               if ic<dernier-1 :
                   ls_dX+=int_c[:-1,0].tolist()
                   ls_dY+=int_c[:-1,1].tolist()
               else :
                   ls_dX+=int_c[:,0].tolist()
                   ls_dY+=int_c[:,1].tolist()
           else :
               ls_dX=int_c[:-1,0].tolist()
               ls_dY=int_c[:-1,1].tolist()
        prof_i=(prof_c+np.array([ls_dX,ls_dY]).T).to_numpy()
        don_mes.loc[ind_prof,['X_int','Y_int']] = prof_i
    return(don_mes)

# fonction de complémentaiton des données topo si présence de Nan après
# interpolation
# en cours le 27/01/2025
def CMD_XY_Nan_completion_old(X,Y):
    indXNan=X.index[X.isna()]
    indYNan=Y.index[Y.isna()]
    if len(indXNan)<1:
        print('aucune valeur à interpoler')
        return(X,Y)
    if np.all(indXNan==indYNan):
        indc=indXNan.copy()
    else:
        MESS_warn_mess("[DEV] NaN en X et NaN en Y n'ont pas les même position dans le tableau (pas d'effet)")
        return(X,Y)
#   on repère tous les points qui ont des coordonnées Nan puis on prend
#  ceux qui ont un écart d'indice supérieur à 1 (ils ne sont pas consécutifs
# dans le fichier)
# ind_aux correspond au dernier point mesuré avant la perte du signal GPS
#ind_aux2 correspond au premier point pour lequel le signal GPS est revenu 
    
    ind_aux=indc[indc.diff()!=1.]-1
    t2=np.arange(0,len(indc))
    ind_aux2=indc[t2[indc.diff()!=1.][1:]-1]+1
    ind_aux2=ind_aux2.append(indc[[-1,]]+1)
    for i_d,i_f in zip (ind_aux,ind_aux2):
        x_d,y_d=X.loc[i_d],Y.loc[i_d]
        x_f,y_f=X.loc[i_f],Y.loc[i_f]
        tab_X=np.linspace(x_d,x_f,num=(i_f-i_d)+1)
        X.loc[i_d:i_f]=tab_X
        tab_Y=np.linspace(y_d,y_f,num=(i_f-i_d)+1)
        Y.loc[i_d:i_f]=tab_Y
    
    print('Valeurs remplacées : {}'.format(len(t2)))
    return(X.copy(),Y.copy())

# Estime la position et le temps des points défectueux à l'aide d'une régression linéaire des points de même profil.

def CMD_XY_Nan_completion(don):
    X = don["X_int"]
    Y = don["Y_int"]
    indXNan=X.index[X.isna()]
    indYNan=Y.index[Y.isna()]
    if len(indXNan)<1:
        print('Aucune valeur à interpoler')
        return don.copy()
    if np.all(indXNan==indYNan):
        indc=indXNan.copy()
    else:
        MESS_warn_mess("[DEV] NaN en X et NaN en Y n'ont pas les même position dans le tableau (pas d'effet)")
        return don.copy()
    
    ind_aux = indc[indc.diff()!=1.]-1
    for i_d in ind_aux:
        prof = don.loc[i_d,'b et p']
        bloc = don.loc[don['b et p'] == prof]
        bloc_notna = bloc.dropna(subset = ["X_int","Y_int"])
        bloc_na = bloc.loc[bloc.index.difference(bloc.dropna(subset = ["X_int","Y_int"]).index)]
        bloc_notna_l = bloc_notna.shape[0]
        
        if bloc_notna_l == 1:
            MESS_warn_mess("Un des profils ne possède qu'un unique point connu : régression impossible.")
        else:
            lin_tab1 = np.array([[index, row["temps (s)"]] for index, row in bloc_notna.iterrows()])
            lin_tab2 = np.array([[index, row["X_int"]] for index, row in bloc_notna.iterrows()])
            lin_tab3 = np.array([[index, row["Y_int"]] for index, row in bloc_notna.iterrows()])
            # La régression ne marche pas avec deux points, mais on peut en créer un troisième
            if bloc_notna_l == 2:
                lin_tab1 = np.concatenate([lin_tab1,[[sum(lin_tab1[:,0])/len(lin_tab1[:,0]),sum(lin_tab1[:,1])/len(lin_tab1[:,1])]]])
                lin_tab2 = np.concatenate([lin_tab2,[[sum(lin_tab2[:,0])/len(lin_tab2[:,0]),sum(lin_tab2[:,1])/len(lin_tab2[:,1])]]])
                lin_tab3 = np.concatenate([lin_tab3,[[sum(lin_tab3[:,0])/len(lin_tab3[:,0]),sum(lin_tab3[:,1])/len(lin_tab3[:,1])]]])
            
            lin_reg1 = linregress(lin_tab1)
            lin_reg2 = linregress(lin_tab2)
            lin_reg3 = linregress(lin_tab3)

            for index, row in bloc_na.iterrows():
                c = lin_reg1.intercept + lin_reg1.slope*index
                don.loc[index, "temps (s)"] = c
                c = lin_reg2.intercept + lin_reg2.slope*index
                don.loc[index, "X_int"] = c
                c = lin_reg3.intercept + lin_reg3.slope*index
                don.loc[index, "Y_int"] = c
        
    
    print('Valeurs remplacées : {}'.format(len(indXNan)))
    return don.copy()
 
# Estime la position de tous les points à l'aide d'une régression linéaire. On considère alors que la trajectoire lors d'un passage est toujours linéaire.
# Sert à corriger les erreurs en cosinus du GPS. Attention, part du principe qu'aucun point n'est NaN.
   
def CMD_pts_rectif(don,ind_deb=None,ind_fin=None):
    
    ind_aux = []
    cpt = -1
    for index, row in don.iterrows():
        if row["b et p"] != cpt:
            cpt = row["b et p"]
            ind_aux.append(index)

    for i_d in ind_aux[ind_deb:ind_fin]:
        prof = don.loc[i_d,'b et p']
        bloc = don.loc[don['b et p'] == prof]
        bloc_l = bloc.shape[0]
        
        if bloc_l == 1:
            MESS_warn_mess("Un des profils ne possède qu'un unique point connu : régression impossible.")
        else:
            # lin_tab1 = np.array([[index, row["temps (s)"]] for index, row in bloc.iterrows()])
            lin_tab2 = np.array([[index, row["X_int"]] for index, row in bloc.iterrows()])
            lin_tab3 = np.array([[index, row["Y_int"]] for index, row in bloc.iterrows()])
            # La régression ne marche pas avec deux points, mais on peut en créer un troisième
            if bloc_l == 2:
                # lin_tab1 = np.concatenate([lin_tab1,[[sum(lin_tab1[:,0])/len(lin_tab1[:,0]),sum(lin_tab1[:,1])/len(lin_tab1[:,1])]]])
                lin_tab2 = np.concatenate([lin_tab2,[[sum(lin_tab2[:,0])/len(lin_tab2[:,0]),sum(lin_tab2[:,1])/len(lin_tab2[:,1])]]])
                lin_tab3 = np.concatenate([lin_tab3,[[sum(lin_tab3[:,0])/len(lin_tab3[:,0]),sum(lin_tab3[:,1])/len(lin_tab3[:,1])]]])
            
            # lin_reg1 = linregress(lin_tab1)
            lin_reg2 = linregress(lin_tab2)
            lin_reg3 = linregress(lin_tab3)
            
            for index, row in bloc.iterrows():
                # c = lin_reg1.intercept + lin_reg1.slope*index
                # don.loc[index, "temps (s)"] = c
                c = lin_reg2.intercept + lin_reg2.slope*index
                don.loc[index, "X_int"] = c
                c = lin_reg3.intercept + lin_reg3.slope*index
                don.loc[index, "Y_int"] = c
    
    return don.copy()

# fonction qui effectue le décalage longitudinal et transverse
# par rapport au sens de déplacement
# X,Y et profs sont de pandas.series
# une amélioration serait de le faire avec la courbe paramètrique enveloppe
# issue du cercle de centre la courbe trajectoire

def CMD_decal_posLT(X,Y,profs,decL=0.,decT=0.):
    ls_Xc=[]
    ls_Yc=[]
    ls_prof=profs.unique()
    for prof in ls_prof:
        ind_c=profs.index[profs==prof]
        XX=X.loc[ind_c].copy()
        YY=Y.loc[ind_c].copy()
        DX=XX.diff()
        DY=YY.diff()
        DX1=DX.copy()
        DY1=DY.copy()
    # pour avoir quelque chose de pas trop moche on fait la moyenne des 
    # décalages avec mouvement avant le point et après le point   
        DX.iloc[0:-1]=DX.iloc[1:]      
        DY.iloc[0:-1]=DY.iloc[1:]
        DX1.iloc[0]=DX1.iloc[1]
        DY1.iloc[0]=DY1.iloc[1]
        
        DR=np.sqrt(DX*DX+DY*DY)       
        DR1=np.sqrt(DX1*DX1+DY1*DY1)
        
        CDir=(DX/DR+DX1/DR1)/2.
        SDir=(DY/DR+DY1/DR1)/2.
        
        decX=CDir*decL-SDir*decT
        decY=SDir*decL+CDir*decT
        
        X1=XX+decX
        Y1=YY+decY
        ls_Xc.append(X1)
        ls_Yc.append(Y1)
       
    Xc=pd.concat(ls_Xc) 
    Yc=pd.concat(ls_Yc)   
    return(Xc,Yc)

# Pour chaque voie, corrige le décalage de position

def CMD_dec_voies(don,ncx,ncy,nb_ecarts,TxRx,gps_dec):
    
    print(ncx)
    for e in range(nb_ecarts):
        decx = gps_dec[0]-(TxRx[e]-TxRx[-1])/2
        X, Y = CMD_decal_posLT(don["X_int"],don["Y_int"],don["Profil"],decL=decx,decT=gps_dec[1])
        don[ncx[e]] = X.round(CONFIG.prec_coos)
        don[ncy[e]] = Y.round(CONFIG.prec_coos)
    return don.copy()

# Fonction principale de la frontière.

def CMD_frontiere(ls_mes,ncx,ncy,nc_data,nb_data,nb_ecarts,nb_res,choice,sep,output_file,not_in_file=False):
    
    don_to_corr = [i for i in range(1,nb_data)]
    don_corr = [0]
    is_corr_done = False
    while is_corr_done == False:
        don_corr_copy = don_corr.copy()
        for i in don_corr_copy:
            don_to_corr_copy = don_to_corr.copy()
            for j in don_to_corr_copy:
                MESS_warn_mess("{} , {}".format(i+1,j+1))
                # print(ls_mes[i])
                # print("---------------------------")
                # print(ls_mes[j])
                ls_mes[j], done = CMD_calc_frontiere(ls_mes[i], ls_mes[j], ncx, ncy, nc_data, nb_res, nb_ecarts, m_size=40, verif=False, verif_pts=False, choice=choice)
                if done:
                    don_to_corr.remove(j)
                    don_corr.append(j)
            don_corr.remove(i)
            if len(don_to_corr) == 0:
                is_corr_done = True
        if len(don_corr) == 0:
            MESS_warn_mess("Certains jeux de données n'ont pas pu être ajustés. Sont-ils tous frontaliers ?")
            is_corr_done = True
    
    if not_in_file:
        return ls_mes
    
    final_df = pd.concat(ls_mes)
    for e in range(nb_ecarts):
        fig,ax=plt.subplots(nrows=1,ncols=nb_res,figsize=(CONFIG.fig_width,CONFIG.fig_height))
        X = ls_mes[ncx[e]]
        Y = ls_mes[ncy[e]]
        for r in range(nb_res):
            Z = ls_mes[nc_data[e]]
            Q5,Q95 = Z.quantile([0.05,0.95])
            col = ax[r].scatter(X,Y,marker='s',c=Z,cmap='cividis',s=6,vmin=Q5,vmax=Q95)
            plt.colorbar(col,ax=ax[r],shrink=0.7)
            ax[r].title.set_text(nc_data[e*nb_res+r])
            ax[r].set_xlabel(ncx[e])
            ax[r].set_ylabel(ncy[e])
            ax[r].set_aspect('equal')
        plt.show(block=False)
        plt.pause(0.25)
        plt.savefig(CONFIG.script_path+"Output/CMDEX_f_" +str(e)+'.png')
        pickle.dump(fig, open(CONFIG.script_path+"Output/CMDEX_f_" +str(e)+'.pickle', 'wb'))
    
    if output_file == None:
        final_df.to_csv("frt.dat", index=False, sep=sep)
    else:
        final_df.to_csv(output_file, index=False, sep=sep)

# Corrige les décalages entre deux fichiers tapissant des zones même secteur. Activer "choice" pour valider ou non les ajustements.

def CMD_calc_frontiere(don1,don2,ncx,ncy,nc_data,nb_res,nb_ecarts,nb=30,tol_inter=0.1,tol_intra=0.2,m_size=14,choice=False,verif=False,verif_pts=False,dat_to_test=0):
    
    i_max = len(don1.index)-1
    j_max = len(don2.index)-1
    nb += int(np.sqrt(min(i_max,j_max))*0.2)
    for e in range(nb_ecarts):
        curr_e = e*nb_res
        x1=list(don1[ncx[e]])
        x2=list(don2[ncx[e]])
        y1=list(don1[ncy[e]])
        y2=list(don2[ncy[e]])
        
        data1 = don1[nc_data[curr_e:(e+1)*nb_res]].values.T.tolist()
        data2 = don2[nc_data[curr_e:(e+1)*nb_res]].values.T.tolist()
        
        i_excl = []
        j_excl = []
        
        if verif_pts:
            fig,ax=plt.subplots(nrows=1,ncols=1,figsize=(9,9))
            ax.plot(x1,y1,'+r',alpha=0.3)
            ax.plot(x2,y2,'+y',alpha=0.3)
            ax.set_xlabel(ncx)
            ax.set_ylabel(ncy)
            ax.set_aspect('equal')
        
        d_moy = 0
        for i in range(nb):
            i_min,j_min,d = CMD_appr_border(x1,x2,y1,y2,i_max,j_max,i_excl,j_excl)
            d_moy = d_moy + d
            i_excl.append(i_min)
            j_excl.append(j_min)
            if verif_pts:
                ax.plot(x1[i_min],y1[i_min],'ok')
                ax.plot(x2[j_min],y2[j_min],'om')
        d_moy = np.sqrt(d_moy / nb)
        d_max = np.sqrt(max(CMD_max_frontiere(x1,y1,i_excl),CMD_max_frontiere(x2,y2,j_excl)))
        d_caract = np.sqrt(min(CMD_appr_taille_grp(x1,y1),CMD_appr_taille_grp(x2,y2)))
        
        if verif:
            print(i_excl)
            print(j_excl)
            plt.show()
            print("d_moy = ",d_moy)
            print("d_caract (inter) = ",d_caract*tol_inter)
            print("d_max = ",d_max)
            print("d_caract (intra) = ",d_caract*tol_intra)
        
        if d_moy > d_caract*tol_inter or d_max < d_caract*tol_intra:
            return don2.copy(), False
        
        #data2[dat_to_test] = [x+0 for x in data2[dat_to_test]]
        diff = []
        mult = []
        for r in range(nb_res):
            d, m = CMD_compute_coeff(data1[r],data2[r],i_excl,j_excl)
            diff.append(d)
            mult.append(m)
            # print("diff (",r,") = ",d)
            # print("mult (",r,") = ",m)
            
        if choice:
            print("----------------------------- FRONTIERE -----------------------------")
            i = 0
            while i < nb_res:
                fig,ax=plt.subplots(nrows=2,ncols=1,figsize=(CONFIG.fig_height,CONFIG.fig_width))
                testouh = don1[nc_data[curr_e+i]].tolist() + don2[nc_data[curr_e+i]].tolist()
                Q = np.quantile(testouh,[0.05,0.95])
                sc1 = ax[0].scatter(x1+x2,y1+y2,marker='8',s=m_size,c=testouh,cmap='cividis',vmin=Q[0],vmax=Q[1])
                ax[0].title.set_text('Avant')
                ax[0].set_xlabel(ncx[e])
                ax[0].set_ylabel(ncy[e])
                ax[0].set_aspect('equal')
                cbar = plt.colorbar(sc1,ax=ax[0])
                cbar.set_label(nc_data[curr_e+i], rotation=270, labelpad=15)
                
                new_don2 = (don2[nc_data[curr_e+i]]*mult[i] + diff[i]).round(CONFIG.prec_data)
            
                testouh = don1[nc_data[curr_e+i]].tolist() + new_don2.tolist()
                Q = np.quantile(testouh,[0.05,0.95])
                sc2 = ax[1].scatter(x1+x2,y1+y2,marker='8',s=m_size,c=testouh,cmap='cividis',vmin=Q[0],vmax=Q[1])
                ax[1].title.set_text('Après')
                ax[1].set_xlabel(ncx[e])
                ax[1].set_ylabel(ncy[e])
                ax[1].set_aspect('equal')
                cbar = plt.colorbar(sc2,ax=ax[1])
                cbar.set_label(nc_data[curr_e+i], rotation=270, labelpad=15)
                plt.show(block=False)
                plt.pause(0.25)
                
                correct = False
                while correct == False:
                    if GUI:
                        MESS_input_GUI(["Valider l'ajustement ?","","~b~ Oui","~b~ Non","~b~ Réessayer"])
                        try:
                            inp = ["y","n","r"][GUI_VAR_LIST[0]]
                        except:
                            MESS_warn_mess("Veuillez sélectionner un réponse")
                            continue
                    else:
                        MESS_input_mess(["Valider l'ajustement ?","","y : Oui (continuer avec)","n : Non (conserver la donnée initiale)","r : Réessayer (relance un nouvel ajustement sur la même donnée)"])
                        inp = input()
                    if inp == "n":
                        correct = True
                        i += 1
                    elif inp == "y":
                        don2.loc[:,nc_data[curr_e+i]] = new_don2
                        correct = True
                        i += 1
                    elif inp == "r":
                        i_excl = []
                        j_excl = []
                        for j in range(nb):
                            i_min,j_min,d = CMD_appr_border(x1,x2,y1,y2,i_max,j_max,i_excl,j_excl)
                            d_moy = d_moy + d
                            i_excl.append(i_min)
                            j_excl.append(j_min)
                        diff = []
                        mult = []
                        for r in range(nb_res):
                            d, m = CMD_compute_coeff(data1[r],data2[r],i_excl,j_excl)
                            diff.append(d)
                            mult.append(m)
                        correct = True
                    else:
                        MESS_warn_mess("Réponse non reconnue !")
                plt.close(fig)
        
        else:
            if verif and dat_to_test >= 0:
                print("----------------------------- FRONTIERE -----------------------------")
                fig,ax=plt.subplots(nrows=2,ncols=1,figsize=(CONFIG.fig_height,CONFIG.fig_width))
                testouh = don1[nc_data[curr_e+dat_to_test]].tolist() + don2[nc_data[curr_e+dat_to_test]].tolist()
                Q = np.quantile(testouh,[0.05,0.95])
                sc1 = ax[0].scatter(x1+x2,y1+y2,marker='8',s=m_size,c=testouh,cmap='cividis',vmin=Q[0],vmax=Q[1])
                ax[0].title.set_text('Avant')
                ax[0].set_xlabel(ncx[e])
                ax[0].set_ylabel(ncy[e])
                ax[0].set_aspect('equal')
                cbar = plt.colorbar(sc1,ax=ax[0])
                cbar.set_label(nc_data[curr_e+dat_to_test], rotation=270, labelpad=15)
                
            for r in range(nb_res):
                don2.loc[:,nc_data[curr_e+r]] = (don2[nc_data[curr_e+r]]*mult[r] + diff[r]).round(CONFIG.prec_data)
            
            if verif and dat_to_test >= 0:
                testouh = don1[nc_data[curr_e+dat_to_test]].tolist() + don2[nc_data[curr_e+dat_to_test]].tolist()
                Q = np.quantile(testouh,[0.05,0.95])
                sc2 = ax[1].scatter(x1+x2,y1+y2,marker='8',s=m_size,c=testouh,cmap='cividis',vmin=Q[0],vmax=Q[1])
                ax[1].title.set_text('Après')
                ax[1].set_xlabel(ncx[e])
                ax[1].set_ylabel(ncy[e])
                ax[1].set_aspect('equal')
                cbar = plt.colorbar(sc2,ax=ax[1])
                cbar.set_label(nc_data[curr_e+dat_to_test], rotation=270, labelpad=15)
                plt.show(block=False)
                plt.pause(0.25)
    
    return don2.copy(), True

# Trouve un duo de points (l'un dans l'ensemble 1, l'autre dans le 2) le plus proche possible (excepté dans les sous-ensembles excl)

def CMD_appr_border(x1,x2,y1,y2,i_max,j_max,i_excl,j_excl):
    
    i_dec = random.randint(0, i_max)
    j_dec = random.randint(0, j_max)
    while i_dec in i_excl:
        i_dec = random.randint(0, i_max)
    while j_dec in j_excl:
        j_dec = random.randint(0, j_max)
    i_min = i_dec
    j_min = j_dec
    i = 0
    j = 0
    i_ = i_dec - i_max
    j_ = j_dec - j_max
    #print("i_ = ",i_," | j_ = ",j_)
    d_min = (x1[i_min]-x2[j_min])**2 + (y1[i_min]-y2[j_min])**2
    turn = True
    
    # Complexité : O(n)
    while i < i_max or j < j_max:
        if turn:
            d = (x1[i_]-x2[j_min])**2 + (y1[i_]-y2[j_min])**2
            if d < d_min and i_%(i_max+1) not in i_excl:
                if j != j_max:
                    turn = False
                #print("|i = {}, i_min = {}, j = {}, j_min = {}, d = {}".format(i,i_min,j,j_min,d))
                d_min = d
                i_min = i_%(i_max+1)
            elif i == i_max:
                turn = False
            else:
                i+=1
                i_+=1
        else:
            d = (x1[i_min]-x2[j_])**2 + (y1[i_min]-y2[j_])**2
            if d < d_min and j_%(j_max+1) not in j_excl:
                if i != i_max:
                    turn = True
                #print("_i = {}, i_min = {}, j = {}, j_min = {}, d = {}".format(i,i_min,j,j_min,d))
                d_min = d
                j_min = j_%(j_max+1)
            elif j == j_max:
                turn = True
            else:
                j+=1
                j_+=1
    # print("i_min = {}, j_min = {}, d_min = {}".format(i_min,j_min,d_min))
    # print("pt 1 = [{},{}]".format(x1[i_min],y1[i_min]))
    # print("pt 2 = [{},{}]".format(x2[j_min],y2[j_min]))
    # print("--------------------------------------------------------------")
    return i_min,j_min,d_min

# Renvoie la moyenne des écarts des points adjacents dans le fichier (plus utilisée)

def CMD_appr_distmoygrp(x1,y1):
    l = len(x1)-1
    d = 0
    for i in range(l):
        d = d + (x1[i]-x1[i+1])**2 + (y1[i]-y1[i+1])**2
    return d / l

# Calcule une taille caractéristique de l'ensemble de points

def CMD_appr_taille_grp(x1,y1):
    x_min = min(x1)
    x_max = max(x1)
    y_min = min(y1)
    y_max = max(y1)
    d = (x_max-x_min)**2 + (y_max-y_min)**2
    return d

# Calcule la distance maximale entre deux points de la même frontière

def CMD_max_frontiere(x1,y1,excl):
    d_max = 0
    for i in excl[:-1]:
        for j in excl[1:]:
            d = (x1[i]-x1[j])**2 + (y1[i]-y1[j])**2
            d_max = max(d_max,d)
    return d_max

# Renvoie le coefficient constant de décalage pour une variable donnée entre deux fichiers

def CMD_compute_coeff(col1,col2,excl1,excl2):
    sig1 = np.std([col1[i] for i in excl1])
    sig2 = np.std([col2[j] for j in excl2])
    
    t = len(excl1)
    diff = 0
    ec = sig1/sig2
    for j in range(t):
        diff = diff + col1[excl1[j]] - (col2[excl2[j]])*ec
    
    return diff/t, ec

# Détecte le décalage des données en fonction du temps grace à la base, puis propose une correction.
# Correction par différence si diff=True, sinon correction par proportion.

def CMD_evol_profils(don,bas,nom_fich,col_z,nb_ecarts,diff=True,auto_adjust=True,man_adjust=False,verif=False,line=False):
    
    global GUI_VAR_LIST
    try:
        prof_deb = don['Profil'].iat[0]
        prof_fin = don['Profil'].iat[-1]
    except KeyError:
        MESS_err_mess("Les données ne sont pas interpolées ({})".format(nom_fich))
    try:
        base_deb = bas['Base'].iat[0]
        base_fin = bas['Base'].iat[-1]
    except KeyError:
        MESS_err_mess("La base associée à {} n'est pas valide (elle doit provenir d'une fusion ou d'une interpolation)".format(nom_fich))
    prof_l = prof_fin-prof_deb+1
    base_l = base_fin-base_deb+1
    
    col_names = don.columns[col_z]
    nb_data = len(col_z)
    nb_res = nb_data//nb_ecarts
    
    prof_med = np.array([[0.0]*prof_l]*nb_data)
    base_med = np.array([[0.0]*base_l]*nb_data)
    prof_bp = []
    base_bp = []
    index_list = []
    
    color = ["blue","green","orange","magenta","red","cyan","black","yellow"]
    if line:
        mrk = 'x-'
    else:
        mrk = 'x'
    
    for i in range(prof_l):
        prof = don[don["Profil"] == i+prof_deb]
        prof_bp.append(prof['b et p'].iat[0])
        index_list.append(prof.index[0])
        for j in range(nb_data):
            prof_med[j,i] = prof[col_names[j]].median()
    index_list.append(None)

    for i in range(base_l):
        base = bas[bas["Base"] == i+base_deb]
        base_bp.append(base['b et p'].iat[0])
        for j in range(nb_data):
            base_med[j,i] = base[col_names[j]].median()
    
    if auto_adjust:
        if verif:
            fig,ax = plt.subplots(nrows=1,ncols=nb_res,figsize=(nb_res*CONFIG.fig_width//2,CONFIG.fig_height),squeeze=False)
            if diff:
                for j in range(nb_data):
                    ax[0][j%nb_res].plot(prof_bp,(prof_med[j]-prof_med[j,0]),mrk,label=col_names[j]+" (profil)",color=color[int(j/2)])
                    ax[0][j%nb_res].plot(base_bp,(base_med[j]-base_med[j,0]),'o--',label=col_names[j]+" (base)",color=color[int(j/2)])
                    ax[0][j%nb_res].set_xlabel("Profil")
                    ax[0][j%nb_res].set_ylabel("Valeur en diff .avec la première")
                    ax[0][j%nb_res].grid(axis="x")
                    ax[0][j%nb_res].legend()
            else:
                for j in range(nb_data):
                    ax[0][j%nb_res].plot(prof_bp,prof_med[j]/max(prof_med[j]),mrk,label=col_names[j]+" (profil)",color=color[int(j/nb_res)])
                    ax[0][j%nb_res].plot(base_bp,base_med[j]/max(base_med[j]),'o--',label=col_names[j]+" (base)",color=color[int(j/nb_res)])
                    ax[0][j%nb_res].set_xlabel("Profil")
                    ax[0][j%nb_res].set_ylabel("Valeur en prop. du max")
                    ax[0][j%nb_res].grid(axis="x")
                    ax[0][j%nb_res].legend()
            fig.suptitle(nom_fich+" (données de base)")
            plt.show(block=False)
            plt.pause(0.25)
    
        for i in range(prof_l):
            prof = don[don["Profil"] == i+prof_deb]
            r = prof["b et p"].iat[0]
            k = 0
            while k < base_l and base_bp[k] < r:
                k = k+1
            
            av = k-1
            ap = k
            if k == 0:
                av = 0
                fact = 0
            elif k == base_l:
                ap = base_l-1
                fact = 1
            else:
                fact = (r-base_bp[av])/(base_bp[ap]-base_bp[av])
            for j in range(nb_data):
                if diff:
                    new_val = prof[col_names[j]] - fact*(base_med[j,ap]-base_med[j,av])
                else:
                    new_val = prof[col_names[j]]/(fact*base_med[j,ap] + (1-fact)*base_med[j,av])
                if index_list[i+1] != None:
                    temp = don.loc[index_list[i+1]][col_names[j]]
                don.loc[index_list[i]:index_list[i+1], col_names[j]] = new_val.round(CONFIG.prec_data)
                if index_list[i+1] != None:
                    don.loc[index_list[i+1], col_names[j]] = temp
                
        for i in range(prof_l):
            prof = don[don["Profil"] == i+prof_deb]
            for j in range(nb_data):
                prof_med[j,i] = prof[col_names[j]].median()
    
    if verif:
        correct = False
        while correct == False:
            fig,ax = plt.subplots(nrows=1,ncols=nb_res,figsize=(nb_res*CONFIG.fig_width//2,CONFIG.fig_height),squeeze=False)
            if diff:
                for j in range(nb_data):
                    ax[0][j%nb_res].plot(prof_bp,(prof_med[j]-prof_med[j,0]),mrk,label=col_names[j]+" (profil)",color=color[int(j/nb_res)])
                    ax[0][j%nb_res].set_xlabel("Profil")
                    ax[0][j%nb_res].set_ylabel("Valeur en diff .avec la première")
                    ax[0][j%nb_res].grid(axis="x")
                    ax[0][j%nb_res].legend()
    
            else:
                for j in range(nb_data):
                    ax[0][j%nb_res].plot(prof_bp,prof_med[j]/max(prof_med[j]),mrk,label=col_names[j]+" (profil)",color=color[int(j/nb_res)])
                    ax[0][j%nb_res].set_xlabel("Profil")
                    ax[0][j%nb_res].set_ylabel("Valeur en prop. du max")
                    ax[0][j%nb_res].grid(axis="x")
                    ax[0][j%nb_res].legend()
            if auto_adjust:
                fig.suptitle(nom_fich+" (données redressées)")
            else:
                fig.suptitle(nom_fich)
            plt.show(block=False)
            plt.pause(0.25)
            
            if man_adjust:
                try:
                    if GUI:
                        MESS_input_GUI(["Sélectionner les bornes du bloc de profils à corriger, puis l'indice des colonnes concernées.Ici, cet indice peut varier de 1 à {}.".format(nb_data),
                                       "Cette procédure se relance automatiquement, faites un bloc à la fois.",
                                       "","a-b x y z: Du profil a à b (inclus), sur les colonnes x,y et z","n : Non (terminer la procédure)","~t~"])
                        try:
                            inp = GUI_VAR_LIST[0]
                        except:
                            MESS_warn_mess("Veuillez sélectionner un réponse")
                            continue
                    else:
                        MESS_input_mess(["Sélectionner les bornes du bloc de profils à corriger, puis l'indice des colonnes concernées.",
                                        "Ici, cet indice peut varier de 1 à {}.".format(nb_data),"Cette procédure se relance automatiquement, faites un bloc à la fois.",
                                        "","a-b x y z: Du profil a à b (inclus), sur les colonnes x,y et z","n : Non (terminer la procédure)"])
                        inp = input()
                    if inp == "n":
                        correct = True
                    else:
                        res = re.split(r"[ ]+",inp)
                        id_prof = re.split(r"-",res[0])
                        first = don[don["b et p"] == int(id_prof[0])]["Profil"].iat[0]-prof_deb
                        last = don[don["b et p"] == int(id_prof[1])]["Profil"].iat[0]-prof_deb
                        column_to_do = []
                        for r in res[1:]:
                            column_to_do.append(int(r)-1)
                        #print(first," ",last)
                        new_med = []
                        av = first
                        ap = last
                        if first == 0:
                            av = last
                        elif last == prof_fin-prof_deb-1:
                            ap = first
                        for j in range(nb_data):
                            new_med.append(np.linspace(prof_med[j,av-1],prof_med[j,ap+1],(last-first)+3))
                        # print(new_med)
                        # print(prof_med[1])
                        for i in range(first,last+1):
                            prof = don[(don["Profil"] == i+prof_deb)]
                            #print("PROF (",i,"): ",prof)
                            if prof.empty: # Base
                                continue
                            r = prof["b et p"].iat[0]
                            k = 0
                            while k < prof_l and prof_bp[k] < r:
                                k = k+1
                            for j in column_to_do:
                                if diff:
                                    new_val = prof[col_names[j]] + (new_med[j][i-first+1]-prof_med[j,k])
                                else:
                                    new_val = prof[col_names[j]] * (new_med[j][i-first+1]/prof_med[j,k])
                                #print(new_med[j][i-first+1]," ",prof_med[j,k]," -> ",(new_med[j][i-first+1]-prof_med[j,k]))
                                #print(new_val)
                                if index_list[k+1] != None:
                                    temp = don.loc[index_list[k+1]][col_names[j]]
                                don.loc[index_list[k]:index_list[k+1], col_names[j]] = new_val.round(CONFIG.prec_data)
                                if index_list[k+1] != None:
                                    don.loc[index_list[k+1], col_names[j]] = temp
                        for i in range(prof_l):
                            prof = don[don["Profil"] == i+prof_deb]
                            for j in range(nb_data):
                                prof_med[j,i] = prof[col_names[j]].median()
                except ValueError:
                    MESS_warn_mess("Réponse non reconnue !")
                except IndexError:
                    MESS_warn_mess("Un des profils {} n'existe pas !".format(id_prof))
            else:
                correct = True
    
    return don.copy()

# Fonction principale de la mise en grille (choix de la méthode)

def CMD_grid(col_x,col_y,col_z,file_list,sep,output_file,m_type,radius,prec,seuil,i_method,no_crop,all_models,plot_pts,matrix):
    
    global GUI_VAR_LIST
    m_type_list = ['h','k','i']
    if m_type == None:
        correct = False
        while correct == False:
            if GUI:
                MESS_input_GUI(["Type d'opération ?","","~r~ heatmap ~!~","~r~ krigeage","~r~ interpolation scipy"])
                try:
                    m_type = m_type_list[GUI_VAR_LIST[0]]
                except:
                    MESS_warn_mess("Veuillez sélectionner un réponse")
                    continue
            else:
                MESS_input_mess(["Type d'opération ?","","h : heatmap","k : krigeage","i : interpolation scipy"])
                m_type = input()
            if m_type in m_type_list:
                correct = True
            else:
                MESS_warn_mess("Réponse non reconnue !")
    elif m_type not in m_type_list:
        MESS_err_mess("Méthode non reconnue ({})".format(m_type_list))
    
    df_l = []
    for f in file_list :
        data = TOOL_check_time_date(f,sep)
        df_l.append(data)
    don_raw = pd.concat(df_l)
    don_l = len(don_raw)
    if m_type == 'k':
        if not no_crop and don_l > 1000:
            MESS_warn_mess("Jeu lourd : on ne prendra qu'une partie de l'ensemble (1000 points)")
            don = don_raw.copy()[::(don_l//1000)+1]
        else:
            don = don_raw
        if prec >= 300:
            correct = False
            while correct == False:
                if GUI:
                    MESS_input_GUI(["Grande précision, le calcul risque d'être conséquent !","Êtes-vous sûr de continuer ?","","~b~ Oui","~b~ Non"])
                    try:
                        inp = ["n","y"][GUI_VAR_LIST[0]]
                    except:
                        MESS_warn_mess("Veuillez sélectionner un réponse")
                        continue
                else:
                    MESS_warn_mess("-------------------------------------------------------------------")
                    MESS_input_mess(["Grande précision, le calcul risque d'être conséquent !","Êtes-vous sûr de continuer ? y/n"])
                    MESS_warn_mess("-------------------------------------------------------------------")
                    inp = input()
                if inp == "n":
                    MESS_err_mess("Vous avez probablement fait le bon choix...")
                elif inp == "y":
                    correct = True
                else:
                    MESS_warn_mess("Réponse non reconnue !")
    elif m_type == 'h':
        if radius == 0:
            MESS_err_mess("Un rayon de 0 ne donne pas de heatmap !")
        don = don_raw
        correct = False
        while correct == False:
            if GUI:
                MESS_input_GUI(["Jeu réduit à 1000 points (test pour kriging) ?","","~b~ Oui","~b~ Non"])
                try:
                    inp = ["y","n"][GUI_VAR_LIST[0]]
                except:
                    MESS_warn_mess("Veuillez sélectionner un réponse")
                    continue
            else:
                MESS_input_mess(["Jeu réduit à 1000 points (test pour kriging) ?","","y : oui","n : non"])
                inp = input()
            if inp == "n":
                correct = True
            elif inp == "y":
                don = don_raw.copy()[::(don_l//1000)+1]
                correct = True
            else:
                MESS_warn_mess("Réponse non reconnue !")
    else:
        don = don_raw
    
    don.reset_index(drop=True,inplace=True)
    
    ncx, ncy, col_T, nb_data, nb_ecarts, nb_res = TOOL_manage_cols(don,col_x,col_y,col_z)
    
    grid, ext, pxy = CMD_dat_to_grid(don,ncx,ncy,nb_ecarts,nb_res,radius,prec,seuil,heatmap=(m_type=='h'))
    
    if m_type == 'k':
        grid_k = CMD_kriging(don,ncx,ncy,ext,pxy,col_T,nb_data,nb_ecarts,nb_res,prec=prec,all_models=all_models,verif=False)
        grid_k_final = np.array([[[np.nan for j in range(pxy[1])] for i in range(pxy[0])] for n in range(nb_data)])
        for e in range(nb_ecarts):
            for j in range(pxy[1]):
                for i in range(pxy[0]):
                    g = grid[e,j,i]
                    if g == g:
                        for r in range(nb_res):
                            n = e*nb_res + r
                            grid_k_final[n,i,j] = grid_k[n*2+3][j*pxy[0]+i]
        CMD_grid_plot(don,grid_k_final,ncx,ncy,ext,pxy,col_T,nb_ecarts,nb_res,output_file,sep,plot_pts=plot_pts,matrix=matrix)
    elif m_type == 'i':
        i_method_list = ['nearest', 'linear', 'cubic']
        if i_method == None:
            correct = False
            while correct == False:
                if GUI:
                    MESS_input_GUI(["Type d'interpolation ?","","~r~ nearest", "~r~ linear ~!~", "~r~ cubic"])
                    try:
                        inp = GUI_VAR_LIST[0]
                    except:
                        MESS_warn_mess("Veuillez sélectionner un réponse")
                        continue
                else:
                    MESS_input_mess(["Type d'interpolation ?","","0 : nearest", "1 : linear", "2 : cubic"])
                    inp = input()
                try :
                    i_method = i_method_list[int(inp)]
                    correct = True
                except:
                    MESS_warn_mess("Réponse non reconnue !")
        elif i_method not in i_method_list:
            MESS_err_mess("Méthode non reconnue ({})".format(i_method_list))
        grid_i = CMD_scipy_interp(don,ncx,ncy,ext,pxy,col_T,nb_data,nb_ecarts,nb_res,prec,i_method)
        for e in range(nb_ecarts):
            for j in range(pxy[1]):
                for i in range(pxy[0]):
                    g = grid[e,j,i]
                    if g != g:
                        for r in range(nb_res):
                            n = e*nb_res + r
                            grid_i[n][i][j] = np.nan
        CMD_grid_plot(don,grid_i,ncx,ncy,ext,pxy,col_T,nb_ecarts,nb_res,output_file,sep,plot_pts=plot_pts,matrix=matrix)
    

# Transpose les données sur une grille rectangulaire, avec au maximum prec cases par ligne/colonne.
# Complexité : O(n) sur le nombre de données, O(n^2) sur prec, O(n^2) sur radius.

def CMD_dat_to_grid(don,ncx,ncy,nb_ecarts,nb_res,radius,prec,seuil,heatmap=False,verif=False):
    
    print("=== Phase préliminaire ===")
    
    try:
        X = np.array(don[ncx])
        Y = np.array(don[ncy])
    except KeyError:
        MESS_err_mess('Les colonnes "{}" et "{}" '.format(ncx,ncy)+"n'existent pas")
    
    try:
        max_X = max(X.flatten())
        min_X = min(X.flatten())
        max_Y = max(Y.flatten())
        min_Y = min(Y.flatten())
    except TypeError:
        MESS_err_mess("Les colonnes ne sont pas valides : les indices sont-ils bons ?")
    if verif:
        print("max_X = ",max_X)
        print("min_X = ",min_X)
        print("max_Y = ",max_Y)
        print("min_Y = ",min_Y)
    diff_X = max_X-min_X
    diff_Y = max_Y-min_Y
    if diff_X > diff_Y:
        prec_X = prec
        prec_Y = int(prec*(diff_Y/diff_X))
    else:
        prec_Y = prec
        prec_X = int(prec*(diff_X/diff_Y))
    pas_X = diff_X/prec_X
    pas_Y = diff_Y/prec_Y
    
    gridx = [min_X + pas_X*i for i in range(prec_X)]
    gridy = [min_Y + pas_Y*j for j in range(prec_Y)]
    
    grid_conv, seuil, quot = CMD_calc_coeff(seuil,radius,prec)
    
    grid = np.array([[[0 for i in range(prec_X)] for j in range(prec_Y)] for e in range(nb_ecarts)])
    
    for ind, row in don.iterrows():
        for e in range(nb_ecarts):
            curr_x = row[ncx[e]]
            curr_y = row[ncy[e]]
            i_x = 1
            i_y = 1
            #print(curr_x," et ",curr_y)
            while i_x < prec_X and gridx[i_x] < curr_x:
                i_x += 1
            while i_y < prec_Y and gridy[i_y] < curr_y:
                i_y += 1
            grid[e,i_y-1,i_x-1] += 1
    
    # HEATMAP : On n'effectue l'opération que sur la première grille (les autres étant très proches)
    if heatmap:
        
        #print(grid)
        grid_final = CMD_heatmap_grid_calc(grid[0],grid_conv,prec_X,prec_Y,quot)
        
        #print(grid_final)
        CMD_heatmap_plot(don,grid_final,grid[0],ncx[0],ncy[0],[min_X,max_X,min_Y,max_Y],[prec_X,prec_Y],seuil)
        correct = False
        while correct == False:
            if GUI:
                MESS_input_GUI(["Test de seuil ?","","Rentrer la valeur du seuil à tester (flottant)","~t~","","~b~ Tester","~b~ Fin"])
                try:
                    inp, fin = GUI_VAR_LIST
                    if fin:
                        inp = "n"
                except:
                    MESS_warn_mess("Veuillez sélectionner un réponse")
                    continue
            else:
                MESS_input_mess(["Test de seuil ?","","Rentrer la valeur du seuil à tester (flottant)","n : terminé"])
                inp = input()
            if inp == "n":
                correct = True
            else:
                try:
                    seuil = float(inp)
                    grid_conv, seuil, quot = CMD_calc_coeff(seuil,radius,prec)
                    grid_final = CMD_heatmap_grid_calc(grid[0],grid_conv,prec_X,prec_Y,quot)
                    print(quot)
                    CMD_heatmap_plot(don,grid_final,grid[0],ncx[0],ncy[0],[min_X,max_X,min_Y,max_Y],[prec_X,prec_Y],seuil)
                except:
                    MESS_warn_mess("Réponse non reconnue !")
        
    else:
        if verif:
            print("Step(2)")
        grid_final = np.array([[[np.nan for i in range(prec_X)] for j in range(prec_Y)] for e in range(nb_ecarts)])
        if radius > 0:
            for e in range(nb_ecarts):
                for j in range(prec_Y):
                    for i in range(prec_X):
                        coeff = 0
                        if grid[e,j,i] != 0:
                            grid_final[e,j,i] = 0
                        else:
                            for gc in grid_conv:
                                n_j = j+gc[0]
                                n_i = i+gc[1]
                                if n_j >= 0 and n_j < prec_Y and n_i >= 0 and n_i < prec_X:
                                    if grid[e,n_j,n_i] != 0:
                                        coeff += gc[2]
                            if coeff > quot:
                                grid_final[e,j,i] = 0
    
    return grid_final, [min_X,max_X,min_Y,max_Y], [prec_X,prec_Y]

# Calcul de la grille de coefficients

def CMD_calc_coeff(seuil,radius,prec):
    
    grid_conv = []
    rc = radius**2
    if seuil < 0:
        mult = 1-seuil
        seuil = 0
    else:
        mult = 1
    for i in range(-radius,radius+1):
        for j in range(-radius,radius+1):
            d = (i**2)+(j**2)
            if d <= rc:
                coeff = ((1+radius-np.sqrt(i**2+j**2))/(1+radius))**seuil * mult
                grid_conv.append([i,j,coeff])
    quot = ((radius)**2)/3
    
    return grid_conv, seuil, quot

# Calcul de la heatmap

def CMD_heatmap_grid_calc(grid,grid_conv,prec_X,prec_Y,quot):
    
    grid_final = np.array([[0.0 for i in range(prec_X)] for j in range(prec_Y)])
    for j in range(prec_Y):
        for i in range(prec_X):
            coeff = 0
            for gc in grid_conv:
                n_j = j+gc[0]
                n_i = i+gc[1]
                if n_j >= 0 and n_j < prec_Y and n_i >= 0 and n_i < prec_X:
                    if grid[n_j,n_i] != 0:
                        coeff += gc[2]
            grid_final[j,i] = coeff/quot
    
    return grid_final

# Gère l'affichage de la heatmap

def CMD_heatmap_plot(don,grid_final,grid,ncx,ncy,ext,pxy,seuil):
    
    print("=== Phase de heatmap ===")
    os.chdir(CONFIG.script_path)

    plt.style.use('_mpl-gallery-nogrid')
    fig,ax = plt.subplots(nrows=1,ncols=2,figsize=(CONFIG.fig_width,CONFIG.fig_height))
    
    Q_l = [z for z in grid_final.flatten() if z == z]
    Q = np.quantile(Q_l,[0.05,0.95])
    ims = ax[0].imshow(grid_final, origin='lower', cmap='YlOrRd', vmin = Q[0], vmax=Q[1] , extent=ext)
    ax[0].set_title("Heatmap")
    ax[0].set_xlabel(ncx)
    ax[0].set_ylabel(ncy)
    ax[0].set_aspect('equal')
    plt.colorbar(ims,ax=ax[0])
    
    grid_restr = np.array([[np.nan for i in range(pxy[0])] for j in range(pxy[1])])
    for j in range(pxy[1]):
        for i in range(pxy[0]):
            if grid_final[j][i] > 1 or grid[j][i] != 0:
                grid_restr[j][i] = 0
    ims = ax[1].imshow(grid_restr, origin='lower', cmap='gray', extent=ext)
    try:
        ax[1].scatter(don[ncx],don[ncy],marker='s',c=don["Num fich"], cmap='YlOrRd',s=5)
    except:
        ax[1].scatter(don[ncx],don[ncy],marker='s', cmap='YlOrRd',s=5)
    ax[1].set_title("Zone sélectionnée (seuil = {})".format(seuil))
    ax[1].set_xlabel(ncx)
    ax[1].set_ylabel(ncy)
    ax[1].set_aspect('equal')
    plt.colorbar(ims,ax=ax[1])
    plt.show(block=False)
    plt.pause(0.25)

# Effectue l'interpolation scipy selon le modèle choisi

def CMD_scipy_interp(don,ncx,ncy,ext,pxy,nc_data,nb_data,nb_ecarts,nb_res,prec,i_method):
    
    print("=== Phase d'interpolation ===")
    grid_interp = []
    gridx, gridy = np.mgrid[ext[0]:ext[1]:pxy[0]*1j, ext[2]:ext[3]:pxy[1]*1j]
    
    for e in range(nb_ecarts):
        pos_data = don[[ncx[e],ncy[e]]].to_numpy()
        for r in range(nb_res):
            n = e*nb_res + r
            print("Tour ",n+1,"/",nb_data)
            val_data = list(don[nc_data[n]])
            grid_interp.append(scii.griddata(pos_data, val_data, (gridx, gridy), method=i_method))
        
    return grid_interp

# Effectue le kriging
# On pourra spécifier le variogramme avec var_choice=True

def CMD_kriging(don,ncx,ncy,ext,pxy,nc_data,nb_data,nb_ecarts,nb_res,prec=100,all_models=False,verif=False):
    
    print("=== Phase de kriging ===")
    min_X = ext[0]
    max_X = ext[1]
    min_Y = ext[2]
    max_Y = ext[3]
    diff_X = max_X-min_X
    diff_Y = max_Y-min_Y
    prec_X = pxy[0]
    prec_Y = pxy[1]
    pas_X = diff_X/prec_X
    pas_Y = diff_Y/prec_Y

    # Le setLocator ne marche pas si le nom de la colonne contient des catactères spéciaux : renommage par indice
    for n in range(nb_data):
        don.rename(columns={nc_data[n]: "c"+str(n)},inplace=True)

    dat = gl.Db_fromPandas(don)
    grid = gl.DbGrid.create(x0=[min_X,min_Y],dx=[pas_X,pas_Y],nx=[prec_X,prec_Y])
    if verif:
        grid.display()
        dat.display()
    
    for e in range(nb_ecarts):
        if e != 0:
            dat.setLocator(ncx[e-1],gl.ELoc.UNKNOWN)
            dat.setLocator(ncy[e-1],gl.ELoc.UNKNOWN)
        dat.setLocator(ncx[e],gl.ELoc.X,0)
        dat.setLocator(ncy[e],gl.ELoc.X,1)
        for r in range(nb_res):
            n = e*nb_res + r
            if n != 0:
                dat.setLocator("c"+str(n-1),gl.ELoc.UNKNOWN)
            dat.setLocator("c"+str(n),gl.ELoc.Z)
            
            print("Tour ",n+1,"/",nb_data)
            fitmod = CMD_variog(dat,all_models)
    
            uniqueNeigh = gl.NeighUnique.create()
            gl.kriging(dbin=dat, dbout=grid, model=fitmod, 
                          neigh=uniqueNeigh,
                          flag_est=True, flag_std=True, flag_varz=False,
                          namconv=gl.NamingConvention("KR")
                          )        
            if verif:
                fig, ax = gp.init(figsize=(16,9), flagEqual=True)
                ax.raster(grid, flagLegend=True)
                ax.decoration(title=nc_data[n])
    
    return grid

# Calcule le variogramme expérimental, puis propose de construire le modèle de variogramme (à la main)

def CMD_variog(dat,all_models):
    
    vario_list = CMD_variog_dir_params(dat)
    print(vario_list)
    print(vario_list[0])
    fitmod = CMD_variog_fit(vario_list[0],all_models)
    for variodir in vario_list[1:]:
        MESS_warn_mess("bjr")
        fitmod_2 = CMD_variog_fit(variodir,all_models)
        #fitmod_3 = gl.model_rule_combine(fitmod,fitmod_2,gl.Rule(0.0))
        #print(fitmod_3)
        MESS_warn_mess("orvwar")
    plt.close()
    for variodir in vario_list:
        gp.varmod(vario=variodir, flagLegend=True).figure.set_size_inches(CONFIG.fig_width, CONFIG.fig_height)
    # gp.varmod(model=fitmod, flagLegend=True).figure.set_size_inches(CONFIG.fig_width, CONFIG.fig_height)
    # gp.decoration(title="Modèle final !")
    # plt.show(block=False)
    # plt.pause(0.25)
    
    return fitmod

# Fait le choix des paramètres du variogramme expérimental

def CMD_variog_dir_params(dat):
    
    varioParamMulti = gl.VarioParam()
    varioParamMulti2 = gl.VarioParam()
    choice = ""
    vario_list = []
    
    big_correct = False
    while big_correct == False:
        correct = False
        while correct == False:
            if GUI:
                MESS_input_GUI(["Variogramme bidirectionel ?","","~b~ oui (bidirectionel)","~b~ non (unidirectionel)"])
                try:
                    inp = ["y","n"][GUI_VAR_LIST[0]]
                except:
                    MESS_warn_mess("Veuillez sélectionner un réponse")
                    continue
            else:
                MESS_input_mess(["Variogramme bidirectionel ?","","y : bidirectionel","n : unidirectionel"])
                inp = input()
            choice = inp
            if inp == "y":
                varioParamMulti = CMD_variog_dir_params_choice(varioParamMulti,1)
                varioParamMulti2 = CMD_variog_dir_params_choice(varioParamMulti2,2)
                correct = True
            elif inp == "n":
                varioParamMulti = CMD_variog_dir_params_choice(varioParamMulti,1)
                correct = True
            else:
                MESS_warn_mess("Réponse non reconnue !")
        
        variodir = gl.Vario(varioParamMulti)
        variodir.compute(dat)
        plt.close()
        try:
            gp.varmod(variodir, flagLegend=True).figure.set_size_inches(CONFIG.fig_width, CONFIG.fig_height)
        except ValueError: # Peut survenir de temps en temps, est réglé en mettant à jour...
            MESS_err_mess("ERREUR GSTLEARN : réessayer, sinon mettre à jour mpl ou python (conda par ex)")
        vario_list.append(variodir)
        if choice == "y":
            variodir2 = gl.Vario(varioParamMulti2)
            variodir2.compute(dat)
            gp.varmod(variodir2, flagLegend=True)
            vario_list.append(variodir2)
            
        #fig.varmod(variodir, flagLegend=True)
        plt.show(block=False)
        plt.pause(0.25)
        print(variodir)
        correct = False
        while correct == False:
            if GUI:
                MESS_input_GUI(["Le variogramme expérimental semble-t-il correct ?","","~b~ Oui","~b~ Non"])
                try:
                    inp = ["y","n"][GUI_VAR_LIST[0]]
                except:
                    MESS_warn_mess("Veuillez sélectionner un réponse")
                    continue
            else:
                MESS_input_mess(["Le variogramme expérimental semble-t-il correct ?","","y : Oui","n : Non"])
                inp = input()
            if inp == "y":
                correct = True
                big_correct = True
            elif inp == "n":
                correct = True
                vario_list = []
            else:
                MESS_warn_mess("Réponse non reconnue !")
    
    return vario_list

# Fait le choix des paramètres du variogramme expérimental sur une direction
# Informations sur https://soft.minesparis.psl.eu/gstlearn/1.7.2/doxygen/classDirParam.html

def CMD_variog_dir_params_choice(varioParamMulti,n):
    
    angle = []
    angle_tol = 0
    dist = 0
    pas = 0
    
    if GUI:
        correct = False
        while correct == False:
            MESS_input_GUI(["CHOIX DU VARIOGRAMME EXPÉRIMENTAL : Direction {}".format(n),"="*20,"ANGLE DIRECTION. Réponse par deux coordonnées",
                            "Exemple : '1 1' pour 45°, '1 0' pour 0°, '-1 2' pour 120°","On prend l'angle orienté avec l'axe des abcisses (x). Reponse en nombre entiers.","~t~",
                            "ANGLE TOLÉRANCE. Réponse en degrés (0-180)","Exemple : '45' pour 45°, '3.14' pour 3.14°","~t~",
                            "DISTANCE CONSIDÉRÉE. Réponse en distance (flottant)","Exemple : '100' pour un rayon consédéré de 100","~t~",
                            "PAS. Réponse en nombre de pas","Exemple : '20' pour créer 20 coupes de l'intervalle","~t~"])
            try:
                inp_a, inp_t, inp_d, inp_p = GUI_VAR_LIST
                res = re.split(r"[ ]+",inp_a)
                angle = [int(res[0]),int(res[1])]
                if angle == [0,0]:
                    MESS_warn_mess("Angle invalide !")
                    continue
                angle_tol = float(inp_t)
                dist = float(inp_d)
                pas = int(inp_p)
                correct = True
            except:
                MESS_warn_mess("Certains champs sont invalides")
    else:
        correct = False
        while correct == False:
            MESS_input_mess(["Direction {} : ANGLE DIRECTION. Réponse par deux coordonnées".format(n),
                            "Exemple : '1 1' pour 45°, '1 0' pour 0°, '-1 2' pour 120°","On prend l'angle orienté avec l'axe des abcisses (x). Reponse en nombre entiers."])
            inp_a = input()
            try:
                res = re.split(r"[ ]+",inp_a)
                angle = [int(res[0]),int(res[1])]
                if angle == [0,0]:
                    MESS_warn_mess("Angle invalide !")
                    continue
                correct = True
            except:
                MESS_warn_mess("Réponse non reconnue !")
        correct = False
        while correct == False:
            MESS_input_mess(["Direction {} : ANGLE TOLÉRANCE. Réponse en degrés (0-180)".format(n),"Exemple : '45' pour 45°, '3.14' pour 3.14°"])
            inp_t = input()
            try:
                angle_tol = float(inp_t)
                correct = True
            except:
                MESS_warn_mess("Réponse non reconnue !")
        correct = False
        while correct == False:
            MESS_input_mess(["Direction {} : DISTANCE CONSIDÉRÉE. Réponse en distance (flottant)".format(n),"Exemple : '100' pour un rayon consédéré de 100"])
            inp_d = input()
            try:
                dist = float(inp_d)
                correct = True
            except:
                MESS_warn_mess("Réponse non reconnue !")
        correct = False
        while correct == False:
            MESS_input_mess(["Direction {} : PAS. Réponse en nombre de pas".format(n),"Exemple : '20' pour créer 20 coupes de l'intervalle"])
            inp_p = input()
            try:
                pas = int(inp_p)
                correct = True
            except:
                MESS_warn_mess("Réponse non reconnue !")
    breaks_list = [dist/pas*i for i in range(pas+1)]
    
    mydir = gl.DirParam(pas,dist,0.5,angle_tol,0,0,np.nan,np.nan,0,breaks_list,angle)
    varioParamMulti.addDir(mydir)
    
    return varioParamMulti

# Calcule le modèle pour la direction choisie

def CMD_variog_fit(variodir, all_models):
    
    _Types_print = ["0 : NUGGET ", "1 : EXPONENTIAL ", "2 : SPHERICAL ", "3 : GAUSSIAN ", "4 : CUBIC ", "5 : SINCARD (Sine Cardinal) ", 
                    "6 : BESSELJ ", "7 : MATERN ", "8 : GAMMA ", "9 : CAUCHY ", "10 : STABLE ", "11 : LINEAR ", "12 : POWER "]
    print_l = 30
    if all_models:
        _Types_print += ["13 : ORDER1_GC (First Order Generalized covariance) ", "14 : SPLINE_GC (Spline Generalized covariance) ", 
                         "15 : ORDER3_GC (Third Order Generalized covariance) ", "16 : ORDER5_GC (Fifth Order Generalized covariance) ", 
                         "17 : COSINUS ", "18 : TRIANGLE ", "19 : COSEXP (Cosine Exponential) ", "20 : REG1D (1-D Regular) ", 
                         "21 : PENTA (Pentamodel) ", "22 : SPLINE2_GC (Order-2 Spline) ", "23 : STORKEY (Storkey covariance in 1-D) ", 
                         "24 : WENDLAND0 (Wendland covariance (2,0)) ", "25 : WENDLAND1 (Wendland covariance (3,1)) ", 
                         "26 : WENDLAND2 (Wendland covariance (4,2)) ", "27 : MARKOV (Markovian covariances) ", "28 : GEOMETRIC (Sphere only) ", 
                         "29 : POISSON (Sphere only) ", "30 : LINEARSPH (Sphere only) ",]
        print_l = 54
    _Symbol_print = [" ",".","-","~"]
    _Color_print = [error_color, success_color]
    nb_models = len(_Types_print)
    type_choice=[False for i in range(nb_models)]
    types_list = []
    constr_list = []
    
    big_correct = False
    while big_correct == False:
        types = []
        if GUI:
            MESS_input_GUI(["Choix du variogramme : rentrer le numéro associé à chaque variogramme pour l'ajouter/le retirer de la sélection",""]
                           +["~r~ " +re.split(r" : ",p)[1]+(print_l-len(re.split(r" : ",p)[1]))*" "+str(type_choice[ic]) for ic,p in enumerate(_Types_print)]
                           +["","~b~ Ajouter","~b~ Fin"])
            try:
                inp, fin = GUI_VAR_LIST
                if fin:
                    inp = 'y'
            except:
                MESS_warn_mess("Veuillez sélectionner un réponse")
                continue
        else:
            MESS_input_mess(["Choix du variogramme : rentrer le numéro associé à chaque variogramme pour l'ajouter/le retirer de la sélection",""]
                           +[p+(print_l-len(p))*_Symbol_print[ic%4]+_Color_print[int(type_choice[ic])]+str(type_choice[ic])+code_color for ic,p in enumerate(_Types_print)]
                           +["y : Fin"])
            inp = input()
        if inp == "y":
            constraints = gl.Constraints()
            if not types_list:
                MESS_warn_mess("Le variogramme ne peut pas être vide")
                continue
            curr_id = -1
            act_id = -1
            for c in constr_list:
                if c[0] != curr_id:
                    curr_id = c[0]
                    act_id += 1
                print(act_id)
                constraints.addItemFromParamId(gl.EConsElem.fromValue(c[1]+1),icov=act_id,type=gl.EConsType.fromValue(c[2]-1),value=c[3])
            print(types_list)
            print(constr_list)
            for t in types_list:
                types.append(gl.ECov.fromValue(t))
            plt.cla()
            fitmod = gl.Model()
            fitmod.fit(variodir,types=types, constraints=constraints)
            gp.varmod(variodir, fitmod, flagLegend=True).figure.set_size_inches(CONFIG.fig_width, CONFIG.fig_height)
            gp.decoration(title="Modèle VS Vario expé")
            plt.show(block=False)
            plt.pause(0.25)
            print(constraints)
            print(fitmod)
            correct = False
            while correct == False:
                if GUI:
                    MESS_input_GUI(["Le modèle de variogramme semble-t-il correct ?","","~b~ Oui","~b~ Non"])
                    try:
                        inp = ["y","n"][GUI_VAR_LIST[0]]
                    except:
                        MESS_warn_mess("Veuillez sélectionner un réponse")
                        continue
                else:
                    MESS_input_mess(["Le modèle de variogramme semble-t-il correct ?","","y : Oui","n : Non"])
                    inp = input()
                if inp == "y":
                    print(constraints)
                    correct = True
                    big_correct = True
                elif inp == "n":
                    correct = True
                else:
                    MESS_warn_mess("Réponse non reconnue !")
        else:
            try:
                inp_id = int(inp)
                type_choice[inp_id] = not type_choice[inp_id]
                if type_choice[inp_id]:
                    types_list.append(inp_id)
                    constr_list += CMD_variog_constraints(inp_id)
                else:
                    types_list.remove(inp_id)
                    new_l = []
                    for e in constr_list:
                        print(e," ",inp_id)
                        if e[0] != inp_id:
                            new_l.append(e)
                    constr_list = new_l
                print(constr_list)
            except KeyError:
                MESS_warn_mess("Réponse non reconnue !")
    print(fitmod)
    return fitmod
    
# Fait le choix des contraintes sur les modèles

def CMD_variog_constraints(var_id):
    
    _ConsElem_exist = [[0,0,0,1,0,0,0,0,0],[1,0,0,1,0,0,0,0,0],[1,0,0,1,0,0,0,0,0],[1,0,0,1,0,0,0,0,0],[1,0,0,1,0,0,0,0,0], # Pour chaque  modèle, sélectionne les contraintes existantes
                       [1,0,0,1,0,0,0,0,0],[1,0,1,1,0,0,0,0,0],[1,0,1,1,0,0,0,0,0],[1,0,1,1,0,0,0,0,0],[1,0,1,1,0,0,0,0,0], # 1 = oui, 0 = non.
                       [1,0,1,1,0,0,0,0,0],[0,0,0,1,0,0,0,0,0],[0,0,1,1,0,0,0,0,0],[0,0,0,1,0,0,0,0,0],[0,0,0,1,0,0,0,0,0],
                       [0,0,0,1,0,0,0,0,0],[0,0,0,1,0,0,0,0,0],[1,1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,1,1],[1,0,0,1,0,0,0,0,0],
                       [1,1,1,1,1,1,1,1,1],[1,0,0,1,0,0,0,0,0],[1,0,0,1,0,0,0,0,0],[1,1,1,1,1,1,1,1,1],[1,0,0,1,0,0,0,0,0],
                       [1,0,0,1,0,0,0,0,0],[1,0,0,1,0,0,0,0,0],[1,0,0,1,0,0,0,0,0],[1,0,0,1,0,0,0,0,0],[1,0,0,1,0,0,0,0,0],
                       [1,0,0,1,0,0,0,0,0]]
    _ConsElem_print = ["1 : RANGE", "2 : ANGLE (Anisotropy rotation angle (degree))", "3 : PARAM (Auxiliary parameter)", 
                       "4 : SILL", "5 : SCALE", "6 : T_RANGE (Tapering range)", "7 : VELOCITY (advection)", 
                       "8 : SPHEROT (Rotation angle for Sphere)", "9 : TENSOR (Anisotropy Matrix term)"]
    ConsElem_curr = _ConsElem_exist[var_id]
    dispo_list = ["Choix de la contrainte (variable)","","0 : Aucune (fin)"]
    for ic,c in enumerate(ConsElem_curr):
        if c:
            dispo_list.append(_ConsElem_print[ic])
    constr_list = []
    
    if GUI:
        correct = False
        while correct == False:
            MESS_input_GUI(dispo_list[:2]+["~r~ " +re.split(r" : ",d)[1] for d in dispo_list[3:]]+["","Choix de la contrainte (type)",
                            "~r~ LOWER (Lower Bound)", "~r~ DEFAULT (Default parameter)", "~r~ UPPER (Upper Bound)", "~r~ EQUAL (Equality) ~!~",
                            "","Entrez la valeur de la contrainte (flottant)","~t~","","~b~ Ajouter","~b~ Fin"])
            try:
                inp1, inp2, inp3, end= GUI_VAR_LIST
                if end:
                    correct = True
                    continue
                print(dispo_list)
                inp1 = int(re.split(r" : ",dispo_list[inp1+3])[0])
                inp2 = int(inp2)
                inp3 = float(inp3)
                print([var_id,inp1-1,inp2,inp3])
                constr_list.append([var_id,inp1-1,inp2,inp3])
            except:
                MESS_warn_mess("Certains champs sont invalides")
    else:
        correct = False
        while correct == False:
            MESS_input_mess(dispo_list)
            try:
                inp1 = int(input())
                if inp1 == 0:
                    correct = True
                elif not ConsElem_curr[inp1-1]:
                    MESS_warn_mess("La contrainte n'existe pas")
                else:
                    MESS_input_mess(["Choix de la contrainte (type)","","0 : LOWER (Lower Bound)", "1 : DEFAULT (Default parameter)", "2 : UPPER (Upper Bound)", "3 : EQUAL (Equality)"])
                    inp2 = int(input())
                    if inp2 < 0 or inp2 > 3:
                        MESS_warn_mess("Le type n'existe pas")
                    else:
                        MESS_input_mess(["Entrez la valeur de la contrainte (flottant)"])
                        inp3 = float(input())
                        constr_list.append([var_id,inp1-1,inp2,inp3])
            except:
                MESS_warn_mess("Réponse non reconnue !")
    
    return constr_list

# Affiche le résultat du kriging (ou de CMD_dat_to_grid sinon)

def CMD_grid_plot(don,grid_final,ncx,ncy,ext,pxy,nc_data,nb_ecarts,nb_res,output_file,sep,plot_pts=False,matrix=False):
    
    nb_data = len(nc_data)
    
    if output_file != None:
        pas_X = (ext[1]-ext[0])/pxy[0]
        pas_Y = (ext[3]-ext[2])/pxy[1]
        if matrix:
            grid_not_np = []
            for n in range(nb_data):
                grid_not_np.append(grid_final[n].T.round(CONFIG.prec_data).tolist())
            grid_save = {"grid" : grid_not_np, "ext" : ext, "pxy" : pxy, "step" : [pas_X,pas_Y],
                         "ncx" : ncx.to_list(), "ncy" : ncy.to_list(), "ncz" : nc_data.to_list()}
            with open(output_file, "w") as f:
                json.dump(grid_save, f, indent=None, cls=MyJSONEncoder)
        else:
            gridx = [ext[0] + pas_X*(i+0.5) for i in range(pxy[0])]
            gridy = [ext[2] + pas_Y*(j+0.5) for j in range(pxy[1])]
            try: # Cas de plusieurs voies
                int(ncx[0][-1])
                col_x = ""
                col_y = ""
                for e in range(nb_ecarts):
                    col_x += ncx[e]+"|"
                    col_y += ncy[e]+"|"
                col_x = col_x[:-1]
                col_y = col_y[:-1]
            except:
                col_x = ncx[0]
                col_y = ncy[0]
            don_f = pd.DataFrame({col_x: np.array([[j for j in gridy] for i in gridx]).round(CONFIG.prec_coos).flatten(),
                                  col_y: np.array([[i for j in gridy] for i in gridx]).round(CONFIG.prec_coos).flatten()})
            for n in range(nb_data):
                don_temp = pd.DataFrame({nc_data[n]: grid_final[n].flatten().round(CONFIG.prec_data)})
                don_f = pd.concat([don_f, don_temp], axis=1)
            don_f.to_csv(output_file, index=False, sep=sep)
    
    plt.style.use('_mpl-gallery-nogrid')
    for i in range(nb_ecarts):
        fig,ax = plt.subplots(nrows=1,ncols=nb_res,figsize=(nb_res*CONFIG.fig_width//2,CONFIG.fig_height),squeeze=False)
        
        for j in range(nb_res):
            Q_l = [z for z in grid_final[i*nb_res+j].flatten() if z == z]
            Q = np.quantile(Q_l,[0.05,0.95])
            ims = ax[0][j].imshow(grid_final[i*nb_res+j].T, origin='lower', cmap='cividis', vmin = Q[0], vmax=Q[1], extent=ext)
            ax[0][j].set_title(nc_data[i*nb_res+j])
            ax[0][j].set_xlabel(ncx[i])
            ax[0][j].set_ylabel(ncy[i])
            ax[0][j].set_aspect('equal')
            plt.colorbar(ims,ax=ax[0][j])
            if plot_pts:
                try:
                    ax[0][j].scatter(don[ncx[i]],don[ncy[i]],marker='s',c=don["Num fich"],s=5)
                except:
                    ax[0][j].scatter(don[ncx[i]],don[ncy[i]],marker='s',s=5)
        plt.show(block=False)
        plt.pause(0.25)
        plt.savefig(CONFIG.script_path+"Output/CMDEX_g_" +str(i)+'.png')
        pickle.dump(fig, open(CONFIG.script_path+"Output/CMDEX_g_" +str(i)+'.pickle', 'wb'))
    

# Change la date dans un fichier .dat

def DAT_change_date(file_list,date_str,sep,replace,output_file_list,not_in_file=False):
    if output_file_list != None and len(file_list) != len(output_file_list) and not replace:
        MESS_err_mess("Le nombre de fichiers entrée ({}) et sortie ({}) ne correspondent pas".format(len(file_list),len(output_file_list)))
    for ic, file in enumerate(file_list):
        try:
            df = pd.read_csv(file, sep=sep, dtype=object)
        except FileNotFoundError:
            MESS_err_mess('Le fichier "{}" est introuvable'.format(file))
        oc = re.split(r"/",date_str)
        
        if len(oc) != 3:
            MESS_err_mess("Le format de la date est invalide (mois/jour/année)")
        
        try:
            datetime.datetime(int(oc[2]), int(oc[0]), int(oc[1]))
        except ValueError:
            MESS_err_mess("La date n'est pas reconnue (mois/jour/année), problème de type ?")
            
        try:
            df["Date"]
        except KeyError:
            MESS_err_mess("Le fichier '{}' ne contient pas de colonne 'Date', le séparateur {} est-il correct ?".format(file,repr(sep)))
    
        for i, row in df.iterrows():
            df.at[i,'Date'] = date_str
            
        if not_in_file:
            return df
        
        if replace:
            df.to_csv(file, index=False, sep=sep)
        elif output_file_list == None:
            df.to_csv(file[:-4]+"_corr.dat", index=False, sep=sep)
        else:
            df.to_csv(output_file_list[ic], index=False, sep=sep)
 
# Retire le nom d'une colonne et décale le reste du jeu de données   

def DAT_pop_and_dec(file_list,colsup,sep,replace,output_file_list,not_in_file=False):
    if output_file_list != None and len(file_list) != len(output_file_list) and not replace:
        MESS_err_mess("Le nombre de fichiers entrée ({}) et sortie ({}) ne correspondent pas".format(len(file_list),len(output_file_list)))
    for ic, file in enumerate(file_list):
        try:
            df = pd.read_csv(file, sep=sep, dtype=object)
        except FileNotFoundError:
            MESS_err_mess('Le fichier "{}" est introuvable'.format(file))
        try:
            dec_ind = df.columns.get_loc(colsup)
        except KeyError:
            MESS_err_mess("Le fichier '{}' ne contient pas de colonne '{}', le séparateur {} est-il correct ?".format(file,colsup,repr(sep)))
        shift_df = pd.concat([df.iloc[:,:dec_ind],df.iloc[:,dec_ind:].shift(periods=1, axis="columns").iloc[:,1:]], axis = 1)
        
        if not_in_file:
            return shift_df
        
        if replace:
            shift_df.to_csv(file, index=False, sep=sep)
        elif output_file_list == None:
            shift_df.to_csv(file[:-4]+"_corr.dat", index=False, sep=sep)
        else:
            shift_df.to_csv(output_file_list[ic], index=False, sep=sep)

# Echange les données de deux colonnes (garde le même ordre) 

def DAT_switch_cols(file_list,col_a,col_b,sep,replace,output_file_list,not_in_file=False):
    if output_file_list != None and len(file_list) != len(output_file_list) and not replace:
        MESS_err_mess("Le nombre de fichiers entrée ({}) et sortie ({}) ne correspondent pas".format(len(file_list),len(output_file_list)))
    for ic, file in enumerate(file_list):
        try:
            df = pd.read_csv(file, sep=sep, dtype=object)
        except FileNotFoundError:
            MESS_err_mess('Le fichier "{}" est introuvable'.format(file))
        
        ind = df.columns.values
        try:
            data_a = df[col_a]
        except KeyError:
            MESS_err_mess("Le fichier '{}' ne contient pas de colonne '{}', le séparateur {} est-il correct ?".format(file,col_a,repr(sep)))
        try:
            data_b = df[col_b]
        except KeyError:
            MESS_err_mess("Le fichier '{}' ne contient pas de colonne '{}', le séparateur {} est-il correct ?".format(file,col_b,repr(sep)))

        df[col_a] = data_a
        df[col_b] = data_b
        df.columns = ind
        
        if not_in_file:
            return df
        
        if replace:
            df.to_csv(file, index=False, sep=sep)
        elif output_file_list == None:
            df.to_csv(file[:-4]+"_corr.dat", index=False, sep=sep)
        else:
            df.to_csv(output_file_list[ic], index=False, sep=sep)

# Retire les colonnes spécifiées des fichiers. On peut aussi, à l'inverse, préciser les colonnes à garder (en supprimant les autres).

def DAT_remove_cols(file_list,colsup_list,keep,sep,replace,output_file_list,not_in_file=False):
    if output_file_list != None and len(file_list) != len(output_file_list) and not replace:
        MESS_err_mess("Le nombre de fichiers entrée ({}) et sortie ({}) ne correspondent pas".format(len(file_list),len(output_file_list)))
    for ic, file in enumerate(file_list):
        try:
            df = pd.read_csv(file, sep=sep, dtype=object)
        except FileNotFoundError:
            MESS_err_mess('Le fichier "{}" est introuvable'.format(file))

        if keep:
            try:
                small_df = df.filter(colsup_list, axis=1)
            except KeyError:
                MESS_err_mess("Le fichier '{}' ne contient pas les colonnes {}, le séparateur {} est-il correct ?".format(file,colsup_list,repr(sep)))
        else:
            try:
                small_df = df.drop(colsup_list)
            except KeyError:
                MESS_err_mess("Le fichier '{}' ne contient pas les colonnes {}, le séparateur {} est-il correct ?".format(file,colsup_list,repr(sep)))
        
        if not_in_file:
            return small_df
        
        if replace:
            small_df.to_csv(file, index=False, sep=sep)
        elif output_file_list == None:
            small_df.to_csv(file[:-4]+"_corr.dat", index=False, sep=sep)
        else:
            small_df.to_csv(output_file_list[ic], index=False, sep=sep)

# Retire les données des lignes i_min à i_max dans les colonnes colsup. Utile si elles sont défectueuses, pour les détecter dans le traitement 

def DAT_remove_data(file_list,colsup_list,i_min,i_max,sep,replace,output_file_list,not_in_file=False):
    if output_file_list != None and len(file_list) != len(output_file_list) and not replace:
        MESS_err_mess("Le nombre de fichiers entrée ({}) et sortie ({}) ne correspondent pas".format(len(file_list),len(output_file_list)))
    for ic, file in enumerate(file_list):
        try:
            df = pd.read_csv(file, sep=sep, dtype=object)
        except FileNotFoundError:
            MESS_err_mess('Le fichier "{}" est introuvable'.format(file))
        
        try:
            col_list = df[colsup_list]
        except KeyError:
            MESS_err_mess("Le fichier '{}' ne contient pas les colonnes {}, le séparateur {} est-il correct ?".format(file,colsup_list,repr(sep)))

        for index, row in df[i_min-2:i_max-1].iterrows():
            for col in col_list:
                df.loc[index, col] = np.nan
        
        if not_in_file:
            return df
        
        if replace:
            df.to_csv(file, index=False, sep=sep)
        elif output_file_list == None:
            df.to_csv(file[:-4]+"_corr.dat", index=False, sep=sep)
        else:
            df.to_csv(output_file_list[ic], index=False, sep=sep)

# Permet d'afficher les valeurs extrêmes d'une colonne, pour potentiellement détecter des données à retirer

def DAT_min_max_col(file_list,col_list,n,sep):
    for ic, file in enumerate(file_list):
        try:
            df = pd.read_csv(file, sep=sep)
        except FileNotFoundError:
            MESS_err_mess('Le fichier "{}" est introuvable'.format(file))
        
        try:
            cl = df[col_list]
        except KeyError:
            MESS_err_mess("Le fichier '{}' ne contient pas les colonnes {}, le séparateur {} est-il correct ?".format(file,col_list,repr(sep)))
        
        print(warning_color+"<<< {} >>>".format(file))
        for c in cl:
            print(bold_color+"- {} -".format(c))
            print(und_color+"[MIN]"+base_color)
            print(df.nsmallest(n, c)[c])
            print(und_color+"[MAX]"+base_color)
            print(df.nlargest(n, c)[c])

# Trie les colonnes du .dat pour uniformiser la structure : X_int_1|X_int_2|Donnée1|Donnée2|...|Num fich|b et p|Base|Profil

def DAT_light_format(file_list,sep,replace,output_file_list,nb_ecarts,restr,not_in_file=False):
    if output_file_list != None and len(file_list) != len(output_file_list) and not replace:
        MESS_err_mess("Le nombre de fichiers entrée ({}) et sortie ({}) ne correspondent pas".format(len(file_list),len(output_file_list)))
    for ic, file in enumerate(file_list):
        try:
            df = pd.read_csv(file, sep=sep, dtype=object)
        except FileNotFoundError:
            MESS_err_mess('Le fichier "{}" est introuvable'.format(file))

        clean_df = pd.DataFrame()
        for e in range(nb_ecarts):
            try:
                ncx = "X_int_"+str(e+1)
                ncy = "Y_int_"+str(e+1)
                clean_df[ncx] = df[ncx]
                clean_df[ncy] = df[ncy]
                for c in df.columns:
                    if str(e+1) in c and c not in [ncx,ncy] and not any([r in c for r in restr]):
                        clean_df[c] = df[c]
            except KeyError:
                MESS_err_mess("Le fichier '{}' ne contient pas les bonnes colonnes, le séparateur {} est-il correct ?".format(file,repr(sep)))
        end_cols = ["Num fich","b et p","Base","Profil"]
        for c in end_cols:
            try:
                clean_df[c] = df[c]
            except KeyError:
                MESS_warn_mess("Le fichier '{}' ne contient pas la colonne {}".format(file,c))
        
        if not_in_file:
            return clean_df
        
        if replace:
            clean_df.to_csv(file, index=False, sep=sep)
        elif output_file_list == None:
            clean_df.to_csv(file[:-4]+"_clean.dat", index=False, sep=sep)
        else:
            clean_df.to_csv(output_file_list[ic], index=False, sep=sep)

# Change le séparateur du fichier

def DAT_change_sep(file_list,sep,new_sep,replace,output_file_list,not_in_file=False):
    if output_file_list != None and len(file_list) != len(output_file_list) and not replace:
        MESS_err_mess("Le nombre de fichiers entrée ({}) et sortie ({}) ne correspondent pas".format(len(file_list),len(output_file_list)))
    for ic, file in enumerate(file_list):
        try:
            df = pd.read_csv(file, sep=sep, dtype=object)
        except FileNotFoundError:
            MESS_err_mess('Le fichier "{}" est introuvable'.format(file))
        
        if len(df.columns) == 1:
            MESS_warn_mess('Le fichier "{}" ne possède pas le séparateur {} : cas ignoré'.format(file,repr(sep)))
            continue
        
        if not_in_file:
            return df
        
        if replace:
            df.to_csv(file, index=False, sep=new_sep)
        elif output_file_list == None:
            df.to_csv(file[:-4]+"_corr.dat", index=False, sep=new_sep)
        else:
            df.to_csv(output_file_list[ic], index=False, sep=new_sep)

# Dans le cas d'un duo de bases (avant et après prospection), les rassemble et les indice par rapport aux profils de la même parcelle

def DAT_fuse_bases(file_B1,file_B2,file_prof,sep,output_file,pair=True,not_in_file=False):
    try:
        B1 = TOOL_check_time_date(file_B1,sep)
    except FileNotFoundError:
        MESS_err_mess('Le fichier "{}" (base 1) est introuvable'.format(file_B1))
    try:
        B2 = TOOL_check_time_date(file_B2,sep)
    except FileNotFoundError:
        MESS_err_mess('Le fichier "{}" (base 2) est introuvable'.format(file_B2))
    try:
        prof = TOOL_check_time_date(file_prof,sep)
    except FileNotFoundError:
        MESS_err_mess('Le fichier "{}" (profils) est introuvable'.format(file_prof))

    try:
        B1["b et p"], B1["Base"], B2["b et p"], B2["Base"] = 0, 1, int(prof['b et p'].iat[-1])+1, 
    except KeyError:
        MESS_err_mess('Le fichier "{}" (profils) n'.format(file_prof)+"'est pas interpolé")
    base = pd.concat([B1[1::2],B2[1::2]])
    base.reset_index(drop=True,inplace=True)
    
    if not_in_file:
        return base
        
    if output_file == None:
        base.to_csv(file_prof[:-4]+"_B.dat", index=False, sep=sep)
    else:
        base.to_csv(output_file, index=False, sep=sep)

# Convertit le format dataframe en matrice

def TRANS_df_to_matrix(file,sep,output_file):
    try:
        df = pd.read_csv(file, sep=sep)
    except FileNotFoundError:
        MESS_err_mess('Le fichier "{}" est introuvable'.format(file))
    
    nc_data = df.columns
    if len(nc_data) <= 1:
        MESS_err_mess("Le fichier n'est pas lu correctement', le séparateur {} est-il correct ?".format(repr(sep)))
    try:
        ncx = nc_data[0]
        ncy = nc_data[1]
        nc_data = nc_data[2:]
        nb_data = len(nc_data)
    except KeyError:
        MESS_err_mess("Le fichier n'est pas lu correctement', le séparateur {} est-il correct ?".format(repr(sep)))
    
    grid_mat_row = [[] for n in range(nb_data)]
    grid_mat = [[] for n in range(nb_data)]
    curr_x = df.loc[0,ncx]
    for index, row in df.iterrows():
        if row[ncx] != curr_x:
            for n in range(nb_data):
                grid_mat[n].append(grid_mat_row[n])
            curr_x = row[ncx]
            grid_mat_row = [[] for n in range(nb_data)]
            
        for n in range(nb_data):
            grid_mat_row[n].append(row[nc_data[n]])
    for n in range(nb_data):
        grid_mat[n].append(grid_mat_row[n])
    
    last = len(df)-1
    pas_X = df.groupby(ncy)[ncx].apply(lambda x: x.diff().mean()).reset_index()[ncx].mean()
    pas_Y = df.groupby(ncx)[ncy].apply(lambda x: x.diff().mean()).reset_index()[ncy].mean()
    ext = [df.loc[0,ncx],df.loc[last,ncx],df.loc[0,ncy],df.loc[last,ncy]]
    pxy = [len(df[df[ncx] == ext[0]]),len(df[df[ncy] == ext[2]])]
    
    grid_mat_t = [[[np.nan for j in range(pxy[1])] for i in range(pxy[0])] for n in range(nb_data)]
    for n in range(nb_data): # Transposer
        for i in range(pxy[0]):
            for j in range(pxy[1]):
                grid_mat_t[n][i][j] = grid_mat[n][j][i]
    
    grid_save = {"grid" : grid_mat_t, "ext" : ext, "pxy" : pxy, "step" : [pas_X,pas_Y],
                 "ncx" : ncx.split("|"), "ncy" : ncy.split("|"), "ncz" : nc_data.to_list()}
    
    with open(output_file, "w") as f:
        json.dump(grid_save, f, indent=None, cls=MyJSONEncoder)

def TRANS_matrix_to_df(file,sep,output_file):
    try:
        with open(file, 'r') as f:
            grid_dict = json.load(f)
    except FileNotFoundError:
        MESS_err_mess('Le fichier "{}" est introuvable'.format(file))
    except json.JSONDecodeError:
        MESS_err_mess('Le fichier "{}" n\'est pas un .json'.format(file))
    
    nb_data = len(grid_dict["ncz"])
    nb_ecarts = len(grid_dict["ncx"])
    grid = np.array(grid_dict["grid"])
    ncx = ""
    ncy = ""
    for e in range(nb_ecarts):
        ncx += grid_dict["ncx"][e]+"|"
        ncy += grid_dict["ncy"][e]+"|"
    ncx = ncx[:-1]
    ncy = ncy[:-1]
    min_X = grid_dict["ext"][0]
    min_Y = grid_dict["ext"][2]
    pas_X = grid_dict["step"][0]
    pas_Y = grid_dict["step"][1]
    nc_data = grid_dict["ncz"]
    df = pd.DataFrame(columns=[ncx,ncy]+nc_data)
    
    for i in range(grid_dict["pxy"][0]):
        for j in range(grid_dict["pxy"][1]):
            row_data = {ncx : round(min_Y+pas_Y*j,CONFIG.prec_coos), ncy : round(min_X+pas_X*i,CONFIG.prec_coos)}
            for n in range(nb_data):
                row_data[nc_data[n]] = grid[n][i][j]
            r = i*grid_dict["pxy"][1] + j
            df.loc[r] = pd.Series(row_data)
    
    df.to_csv(output_file, index=False, sep=sep)

# Charge et affiche des figures en .pickle

def FIG_display_fig(file_list):
    os.chdir(CONFIG.script_path)
    if file_list == None:
        file_list = glob.glob("Output/*.pickle")
    for f in file_list:
        print(f)
        try:
            figx = pickle.load(open(f, 'rb'))
        except FileNotFoundError:
            try:
                figx = pickle.load(open('Output/'+f, 'rb'))
            except FileNotFoundError:
                MESS_err_mess('Le fichier "{}" est introuvable'.format(f))
        figx.show()
    keep_plt_for_cmd()

# Plot en nuage de pts

def FIG_plot_data(file,sep,col_x,col_y,col_z):
    try:
        df = pd.read_csv(file, sep=sep)
    except FileNotFoundError:
        MESS_err_mess('Le fichier "{}" est introuvable'.format(file))
    
    if len(df.columns) <= 1:
        MESS_err_mess("Le fichier n'est pas lu correctement', le séparateur {} est-il correct ?".format(repr(sep)))
    
    multi_col = False
    if col_x == None:
        col_x = [0]
    ncx = df.columns[col_x]
    ncx_t = df.columns[col_x]
    rx = ncx[0].split("|")
    if len(rx) != 1:
        ncx = rx
        multi_col = True
    if col_y == None:
        col_y = [1]
    ncy = df.columns[col_y]
    ncy_t = df.columns[col_y]
    ry = ncy[0].split("|")
    if len(ry) != 1:
        ncy = ry
        multi_col = True
    if col_z == None:
        col_z = df.columns.drop(ncx_t)
        col_z = col_z.drop(ncy_t)
    nc_data = col_z
    nb_data = len(nc_data)
    nb_ecarts = len(ncx)
    nb_res = nb_data//nb_ecarts
    
    for e in range(nb_ecarts):
        fig,ax=plt.subplots(nrows=1,ncols=nb_res,figsize=(nb_res*CONFIG.fig_width//2,CONFIG.fig_height))
        if multi_col:
            X = df[ncx_t]
            Y = df[ncy_t]
        else:
            X = df[ncx_t[e]]
            Y = df[ncy_t[e]]
        for r in range(nb_res):
            n = e*nb_res + r
            Z = df[nc_data[n]]
            Q5,Q95 = Z.dropna().quantile([0.05,0.95])
            col = ax[r].scatter(X,Y,marker='s',c=Z,cmap='cividis',s=6,vmin=Q5,vmax=Q95)
            plt.colorbar(col,ax=ax[r])
            ax[r].title.set_text(nc_data[n])
            ax[r].set_xlabel(ncx[e])
            ax[r].set_ylabel(ncy[e])
            ax[r].set_aspect('equal')
        plt.show(block=False)
        plt.pause(0.25)
        plt.savefig(CONFIG.script_path+"Output/FIG_" +str(e)+'.png')
        pickle.dump(fig, open(CONFIG.script_path+"Output/FIG_" +str(e)+'.pickle', 'wb'))
        
    keep_plt_for_cmd()

# Plot en grille

def FIG_plot_grid(file):
    try:
        with open(file, 'r') as f:
            grid_dict = json.load(f)
    except FileNotFoundError:
        MESS_err_mess('Le fichier "{}" est introuvable'.format(file))
    except json.JSONDecodeError:
        MESS_err_mess('Le fichier "{}" n\'est pas un .json'.format(file))
    
    nb_ecarts = len(grid_dict["ncx"])
    nb_res = len(grid_dict["ncz"])//nb_ecarts
    grid = np.array([])
    #print(grid_dict["grid"][5])
    grid = np.array(grid_dict["grid"])
    
    plt.style.use('_mpl-gallery-nogrid')
    for e in range(nb_ecarts):
        fig,ax = plt.subplots(nrows=1,ncols=nb_res,figsize=(nb_res*CONFIG.fig_width//2,CONFIG.fig_height),squeeze=False)
        
        for r in range(nb_res):
            n = e*nb_res+r
            Q_l = [z for z in grid[n].flatten() if z == z]
            Q = np.quantile(Q_l,[0.05,0.95])
            ims = ax[0][r].imshow(grid[n], origin='lower', cmap='cividis', vmin = Q[0], vmax=Q[1], extent=grid_dict["ext"])
            ax[0][r].set_title(grid_dict["ncz"][n])
            ax[0][r].set_xlabel(grid_dict["ncx"][e])
            ax[0][r].set_ylabel(grid_dict["ncy"][e])
            ax[0][r].set_aspect('equal')
            plt.colorbar(ims,ax=ax[0][r])
        plt.show(block=False)
        plt.pause(0.25)
        plt.savefig(CONFIG.script_path+"Output/FIG_" +str(e)+'.png')
        pickle.dump(fig, open(CONFIG.script_path+"Output/FIG_" +str(e)+'.pickle', 'wb'))
        
    keep_plt_for_cmd()

# ajoute un nouvel appareil à la base en JSON

def JSON_add_device(app_name,config,nb_ecarts,TxRx,freq_list,gps,gps_dec,height,bucking_coil,coeff_construct,config_angles=None,autosave=False):
    
    app_list = {}
    with open(CONFIG.json_path+"Appareil.json", 'r') as f:
        app_list = json.load(f)
    
    ### À DÉCOMMENTER POUR RÉINITIALISER LE FICHIER ###
    # app_list ={
    #     "app_list": []
    #    }
    
    config_list = ["HCP","VCP","PRP_CS","PRP_DEM","PAR","CUS"]
    if config not in config_list:
        MESS_err_mess("La configuration choisie est inconnue ({})".format(config_list))
    if len(TxRx) != nb_ecarts:
        MESS_err_mess("Le nombre de positions ({}) n'est pas égal au nombre de bobines ({})".format(len(TxRx),nb_ecarts))
    
    new_app = {}
    new_app["app_id"] = len(app_list["app_list"])
    new_app["app_name"] = app_name
    new_app["config"] = config
    if config == "CUS":
        if config_angles == None:
            MESS_err_mess("La configuration CUS n'est pas spécifiée")
        if len(config_angles) != nb_ecarts:
            MESS_err_mess("La configuration CUS (de taille {}) doit être de taille {}".format(len(gps_dec),nb_ecarts))
        new_app["config_angles"] = config_angles
    new_app["GPS"] = gps
    if gps_dec != None:
        if len(gps_dec) != 2:
            MESS_err_mess("Le décalage GPS (de taille {}) doit être de taille 2".format(len(gps_dec)))
        new_app["GPS_dec"] = gps_dec
    new_app["nb_ecarts"] = nb_ecarts
    new_app["TxRx"] = TxRx
    new_app["height"] = height
    new_app["freq_list"] = freq_list
    new_app["bucking_coil"] = bucking_coil
    new_app["coeff_construct"] = coeff_construct
    
    # INSÉRER FONCTION FORTRAN #
    # os.system
    
    new_app["coeff_calc"] = 0 
    
    for app in app_list["app_list"]:
        if {i:new_app[i] for i in new_app if i!='app_id'} == {i:app[i] for i in app if i!='app_id'}:
            MESS_warn_mess("Appareil ({}, {}) déjà ajouté.".format(app_name,config))
            return new_app
    if autosave:
        app_list["app_list"].append(new_app)
    else:
        correct = False
        while correct == False:
            if GUI:
                MESS_input_GUI(["Voulez-vous sauvegarder la configuration dans la base ?","","~b~ Oui","~b~ Non"])
                try:
                    inp = ["y","n"][GUI_VAR_LIST[0]]
                except:
                    MESS_warn_mess("Veuillez sélectionner un réponse")
                    continue
            else:
                MESS_input_mess(["Voulez-vous sauvegarder la configuration ?","","y : Oui (mise à jour du JSON)","n : Non (continuer sans sauvegarder)"])
                inp = input()
                if inp == "n":
                    correct = True
                elif inp == "y":
                    app_list["app_list"].append(new_app)
                    correct = True
                else:
                    MESS_warn_mess("Réponse non reconnue !")
        
    with open(CONFIG.json_path+"Appareil.json", "w") as f:
        json.dump(app_list, f, indent=2)
        
# Récupère la valeur des paramètres de l'appareil dans le JSON à partir de l'uid.
# Stoppe l'exécution si il n'existe pas.

def JSON_find_device(uid):
    
    app_list = {}
    with open(CONFIG.json_path+"Appareil.json", 'r') as f:
        app_list = json.load(f)
    
    nc = os.get_terminal_size().columns
    for app in app_list["app_list"]:
        if app["app_id"] == uid:
            JSON_print_device_selected(app,nc)
            print(success_color+"-"*nc)
            print(base_color)
            return app
    
    MESS_err_mess("L'appareil sélectionné n'existe pas dans la base locale")

# Supprime un appareil de la base

def JSON_remove_device(uid):
    
    app_list = {}
    with open(CONFIG.json_path+"Appareil.json", 'r') as f:
        app_list = json.load(f)
    try:
        del app_list["app_list"][uid]
    except IndexError:
        MESS_err_mess("L'appareil sélectionné (uid = {}) n'existe pas dans la base locale".format(uid))
    
    for ic, app in enumerate(app_list["app_list"]):
        app["app_id"] = ic
    
    with open(CONFIG.json_path+"Appareil.json", "w") as f:
        json.dump(app_list, f, indent=2)

# Affiche les appareils déjà enregistrés.
# La première envoie les infos à afficher à la seconde.

def JSON_print_devices(uid=None):
    
    app_list = {}
    with open(CONFIG.json_path+"Appareil.json", 'r') as f:
        app_list = json.load(f)
    
    print("")
    nc = os.get_terminal_size().columns
    if uid == None:
        for app in app_list["app_list"]:
            JSON_print_device_selected(app,nc)
    else:
        JSON_print_device_selected(next(app for app in app_list["app_list"] if app["app_id"] == uid),nc)
    
    print(success_color+"-"*nc)
    print(base_color)

# Affiche dans le terminal les informations relatives à un/tous les appareils de la base.

def JSON_print_device_selected(app,nc):
    
    print(success_color+"-"*nc)
    print(type_color+"{} : ".format(app["app_id"])+title_color+"{} ({})".format(app["app_name"],app["config"]))
    print(success_low_color+"\tGPS : "+base_color+"{}".format(app["GPS"]))
    print(success_low_color+"\tNb T/R : "+base_color+"{}, ".format(app["nb_ecarts"])+success_low_color+"pos : "+base_color+"{}".format(app["TxRx"]))
    print(success_low_color+"\tz : "+base_color+"{}, ".format(app["height"])+success_low_color+"frequences : "+base_color+"{}".format(app["freq_list"]))
        

# Récupère les constantes associées à l'appareil.
# Les créent si elles n'existent pas.

def JSON_add_coeff(config,TxRx,height,freq_list):
    
    const_list = {}
    with open(CONFIG.json_path+"Constantes.json", 'r') as f:
       const_list = json.load(f)
    
    ### À DÉCOMMENTER POUR RÉINITIALISER LE FICHIER ###
    #const_list ={}
    
    new_const = {}
    new_const["config"] = [[config, {}]]
    new_const["config"][0][1]["TxRx"] = [[TxRx, {}]]
    new_const["config"][0][1]["TxRx"][0][1]["height"] = [[height, {}]]
    new_const["config"][0][1]["TxRx"][0][1]["height"][0][1]["freq_list"] = [[freq_list, {}]]
    
    # INSÉRER FONCTION FORTRAN #
    #os.system

    # new_const["config"][1]["TxRx"][1]["height"][1]["freq_list"][1] = fortran.coeffs()
    
    new_const["config"][0][1]["TxRx"][0][1]["height"][0][1]["freq_list"][0][1] = {"sigma_a_ph": [[0,0,0,0],[0,0,0,0],[0,0,0,0]],
                                                                     "Kph_a_ph": [0,0,0],
                                                                     "sigma_a_qu": [0,0,0],
                                                                     "Kph_a_qu": 0 }
    
    
    try:
        ic1 = [e[0] for e in const_list["config"]].index(new_const["config"][0][0])
        #print("(1)", [e[0] for e in const_list["config"]])
        new_const_part = new_const["config"][0][1]
        const_list_part = const_list["config"][ic1][1]
        try:
            ic2 = [e[0] for e in const_list_part["TxRx"]].index(new_const_part["TxRx"][0][0])
            #print("(2)", [e[0] for e in const_list_part["TxRx"]])
            new_const_part = new_const_part["TxRx"][0][1]
            const_list_part = const_list_part["TxRx"][ic2][1]
            try:
                ic3 = [e[0] for e in const_list_part["height"]].index(new_const_part["height"][0][0])
                #print("(3)", [e[0] for e in const_list_part["height"]])
                new_const_part = new_const_part["height"][0][1]
                const_list_part = const_list_part["height"][ic3][1]
                try:
                    ic4 = [e[0] for e in const_list_part["freq_list"]].index(new_const_part["freq_list"][0][0])
                    #print("(4)", [e[0] for e in const_list_part["freq_list"]])
                    new_const_part = new_const_part["freq_list"][0][1]
                    const_list_part = const_list_part["freq_list"][ic4][1]
                    MESS_warn_mess("Résultat ({}, {}) déjà ajouté".format(config,TxRx))
                except ValueError:
                    const_list["config"][ic1][1]["TxRx"][ic2][1]["height"][ic3][1]["freq_list"].append(new_const_part["freq_list"])
                    const_list["config"][ic1][1]["TxRx"][ic2][1]["height"][ic3][1]["freq_list"] = sorted(const_list["config"][ic1][1]["TxRx"][ic2][1]["height"][ic3][1]["freq_list"], key=lambda x: x[0])
            except ValueError:
                const_list["config"][ic1][1]["TxRx"][ic2][1]["height"].append(new_const_part["height"][0])
                const_list["config"][ic1][1]["TxRx"][ic2][1]["height"] = sorted(const_list["config"][ic1][1]["TxRx"][ic2][1]["height"], key=lambda x: float(x[0]))
        except ValueError:
            const_list["config"][ic1][1]["TxRx"].append(new_const_part["TxRx"][0])
            const_list["config"][ic1][1]["TxRx"] = sorted(const_list["config"][ic1][1]["TxRx"], key=lambda x: x[0])
    except ValueError:
        const_list["config"].append(new_const["config"][0])
        const_list["config"] = sorted(const_list["config"], key=lambda x: x[0])
    except KeyError or IndexError:
        MESS_warn_mess("Base de résultat réinitialisée")
        const_list = new_const
    # except:
    #     MESS_err_mess("Une erreur inconnue s'est produite (JSON_add_coeff)")
           
    # remise à un format plus lisible
    dict_const = {}
    dict_const["config"] = new_const["config"][0][0]
    dict_const["TxRx"] = new_const["config"][0][1]["TxRx"][0][0]
    dict_const["height"] = new_const["config"][0][1]["TxRx"][0][1]["height"][0][0]
    dict_const["freq_list"] = new_const["config"][0][1]["TxRx"][0][1]["height"][0][1]["freq_list"][0][0]
    dict_const["sigma_a_ph"] = new_const["config"][0][1]["TxRx"][0][1]["height"][0][1]["freq_list"][0][1]["sigma_a_ph"]
    dict_const["Kph_a_ph"] = new_const["config"][0][1]["TxRx"][0][1]["height"][0][1]["freq_list"][0][1]["Kph_a_ph"]
    dict_const["sigma_a_qu"] = new_const["config"][0][1]["TxRx"][0][1]["height"][0][1]["freq_list"][0][1]["sigma_a_qu"]
    dict_const["Kph_a_qu"] = new_const["config"][0][1]["TxRx"][0][1]["height"][0][1]["freq_list"][0][1]["Kph_a_qu"]    
        
    with open(CONFIG.json_path+"Constantes.json", "w") as f:
        json.dump(const_list, f, indent=None, cls=MyJSONEncoder)
    
    #print(dict_const)
    return dict_const






