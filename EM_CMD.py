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
import platform
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import linregress
import scipy.interpolate as scii
import gstlearn as gl
import gstlearn.plot as gp
from sklearn.linear_model import (HuberRegressor,TheilSenRegressor)
from sklearn.metrics import mean_squared_error
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures
import random
import re
import datetime
import json
import pickle
import tkinter as tk
from IPython import get_ipython
import warnings

import CONFIG
import grd

# plt.rcParams['figure.subplot.left'] = 0.086
# plt.rcParams['figure.subplot.right'] = 0.97
# plt.rcParams['figure.subplot.bottom'] = 0.086
# plt.rcParams['figure.subplot.top'] = 0.97
# print(matplotlib.matplotlib_fname())

# --- Constantes de DEV (à ne pas toucher pour conserver l'expérience originale) ---

GUI = CONFIG.ui_popups_from_cmd # Si on utilise l'interface graphique
FROM_GI_PY = False
GUI_VAR_LIST = []
OS_KERNEL = platform.system()
"""
OS_KERNEL : str, {``"Windows``, ``Linux``, ``Darwin``, ``Java``"}
"""

# Détecte si le programme est lancé depuis Spyder

def is_from_spyder():
    """ [TA]\n
    Detect whether the execution is launcher from the Spyder IPython shell.\n
    Result is saved in the 'spyder' global variable.

    Returns
    -------
    spyder : bool
    """
    return get_ipython().__class__.__name__ == 'SpyderShell'

spyder = is_from_spyder()

# Attend une réponse utilisateur si l'exécution provient du cmd (matplotlib est fermé automatiquement sinon)

def keep_plt_for_cmd():
    """ [TA]\n
    If the execution is launch from the cmd prompt, wait for a user input before terminating.\n
    Useful to keep matplotlib figures open.
    """
    if not spyder and not FROM_GI_PY:
        input()

if CONFIG.no_warnings:
    warnings.filterwarnings("ignore")

# Termine l'exécution et revient dans le dossier de départ

def shutdown(v):
    """ [TA]\n
    Terminate the execution with a specified exit code.\n
    For shell purpose, reset the work directory to the script path.

    Parameters
    ----------
    v : int
        Exit code.
    """
    os.chdir(CONFIG.script_path)
    if spyder:
        warnings.filterwarnings("ignore")
        sys.exit(v)
    else:
        sys.exit(v)

# Couleurs de terminal. Elles sont persistantes entre les prints donc il faut revenir sur base_color
# si on veut annuler la modification de l'affichage.
# Documentation disponible avec la commande "man dir colors".

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
if spyder:
    code_color = '\33[0;1;34m'
    success_color = '\33[0;1;32m'
    success_low_color = '\33[0;1;36m'
else:
    code_color = '\33[0;1;36m'
    success_color = '\33[0;1;92m'
    success_low_color = '\33[0;92m'
title_color = '\33[0;1;4;33m' 
title_next_color = '\33[0;33m' 
type_color = '\33[35m'
#true_color = '\33[0;1;32m'

# change l'indentation lors du passage en format .JSON

class MyJSONEncoder(json.JSONEncoder):
    """ [TA]\n
    Modify the JSON indent rule for readability (`Constantes.json`).
    """
    def iterencode(self, o, _one_shot=False):
        dict_lvl = 0
        list_lvl = 0
        for s in super(MyJSONEncoder, self).iterencode(o, _one_shot=_one_shot):
            if s.startswith('{'):
                dict_lvl += 1
                s = s.replace('{', '{\n'+dict_lvl*"  ")
            elif s.startswith('}'):
                dict_lvl -= 1
                s = s.replace('}', '\n'+dict_lvl*"  "+'}')
            elif s.startswith('['):
                list_lvl += 1
            elif s.startswith(']'):
                list_lvl -= 1
            elif s.startswith(',') and list_lvl == 8:
                s = s.replace(',', ',\n'+dict_lvl*"  ")
            yield s

# Message d'erreur

def MESS_err_mess(mess):
    """ [TA]\n
    Print message in a specific 'error' format.\n
    Terminate the execution.

    Parameters
    ----------
    mess : str
        Message to display.
    """
    l = len(mess)
    print(error_color)
    print("  ^  "+l*" "+"  ^  ")
    print(" /!\\ "+mess+" /!\\ ")
    print("·---·"+l*" "+"·---·")
    print(base_color)
    shutdown(1)

# Message d'avertissement

def MESS_warn_mess(mess):
    """ [TA]\n
    Print message in a specific 'warning' format.

    Parameters
    ----------
    mess : str
        Message to display.
    """ 
    l = len(mess)
    print(warning_color)
    print("  ^  "+l*" "+"  ^  ")
    print(" |?| "+mess+" |?| ")
    print("  v  "+l*" "+"  v  ")
    print(base_color)

# Message de succès

def MESS_succ_mess(mess):
    """ [TA]\n
    Print message in a specific 'success' format.

    Parameters
    ----------
    mess : str
        Message to display.
    """ 
    l = len(mess)
    print(success_color)
    print("\\    "+l*" "+" \\   ")
    print(" \\ / "+mess+"  \\ /")
    print("  V  "+l*" "+"   V ")
    print(base_color)

# Message pour intervention utilisateur

def MESS_input_mess(mess_list):
    """ [TA]\n
    Print message in a specific 'user input' format.
    Is meant to be used before the ``input()`` function and if the ``GUI`` global variable is set to ``False``.

    Parameters
    ----------
    mess_list : list of str
        Message to display, row per row.
    """ 
    nc = os.get_terminal_size().columns - 1
    print(code_color+blink_color)
    print("+---"*(nc//4)+"+")
    print(code_color)
    for mess in mess_list:
        print(mess)
    print(code_color+blink_color)
    print("+---"*(nc//4)+"+")
    print(base_color)

# Boîte de dialogue tkinter pour intervention utilisateur (GUI)

def MESS_input_GUI(mess_list):
    """ [TA]\n
    Display message in a separate tkinter dialog box.\n
    Is meant to be used if the ``GUI`` global variable is set to ``True``.\n
    If no custom button is added, is closed with a ``"Valider"`` button.
    
    Notes
    -----
    List of key strings :\n
    * ``'~t~'`` : Create a tkinter entry widget with a str parameter.
        'Entry' is a line of text.
    * ``'~c~'`` : Create a tkinter checkbutton widget with a int parameter (value of 0 or 1).
        Checkbuttons are always set to ``False`` by default
    * ``'~r~'`` + string : Create a tkinter radiobutton widget with a int parameter.
        Successive radiobuttons are connected.
        If the following string end with ``'~!~'``, the current radiobutton is selected by default.
        Returns the selected radiobutton index (0 is first).\n
    * ``'~b~'`` + string : Create a tkinter button widget with a int parameter.
        Returns the selected radiobutton index (0 is first), and close the window.
    
    Parameters
    ----------
    mess_list : list of str
        Message to display, row per row. Also include key strings.
    """ 
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
        for ic,b in enumerate(s_b_list):
            pos = sum(s_b_label_list[:ic])+(dim_width//20)*(ic) - total_l//2
            canvas.create_window( dim_width//2 + pos,dim_height-60, anchor = "nw",window = b)
    else:
        bs = tk.Button(root, text = 'Valider', font=('Terminal', font_s_t, 'bold'), compound="center", command=on_submit_button_pressed)
        canvas.create_window( dim_width//2-70,dim_height-60, anchor = "nw",window = bs)
        
    root.mainloop() 

# Retire les caractères indésirables des strings.

def TOOL_str_clean(dirty_str,l=False,path=False):
    """ [TA]\n
    Remove unwanted characters from string.
    Is used on function call arguments.
    
    Notes
    -----
    Filters ``'[', ']', ' ', '"'`` and ``'''``.
    
    Parameters
    ----------
    dirty_str : str
        String to filter
    ``[opt]`` l : bool, default : ``False``
        If we keep brackets (mainly for column names)
    ``[opt]`` path : bool, default : ``False``
        If we keep spaces (mainly for file paths)
    
    Returns
    -------
    dirty_str : str
        Output str after cleaning process.
    
    See Also
    --------
    ``TOOL_optargs_list, TOOL_split_list``
    """ 
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
    """ [TA]\n
    Split a list string to list of elements from a specified type.
    
    Parameters
    ----------
    list_string : str
        String to split.
    list_type : data-type
        Type of output list.
    ``[opt]`` path : bool, default : ``False``
        If we keep spaces.
    ``[opt]`` noclean : bool, default : ``False``
        If we do not filter the splitted strings.
    
    Returns
    -------
    l : list of type ``list_type``
        Output list.
    
    See Also
    --------
    ``TOOL_optargs_list, TOOL_str_clean, TOOL_str_to_bool``
    """ 
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
    """ [TA]\n
    Associate each optional argument with the correct value (if specified).
    
    Parameters
    ----------
    list_args : list of str
        List of all optional arguments specified by user.
    list_args_name : list of str
        List of all existing optional arguments names of the selected function.
    list_args_type : list of data-type
        List of all existing optional arguments types of the selected function.
    
    Returns
    -------
    l : dict of [``arg_name : arg_value``]
        Dictionary of every specified argument and their value.
    
    Notes
    -----
    All arguments should be written as such : ``[arg_name]=[arg_value]``.\n
    Variable names in '``occurs[0] in [values]``' line are hardcoded path variable names.
    They are processed differently from the others in order to keep their path structure.
    If a new path variable name is to be added, it should be indicated in theses statements.\n
    ``GraphicUI``, ``GraphicUIn't`` and ``GraphicUI_ignore`` are special keywords related to ``GraphicInterface.py``.
    
    Raises
    ------
    * Parameter does not exist.
    * Parameter does not have any value.
    * Parameter is of a wrong type.
    
    See Also
    --------
    ``TOOL_split_list, TOOL_str_clean, TOOL_str_to_bool``
    """ 
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
                if occurs[0] in ["file_list","file_list_rev","cfg_file_list"]:
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
        except IndexError:
            MESS_err_mess("Le paramètre optionnel '{}' n'a pas de valeur associé".format(occurs[0]))
    print(dict_args)
    return dict_args

# Convertis un string en bool (de manière acceptable).

def TOOL_str_to_bool(bool_str):
    """ [TA]\n
    Convert 'bool' str to bool.
    
    Parameters
    ----------
    bool_str : str
        String to convert.
    
    Returns
    -------
    bool
        ``True`` if ``bool_str = "True", "true", "T", "t", "1"``.\n
        ``False`` if ``bool_str = "False", "false", "F", "f", "0"``.
    
    Notes
    -----
    Any other value returns 'False' but raises a warning.
    
    See Also
    --------
    ``TOOL_str_clean``
    """ 
    if TOOL_str_clean(bool_str).lower() in ["true","t","1"]:
        return True
    elif TOOL_str_clean(bool_str).lower() not in ["false","f","0"]:
        MESS_warn_mess('La valeur "{}"'.format(bool_str)+" n'est pas reconnue, considérée comme False.")
    return False

# Gère le cas où les fichier ne sont pas spécifiés

def TOOL_true_file_list(file_list=None):
    """ [TA]\n
    Return the file list path of 'file_list'.
    If no path is specified (``None``), return the list of every .dat files in the current working directory (``CONFIG.script_path``).
    
    Parameters
    ----------
    ``[opt]`` file_list : ``None`` or list of str, default : ``None``
        List of path, or None.
    
    Returns
    -------
    ls_nomfich : list of str
        List of path of active files.
    """ 
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
    """ [TA]\n
    Obtain meaningful informations from active columns of the ``don`` dataframe.
    
    Parameters
    ----------
    don : dataframe
        Active dataframe.
    col_x : list of int
        Index of every X coordinates columns.
    col_y : list of int
        Index of every Y coordinates columns.
    col_z : list of int
        Index of every Z coordinates columns (actual data).
    
    Returns
    -------
    ncx : list of str
        Names of every X columns.
    ncy : list of str
        Names of every Y columns.
    col_T : list of str
        Names of every Z columns (actual data).
    nb_data : int
        Number of Z columns. The number of data.
    nb_ecarts : int
        Number of X and Y columns. The number of coils.
    nb_res : int
        The number of data per coil.
    
    Raises
    ------
    * The numbers of X and Y columns are not the same.
    * The numbers of Z columns are not multiple of the number of X/Y columns.
    """ 
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
    """ [TA]\n
    Load dataframe from file.\n
    Detect and remove ``"Time"`` or ``"Date"`` column labels that are empty.\n
    Convert dataframe to numeric (if possible).
    
    Parameters
    ----------
    f : str
        File name or path to load.
    ``[opt]`` sep : str, default : ``'\\t'``
        Dataframe separator.
    
    Returns
    -------
    data : dataframe
        Output dataframe.
    
    Notes
    -----
    If such column is detected, raises a warning and delete it.
    
    Raises
    ------
    * File not found.
    * Wrong separator.
    
    See Also
    --------
    ``DAT_pop_and_dec``
    """ 
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
        TR_l=np.array((0.32,0.71,1.18))
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
        TR_l=np.array((0.2,0.33,0.5,0.72,1.03,1.5))
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
        TR_l=np.array((1.5,2.4,4.6))
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
    
    return (TR_l,cond2ppt,ppmcubcond,cond2ph,ppt2ppm,ppm2Kph)

def CMD_init(uid,file_list=None,sep='\t',sup_na=True,regr=False,corr_base=True,not_in_file=False):
    """ [TA]\n
    Apply to dataframe the first steps of CMD processing.\n
    1) Time correction, if GPS.\n
    2) Profile / base detection.\n
    3) Coordinates interpolation.\n
    4) ``[opt]`` ``NaN`` completion and profile linearization.\n
    5) Coil / GPS offsets.
    
    Parameters
    ----------
    uid : int
        Device's ``"app_id"`` value.
    ``[opt]`` file_list : ``None`` or list of str, default : ``None``
        List of files to process.
    ``[opt]`` sep : str, default : ``'\\t'``
        Dataframe separator.
    ``[opt]`` sup_na : bool, default : ``True``
        If ``NaN`` completion is done.
    ``[opt]`` regr : bool, default : ``False``
        If profile linearization is done.
    ``[opt]`` corr_base : bool, default : ``True``
        If base correction is done.
    ``[opt]`` not_in_file : bool, default : ``False``
        If call comes from script function instead of user.
    
    Returns
    -------
    * ``not_in_file = False``
        none, but save dataframe for profiles and bases in separated .dat
    * ``not_in_file = True``
        don_base : dataframe
            Dataframe of all bases
        don_mes : dataframe
            Dataframe of all profiles
        ls_base : list of dataframe
            List of bases for each file
        ls_mes : list of dataframe
            List of profiles for each file
        ncx : list of str
            Names of every X columns.
        ncy : list of str
            Names of every Y columns.
        nc_data : list of str
            Names of every Z columns (actual data).
        nb_res : int
            The number of data per coil.
        ls_pd_done_before : list of dataframe
            List of all dataframe that were already processed by a previous function call.
    
    Notes
    -----
    This function ignores any dataframe that was already processed by a previous function call.\n
    Can plot data.
    
    See Also
    --------
    ``TOOL_check_time_date, CMD_time, CMD_detect_chgt, CMD_intrp_prof, CMD_detect_base_pos, CMD_detec_profil_carre,
    CMD_XY_Nan_completion, CMD_sep_BM, CMD_pts_rectif, CMD_evol_profils, CMD_dec_voies``
    """ 
    file_list = TOOL_true_file_list(file_list)
    app_data = JSON_find_device(uid)
    
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
    
    nb_f = len(ls_pd)
    nb_res = 2
    const_GPS = 2
    if app_data["GPS"] :
        n_col_X='Easting'
        n_col_Y='Northing'
    else :
        n_col_X='x[m]'
        n_col_Y='y[m]'
    if nb_f == 0:
        cdata = ls_pd_done_before[0]
    else:
        cdata = ls_pd[0]
    for c in ["Altitude","Date","Time","DOP","Satelites"]:
        try:
            cdata[c]
            const_GPS += 1
        except KeyError:
            pass
    
    ls_base = []
    ls_mes = []
    col_z=[const_GPS+i for i in range(app_data["nb_ecarts"]*nb_res)]
    ncx = ["X_int_"+str(e+1) for e in range(app_data["nb_ecarts"])]
    ncy = ["Y_int_"+str(e+1) for e in range(app_data["nb_ecarts"])]
    
    for ic,don_c in enumerate(ls_pd) :
        print("Fichier de données n°{} : '{}'".format(ic+1,file_list[ic]))
      
    if nb_f != 0:
        don_raw = pd.concat(ls_pd)
        don_raw.index=np.arange(don_raw.shape[0])

        # Si le fichier contient des données temporelles
        try:
            # On gère les prospections faites des jours différents
            don_raw['temps (s)']=CMD_time(don_raw)
            for ic,date_c in enumerate(don_raw['Date'].unique()) :
                if ic>0 :
                    ind_d =don_raw.index[don_raw['Date']==date_c]
                    don_raw.loc[ind_d,'temps (s)']=don_raw.loc[ind_d,'temps (s)']+ic*86400
        except KeyError:
            pass
        if app_data["GPS"]:
            don_d=CMD_detect_chgt(don_raw)
            #MESS_warn_mess("uno")
            don_i=CMD_intrp_prof(don_d,acq_GPS=app_data["GPS"])
            #MESS_warn_mess("dos")
            don_i=CMD_detect_base_pos(don_i,2)
            #MESS_warn_mess("tres")
        else:
            don_raw["X_int"] = don_raw.iloc[:,0]
            don_raw["Y_int"] = don_raw.iloc[:,1]
            don_i = CMD_detec_profil_carre(don_raw)
            
        if sup_na:
            don_i.dropna(subset = [n_col_X,n_col_Y,"X_int","Y_int"],inplace=True)
            don_i.reset_index(drop=True,inplace=True)
        else:
            if max(don_i["Profil"]) == 1:
                don_i = CMD_XY_Nan_completion_solo(don_i)
            else:
                don_i = CMD_XY_Nan_completion(don_i)
        if max(don_i["Profil"]) == 1:
            don_i = CMD_detec_pseudoprof(don_i,"X_int","Y_int",l_p=None,verif=True)
            correct = False
            while correct == False:
                if GUI:
                    MESS_input_GUI(["La détection de profils est-elle correcte ?","","~r~ Oui","~r~ Tenter sans donner de segments (option de base)"
                                     "Sinon rentrer les coordonnées des points formant les segments passant par les centres des profils",
                                     "Exemple : 50,20 82.5,0 100,-15 crée deux segments","~t~"])
                    try:
                        fin, inp = GUI_VAR_LIST
                        if inp == "":
                            inp = ["y","n"][fin]
                    except:
                        MESS_warn_mess("Veuillez sélectionner un réponse")
                        continue
                else:
                    MESS_input_mess(["La détection de profils est-elle correcte ?","","y : Oui","n : Tenter sans donner de segments (option de base)"
                                     "Sinon rentrer les coordonnées des points formant les segments passant par les centres des profils",
                                     "Exemple : 50,20 82.5,0 100,-15 crée deux segments"])
                    inp = input()
                try:
                    if inp == "y":
                        correct = True
                    elif inp == "n":
                        don_i = CMD_detec_pseudoprof(don_i,"X_int","Y_int",l_p=None,verif=True)
                    else:
                        pts = re.split(r"[ ]+",inp)
                        vect = [[int(c) for c in re.split(r",",pt)] for pt in pts]
                        if len(vect) < 2:
                            MESS_warn_mess("Choisir au moins deux points !")
                        else:
                            don_i = CMD_detec_pseudoprof(don_i,"X_int","Y_int",l_p=vect,verif=True)
                except:
                    MESS_warn_mess("Réponse non reconnue !")
            plt.close('all')
        don_base,don_mes=CMD_sep_BM(don_i)
        nc_data = don_raw.columns[col_z]
        if not don_base.empty:
            d_nf,d_bp,d_t,d_min = CMD_synthBase(don_base,nc_data,CMDmini=(max(app_data["TR"])<2))
            don_base = d_min.transpose()
            don_base["Num fich"] = d_nf
            don_base["temps (s)"] = d_t
            don_base["b et p"] = d_bp
            don_base["Base"] = d_t.index+1
            don_base["Profil"] = 0
        #MESS_warn_mess("quatro")
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
                plt.pause(CONFIG.fig_render_time) # À augmenter si la figure ne s'affiche pas, sinon on pourra le baisser pour accélérer la vitesse de l'input
                
                correct = False
                while correct == False:
                    if GUI:
                        MESS_input_GUI(["fichier {} : redressement ?".format(file_list[i]),"","~r~ Oui (tous les profils)","~r~ Non ~!~","",
                                        "Oui, à partir du profil k, ou jusqu'au profil -k (-1 est le dernier profil)","Ignore le choix précédent si non vide","~t~","",
                                        "Le premier profil est indiqué en bleu"])
                        try:
                            fin, inp = GUI_VAR_LIST
                            if inp == "":
                                inp = ["y","n"][fin]
                        except:
                            MESS_warn_mess("Veuillez sélectionner un réponse")
                            continue
                    else:
                        MESS_input_mess(["fichier {} : redressement ?".format(file_list[i]),"","y : Oui (tous les profils)","k >= 0 : Oui, à partir du profil k",
                                         "k < 0 : Oui, jusqu'au profil -k (-1 est le dernier profil)","n : Non","","Le premier profil est indiqué en bleu"])
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
                    except IndexError as e:
                        MESS_warn_mess("Le profil {} n'existe pas !".format(inp),e)
                plt.close(fig)
                
            if corr_base:
                try:
                    i_fich_mes = CMD_evol_profils(i_fich_mes,i_fich_base,file_list[i],col_z,app_data["nb_ecarts"],verif=False)
                except IndexError:
                    MESS_warn_mess("Base externe au fichier {}, pas d'ajustement".format(file_list[i]))
            i_fich_mes = CMD_dec_voies(i_fich_mes,ncx,ncy,app_data["nb_ecarts"],app_data["TR_l"],app_data["TR_t"],app_data["GPS_dec"])
            ls_mes.append(i_fich_mes)
            ls_base.append(i_fich_base)
            
            if not not_in_file:
                i_fich_mes.to_csv(file_list[i][:-4]+"_init_P.dat", index=False, sep=sep) 
                if not i_fich_base.empty:
                    i_fich_base.to_csv(file_list[i][:-4]+"_init_B.dat", index=False, sep=sep)
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
                n = e*nb_res + r
                Z = final_df[nc_data[n]]
                Q5,Q95 = Z.quantile([0.05,0.95])
                col = ax[r].scatter(X,Y,marker='s',c=Z,cmap='cividis',s=6,vmin=Q5,vmax=Q95)
                plt.colorbar(col,ax=ax[r],shrink=0.7)
                ax[r].title.set_text(nc_data[e*nb_res+r])
                ax[r].set_xlabel(ncx[e])
                ax[r].set_ylabel(ncy[e])
                ax[r].set_aspect('equal')
            plt.show(block=False)
            plt.pause(CONFIG.fig_render_time) # À augmenter si la figure ne s'affiche pas, sinon on pourra le baisser pour accélérer la vitesse de l'input
            plt.savefig(CONFIG.script_path+"Output/CMDEX_i_" +str(e)+'.png')
            pickle.dump(fig, open(CONFIG.script_path+"Output/CMDEX_i_" +str(e)+'.pickle', 'wb'))

# fonction de conversion du temps sous forme de chaine de caractère en seconde
# en entrée, ce peut être le Dataframe complet issu du fichier CMD ou simplement
# la colonne 'Time'
# le format doit être une chaîne de caractère séparée par sep, par défaut ce
# son des ":"
 
def CMD_time(don,dep_0=False,sep=':'):
    """ [JT]\n
    Convert time from a string to seconds.\n
    Input can be the full dataframe from the CMD file or simply the ``"Time"`` column.\n
    Format must be a string separated by ``sep``.
    
    Parameters
    ----------
    don : dataframe
        Active dataframe.
    ``[opt]`` dep_0 : bool, default : ``False``
        If first time is set to 0.
    ``[opt]`` sep : str, default : ``':'``
        Time string separator.
    
    Returns
    -------
    ls_tps_sec : dataframe column
        Updated time column.
    """ 
    ls_tps_sec=list()
    premier=0.
    if type(don)==type(pd.DataFrame()):
        
        for temps in don['Time'] :
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
        for temps in don:
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
def CMD_interp(don,acq_GPS=True):
    """ [JT]\n
    *** OUTDATED ***
    """ 
    if acq_GPS :
        colXY=['Northing','Easting']
    else:
        colXY=['x[m]','y[m]']
        
    X,Y=don[colXY[0]],don[colXY[1]]
    DX,DY=X.diff(),Y.diff()
    DX[0:-1],DY[0:-1]=DX[1:],DY[1:]
    DR=np.sqrt(DX*DX+DY*DY)
    
    don['X_int']=0
    don['Y_int']=0
    
           
    ind_a_garder=(don.index[DR!=0]+1)[:-1]
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
            don['X_int']=pd.Series(np.concatenate(ls_intrpX))
            don['Y_int']=pd.Series(np.concatenate(ls_intrpY))
            return(don.copy())
        except:
            X_int1=pd.Series(np.concatenate(ls_intrpX))
            Y_int1=pd.Series(np.concatenate(ls_intrpY))
            MESS_warn_mess("[DEV] Attention, l'interpolation n'a pas la même taille que les données d'entrée")
    return(X_int1,Y_int1)

#détection de base par comparaison avec les coordonnées de la base de début
#(deb=True) ou de fin (deb=False)
# ne s'applique qu'aux cartes non concaténées

def CMD_detect_baseb(don,acq_GPS=True,Rd=2.,deb=True):
    """ [JT]\n
    *** OUTDATED ***
    """ 
    if acq_GPS :
        colXY=['Northing','Easting']
    else :
        colXY=['x[m]','y[m]']
    X,Y=don[colXY[0]],don[colXY[1]]
    DX,DY=X.diff(),Y.diff()
    DX[0:-1],DY[0:-1]=DX[1:],DY[1:]
    DR=np.sqrt(DX*DX+DY*DY)
    indbp=DR.index[DR>Rd]
    indbp=indbp.insert(0,0)
    indbp=indbp.insert(len(indbp),don.index[-1])
    
    if deb:
        Xmed,Ymed=don.loc[indbp[0]:indbp[1],colXY].median()
    else :
        Xmed,Ymed=don.loc[indbp[-2]:indbp[-1],colXY].median()
        
    DRb=np.sqrt((X-Xmed)*(X-Xmed)+(Y-Ymed)*(Y-Ymed))
    ind_base=DRb.index[DRb<0.5]
    
    don['Base']=0
    ind0=ind_base[0]
    ibase=1
    for ind in ind_base :
        if ind-ind0>1 :
            ibase+=1
        don.loc[ind,'Base']=ibase
        ind0=ind
    mod_i=0
    for d in don['Base'].unique() :
        ind_cour=don.index[don['Base']==d]
        if len(ind_cour)<4 :
            don.loc[ind_cour,'Base']=0
            mod_i+=1
        else:
            don.loc[ind_cour,'Base']-=mod_i
 
    return(don.copy())

# le seuil est à changer en fonction de la prospection
# on considère que les premières mesures et/ou le sdernières sont effectuées à
# la base

def CMD_detect_basec(don,acq_GPS=True,seuil=1.,deb=True):
    """ [JT]\n
    *** OUTDATED ***
    """ 
    if acq_GPS :
        colXY=['Northing','Easting']
    else :
        colXY=['x[m]','y[m]']
        
    X,Y=don[colXY[0]],don[colXY[1]]
    if not('b et p' in don.columns) :
        don=CMD_detect_chgt(don)
        MESS_warn_mess("[DEV] Attention, création par défaut d'une colonne 'b et p'")
    
    baseD,baseF=don['b et p'].iloc[[0,-1]]
    if deb :
        ind_b=don.index[don['b et p']==baseD]
    else :            
        ind_b= don.index[don['b et p']==baseF]
    
    Xmed,Ymed=don.loc[ind_b,colXY].median()
    
    DRb=np.sqrt((X-Xmed)*(X-Xmed)+(Y-Ymed)*(Y-Ymed))
    ind_base=DRb.index[DRb<seuil]
    
    don['Base']=0
    ind0=ind_base[0]
    ibase=1
    for ind in ind_base :
        if ind-ind0>1 :
            ibase+=1
        don.loc[ind,'Base']=ibase
        ind0=ind
    
    
    mod_i=0
    for d in don['Base'].unique() :
        ind_cour=don.index[don['Base']==d]
        if len(ind_cour)<4 :
            don.loc[ind_cour,'Base']=0
            mod_i+=1
        else:
            don.loc[ind_cour,'Base']-=mod_i
    
    ind_base=don.index[don['Base']!=0]
    for d in don['Base'].unique() :
        if d!=0 :
            ind_cour=don.index[don['Base']==d]
            dt=don.loc[ind_cour,'temps (s)'].diff()
            ind_split=dt.index[np.abs(dt)>1.] 
            if len(ind_split)==1 :
                ind_courb=ind_base[ind_base>ind_split.array[0]-1]                
                don.loc[ind_courb,'Base']+=1
    
 
    return(don.copy())
    
def CMD_detect_base(don,acq_GPS=True,nbbase=[2,]):
    """ [JT]\n
    *** OUTDATED ***
    """ 
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
    Q=1-Q/don.shape[0]
    
    X,Y=don[colXY[0]],don[colXY[1]]
    DX,DY=X.diff(),Y.diff()
    DX[0:-1],DY[0:-1]=DX[1:],DY[1:]
    DR=np.sqrt(DX*DX+DY*DY)
    
    ind_base=don.index[DR>DR.quantile(Q)]
    
    # on commence par une base donc le premier indice est le début de
    # la première base on l'ajoute
    ind_base=ind_base.insert(0,0)
    # on fini par une base donc le dernier indice est la fin de la dernière
    # base on l'ajoute à la fin
    ind_base=ind_base.insert(len(ind_base),don.index[-1])
    # si le nombre de base est une liste alors il y a plusieurs prospection
    # dans les données (concaténation en amont) il faut donc séparer les bases
    # de fin et de début de chacune des prospections. On utilise le temps
    if len(nbbase) !=1 :
        i_d=0
        for nbb in nbbase[:-1]:
            aux=i_d+(nbb-1)*2
            ind_deb=ind_base[aux]
            ind_fin=ind_base[aux+1]
            T=don['temps (s)'].loc[ind_deb:ind_fin]
            DT=T.diff()
            ind_d=DT.index[np.abs(DT)>60]
            ind_f=ind_d-1
            ind_base=ind_base.insert(aux+1,ind_f)
            ind_base=ind_base.insert(aux+2,ind_d)
     
    
    don['Base']=0
    for ic,ind_c in enumerate(zip(ind_base[::2],ind_base[1::2])):
        don.loc[ind_c[0]:ind_c[1],'Base']=ic+1
 
    
    return(don.copy())

def CMD_detect_base_pos(don_c, seuil,trace=False):
    """ [JT]\n
    Separate bases and profiles
    
    Parameters
    ----------
    don_c : dataframe
        Active dataframe.
    seuil : float
        Threshold of acceptance for bases / profiles.
    ``[opt]`` trace : bool, default : ``False``
        Enables plotting.
    
    Returns
    -------
    don_int : dataframe
        Output dataframe.
        
    Raises
    ------
    * Dataframe not interpolated
    """ 
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
    
    # Un seul profil en continu
    if max(don_int['b et p']) < 2:
        don_int['Base']=0
        don_int['Profil']=1
        return(don_int.copy())
    
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

def CMD_detect_chgt(don,acq_GPS=True,verif=False):
    """ [JT]\n
    Detect profiles (or bases) from time difference (gap means new profile).
    
    Parameters
    ----------
    don : dataframe
        Active dataframe.
    ``[opt]`` acq_GPS : bool, default : ``True``
        If got GPS data.
    ``[opt]`` verif : bool, default : ``False``
        Enables plotting.
    
    Returns
    -------
    don : dataframe
        Output dataframe.
    """ 
    if acq_GPS :
        colXY=['Northing','Easting']
    else:
        colXY=['x[m]','y[m]']
    
    X,Y=don[colXY[0]],don[colXY[1]]
   
    if 'temps (s)' in don.columns :
        pass
    else :
        don['temps (s)']=CMD_time(don)
        
        
    T=don['temps (s)'].copy()
    
    for indc in T.index[T.isna()]:
        T.loc[indc]=T.loc[indc-1]
        
    DT=T.diff()
    # la différence de temps donne les débuts de profils ou de base
    ind_chgtd=DT.index[DT>5*DT.median()]
    
    # la fin est l'indice avant le début donc - 1 par rapport au précédent 
    ind_chgtf=ind_chgtd-1
    
    ind_chgtd=ind_chgtd.insert(0,0)
    ind_chgtf=ind_chgtf.append(DT.index[[-1,]])
           
    don['b et p']=0
    for ic,(ind_d,ind_f) in enumerate(zip(ind_chgtd,ind_chgtf)):
        don.loc[ind_d:ind_f,'b et p']=ic+1
        
    if verif==True:    
        fig,ax=plt.subplots(nrows=1,ncols=1,figsize=(7,7))
        ax.scatter(X.loc[ind_chgtd],Y.loc[ind_chgtd],marker='s',color='green')
        ax.scatter(X.loc[ind_chgtf],Y.loc[ind_chgtf],marker='s',color='red')
        
        ax.scatter(X,Y,marker='+',c=don['b et p'],cmap='cividis')
        ax.set_aspect('equal')
    
    return(don.copy())
    
def CMD_num_prof(don, acq_GPS=True):
    """ [JT]\n
    Numbers each profile (or base) in chronological order.
    
    Parameters
    ----------
    don : dataframe
        Active dataframe.
    ``[opt]`` acq_GPS : bool, default : ``True``
        If got GPS data.
    
    Returns
    -------
    don : dataframe
        Output dataframe.
    """ 
    if not('Base' in don.columns) :
        don=CMD_detect_basec(don)
        MESS_warn_mess("[DEV] Attention, création automatique d'une colonne 'base'")
        
    ind_mes=don.index[don['Base']==0]
    don['Profil']=0
    num_Pent=don.loc[ind_mes,'b et p'].unique()
    for ic,val in enumerate(num_Pent) :
        ind_c=don.index[don['b et p']==val]
        don.loc[ind_c,'Profil']=ic+1
    return(don.copy())
    
# semble fonctionner le 14/11/2024
# Résume une base en un point
  
def CMD_synthBase(don,nc_data,CMDmini=True):
    """ [JT] + [TA]\n
    Resume each base by one single line.\n
    It contains all data pointed by ``nc_data``, its profile/base index and its time.\n
    Does not return a single dataframe, is managed by ``CMD_init``.
    
    Parameters
    ----------
    don : dataframe
        Active base dataframe.
    nc_data : list of str
        Names of every Z columns (actual data).
    ``[opt]`` CMDmini : bool, default : ``True``
        If bases were taken in the air (device's 0). 
    
    Returns
    -------
    pd_num_fich : pd.Series
        ``"Num fich"`` column (file order).
    pd_bp : pd.Series
        ``"b et p"`` column (base + profile index).
    pd_tps : pd.Series
        ``"temps (s)"`` column (base + profile index).
    * ``CMDmini = True``
        pd_inf : pd.Series
            Data columns for lowest values (device's 0).
    * ``CMDmini = False``
        pd_valmd : pd.Series
            Data columns for average values, since all points are on the ground.
    
    Notes
    -----
    Subfunction of ``CMD_init``.\n
    If ``CMDmini = False``, the result will not give enough information to remove the device's 0, although the variations between bases will stand.
    
    See also
    --------
    ``CMD_init, CMD_evol_profils``
    """ 
    if not('Base' in don.columns) :
        MESS_err_mess("[DEV] Veuillez créer une colonne des numéro de base avec CMD_detect_base")
    if not('temps (s)' in don.columns) :
        don['temps (s)']=CMD_time(don)
    num_base=don['Base'].unique()
    num_base=num_base[num_base>0]    
    ls_num_fich,ls_bp,ls_tps,ls_val=[],[],[],[]
    for n_base in num_base :
        ind_c=don.index[don['Base']==n_base]
        tps_c=don.loc[ind_c,'temps (s)'].median()
        Q5=don.loc[ind_c,nc_data].quantile(0.05)
        Q95=don.loc[ind_c,nc_data].quantile(0.95)
        valb_c=(Q95+Q5)/2.
        ls_num_fich.append(don.loc[ind_c[0],"Num fich"])
        ls_bp.append(don.loc[ind_c[0],"b et p"])
        ls_tps.append(tps_c),ls_val.append(valb_c)
     
    pd_valmd=pd.concat(ls_val,axis=1)
    ls_sup,ls_inf=[],[]
          
    for n_base in num_base :
        ind_c=don.index[don['Base']==n_base]
        seuil=pd_valmd[n_base-1]
        bas='ND'
        ls_s,ls_i=[],[]
        for ic,sc in enumerate(seuil) :
            dat_c=don.loc[ind_c,nc_data[ic]].copy()
            prem=dat_c.index[0]
            ind1=dat_c.index[dat_c>sc]
            ind2=dat_c.index[dat_c<sc]
            ls_s.append(dat_c.loc[ind1].median())     
            ls_i.append(dat_c.loc[ind2].median())
        
        ls_sup.append(pd.Series(ls_s))
        ls_inf.append(pd.Series(ls_i))
    
    pd_sup=pd.concat(ls_sup,axis=1).round(CONFIG.prec_data)
    pd_inf=pd.concat(ls_inf,axis=1).round(CONFIG.prec_data)
    pd_sup.index=seuil.index
    pd_inf.index=seuil.index 
    pd_num_fich=pd.Series(ls_num_fich)  
    pd_bp=pd.Series(ls_bp)     
    pd_tps=pd.Series(ls_tps).round(CONFIG.prec_data)
    
    if CMDmini :
        return(pd_num_fich,pd_bp,pd_tps,pd_inf)
    else :
        return(pd_num_fich,pd_bp,pd_tps,pd_valmd)
    
                
def CMD_sep_BM(don):
    """ [JT]\n
    Split dataframe between profiles and bases.
    
    Parameters
    ----------
    don : dataframe
        Active dataframe.
    
    Returns
    -------
    don_base : dataframe
        Output dataframe of all bases.
    don_mes : dataframe
        Output dataframe of all profiles.
    
    Raises
    ------
    * Profiles not detected.
    """
    if not('Profil' in don.columns):
        MESS_err_mess("[DEV] Veuillez créer une colonne des numéro de profil avec CMD_num_prof")
    else :
        ind_p=don.index[don['Profil']!=0]
        ind_b=don.index[don['Base']!=0]
        return(don.loc[ind_b],don.loc[ind_p])

# Dans le cas d'une prospection sur un carré, on peut identifier les profils par la première coordonnée

def CMD_detec_profil_carre(don):
    """ [TA]\n
    Detect profiles (or bases) from X coordinates (data without GPS only).
    
    Notes
    -----
    ``"temps (s)"`` column is created but set to ``-1`` (placeholder).
    
    Parameters
    ----------
    don : dataframe
        Active dataframe.
    
    Returns
    -------
    don : dataframe
        Output dataframe.
    """
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

def CMD_detec_pseudoprof(don,X_n,Y_n,l_p=None,tn=10,tn_c=10,min_conseq=8,verif=False):
    """ [TA]\n
    Given a database with continuous timestamps, estimate profiles by finding one point (called `center`) per profile, possibly at the center.\n
    Each prospection point is then assigned to the closest center in term of index to form pseudo-profiles.\n
    By default, perform a linear regression and select the closest points as centers. For more flexibility, one can set a range of points which will create segments with ``l_p``.\n
    This procedure is to be used only if no other profile detection method has been successful.
    
    Notes
    -----
    It is advised to check if the result is coherent by setting ``verif = True``.\n
    If many centers are missing, raise ``tn`` and / or ``tn_c``. On the contrary, lowering them also works.\n
    If you can expect profiles of less than 8 points, try lowering ``min_conseq``. If some profiles are detected twice, you can raise it.\n
    Profiles found this way are not neccesarely straight. To improve the detection, try setting 
    
    Parameters
    ----------
    don : dataframe
        Profile dataframe.
    X_n : str
        Name of X column.
    Y_n : str
        Name of Y column.
    ``[opt]`` l_p : ``None`` or list of [float, float], default : ``None``
        List of points coordinates for segments. If ``None``, perform a linear regression instead.
    ``[opt]`` tn : int, default : ``10``
        Number of nearest points used to determinate the max distance treshold.
    ``[opt]`` tn_c : int, default : ``10``
        Multiplier of median distance of the ``tn`` nearest points used to determinate the max distance treshold.
    ``[opt]`` min_conseq : int, default : ``8``
        Minimal index distance that is allowed between two found centers.
    ``[opt]`` verif : bool, default : ``False``
        Enables plotting.

    Returns
    -------
    don : dataframe
        Updated profile dataframe
    
    Raises
    ------
    * ``l_p`` vector too small.
    
    See also
    --------
    ``CMD_init, CMD_detec_profil_carre, CMD_detect_chgt`` 
    """
    for label in ["Profile","Base","b et p"]:
        try:
            don.drop(columns=label)
        except:
            pass
    
    try:
        don[X_n], don[Y_n]
    except KeyError:
        MESS_err_mess('Les colonnes "{}" et/ou "{}" n\'existent pas'.format(X_n,Y_n))
    
    nb_pts = len(don)
    regr = (l_p == None)
    
    dist_list = []
    
    if regr:
        lin_tab_i = np.array(don.index)
        lin_tab_x = np.array(don[X_n])
        lin_tab_y = np.array(don[Y_n])
        lin_reg_x = linregress(lin_tab_i,lin_tab_x)
        lin_reg_y = linregress(lin_tab_i,lin_tab_y)
        
        eq = [lin_reg_x.slope, lin_reg_x.intercept, lin_reg_y.slope, lin_reg_y.intercept]
        
        for index, row in don.iterrows():
            dist_list.append(np.abs(eq[2]*(row[X_n]-eq[1]) - eq[0]*(row[Y_n]-eq[3])))
    else:
        l_p = np.array(l_p)
        if len(l_p) < 2:
            MESS_err_mess("Le vecteur de points 'l_p' doit au moins en contenir 2 pour créer un segment")
        for index, row in don.iterrows():
            d_l = []
            for p1,p2 in zip(l_p,l_p[1:]):
                p3 = np.array([row[X_n],row[Y_n]])
                ba = p1 - p2
                lba = np.linalg.norm(ba)
                bc = p3 - p2
                lbc = np.linalg.norm(bc)
                angle_1 = np.degrees(np.arccos(np.dot(ba, bc) / (lba * lbc)))
                if angle_1 >= 90.0:
                    d_l.append(lbc)
                    continue
                ac = p3 - p1
                lac = np.linalg.norm(ac)
                ab = -ba
                lab = lba
                angle_2 = np.degrees(np.arccos(np.dot(ab, ac) / (lab * lac)))
                if angle_2 >= 90.0:
                    d_l.append(lac)
                    continue
                d_l.append(np.abs(np.cross(ab,ac)/lba))
            dist_list.append(min(d_l))
    
    m1_list = []
    up = True
    for ic,d in enumerate(dist_list[:-1]):
        new_up = (d < dist_list[ic+1])
        if new_up and not up:
            m1_list.append(ic)
        up = new_up
    
    #print(m1_list)
    m2_list = []
    top_n = sorted([dist_list[i] for i in m1_list], key = lambda x: x, reverse = False)[:tn]
    min_med = sum(top_n)/tn * tn_c
    
    for m in m1_list:
        #print(dist_list[m], " ", min_med)
        if dist_list[m] < min_med:
            m2_list.append(m)
    
    min_list = []
    if regr:
        max_conseq = (2*nb_pts)//len(m2_list)
    else:
        max_conseq = np.inf
    l_min = len(m2_list)
    i = 0
    j = 1
    while j < l_min:
        d = m2_list[j] - m2_list[i]
        if d > max_conseq:
            min_list.append(m2_list[i])
            nb_new_points = int(d*2//max_conseq)-1
            for n in range(1,nb_new_points+1):
                min_list.append(m2_list[i]+((m2_list[j]-m2_list[i])*n)//(nb_new_points+1))
            i = j
            j += 1
        if d < min_conseq:
            if dist_list[m2_list[j]] < dist_list[m2_list[i]]:
                min_list.append(m2_list[j])
                i = j
            elif m2_list[i] not in min_list:
                min_list.append(m2_list[i])
            j += 1
        else:
            if m2_list[i] not in min_list:
                min_list.append(m2_list[i])
            i = j
            j += 1
    if i == l_min-1:
        min_list.append(m2_list[-1])
    
    don["Profil"] = 0
    don["Base"] = 0
    l_min = len(min_list)
    for index, row in don.iterrows():
        ind = -1
        for ic, m in enumerate(min_list[1:]):
            if m > index:
                if m-index > index-min_list[ic]:
                    ind = ic+1
                else:
                    ind = ic+2
                break
        if ind == -1:
            ind = l_min
        don.loc[index,"Profil"] = ind   
    don["b et p"] = don["Profil"]
    
    if verif:
        print(min_list)
        index_list = range(nb_pts)
        fig,ax = plt.subplots(nrows=1,ncols=3,figsize=(CONFIG.fig_width,CONFIG.fig_height),squeeze=False)
        ax[0][0].plot(index_list,dist_list,'-')
        ax[0][0].plot([index_list[i] for i in min_list],[dist_list[i] for i in min_list],'xr')
        ax[0][0].set_xlabel("Index")
        ax[0][0].set_ylabel("Distance")
        ax[0][0].set_title("Évolution de la distance à la droite")
        ax[0][1].plot(don[X_n],don[Y_n],'x')
        if regr:
            ax[0][1].plot([eq[0]*i+eq[1] for i in index_list],[eq[2]*i+eq[3] for i in index_list],'-k')
        else:
            ax[0][1].plot(l_p[:,0],l_p[:,1],'-k')
        ax[0][1].plot([don[X_n][index_list[i]] for i in min_list],[don[Y_n][index_list[i]] for i in min_list],'xr')
        ax[0][1].set_aspect('equal')
        ax[0][1].set_xlabel(X_n)
        ax[0][1].set_ylabel(Y_n)
        ax[0][1].set_title("Centres et droite")
        ax[0][1].ticklabel_format(useOffset=False)
        ax[0][2].scatter(don[X_n],don[Y_n],marker='x',c=don["Profil"]%8, cmap='nipy_spectral')
        ax[0][2].set_aspect('equal')
        ax[0][2].set_xlabel(X_n)
        ax[0][2].set_ylabel(Y_n)
        ax[0][2].set_title("Division en pseudo-profils")
        ax[0][2].ticklabel_format(useOffset=False)
        plt.show(block=False)
        plt.pause(CONFIG.fig_render_time) # À augmenter si la figure ne s'affiche pas, sinon on pourra le baisser pour accélérer la vitesse de l'input
    
    return don.copy()

#interpolation fine et intelligente se basant sur les profils détectés
# fonctionne le 01/01/2025
# doit être testé avec des données sans GPS et sur plusieurs cas

def CMD_intrp_prof(don_mes,acq_GPS=True):
    """ [JT]\n
    Interpolate groups of points of same coordinates by linear regression.
    Used if the GPS refresh time is slower than the actual prospection.
    
    Parameters
    ----------
    don : dataframe
        Active dataframe.
    ``[opt]`` acq_GPS : bool, default : ``True``
        If got GPS data.
    
    Returns
    -------
    don_mes : dataframe
        Output dataframe of all profiles.
    
    Raises
    ------
    * Profiles not detected.
    """
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
    """ [JT]\n
    *** OUTDATED ***
    """
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

# Estime la position et le temps des points défectueux à l'aide de ses voisins, si aucun profil n'a pu être détecté.

def CMD_XY_Nan_completion_solo(don):
    """ [TA]\n
    Estimates ``NaN`` points coordinates by linear regression from neighbors.
    Others are left unchanged.
    
    Notes
    -----
    Procedure is cancelled if NaN on X and Y are from different positions (should be an issue of column splitting).\n
    Is meant to be used if the prospection is not splitted in profiles. Otherwise, see ``CMD_XY_Nan_completion``.
    Interpolation also corrects time.
    
    Parameters
    ----------
    don : dataframe
        Active dataframe.
    
    Returns
    -------
    don : dataframe
        Output dataframe.
    
    See Also
    --------
    ``CMD_init, CMD_XY_Nan_completion``
    """
    X = don["X_int"]
    Y = don["Y_int"]
    indXNan=X.index[X.isna()]
    indYNan=Y.index[Y.isna()]
    if len(indXNan)<1:
        print('Aucune valeur à interpoler')
        return don.copy()
    if not np.all(indXNan==indYNan):
        MESS_warn_mess("[DEV] NaN en X et NaN en Y n'ont pas les même position dans le tableau (pas d'effet)")
        return don.copy()
    
    full_na = don.iloc[indXNan,:]
    bloc_na_list = [d for _, d in full_na.groupby(full_na.index - np.arange(len(full_na)))]
    #print(bloc_na_list)
    
    for bloc_na in bloc_na_list:
        bnai = bloc_na.index
        l_n = bnai.size
        if bnai[0] == 0: # Bloc au début
            row1 = don.iloc[bnai[-1]+1]
            row2 = don.iloc[bnai[-1]+2]
            pas_x = row2["X_int"] - row1["X_int"]
            pas_y = row2["Y_int"] - row1["Y_int"]
            new_x = [row1["X_int"] - pas_x*i for i in range(1,l_n+1,-1)]
            new_y = [row1["Y_int"] - pas_y*i for i in range(1,l_n+1,-1)]
        elif bnai[-1] == len(don)-1: # Bloc à la fin
            row1 = don.iloc[bnai[0]-2]
            row2 = don.iloc[bnai[0]-1]
            pas_x = row2["X_int"] - row1["X_int"]
            pas_y = row2["Y_int"] - row1["Y_int"]
            new_x = [row2["X_int"] + pas_x*i for i in range(1,l_n+1)]
            new_y = [row2["Y_int"] + pas_y*i for i in range(1,l_n+1)]
        else:
            row1 = don.iloc[bnai[0]-1]
            row2 = don.iloc[bnai[-1]+1]
            pas_x = (row2["X_int"] - row1["X_int"]) / (l_n+1)
            pas_y = (row2["Y_int"] - row1["Y_int"]) / (l_n+1)
            new_x = [row1["X_int"] + pas_x*i for i in range(1,l_n+1)]
            new_y = [row1["Y_int"] + pas_y*i for i in range(1,l_n+1)]
        don.loc[bnai, "X_int"] = new_x
        don.loc[bnai, "Y_int"] = new_y
    
    print('Valeurs remplacées : {}'.format(len(indXNan)))
    return don.copy()

# Estime la position et le temps des points défectueux à l'aide d'une régression linéaire des points de même profil.

def CMD_XY_Nan_completion(don):
    """ [TA]\n
    Estimates ``NaN`` points coordinates by linear regression on associated profile.
    Others are left unchanged.
    
    Notes
    -----
    Procedure is cancelled if NaN on X and Y are from different positions (should be an issue of column splitting).\n
    Profiles of only one known point can't be interpolated.
    Profiles of only two known point are handled by creating a third middle point (otherwise glitchy).\n
    Interpolation also corrects time.
    
    Parameters
    ----------
    don : dataframe
        Active dataframe.
    
    Returns
    -------
    don : dataframe
        Output dataframe.
    
    See Also
    --------
    ``CMD_init, CMD_pts_rectif``
    """
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
    
    try:
        ind_aux = indc[indc.diff()!=1.]-1
    except AttributeError:
        MESS_err_mess("ERREUR PANDAS : nécessite au minimum la version 2.1.0 (et python 3.10).")
    for i_d in ind_aux:
        prof = don.loc[i_d,'b et p']
        bloc = don.loc[don['b et p'] == prof]
        bloc_notna = bloc.dropna(subset = ["X_int","Y_int"])
        bloc_na = bloc.loc[bloc.index.difference(bloc.dropna(subset = ["X_int","Y_int"]).index)]
        bloc_notna_l = bloc_notna.shape[0]
        
        if bloc_notna_l == 1:
            MESS_warn_mess("Un des profils ne possède qu'un unique point connu : régression impossible.")
        else:
            lin_tab_i = np.array(bloc_notna.index)
            lin_tab1 = np.array(bloc_notna["temps (s)"])
            lin_tab2 = np.array(bloc_notna["X_int"])
            lin_tab3 = np.array(bloc_notna["Y_int"])
            # La régression ne marche pas avec deux points, mais on peut en créer un troisième
            if bloc_notna_l == 2:
                lin_tab1 = np.concatenate([lin_tab1,[sum(lin_tab1[:,1])/len(lin_tab1[:,1])]])
                lin_tab2 = np.concatenate([lin_tab2,[sum(lin_tab2[:,1])/len(lin_tab2[:,1])]])
                lin_tab3 = np.concatenate([lin_tab3,[sum(lin_tab3[:,1])/len(lin_tab3[:,1])]])
            
            lin_reg1 = linregress(lin_tab_i,lin_tab1)
            lin_reg2 = linregress(lin_tab_i,lin_tab2)
            lin_reg3 = linregress(lin_tab_i,lin_tab3)

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
    """ [TA]\n
    Estimates all points coordinates of same profile by linear regression.\n
    To be used if the GPS error is too important.
    
    Notes
    -----
    Profiles of only one known point can't be interpolated.
    Profiles of only two known point are handled by creating a third middle point (otherwise glitchy).
    
    Parameters
    ----------
    don : dataframe
        Active dataframe.
    ``[opt]`` ind_deb : ``None`` or int, default : ``None``
        Index of first profile to interpolate. ``None`` for all.
    ``[opt]`` ind_fin : ``None`` or int, default : ``None``
        Index of last profile to interpolate. ``None`` for all.
    
    Returns
    -------
    don : dataframe
        Output dataframe.
    
    See Also
    --------
    ``CMD_XY_Nan_completion``
    """
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
            lin_tab_i = np.array(bloc.index)
            lin_tab2 = np.array(bloc["X_int"])
            lin_tab3 = np.array(bloc["Y_int"])
            # La régression ne marche pas avec deux points, mais on peut en créer un troisième
            if bloc_l == 2:
                # lin_tab1 = np.concatenate([lin_tab1,[sum(lin_tab1[:,1])/len(lin_tab1[:,1])]])
                lin_tab2 = np.concatenate([lin_tab2,[sum(lin_tab2[:,1])/len(lin_tab2[:,1])]])
                lin_tab3 = np.concatenate([lin_tab3,[sum(lin_tab3[:,1])/len(lin_tab3[:,1])]])
            
            # lin_reg1 = linregress(lin_tab1)
            lin_reg2 = linregress(lin_tab_i,lin_tab2)
            lin_reg3 = linregress(lin_tab_i,lin_tab3)
            
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
    """ [JT]\n
    Shifts X and Y according to the GPS and coil position from the center.
    
    Notes
    -----
    If no GPS, only the coil shift will be taken into account.
    
    Parameters
    ----------
    X : dataframe column
        X coordinates.
    Y : dataframe column
        Y coordinates.
    profs : dataframe column
        Indexes of profiles.
    ``[opt]`` decL : float, default : ``0.0``
        Total shift on device axis, with direction from first to last coil.
    ``[opt]`` decT : float, default : ``0.0``
        Total shift on device perpendicular axis, with direction from behind to front.
    
    Returns
    -------
    Xc : dataframe column
        Shifted X.
    Yc : dataframe column
        Shifted Y.
    
    See Also
    --------
    ``CMD_dec_voies``
    """
    ls_Xc=[]
    ls_Yc=[]
    ls_prof=profs.unique()
    #print(ls_prof)
    for prof in ls_prof:
        ind_c=profs.index[profs==prof]
        XX=X.loc[ind_c].copy()
        YY=Y.loc[ind_c].copy()
        DX=XX.diff()
        DY=YY.diff()
        DX1=DX.copy()
        DY1=DY.copy()
        if len(DX1) == 1:
            ls_Xc.append(XX)
            ls_Yc.append(YY)
            continue
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

def CMD_dec_voies(don,ncx,ncy,nb_ecarts,TR_l,TR_t, gps_dec):
    """ [TA]\n
    Shifts X and Y according to the GPS and coil position from the center, for each coil.
    
    Notes
    -----
    If no GPS, only the coil shift will be taken into account.
    
    Parameters
    ----------
    don : dataframe
        Active dataframe.
    ncx : list of str
        Names of every X columns.
    ncy : list of str
        Names of every Y columns.
    nb_ecarts : int
        Number of X and Y columns. The number of coils.
    TR_l : list of float
        Distance between each coil and the transmitter coil, on lateral axis.
    TR_t : list of float
        Distance between each coil and the transmitter coil, on transversal axis.
    gps_dec : [float, float]
        Shift between the GPS antenna and the device center, on both axis. Should be ``[0,0]`` if none.
    
    Returns
    -------
    don : dataframe
        Output dataframe.
    
    See Also
    --------
    ``CMD_decal_posLT``
    """
    for e in range(nb_ecarts):
        decx = gps_dec[0]-(TR_l[e]-TR_l[-1])/2
        decy = gps_dec[1]-(TR_t[e]-TR_t[-1])/2
        #print(don["Profil"])
        X, Y = CMD_decal_posLT(don["X_int"],don["Y_int"],don["Profil"],decL=decx,decT=decy)
        don[ncx[e]] = X.round(CONFIG.prec_coos)
        don[ncy[e]] = Y.round(CONFIG.prec_coos)
    return don.copy()

# Fonction principale de la frontière.

def CMD_frontiere(col_x,col_y,col_z,file_list=None,sep='\t',output_file="frt.dat",choice=False):
    """
    Main function for calibration from borders.\n
    See ``CMD_frontiere_loop`` for more infos.
    
    Parameters
    ----------
    col_x : list of int
        Index of every X coordinates columns.
    col_y : list of int
        Index of every Y coordinates columns.
    col_z : list of int
        Index of every Z coordinates columns (actual data).
    ``[opt]`` file_list : ``None`` or list of str, default : ``None``
        List of files to process.
    ``[opt]`` sep : str, default : ``'\\t'``
        Dataframe separator.
    ``[opt]`` output_file : ``None`` or str, default : ``None``
        Name of output file. If ``None``, is set to ``"frt.dat"``.
    ``[opt]`` choice : bool, default : ``False``
        Enables manual acceptance of each adjustment.
    
    See also
    --------
    ``CMD_frontiere_loop, TOOL_check_time_date, TOOL_true_file_list``
    """
    file_list = TOOL_true_file_list(file_list)
    df_list = []
    for ic, file in enumerate(file_list):
        df = TOOL_check_time_date(file,sep)
        df_list.append(df)
    
    ncx, ncy, nc_data, nb_data, nb_ecarts, nb_res = TOOL_manage_cols(df_list[0],col_x,col_y,col_z)
    CMD_frontiere_loop(df_list,ncx,ncy,nc_data,nb_data,nb_ecarts,nb_res,choice,sep,output_file)

# Boucle sur tous les duos de fichiers et essaie d'établir une frontière. Si elle existe, calcule les ajustements.

def CMD_frontiere_loop(ls_mes,ncx,ncy,nc_data,nb_data,nb_ecarts,nb_res,choice=False,sep='\t',output_file=None,not_in_file=False):
    """ [TA]\n
    Given a list of dataframe, try the two-by-two correction by juncture if they are close enough.\n
    The first in the list is used as reference and will not be modified.\n
    Each dataframe can only be adjusted one time, and will then be used as reference as well, until all of them are treated.\n
    If a dataframe is not connected to any of the references, they will be ignored and raise a warning.\n
    Plot the result.
    
    Parameters
    ----------
    ls_mes : list of dataframe
        List of active dataframes (profiles only).
    ncx : list of str
        Names of every X columns.
    ncy : list of str
        Names of every Y columns.
    nc_data : list of str
        Names of every Z columns (actual data).
    nb_data : int
        Number of Z columns. The number of data.
    nb_ecarts : int
        Number of X and Y columns. The number of coils.
    nb_res : int
        The number of data per coil.
    ``[opt]`` choice : bool, default : ``False``
        Enables manual acceptance of each adjustment.
    ``[opt]`` sep : str, default : ``'\\t'``
        Dataframe separator.
    ``[opt]`` output_file : ``None`` or str, default : ``None``
        Name of output file. If ``None``, is set to ``"frt.dat"``.
    ``[opt]`` not_in_file : bool, default : ``False``
        If call comes from script function instead of user.
    
    Returns
    -------
    * ``not_in_file = False``
        none, but save dataframe for profiles and bases in separated .dat
    * ``not_in_file = True``
        ls_mes : list of dataframe
            List of output dataframes.
    
    See Also
    --------
    ``CMD_calc_frontiere``
    """
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
        plt.pause(CONFIG.fig_render_time) # À augmenter si la figure ne s'affiche pas, sinon on pourra le baisser pour accélérer la vitesse de l'input
        plt.savefig(CONFIG.script_path+"Output/CMDEX_f_" +str(e)+'.png')
        pickle.dump(fig, open(CONFIG.script_path+"Output/CMDEX_f_" +str(e)+'.pickle', 'wb'))
    
    if output_file == None:
        final_df.to_csv("frt.dat", index=False, sep=sep)
    else:
        final_df.to_csv(output_file, index=False, sep=sep)

# Corrige les décalages entre deux fichiers en sélectionnant des points frontaliers, si ils existent. Activer "choice" pour valider ou non les ajustements.

def CMD_calc_frontiere(don1,don2,ncx,ncy,nc_data,nb_res,nb_ecarts,nb=30,tol_inter=0.1,tol_intra=0.2,m_size=14,choice=False,verif=False,verif_pts=False,dat_to_test=0):
    """ [TA]\n
    Given two dataframes, try to adjust the second one by juncture if they are close enough.\n
    Frontiers are approximated by distincts pairs of points between both set of points.\n
    It also check if found points are sparse enough, so corners are not considered as frontiers.
    Those checks are weighted by ``tol_inter`` and ``tol_intra`` respectively, though they should not be modified for intended results (unless unexpected behaviours).\n
    Adjustment follows a linear relation *a + bx* where *a* and *b* are constants to determinate.\n
    Points in the frontier must share the same average value and standard deviation after the procedure.
    
    Parameters
    ----------
    don1 : dataframe
        First dataframe (reference).
    don2 : dataframe
        Second dataframe (to adjust).
    ncx : list of str
        Names of every X columns.
    ncy : list of str
        Names of every Y columns.
    nc_data : list of str
        Names of every Z columns (actual data).
    nb_ecarts : int
        Number of X and Y columns. The number of coils.
    nb_res : int
        The number of data per coil.
    ``[opt]`` nb : int, default : ``30``
        Minimum number of pairs of points to find for adjustment. Scale with the number of total points in ``don1`` and ``don2``.
    ``[opt]`` tol_inter : float, default : ``0.1``
        Tolerance of acceptance for pairs distance.
    ``[opt]`` tol_intra : float, default : ``0.2``
        Tolerance of acceptance for intern points dispersion.
    ``[opt]`` m_size : float, default : ``14``
        Plotting size of points.
    ``[opt]`` choice : bool, default : ``False``
        Enables manual acceptance of each adjustment.
    ``[opt]`` verif : bool, default : ``False``
        Display various informations regarding step 2 (adjust).
    ``[opt]`` verif_pts : bool, default : ``False``
        Display various informations regarding step 1 (find pairs).
    ``[opt]`` dat_to_test : int, default : ``0``
        Index of the data to display with ``verif``.
    
    Returns
    -------
    don2 : dataframe
        Updated second dataframe.
    
    See Also
    --------
    ``CMD_frontiere, CMD_appr_border, CMD_max_frontiere, CMD_appr_taille_grp, CMD_compute_coeff``
    """
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
        
        # Calcul de la différence / 
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
                plt.pause(CONFIG.fig_render_time) # À augmenter si la figure ne s'affiche pas, sinon on pourra le baisser pour accélérer la vitesse de l'input
                
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
                        MESS_input_mess(["Valider l'ajustement ?","","y : Oui (continuer avec)","n : Non (conserver la donnée initiale)",
                                         "r : Réessayer (relance un nouvel ajustement sur la même donnée)"])
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
                plt.pause(CONFIG.fig_render_time) # À augmenter si la figure ne s'affiche pas, sinon on pourra le baisser pour accélérer la vitesse de l'input
    
    return don2.copy(), True

# Trouve un duo de points (l'un dans l'ensemble 1, l'autre dans le 2) le plus proche possible (excepté dans les sous-ensembles excl)

def CMD_appr_border(x1,x2,y1,y2,i_max,j_max,i_excl,j_excl):
    """ [TA]\n
    Find one point of each dataframe that are close to each other.\n
    They may not be included in the exclusion lists ``i_excl`` and ``j_excl`` to avoid duplicates.
    
    Notes
    -----
    This function does not provide the global minimum of distance, it converges to a fair enough pair.\n
    It runs through both lists and remove far points one by one (linear complexity).\n
    Starting points are taken randomly.
    
    Parameters
    ----------
    x1 : list of float
        X coordinates of first dataframe.
    x2 : list of float
        X coordinates of second dataframe.
    y1 : list of float
        Y coordinates of first dataframe.
    y2 : list of float
        Y coordinates of second dataframe.
    i_max : int
        Number of points of first dataframe.
    j_max : int
        Number of points of second dataframe.
    i_excl : list of int
        Exclusion list (indexes) of points of first dataframe.
    j_excl : list of int
        Exclusion list (indexes) of points of second dataframe.
    
    Returns
    -------
    i_min : int
        Selected point (index) of first dataframe.
    j_min : int
        Selected point (index) of second dataframe.
    d_min : float
        Distance between ``i_min`` and ``j_min``.
    
    See Also
    --------
    ``CMD_calc_frontiere``
    """
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
    """ [TA]\n
    Compute the mean distance of points from same dataframe.
    """
    l = len(x1)-1
    d = 0
    for i in range(l):
        d = d + (x1[i]-x1[i+1])**2 + (y1[i]-y1[i+1])**2
    return d / l

# Calcule une taille caractéristique de l'ensemble de points

def CMD_appr_taille_grp(x1,y1):
    """ [TA]\n
    Compute the diagonal distance of one dataframe.
    """
    x_min = min(x1)
    x_max = max(x1)
    y_min = min(y1)
    y_max = max(y1)
    d = (x_max-x_min)**2 + (y_max-y_min)**2
    return d

# Calcule la distance maximale entre deux points de la même frontière

def CMD_max_frontiere(x1,y1,excl):
    """ [TA]\n
    Compute the maximal distance of points from same dataframe in selected list.
    """
    d_max = 0
    for i in excl[:-1]:
        for j in excl[1:]:
            d = (x1[i]-x1[j])**2 + (y1[i]-y1[j])**2
            d_max = max(d_max,d)
    return d_max

# Renvoie les coefficients de décalage pour une variable donnée entre deux fichiers

def CMD_compute_coeff(col1,col2,excl1,excl2):
    """ [TA]\n
    Compute a and b in the adjustment relation of type a + bx between both dataframes.
    """
    sig1 = np.std([col1[i] for i in excl1])
    sig2 = np.std([col2[j] for j in excl2])
    
    t = len(excl1)
    diff = 0
    ec = sig1/sig2
    for j in range(t):
        diff = diff + col1[excl1[j]] - (col2[excl2[j]])*ec
    
    return diff/t, ec

# Fonction principale de l'étalonnage par base

def CMD_evol_profils(file_prof_list,file_base_list,col_z,sep='\t',replace=False,output_file_list=None,nb_ecarts=1,diff=True,auto_adjust=True,man_adjust=False,line=False):
    """ [TA]\n
    Main function for profile calibration from bases.\n
    See ``CMD_evol_profils_solo`` for more infos.
    
    Notes
    -----
    Each file is managed separately.\n
    If ``auto_adjust = False``, ignore ``file_base_list``.
    
    Parameters
    ----------
    file_prof_list : list of str
        List of profiles files to process.
    file_prof_list : list of str
        List of bases files to process, ordered as ``file_prof_list``.
    col_z : list of int
        Index of every Z coordinates columns (actual data).
    ``[opt]`` sep : str, default : ``'\\t'``
        Dataframe separator.
    ``[opt]`` replace : bool, default : ``False``
        If the previous file is overwritten.
    ``[opt]`` output_file_list : ``None`` or list of str, default : ``None``
        List of output files names, ordered as ``file_prof_list``, otherwise do not save the result (plot only).
    ``[opt]`` nb_ecarts : int, default : ``1``
        Number of X and Y columns. The number of coils.
    ``[opt]`` diff : bool, default : ``True``
        Define which adjustment method (difference or ratio) is used.
    ``[opt]`` auto_adjust : bool, default : ``True``
        Enables the first step.
    ``[opt]`` man_adjust : bool, default : ``False``
        Enables the second step.
    ``[opt]`` line : bool, default : ``False``
        Shows lines between profiles. Makes the visualization easier.

    Raises
    ------
    * ``file_prof_list``, ``file_base_list`` and/or ``output_file_list`` are different sizes.
    
    See also
    --------
    ``CMD_evol_profils_solo, TOOL_check_time_date``
    """
    print(auto_adjust)
    if auto_adjust and len(file_prof_list) != len(file_base_list):
        MESS_err_mess("Le nombre de fichiers profil ({}) et base ({}) ne correspondent pas".format(len(file_prof_list),len(file_base_list)))
    if output_file_list == None:
        MESS_warn_mess("Le résultat ne sera pas enregistré")
    elif not replace and len(file_prof_list) != len(output_file_list):
        MESS_err_mess("Le nombre de fichiers profil ({}) et résultat ({}) ne correspondent pas".format(len(file_prof_list),len(output_file_list)))
    for i in range(len(file_prof_list)):
        data_prof = TOOL_check_time_date(file_prof_list[i],sep)
        if auto_adjust:
            data_base = TOOL_check_time_date(file_base_list[i],sep)
        else:
            data_base = pd.DataFrame()
        res = CMD_evol_profils_solo(data_prof,data_base,file_prof_list[i],col_z,nb_ecarts,diff=diff,auto_adjust=auto_adjust,man_adjust=man_adjust,verif=True,line=line)
        if replace:
            res.to_csv(file_prof_list[i], index=False, sep=sep)
        elif output_file_list == None:
            continue
        else:
            res.to_csv(output_file_list[i], index=False, sep=sep)

# Détecte le décalage des données en fonction du temps grace à la base, puis propose une correction.
# Correction par différence si diff=True, sinon correction par proportion.

def CMD_evol_profils_solo(don,bas,nom_fich,col_z,nb_ecarts,diff=True,auto_adjust=True,man_adjust=False,verif=False,line=False):
    """ [TA]\n
    Given a profile database and an associated base database, perform profile calibration by alignment of bases (bases are supposed to give the same value each time).\n
    The operation is performed by difference, but it is also possible to perform it by multiplication (ratio).\n
    It is possible to request the rectification of profile blocks if other imperfections are visible, using ``man_adjust = True``.\n
    If you only want to perform this operation, you can disable the first step using the ``auto_adjust = False``.
    
    Notes
    -----
    If used as a standalone, plots every step.\n
    If ``auto_adjust = False``, ignore ``bas``.\n
    If both ``man_adjust`` and ``auto_adjust`` are set to false, nothing happens.
    
    Parameters
    ----------
    don : dataframe
        Profile dataframe.
    bas : dataframe
        Base dataframe.
    nom_fich : str
        Profile file name. Used in plots.
    col_z : list of int
        Index of every Z coordinates columns (actual data).
    nb_ecarts : int
        Number of X and Y columns. The number of coils.
    ``[opt]`` diff : bool, default : ``True``
        Define which adjustment method (difference or ratio) is used.
    ``[opt]`` auto_adjust : bool, default : ``True``
        Enables the first step.
    ``[opt]`` man_adjust : bool, default : ``False``
        Enables the second step.
    ``[opt]`` verif : bool, default : ``False``
        Enables plotting.
    ``[opt]`` line : bool, default : ``False``
        Shows lines between profiles. Makes the visualization easier.
    
    Returns
    -------
    don : dataframe
        Updated profile dataframe
    
    Raises
    ------
    * Profile dataframe is not interpolated.
    * Base dataframe does not contains a ``"Base"`` column.
    
    See also
    --------
    ``CMD_evol_profils, TOOL_check_time_date``
    """
    global GUI_VAR_LIST
    
    color = ["blue","green","orange","magenta","red","cyan","black","yellow"]
    if line:
        mrk = 'x-'
    else:
        mrk = 'x'
    
    try:
        prof_deb = don['Profil'].iat[0]
        prof_fin = don['Profil'].iat[-1]
    except KeyError:
        MESS_err_mess("Les données ne sont pas interpolées ({})".format(nom_fich))
    prof_l = prof_fin-prof_deb+1
    
    col_names = don.columns[col_z]
    nb_data = len(col_z)
    nb_res = nb_data//nb_ecarts
    
    prof_med = np.array([[0.0]*prof_l]*nb_data)
    prof_bp = []
    index_list = []
    
    for i in range(prof_l):
        prof = don[don["Profil"] == i+prof_deb]
        prof_bp.append(prof['b et p'].iat[0])
        index_list.append(prof.index[0])
        for j in range(nb_data):
            prof_med[j,i] = prof[col_names[j]].median()
    index_list.append(None)
    
    if auto_adjust:
        try:
            base_deb = bas['Base'].iat[0]
            base_fin = bas['Base'].iat[-1]
        except KeyError:
            MESS_err_mess("La base associée à {} n'est pas valide (elle doit provenir d'une fusion ou d'une interpolation)".format(nom_fich))
        base_l = base_fin-base_deb+1
        
        base_med = np.array([[0.0]*base_l]*nb_data)
        base_bp = []
        
        for i in range(base_l):
            base = bas[bas["Base"] == i+base_deb]
            base_bp.append(base['b et p'].iat[0])
            for j in range(nb_data):
                base_med[j,i] = base[col_names[j]].median()
        
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
            plt.pause(CONFIG.fig_render_time) # À augmenter si la figure ne s'affiche pas, sinon on pourra le baisser pour accélérer la vitesse de l'input
    
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
    
    if verif or man_adjust:
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
            plt.pause(CONFIG.fig_render_time) # À augmenter si la figure ne s'affiche pas, sinon on pourra le baisser pour accélérer la vitesse de l'input
            
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

def CMD_grid(col_x,col_y,col_z,file_list,sep='\t',output_file=None,m_type=None,radius=0,prec=100,step=None,seuil=0.0,i_method=None,only_nan=True,no_crop=False,all_models=False,plot_pts=False,matrix=False):
    """ [TA]\n
    From a data file, proposes gridding according to the method used.\n
    If ``m_type='h'``, then a heatmap of the point density is created. Useful for determining the threshold ``seuil``.\n
    If ``m_type='i'``, grid interpolation is performed using one of the following algorithms: ``nearest``, ``linear``, or ``cubic``.\n
    If ``m_type='k'``, a variogram selection process will then be runned to select the kriging parameters. Only cells detected by the previous algorithm will be considered.\n
    To define the dimensions of the grid, you can either set its size (``prec``) or its step (``step```).\n
    Be careful not to run kriging on a large dataset or a grid that is too precise, as this may result in the kriging process never being completed.
    
    Notes
    -----
    Does not make any meaningful computation on its own.\n
    Expected complexity is detailled in the ``CMD_dat_to_grid`` function.\n
    Does only exists as a standalone, is not part of the main process.
    
    Parameters
    ----------
    col_x : list of int
        Index of every X coordinates columns.
    col_y : list of int
        Index of every Y coordinates columns.
    col_z : list of int
        Index of every Z coordinates columns (actual data).
    file_list : list of str
        List of files to process.
    ``[opt]`` sep : str, default : ``'\\t'``
        Dataframe separator.
    ``[opt]`` output_file : ``None`` or str, default : ``None``
        Name of output file. If ``None``, do not save.
    ``[opt]`` m_type : str, ``None`` or {``'h'``, ``'i'``, ``'k'``}, default : ``None``
        Procedure type. If ``None``, will ask the user.
    ``[opt]`` radius : int, default : ``0``
        Detection radius around each tile for ``NaN`` completion.
    ``[opt]`` prec : int, default : ``100``
        Grid size of the biggest axis. The other one is deducted by proportionality.
    ``[opt]`` step : ``None`` or float, default : ``None``
        Step between each tile, according to the unit used by the position columns. If not ``None``, ignore ``prec`` value.
    ``[opt]`` seuil : float, default : ``0.0``
        Exponent of the function used to compute the detection window coefficients. If negative, will be set to 0 but widen the acceptance.
    ``[opt]`` i_method : str, ``None`` or {``'nearest'``, ``'linear'``, ``'cubic'``}, default : ``None``
        Interpolation method from scipy. If ``None``, will ask the user.
    ``[opt]`` only_nan : bool, default : ``True``
        If ``True``, tiles that contains at least one point are always kept. If ``False``, will remove those that are too eccentric.
    ``[opt]`` no_crop : bool, default : ``False``
        If dataframe must be cropped to 1000 points for kriging.
    ``[opt]`` all_models : bool, default : ``False``
        Enables all the variogram models. Some of them can *crash the kernel*.
    ``[opt]`` plot_pts : bool, default : ``False``
        Plots the raw points on top of the output grid.
    ``[opt]`` matrix : bool, default : ``False``
        Whether the output should be saved as a dataframe or as the custom 'matrix' format.
    
    
    Returns
    -------
    none, but ``CMD_grid_plot`` do.
    
    See also
    --------
    ``TOOL_check_time_date, TOOL_manage_cols, CMD_dat_to_grid, CMD_kriging, CMD_scipy_interp, CMD_grid_plot``
    """
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
        if prec >= 300 and step == None:
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
    
    grid, ext, pxy = CMD_dat_to_grid(don,ncx,ncy,nb_ecarts,nb_res,radius,prec,step,seuil,only_nan,heatmap=(m_type=='h'))
    
    if m_type == 'k':
        grid_k = CMD_kriging(don,ncx,ncy,ext,pxy,col_T,nb_data,nb_ecarts,nb_res,all_models=all_models,verif=False)
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
        i_method_list = ['nearest','linear','cubic','RBF_linear','RBF_thin_plate_spline','RBF_cubic','RBF_quintic']
                         #,'RBF_multiquadric','RBF_inverse_multiquadric','RBF_inverse_quadratic','RBF_gaussian'] RESTRICTION
        if i_method == None:
            correct = False
            while correct == False:
                if GUI:
                    MESS_input_GUI(["Type d'interpolation ?",""]+["~r~ "+m+[""," ~!~"][i==1] for i,m in enumerate(i_method_list)])
                    try:
                        inp = GUI_VAR_LIST[0]
                    except:
                        MESS_warn_mess("Veuillez sélectionner un réponse")
                        continue
                else:
                    MESS_input_mess(["Type d'interpolation ?",""]+[str(i)+" : "+m for i,m in enumerate(i_method_list)])
                    inp = input()
                try :
                    i_method = i_method_list[int(inp)]
                    correct = True
                except:
                    MESS_warn_mess("Réponse non reconnue !")
        elif i_method not in i_method_list:
            MESS_err_mess("Méthode non reconnue ({})".format(i_method_list))
        grid_i = CMD_scipy_interp(don,ncx,ncy,ext,pxy,col_T,nb_ecarts,nb_res,i_method)
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

def CMD_dat_to_grid(don,ncx,ncy,nb_ecarts,nb_res,radius=0,prec=100,step=None,seuil=0.0,only_nan=True,heatmap=False,verif=False):
    """ [TA]\n
    Put raw data on a grid, then determine which tile should be removed (with ``NaN`` value).\n
    Removal procedure is detailled in the ``CMD_calc_coeff`` description.
    If ``heatmap = True``, launch a trial process giving the effective selected grid area for a given ``seuil`` value.
    
    Notes
    -----
    Complexity :
        .. math:: O(d + p^2r^2) 
        where d is the number of points, p is ``prec`` and r is ``radius``.
        
    
    Parameters
    ----------
    don : dataframe
        Active dataframe.
    ncx : list of str
        Names of every X columns.
    ncy : list of str
        Names of every Y columns.
    nb_ecarts : int
        Number of X and Y columns. The number of coils.
    nb_res : int
        The number of data per coil.
    ``[opt]`` radius : int, default : ``0``
        Detection radius around each tile for ``NaN`` completion.
    ``[opt]`` prec : int, default : ``100``
        Grid size of the biggest axis. The other one is deducted by proportionality.
    ``[opt]`` step : ``None`` or float, default : ``None``
        Step between each tile, according to the unit used by the position columns. If not ``None``, ignore ``prec`` value.
    ``[opt]`` seuil : float, default : ``0.0``
        Exponent of the function used to compute the detection window coefficients. If negative, will be set to 0 but widen the acceptance.
    ``[opt]`` only_nan : bool, default : ``True``
        If ``True``, tiles that contains at least one point are always kept. If ``False``, will remove those that are too eccentric.
    ``[opt]`` heatmap : bool, default : ``False``
        If we compute the heatmap instead of the regular grid.
    ``[opt]`` verif : bool, default : ``False``
        Print some useful informations for testing.
    
    
    Returns
    -------
    grid_final : np.ndarray (dim 3) of float
        For each data column, contains the grid values (``0`` if tile is taken, ``NaN`` if not)
    ext : [float, float, float, float]
        Extend of the grid. Contains ``[min_X, max_X, min_Y, max_Y]``.
    pxy : [float, float]
        Size of the grid for each axis. Contains ``[prec_X, prec_Y]``.
    
    Raises
    ------
    * Some columns does not exist.
    * Some columns are not numeric.
    
    See also
    --------
    ``CMD_grid, CMD_heatmap_grid_calc, CMD_heatmap_plot``
    """
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
    if step == None:
        if diff_X > diff_Y:
            prec_X = prec
            prec_Y = int(prec*(diff_Y/diff_X))
        else:
            prec_Y = prec
            prec_X = int(prec*(diff_X/diff_Y))
        pas_X = diff_X/prec_X
        pas_Y = diff_Y/prec_Y
    else:
        pas_X = step
        pas_Y = step
        prec_X = int(diff_X/pas_X)+1
        prec_Y = int(diff_Y/pas_Y)+1

    gridx = [min_X + pas_X*i for i in range(prec_X)]
    gridy = [min_Y + pas_Y*j for j in range(prec_Y)]
    
    grid_conv, seuil, seuil_, quot = CMD_calc_coeff(seuil,radius)
    
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
        CMD_heatmap_plot(don,grid_final,grid[0],ncx[0],ncy[0],[min_X,max_X,min_Y,max_Y],[prec_X,prec_Y],seuil_)
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
                    grid_conv, seuil, seuil_, quot = CMD_calc_coeff(seuil,radius)
                    grid_final = CMD_heatmap_grid_calc(grid[0],grid_conv,prec_X,prec_Y,quot)
                    CMD_heatmap_plot(don,grid_final,grid[0],ncx[0],ncy[0],[min_X,max_X,min_Y,max_Y],[prec_X,prec_Y],seuil_)
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
                        if grid[e,j,i] != 0 and only_nan:
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

def CMD_calc_coeff(seuil,radius):
    """ [TA]\n
    Create the window for the grid.\n
    Removal procedure uses a circular window of radius ``radius``. Each tile is given a proximity coefficient from the center from 0 to 1.
    For each empty tile (containing no points), sum the coefficients of all non empty tiles included in the window.\n
    If the output sum surpasses ``quot``, we accept the tile. Otherwise, we will set its value to ``NaN``.
    
    Notes
    -----
    The ``mult`` variable is use if ``seuil < 0`` to continue the acceptance trend, while not creating a curve of negative exponent.
    
    Parameters
    ----------
    radius : int
        Detection radius around each tile for ``NaN`` completion.
    seuil : float
        Exponent of the function used to compute the detection window coefficients. If negative, will be set to 0 but widen the acceptance.
    
    Returns
    -------
    grid_conv : list of ``[x,y,coeff]``
        Contains every tile of the window with its x, y and associated coefficient.
    seuil : float
        Updated exponent. Is equal to ``max(seuil,0)``.
    seuil_ : float
        Original value of exponent.
    quot : float
        Quotient used to set the acceptance value of a tile.
    
    See also
    --------
    ``CMD_dat_to_grid``
    """
    grid_conv = []
    rc = radius**2
    seuil_ = seuil
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
    
    return grid_conv, seuil, seuil_, quot

# Calcul de la heatmap

def CMD_heatmap_grid_calc(grid,grid_conv,prec_X,prec_Y,quot):
    """ [TA]\n
    Associate a (positive) density coefficient to each tile.
    
    Notes
    -----
    Normally, a tile is included in the interpolation if its density coefficient is greater than ``quot``.\n
    For clarity, its density value is divided by ``quot``, so we can only check tiles acceptance by comparing their value to ``1``.\n
    Thus, il will be easier to judge by looking at the heatmap.
    
    Parameters
    ----------
    grid : np.ndarray (dim 2) of float
        Contains the number of points included in each tile. Only the emptiness (``0`` or ``> 0``) is important.
    grid_conv : list of ``[x,y,coeff]``
        Contains every tile of the window with its x, y and associated coefficient.
    prec_X : float
        Size of the grid for x axis.
    prec_Y : float
        Size of the grid for y axis.
    quot : float
        Quotient used to set the acceptance value of a tile.
    
    Returns
    -------
    grid_final : np.ndarray (dim 2) of float
        Contains the grid density values.
    
    See also
    --------
    ``CMD_dat_to_grid``
    """
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
    """ [TA]\n
    Plotting the heatmap results.
    To the left : the heatmap of density of each tile.
    To the right : the subgrid where only tiles of value > 1 are selected, which would be the selected area for interpolation/kriging.
    
    Parameters
    ----------
    don : dataframe
        Active dataframe.
    grid_final : list (dim 2) of float
        Contains the grid density score.
    grid : np.ndarray (dim 2) of float
        Contains the number of points located in each tile.
    ncx : list of str
        Names of every X columns.
    ncy : list of str
        Names of every Y columns.
    ext : [float, float, float, float]
        Extend of the grid. Contains ``[min_X, max_X, min_Y, max_Y]``.
    pxy : [float, float]
        Size of the grid for each axis. Contains ``[prec_X, prec_Y]``.
    seuil : float
        Exponent of the function used to compute the detection window coefficients. Can be negative, only used for plot display.

    Notes
    -----
    The ``don``parameter only serves to plot points and does not modify the grids.
    
    See also
    --------
    ``CMD_dat_to_grid``
    """
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
    plt.pause(CONFIG.fig_render_time) # À augmenter si la figure ne s'affiche pas, sinon on pourra le baisser pour accélérer la vitesse de l'input

# Effectue l'interpolation scipy selon le modèle choisi

def CMD_scipy_interp(don,ncx,ncy,ext,pxy,nc_data,nb_ecarts,nb_res,i_method):
    """ [TA]\n
    Interpolate data following one given method (``i_method``).\n
    If ``i_method`` starts with ``"RBF_"``, it is part of the radial basis function.
    
    Parameters
    ----------
    don : dataframe
        Active dataframe.
    ncx : list of str
        Names of every X columns.
    ncy : list of str
        Names of every Y columns.
    ext : [float, float, float, float]
        Extend of the grid. Contains ``[min_X, max_X, min_Y, max_Y]``.
    pxy : [float, float]
        Size of the grid for each axis. Contains ``[prec_X, prec_Y]``.
    nc_data : list of str
        Names of every Z columns (actual data).
    nb_ecarts : int
        Number of X and Y columns. The number of coils.
    nb_res : int
        The number of data per coil.
    i_method : str, {``'nearest'``, ``'linear'``, ``'cubic'``, ``'RBF_linear'``, ``'RBF_thin_plate_spline'``, ``'RBF_cubic'``, ``'RBF_quintic'``, \
    ``'RBF_multiquadric'``, ``'RBF_inverse_multiquadric'``, ``'RBF_inverse_quadratic'``, ``'RBF_gaussian'``}
        Interpolation method from scipy.
    
    Returns
    -------
    grid_interp : np.ndarray (dim 3) of float
        For each data column, contains the grid interpolation values.
    
    Notes
    -----
    scipy has a automatic built-in method for convex cropping the grid, but the process will use the ``CMD_dat_to_grid`` crop.\n
    The last 4 methods of RBF are not to be used as of now. Otherwise, the ``epsilon`` parameter has to be modified.
    
    Raises
    ------
    * Columns contain NaN (probably not interpolated).
    
    See also
    --------
    ``CMD_grid, np.mgrid, scipy.interpolate.griddata, scipy.interpolate.RBFInterpolator``
    """
    print("=== Phase d'interpolation ===")
    
    gd = i_method in ['nearest','linear','cubic']
    
    grid_interp = []
    if gd:
        gridx, gridy = np.mgrid[ext[0]:ext[1]:pxy[0]*1j, ext[2]:ext[3]:pxy[1]*1j]
    else:
        gridxy = np.mgrid[ext[0]:ext[1]:pxy[0]*1j, ext[2]:ext[3]:pxy[1]*1j]
    
    for e in range(nb_ecarts):
        pos_data = don[[ncx[e],ncy[e]]].to_numpy()
        for r in range(nb_res):
            n = e*nb_res + r
            val_data = list(don[nc_data[n]])
            try:
                if gd:
                    grid_interp.append(scii.griddata(pos_data, val_data, (gridx, gridy), method=i_method))
                else:
                    flat = gridxy.reshape(2, -1).T
                    grid_flat = scii.RBFInterpolator(pos_data, val_data, kernel=i_method[4:], epsilon=1)(flat)
                    grid_res = np.array([[np.nan for j in range(pxy[1])] for i in range(pxy[0])])
                    for ic,gf in enumerate(grid_flat):
                        i = ic//pxy[1]
                        j = ic%pxy[1]
                        grid_res[i][j] = gf
                    grid_interp.append(grid_res)
            except ValueError:
                MESS_err_mess('NaN détecté dans les colonnes "{}", "{}" et/ou "{}"'.format(ncx[e],ncy[e],nc_data[n]))
        
    return grid_interp

# Effectue le kriging

def CMD_kriging(don,ncx,ncy,ext,pxy,nc_data,nb_data,nb_ecarts,nb_res,all_models=False,verif=False):
    """ [TA]\n
    Main loop for kriging.\n
    Set the right columns for X, Y and Z, asks for both experimental and theoretical variograms
    
    Parameters
    ----------
    don : dataframe
        Active dataframe.
    ncx : list of str
        Names of every X columns.
    ncy : list of str
        Names of every Y columns.
    ext : [float, float, float, float]
        Extend of the grid. Contains ``[min_X, max_X, min_Y, max_Y]``.
    pxy : [float, float]
        Size of the grid for each axis. Contains ``[prec_X, prec_Y]``.
    nc_data : list of str
        Names of every Z columns (actual data).
    nb_data : int
        Number of Z columns. The number of data.
    nb_ecarts : int
        Number of X and Y columns. The number of coils.
    nb_res : int
        The number of data per coil.
    ``[opt]`` all_models : bool, default : ``False``
        Add advanced models to selection. Some are expected to crash.
    ``[opt]`` verif : bool, default : ``False``
        Enables plotting and print grid infos
    
    Returns
    -------
    grid : np.ndarray (dim 3) of float
        For each data column, contains the grid kriging values.
    
    Notes
    -----
    Most of the procedure is made by the ``CMD_variog + suffix`` functions.
    
    See also
    --------
    ``CMD_grid, CMD_variog, gstlearn.DbGrid, gstlearn.kriging, gstlearn.Db.setLocator``
    """
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

def CMD_variog(dat,all_models=False):
    """ [TA]\n
    Main loop for variogram computation.\n
    **TO DO :** Fuse multiple variograms of different directions into one single model.
    
    Parameters
    ----------
    dat : gstlearn.Db
        Database object of active dataframe.
    ``[opt]`` all_models : bool, default : ``False``
        Add advanced models to selection. Some are expected to crash.
    
    Returns
    -------
    fitmod : gstlearn.Model
        Effective variogram model.
    
    Notes
    -----
    Subfunction of ``CMD_kriging``.
    
    See also
    --------
    ``CMD_kriging, CMD_variog_dir_params, CMD_variog_fit, gstlearn.plot.varmod``
    """
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
    # plt.pause(CONFIG.fig_render_time) # À augmenter si la figure ne s'affiche pas, sinon on pourra le baisser pour accélérer la vitesse de l'input
    
    return fitmod

# Fait le choix des paramètres du variogramme expérimental

def CMD_variog_dir_params(dat):
    """ [TA]\n
    Main loop for experimental variogram.\n
    Asks for the number of desired directions, then verify for one if they are correct by user input.
    **TO DO** Currently, the second direction is idle (see ``CMD_variog``)
    Compute the experimental variogram from parameters set by user at execution time.\n
    
    Parameters
    ----------
    dat : gstlearn.Db
        Database object of active dataframe.
    
    Returns
    -------
    vario_list : list of gstlearn.VarioParam
        List of all experimental variograms (for each direction).
    
    Notes
    -----
    Subfunction of ``CMD_variog``.
    
    See also
    --------
    ``CMD_variog, CMD_variog_dir_params_choice, gstlearn.Vario.compute``
    """
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
                varioParamMulti = CMD_variog_dir_params_choice(varioParamMulti,n=1)
                varioParamMulti2 = CMD_variog_dir_params_choice(varioParamMulti2,n=2)
                correct = True
            elif inp == "n":
                varioParamMulti = CMD_variog_dir_params_choice(varioParamMulti,n=1)
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
        plt.pause(CONFIG.fig_render_time) # À augmenter si la figure ne s'affiche pas, sinon on pourra le baisser pour accélérer la vitesse de l'input
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

def CMD_variog_dir_params_choice(varioParamMulti,n=1):
    """ [TA]\n
    Compute the experimental variogram from parameters set by user at execution time.\n
    
    Parameters
    ----------
    varioParamMulti : list of gstlearn.VarioParam
        Empty variogram.
    ``[opt]`` n : int, default : ``1``
        Index of the direction in the full procedure. Only useful in prints.
    
    Returns
    -------
    varioParamMulti : list of gstlearn.VarioParam
        Experimental variogram with selected direction.
    
    Notes
    -----
    Subfunction of ``CMD_variog_dir_params``.
    
    See also
    --------
    ``CMD_variog_dir_params, gstlearn.DirParam``
    https://soft.minesparis.psl.eu/gstlearn/1.7.2/doxygen/classDirParam.html
    """
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

def CMD_variog_fit(variodir,all_models=False):
    """ [TA]\n
    Compute the experimental variogram from parameters set by user at execution time.\n
    Organize the selection of the variogram model types.
    
    Parameters
    ----------
    dat : gstlearn.Db
        Database object of active dataframe.
    ``[opt]`` all_models : bool, default : ``False``
        Add advanced models to selection. Some are expected to crash.
    
    Returns
    -------
    fitmod : gstlearn.Model
        Effective variogram model.
    
    Notes
    -----
    Subfunction of ``CMD_variog``.
    Constants starts with a ``_`` and their order correspond the the built-in index of each gstlearn component. It should not be modified.
    
    See also
    --------
    ``CMD_variog, gstlearn.Constraints.addItemFromParamId, gstlearn.ECov.fromValue, gstlearn.EConsElem.fromValue, gstlearn.EConsType.fromValue``
    """
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
            plt.pause(CONFIG.fig_render_time) # À augmenter si la figure ne s'affiche pas, sinon on pourra le baisser pour accélérer la vitesse de l'input
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
    """ [TA]\n
    Organize the selection of the variogram model constraints.\n
    ``_ConsElem_exist`` contains whether the constraint exists for the current model, ordered as in the ``_ConsElem_print``.
    Each subset of the 2D list correspond to the respective model in the ``_Types_print`` constant of ``CMD_variog_fit``.
    
    Parameters
    ----------
    var_id : int
        Index of the current model.
    
    Returns
    -------
    constr_list : [int, int, int , float]
        Contains the indexes of each constraint elements and the associated value.
    
    Notes
    -----
    Subfunction of ``CMD_variog_fit``\n
    Constants starts with a ``_`` and their order correspond the the built-in index of each gstlearn component. It should not be modified.\n
    Some 'advanced' models are apparently not fonctionnal and kill the kernel.
    In particular, if a model is marked as accepting all constraints, it means that it crashes the kernel (in all known cases).
    
    See also
    --------
    ``CMD_variog_fit``
    """
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

def CMD_grid_plot(don,grid_final,ncx,ncy,ext,pxy,nc_data,nb_ecarts,nb_res,output_file=None,sep='\t',plot_pts=False,matrix=False):
    """ [TA]\n
    Plot the result of ``CMD_grid``.
    
    Parameters
    ----------
    don : dataframe
        Active dataframe.
    grid_final : np.ndarray (dim 3) of float
        For each data column, contains the grid values after the chosen method.
    ncx : list of str
        Names of every X columns.
    ncy : list of str
        Names of every Y columns.
    ext : [float, float, float, float]
        Extend of the grid. Contains ``[min_X, max_X, min_Y, max_Y]``.
    pxy : list of 4 floats
        Steps of the grid for each axis. Contains ``[pas_X, pas_Y]``.
    nc_data : list of str
        Names of every Z columns (actual data).
    nb_ecarts : int
        Number of X and Y columns. The number of coils.
    nb_res : int
        The number of data per coil.
    ``[opt]`` output_file : ``None`` or str, default : ``None``
        Name of output file. If ``None``, do not save.
    ``[opt]`` sep : str, default : ``'\\t'``
        Dataframe separator.
    ``[opt]`` plot_pts : bool, default : ``False``
        Plots the raw points on top of the grid.
    ``[opt]`` matrix : bool, default : ``False``
        Whether the output should be saved as a dataframe or as the custom 'matrix' format.
    
    Returns
    -------
    none, but plots the final grid and saves the figures.\n
    * ``output_file = None``
        Nothing more
    * ``output_file != None``
        Saves the grid in a dataframe or in the custom 'matrix format'.
    
    Notes
    -----
    Subfunction of ``CMD_grid``\n
    Is not called if heatmap was activated.
    
    See also
    --------
    ``CMD_grid, TRANS_df_to_matrix``
    """
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
        plt.pause(CONFIG.fig_render_time) # À augmenter si la figure ne s'affiche pas, sinon on pourra le baisser pour accélérer la vitesse de l'input
        plt.savefig(CONFIG.script_path+"Output/CMDEX_g_" +str(i)+'.png')
        pickle.dump(fig, open(CONFIG.script_path+"Output/CMDEX_g_" +str(i)+'.pickle', 'wb'))

# Estime les coefficients de la relation quasi-linéaire sur la conductivité

def CMD_coeffs_relation(X,Y,m_type="linear",choice=False,conv=True,nb_conv=50,plot=False):
    """ [TA]\n
    Given two arrays ``X`` and ``Y``, compute the coefficients of the chosen regression.\n
    To be used in the context of finding a formula for a physical relation.
    
    Parameters
    ----------
    X : np.array of float
        X axis of relation.
    Y : np.array of float
        Y axis of relation.
    ``[opt]`` m_type : str, {``"linear"``, ``"poly_3"``, ``"inverse_3"``}, default : ``"linear"``
        Type of wanted relation.\n
        * ``"linear"`` is a simple linear regression.
            .. math::
                a + bx
        * ``"poly_3"`` is a polynomial regression of degree 3.
            .. math::
                a + bx + cx^{2} + dx^{3}
        * ``"inverse_3"`` is a symetrical relation of ``"poly_3"``.
            .. math::
                a + bx + cx^{\\frac{1}{2}} + dx^{\\frac{1}{3}}
    ``[opt]`` choice : bool, default : ``False``
        Allows the user to chose which regression estimator fits the best (between numpy's `polyfit` as 'linear' \
        and sklearn's `TheilSenRegressor` and `HuberRegressor`). If ``False``, choose `HuberRegressor`. Ignored if ``m_type = linear``.
    ``[opt]`` conv : bool, default : ``True``
        If ``m_type = inverse_3``, uses an iterative method to estimate the coefficients. Otherwise, uses a simple linear system.\n
        The iterative method usually gives better results but is a bit slower.
    ``[opt]`` nb_conv : int, default : ``50``
        If ``conv = True``, represent the number of points used for the iterative method. Taking more points is slower but more precise.
    ``[opt]`` plot : bool, default : ``False``
        Plots all steps.
    
    Returns
    -------
    model : list of float
        List of found coefficients for the chosen method (2 for linear, else 4).
    
    Notes
    -----
    [DEV] The ``conv`` parameter may be removed if one of the two procedure is deemed better in all cases.
    
    See also
    --------
    ``FORTRAN_new_const, CMD_poly_regr, CMD_convergence_inv_poly``
    """
    if plot or (choice and m_type != "linear"):
        fig,ax=plt.subplots(nrows=1,ncols=1,figsize=(CONFIG.fig_width,CONFIG.fig_height))
        ax.plot(X,Y,'+',label="Points initiaux")
        ax.set_xlabel(r"signal(ph)")
        ax.set_ylabel(r"$\sigma$")
    if m_type == "linear":
        l_r = linregress(X,Y)
        if plot:
            ax.plot(X,l_r.intercept+X*l_r.slope,'o',ms=1,label="Régression linéaire")
            ax.set_title("Modèle linéaire VS nuage de points")
            plt.legend()
        return [l_r.intercept, l_r.slope]
    else:
        if choice:
            l = ["linear","theilsen","huber"]
        else:
            l = ["huber"]
        if m_type == "poly_3":
            p_r = CMD_poly_regr(X,Y,choice)
            p_r_list = []
            for i,c in enumerate(p_r):
                p_r_list.append(c[0]+c[1]*X+c[2]*X**2+c[3]*X**3)
                if plot or choice:
                    ax.plot(X,p_r_list[i],"o",ms=1,label=l[i])
        else:
            p_r = CMD_poly_regr(Y,X,choice)
            p_r_list = []
            for i,c in enumerate(p_r):
                p_r_list.append(c[0]+c[1]*Y+c[2]*Y**2+c[3]*Y**3)
                if plot or choice:
                    ax.plot(p_r_list[i],Y,"o",ms=1,label=l[i])
        if plot or choice:
            ax.set_title("Modèles VS nuage de points")
            plt.legend()
            plt.show(block=False)
            plt.pause(CONFIG.fig_render_time) # À augmenter si la figure ne s'affiche pas, sinon on pourra le baisser pour accélérer la vitesse de l'input
        if choice:
            correct = False
            while correct == False:
                if GUI:
                    MESS_input_GUI(["Quel modèle choisir ?","","~r~ linear","~r~ theilsen ~!~","~r~ huber"])
                    try:
                        inp = GUI_VAR_LIST[0]
                    except:
                        MESS_warn_mess("Veuillez sélectionner un réponse")
                        continue
                else:
                    MESS_input_mess(["Quel modèle choisir ?","","0 : linear","1 : theilsen","2 : huber"])
                    inp = input()
                try:
                    inp = int(inp)
                    if m_type == "poly_3":
                        model = p_r[inp]
                    else:
                        model = p_r_list[inp]
                    correct = True
                except ValueError:
                    MESS_warn_mess("Réponse non reconnue !")
                except IndexError:
                    MESS_warn_mess("Le modèle {} n'existe pas !".format(inp))
            plt.close(fig)
        else:
            if m_type == "poly_3":
                model = p_r[0]
            else:
                model = p_r[0][0]+p_r[0][1]*Y+p_r[0][2]*Y**2+p_r[0][3]*Y**3
        
        if m_type == "poly_3":
            return list(model)
        
        nb_pts = len(Y)
        if conv:
            mc = len(Y)/(nb_conv**2)
            npc_l = np.array([int(mc*i**2) for i in range(nb_conv)])
            X_c = model[npc_l]
            Y_c = Y[npc_l]
            fc = CMD_convergence_inv_poly(Y_c,X_c,nb_conv) # Inversion X et Y
        else:
            npc_l = np.array([0,nb_pts//3,2*nb_pts//3,nb_pts-1])
            X_c = model[npc_l]
            X_c_l = np.array([[1,xi,xi**(1/2),xi**(1/3)] for xi in X_c])
            Y_c = Y[npc_l]
            fc = np.linalg.solve(X_c_l, Y_c)
        
        if plot:
            X_plot = np.linspace(min(model),max(model),100)
            fig,ax=plt.subplots(nrows=1,ncols=1,figsize=(CONFIG.fig_width,CONFIG.fig_height))
            ax.plot(model,Y,"o",ms=7,label="Estimation")
            ax.plot(X_plot,fc[0]+fc[1]*X_plot+fc[2]*X_plot**(1/2)+fc[3]*X_plot**(1/3),"-",label="Modèle inverse")
            ax.set_title("Allure de la relation")
            ax.set_xlabel(r"signal(ph)")
            ax.set_ylabel(r"$\sigma$")
            plt.legend()
            plt.show(block=False)
            plt.pause(CONFIG.fig_render_time) # À augmenter si la figure ne s'affiche pas, sinon on pourra le baisser pour accélérer la vitesse de l'input
        return fc

def CMD_poly_regr(X,Y,choice=False):
    """ [TA]\n
    Given two arrays ``X`` and ``Y``, compute the coefficients of the polynomial regression.\n
    To be used in the context of finding a formula for a physical relation.
    
    Parameters
    ----------
    X : np.array of float
        X axis of relation.
    Y : np.array of float
        Y axis of relation.
    ``[opt]`` choice : bool, default : ``False``
        Allows the user to chose which regression estimator fits the best (between numpy's `polyfit`\
        and sklearn's `TheilSenRegressor` and `HuberRegressor`). If ``False``, choose `HuberRegressor`
    
    Returns
    -------
    coefs_list : list of float
        List of found coefficients for the chosen method (2 for linear, else 4).
    
    Notes
    -----
    Subfunction of ``CMD_coeffs_relation``.\n
    sklearn's estimators are glitchy and returns half the value of degree 0 coefficient. Hence it is manually doubled
    
    See also
    --------
    ``CMD_coeffs_relation, sklearn.preprocessing.PolynomialFeatures, sklearn.pipeline.make_pipeline``
    """
    x = X.copy()
    y = Y.copy()

    coefs_list = []
    xd = x[:,np.newaxis]
    if choice:
        mymodel = np.poly1d(np.polyfit(x, y, 3))
        
        coefs = mymodel.c[::-1]
        coefs_list.append(coefs)
        
        r = np.random.randint(10000)
        estimator = [TheilSenRegressor(random_state=r),HuberRegressor(),]
    else:
        estimator = [HuberRegressor()]
    
    for i,e in enumerate(estimator):
        poly = PolynomialFeatures(3)
        model = make_pipeline(poly, e)
        model.fit(xd, y)
        coefs = e.coef_
        coefs[0] *= 2
        coefs_list.append(coefs)
            
    return coefs_list

def CMD_mse(X,Y,c):
    """ [TA]\n
    Compute the mean square error between the ``Y`` of the polynomial model (target) and the ``new_Y`` of the current inverse model.
    Is the main convergence critera for the iterative method.
    
    Parameters
    ----------
    X : np.array of float
        X axis of relation.
    Y : np.array of float
        Y axis of relation.
    c : [float, float, float, float]
        List of coefficients of the current inverse model.
    
    Returns
    -------
    mse : float
        Mean square error between ``Y`` and ``new_Y``.
    
    Notes
    -----
    Subfunction of ``CMD_convergence_inv_poly`` and ``CMD_convergence_inv_step``.\n
    """
    new_Y = c[0] + c[1]*X + c[2]*X**(1/2) + c[3]*X**(1/3)
    mse = sum((new_Y - Y)**2)
    return mse
    

def CMD_convergence_inv_poly(X,Y,nb_pts,nb_tours=1000,force_fin=25,verif=False):
    """ [TA]\n
    Given two arrays ``X`` and ``Y``, converges to a transposed polynomial formula with an inverse polynomial formula (see ``CMD_coeffs_relation``, ``"inverse_3"``).
    
    Parameters
    ----------
    X : np.array of float
        X axis of relation.
    Y : np.array of float
        Y axis of relation.
    nb_pts : int
        Number of points used for the iterative method (length of ``X`` and ``Y``). Taking more points is slower but more precise.
    ``[opt]`` nb_tours : int, default : ``1000``
        Number of loops for each iterative cycle. At the end, check if mse is lower that the ``fin_mse`` threshold. Otherwise, redo a cycle.
    ``[opt]`` force_fin : int, default : ``25``
        Number of maximum cycles. Upon reach, return the final result regardless of its relevance.
    ``[opt]`` verif : bool, default : ``False``
        Prints some relevant informations each cycle for tesing purposes.
    
    Returns
    -------
    best_cl : list of float
        List of best found coefficients.
    
    Notes
    -----
    Subfunction of ``CMD_coeffs_relation``.\n
    Description of the method :\n
    The algorithm is a probabilistic iterative method minimizing the mean square error between the target ``Y`` and the current model (``CMD_mse``).
    For each step, one of the four coefficients is chosen randomly. It is set to a value which is in a local minimum for mse.
    If the current model is better, we keep it. Else, its is kept with a certain probability (``CMD_convergence_inv_step``).
    The overall best model is saved as ``best_cl``.
    The maximum number of steps is ``nb_tours * force_fin``.
    
    See also
    --------
    ``CMD_coeffs_relation, CMD_convergence_inv_step, CMD_mse``
    """
    coef_list = [float(min(X)), float((max(Y)-min(Y))/(max(X)-min(X))), 0, 0]
    current_coef = 3
    diff_y = max(Y)-min(Y)
    fin = False
    fin_mse = diff_y/5
    if verif:
        print("fin : ",fin_mse)
    best_mse = np.inf
    best_cl = coef_list.copy()
    cpt = 0
    while not fin:
        for i in range(nb_tours):
            mse = CMD_mse(X,Y,coef_list)
            r = np.random.randint(4)
            coef_list, mse = CMD_convergence_inv_step(X,Y,coef_list,mse,current_coef)
            current_coef = r
            if best_mse > mse:
                best_mse = mse
                best_cl = coef_list.copy()
            cpt += 1
        if verif:
            print(best_mse)
        if best_mse < fin_mse or cpt >= nb_tours*force_fin:
            fin = True
    if verif:
        print(cpt," ",fin_mse," ",best_mse)
    return best_cl
    
def CMD_convergence_inv_step(X,Y,coef_list,mse,cc):
    """ [TA]\n
    Perform one step of the iterative method.
    Converges to the best mean square error by incrementing the chosen parameter (of index ``cc``) by a fixed value until mse increases.\n
    Then, go the other way with a step twice as small, until the step is small enough.
    
    Parameters
    ----------
    X : np.array of float
        X axis of relation.
    Y : np.array of float
        Y axis of relation.
    coefs_list : list of float
        List of current coefficients.
    mse : float
        Mean square error with the initial configuration.
    cc : int, {``0``, ``1``, ``2``, ``3``}
        Index of the coefficient to iterate on.
    
    Returns
    -------
    best_cl : list of float
        List of best found coefficients.
    
    Notes
    -----
    Subfunction of ``CMD_convergence_inv_poly``.\n

    See also
    --------
    ``CMD_convergence_inv_poly, CMD_mse``
    """
    cl_cpy = coef_list.copy()
    sign = True
    fin = False
    prev_mse = mse
    step = 1
    while not fin:
        mse = CMD_mse(X,Y,cl_cpy)
        if mse > prev_mse:
            sign = not sign
            step /= 2
            r = np.random.random()
            if r > np.exp(-(mse/prev_mse)*3):
                cl_cpy[cc] = coef_list[cc]
            else:
                prev_mse = mse
                coef_list[cc] = cl_cpy[cc]
        else:
            prev_mse = mse
            coef_list[cc] = cl_cpy[cc]
        cl_cpy[cc] += (int(not sign) - int(sign))*step
        if step < 0.01:
            fin = True
    return coef_list, prev_mse

# Change la date dans un fichier .dat

def DAT_change_date(file_list,date_str,sep='\t',replace=False,output_file_list=None,not_in_file=False):
    """ [TA]\n
    Change the date of a dataframe.
    
    Notes
    -----
    Date format is *mm/dd/yyyy*.
    
    Parameters
    ----------
    file_list : list of str
        List of files to process.
    date_str : str
        New date in the correct date format.
    ``[opt]`` sep : str, default : ``'\\t'``
        Dataframe separator.
    ``[opt]`` replace : bool, default : ``False``
        If the previous file is overwritten.
    ``[opt]`` output_file_list : ``None`` or list of str, default : ``None``
        List of output files names, ordered as ``file_list``, otherwise add the suffix ``"_corr"``. Is ignored if ``replace = True``.
    ``[opt]`` not_in_file : bool, default : ``False``
        If call comes from script function instead of user.
    
    Returns
    -------
    * ``not_in_file = False``
        none, but save output dataframe in a .dat
    * ``not_in_file = True``
        df : dataframe
            Output dataframe.
    
    Raises
    ------
    * File not found.
    * Wrong separator or ``"Date"`` column not found.
    * ``file_list`` and ``output_file_list`` are different sizes.
    * Invalid date.
    """
    if output_file_list != None and len(file_list) != len(output_file_list) and not replace and not not_in_file:
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

def DAT_pop_and_dec(file_list,colsup,sep='\t',replace=False,output_file_list=None,not_in_file=False):
    """ [TA]\n
    Remove specified column name from dataframe.\n
    Does not interfere with the data.
    To be used if some column labels are not associated with any data to avoid shifts.
    
    Notes
    -----
    Most functions in CMD processes are loading data with ``TOOL_check_time_date``, which should handle this issue for ``"Date"`` and ``"Time"`` columns.
    
    Parameters
    ----------
    file_list : list of str
        List of files to process.
    colsup : str
        Column label to remove.
    ``[opt]`` sep : str, default : ``'\\t'``
        Dataframe separator.
    ``[opt]`` replace : bool, default : ``False``
        If the previous file is overwritten.
    ``[opt]`` output_file_list : ``None`` or list of str, default : ``None``
        List of output files names, ordered as ``file_list``, otherwise add the suffix ``"_corr"``. Is ignored if ``replace = True``.
    ``[opt]`` not_in_file : bool, default : ``False``
        If call comes from script function instead of user.
    
    Returns
    -------
    * ``not_in_file = False``
        none, but save output dataframe in a .dat
    * ``not_in_file = True``
        shift_df : dataframe
            Output dataframe.
    
    Raises
    ------
    * File not found.
    * Wrong separator or column not found.
    * ``file_list`` and ``output_file_list`` are different sizes.
    """
    if output_file_list != None and len(file_list) != len(output_file_list) and not replace and not not_in_file:
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

def DAT_switch_cols(file_list,col_a,col_b,sep='\t',replace=False,output_file_list=None,not_in_file=False):
    """ [TA]\n
    Switches specified column names from dataframe.\n
    Does not interfere with the data.
    To be used if some columns labels are mismatched, like X and Y being misplaced.
    
    Parameters
    ----------
    file_list : list of str
        List of files to process.
    col_a: str
        First column label to switch.
    col_b: str
        Second column label to switch.
    ``[opt]`` sep : str, default : ``'\\t'``
        Dataframe separator.
    ``[opt]`` replace : bool, default : ``False``
        If the previous file is overwritten.
    ``[opt]`` output_file_list : ``None`` or list of str, default : ``None``
        List of output files names, ordered as ``file_list``, otherwise add the suffix ``"_corr"``. Is ignored if ``replace = True``.
    ``[opt]`` not_in_file : bool, default : ``False``
        If call comes from script function instead of user.
    
    Returns
    -------
    * ``not_in_file = False``
        none, but save output dataframe in a .dat
    * ``not_in_file = True``
        df : dataframe
            Output dataframe.
    
    Raises
    ------
    * File not found.
    * Wrong separator or column not found.
    * ``file_list`` and ``output_file_list`` are different sizes.
    """
    if output_file_list != None and len(file_list) != len(output_file_list) and not replace and not not_in_file:
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

def DAT_remove_cols(file_list,colsup_list,keep=False,sep='\t',replace=False,output_file_list=None,not_in_file=False):
    """ [TA]\n
    Remove specified columns from dataframe.\n
    To be used if some columns are not significant to lighten data or improve readability.
    
    Notes
    -----
    For a more automatic procedure, see ``DAT_light_format``.
    
    Parameters
    ----------
    file_list : list of str
        List of files to process.
    colsup_list: list of str
        Column names.
    ``[opt]`` keep : bool, default : ``False``
        If the specified columns are to be kept, and removing the others instead.
    ``[opt]`` sep : str, default : ``'\\t'``
        Dataframe separator.
    ``[opt]`` replace : bool, default : ``False``
        If the previous file is overwritten.
    ``[opt]`` output_file_list : ``None`` or list of str, default : ``None``
        List of output files names, ordered as ``file_list``, otherwise add the suffix ``"_corr"``. Is ignored if ``replace = True``.
    ``[opt]`` not_in_file : bool, default : ``False``
        If call comes from script function instead of user.
    
    Returns
    -------
    * ``not_in_file = False``
        none, but save output dataframe in a .dat
    * ``not_in_file = True``
        small_df : dataframe
            Output dataframe.
    
    Raises
    ------
    * File not found.
    * Wrong separator or columns not found.
    * ``file_list`` and ``output_file_list`` are different sizes.
    
    See also
    --------
    ``DAT_light_format``
    """
    if output_file_list != None and len(file_list) != len(output_file_list) and not replace and not not_in_file:
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

def DAT_remove_data(file_list,colsup_list,i_min,i_max,sep='\t',replace=False,output_file_list=None,not_in_file=False):
    """ [TA]\n
    Remove data between two lines in specified columns from dataframe.\n
    In this context, deleting means setting values to ``NaN``.\n
    To be used if some column contains incorrect data.
    
    Notes
    -----
    Both first and last lines are included in the deletion.\n
    The first line of ``df`` is indexed at ``0``, since its how it is labelled in pandas.
    Consequently, line indexes may not match if opened with a regular text editor.\n
    To ease the detection of problematic lines, the ``DAT_min_max_col`` function can be used.
    
    Parameters
    ----------
    file_list : list of str
        List of files to process.
    colsup_list: list of str
        Column names.
    i_min : bool
        First line of the block.
    i_max : bool
        Last line of the block.
    ``[opt]`` sep : str, default : ``'\\t'``
        Dataframe separator.
    ``[opt]`` replace : bool, default : ``False``
        If the previous file is overwritten.
    ``[opt]`` output_file_list : ``None`` or list of str, default  ``None``
        List of output files names, ordered as ``file_list``, otherwise add the suffix ``"_corr"``. Is ignored if ``replace = True``.
    ``[opt]`` not_in_file : bool, default : ``False``
        If call comes from script function instead of user.
    
    Returns
    -------
    * ``not_in_file = False``
        none, but save output dataframe in a .dat
    * ``not_in_file = True``
        df : dataframe
            Output dataframe.
    
    Raises
    ------
    * File not found.
    * Wrong separator or columns not found.
    * ``file_list`` and ``output_file_list`` are different sizes.
    * Indexes are not ordered correctly.
    * Index is negative.
    * Index goes beyond dataframe.
    
    See also
    --------
    ``DAT_min_max_col``
    """
    if output_file_list != None and len(file_list) != len(output_file_list) and not replace and not not_in_file:
        MESS_err_mess("Le nombre de fichiers entrée ({}) et sortie ({}) ne correspondent pas".format(len(file_list),len(output_file_list)))
    if i_min > i_max:
        MESS_err_mess("La ligne de fin ({}) et avant celle du début ({})".format(i_max,i_min))
    if i_min < 0:
        MESS_err_mess("La fonction ne prend pas en compte les indices négatifs")
    for ic, file in enumerate(file_list):
        try:
            df = pd.read_csv(file, sep=sep, dtype=object)
        except FileNotFoundError:
            MESS_err_mess('Le fichier "{}" est introuvable'.format(file))
        
        try:
            col_list = df[colsup_list]
        except KeyError:
            MESS_err_mess("Le fichier '{}' ne contient pas les colonnes {}, le séparateur {} est-il correct ?".format(file,colsup_list,repr(sep)))
        
        if i_max >= len(df):
            MESS_err_mess("Indice '{}' en dehors du data frame (taille {})".format(i_max,len(df)))
        for index, row in df[i_min:i_max+1].iterrows():
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

# Génère des histogrammes sur des colonnnes spécifiées
# Permet d'afficher les valeurs extrêmes d'une colonne, pour potentiellement détecter des données à retirer

def DAT_stats(file_list,col_list,sep='\t',bins=25,n=10,**kwargs):
    """ [TA]\n
    Prints the top and bottom ``n`` values of the requested columns.
    To be used to find extreme values that are due to glitches.
    
    Parameters
    ----------
    file_list : list of str
        List of files to process.
    col_list: list of str
        Column names.
    ``[opt]`` sep : str, default : ``'\\t'``
        Dataframe separator.
    ``[opt]`` bins : int, default : ``25``
        Number of bars in histogram.
    ``[opt]`` n : int, default : ``10``
        Number of top values to print.
    **kwargs
        Optional arguments for ``pandas.Dataframe.hist`` that are not ``column`` (overwritten).
    
    Raises
    ------
    * File not found.
    * Wrong separator or columns not found.
    
    See also
    --------
    ``pandas.Dataframe.hist``
    """
    for ic, file in enumerate(file_list):
        try:
            df = pd.read_csv(file, sep=sep)
        except FileNotFoundError:
            MESS_err_mess('Le fichier "{}" est introuvable'.format(file))
        
        try:
            cl = df[col_list]
        except KeyError:
            MESS_err_mess("Le fichier '{}' ne contient pas les colonnes {}, le séparateur {} est-il correct ?".format(file,col_list,repr(sep)))
        
        kwargs["column"] = col_list
        kwargs["bins"] = bins
        if "figsize" not in kwargs:
            kwargs["figsize"] = (CONFIG.fig_width,CONFIG.fig_height)
        df.hist(**kwargs)
        
        print(warning_color+"<<< {} >>>".format(file))
        for c in cl:
            print(bold_color+"- {} -".format(c))
            print(und_color+"[MIN]"+base_color)
            print(df.nsmallest(n, c)[c])
            print(und_color+"[MAX]"+base_color)
            print(df.nlargest(n, c)[c])

# Trie les colonnes du .dat pour uniformiser la structure : X_int_1|Y_int_1|Donnée1|Donnée2|...|Num fich|b et p|Base|Profil

def DAT_light_format(file_list,sep='\t',replace=False,output_file_list=None,nb_ecarts=3,restr=None,not_in_file=False):
    """ [TA]\n
    Sort columns to match the following structure :\n
    ``X_int_1|Y_int_1|data1_1|data1_2|...|X_int_2|...|Num fich|b et p|Base|Profil``\n
    Any other column is deleted.
    To be used if some columns are not significant to lighten data or improve readability.
    
    Notes
    -----
    Data columns are detected as long as they have the coil index in their name.
    If some of them are still not to be included, use the exclusion parameter ``restr``.\n
    For a less strict approach, see ``DAT_remove_cols``.\n
    ``restr = ['']`` (which is supposed to be an empty list) is equivalent to ``None``.
    
    Parameters
    ----------
    file_list : list of str
        List of files to process.
    ``[opt]`` sep : str, default : ``'\\t'``
        Dataframe separator.
    ``[opt]`` replace : bool, default : ``False``
        If the previous file is overwritten.
    ``[opt]`` output_file_list : ``None`` or list of str, default : ``None``
        List of output files names, ordered as ``file_list``, otherwise add the suffix ``"_clean"``. Is ignored if ``replace = True``.
    ``[opt]`` nb_ecarts : int, default : ``3``
        Number of X and Y columns. The number of coils.
    ``[opt]`` restr : ``None`` or list of str, default : ``None``
        Exclusion strings: any data including one of the specified strings will be ignored. If ``None``, is an empty list.
    ``[opt]`` not_in_file : bool, default : ``False``
        If call comes from script function instead of user.
    
    Returns
    -------
    * ``not_in_file = False``
        none, but save output dataframe in a .dat
    * ``not_in_file = True``
        clean_df : dataframe
            Output dataframe.
    
    Raises
    ------
    * File not found.
    * Wrong separator or columns not found.
    * ``file_list`` and ``output_file_list`` are different sizes.
    
    See also
    --------
    ``DAT_remove_cols``
    """
    if output_file_list != None and len(file_list) != len(output_file_list) and not replace and not not_in_file:
        MESS_err_mess("Le nombre de fichiers entrée ({}) et sortie ({}) ne correspondent pas".format(len(file_list),len(output_file_list)))
    if restr in [[''],None]:
        restr = []
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

def DAT_change_sep(file_list,sep,new_sep,replace=False,output_file_list=None,not_in_file=False):
    """ [TA]\n
    Change dataframe sepator in file
    To be used if files with different separators are to be used in a single operation.
    
    Parameters
    ----------
    file_list : list of str
        List of files to process.
    sep : str
        Dataframe old separator.
    new_sep : str
        Dataframe new separator.
    ``[opt]`` replace : bool, default : ``False``
        If the previous file is overwritten.
    ``[opt]`` output_file_list : ``None`` or list of str, default : ``None``
        List of output files names, ordered as ``file_list``, otherwise add the suffix ``"_corr"``. Is ignored if ``replace = True``.
    ``[opt]`` not_in_file : bool, default : ``False``
        If call comes from script function instead of user.
    
    Returns
    -------
    * ``not_in_file = False``
        none, but save output dataframe in a .dat
    * ``not_in_file = True``
        df : dataframe
            Output dataframe.
    
    Warns
    -----
    * Only one column found (wrong separator).
    
    Raises
    ------
    * File not found.
    * ``file_list`` and ``output_file_list`` are different sizes.
    """
    if output_file_list != None and len(file_list) != len(output_file_list) and not replace and not not_in_file:
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

# Rassemble plusieurs fichiers .dat en un seul.

def DAT_fuse_data(file_list,sep='\t',output_file="fused.dat",not_in_file=False):
    """ [TA]\n
    Fuses a list of prospection files in one .dat\n
    This procedure works as soon as all columns are matching 
    
    Notes
    -----
    Files are put in the same order as in ``file_list``.\n
    All files must have the same columns, but the order is not important (will match the order of the first one).
    
    Parameters
    ----------
    file_list : list of str
        List of files to process.
    ``[opt]`` sep : str, default : ``'\\t'``
        Dataframe separator.
    ``[opt]`` output_file : str, default : "fused.dat"
        Output file name.
    ``[opt]`` not_in_file : bool, default : ``False``
        If call comes from script function instead of user.
    
    Returns
    -------
    * ``not_in_file = False``
        none, but save output dataframe in a .dat
    * ``not_in_file = True``
        big_df : dataframe
            Output base dataframe.
    
    Raises
    ------
    * Not enough files (at least 2).
    * File not found.
    * Wrong separator or columns not found.
    * Columns are not matching.
    * Eror during ``pd.concat``.
    """
    if len(file_list) < 2:
        MESS_err_mess('Nécessite au moins deux fichiers')
    df_list = []
    for ic, file in enumerate(file_list):
        try:
            df = pd.read_csv(file, sep=sep, dtype=object)
            if len(df.columns) < 2:
                MESS_err_mess("Le fichier '{}' ne possède pas le séparateur {}?".format(file,repr(sep)))
            df_list.append(df)
            if set(df.columns) != set(df_list[0].columns):
                MESS_err_mess('Les colonnes de {} et {} ne correspondent pas'.format(file_list[0],file_list[ic]))
        except FileNotFoundError:
            MESS_err_mess('Le fichier "{}" est introuvable'.format(file))

    try:
        big_df = pd.concat(df_list)
    except Exception as e:
        MESS_err_mess("Erreur de fusion : {}".format(e))
    
    if not_in_file:
        return big_df
        
    big_df.to_csv(output_file, index=False, sep=sep)

# Dans le cas d'un duo de bases (avant et après prospection), les rassemble et les indice par rapport aux profils de la même parcelle

def DAT_fuse_bases(file_B1,file_B2,file_prof,sep='\t',output_file=None,not_in_file=False):
    """ [TA]\n
    Given two files containing bases from the same prospection, fuse them and add ``"b et p"`` and ``"Base"`` columns.\n
    To be used if bases have been taken separately.
    
    Notes
    -----
    ``file_B1`` is done before ``file_prof``, whereas ``file_B2`` is done after.\n
    ``file_prof`` is required in order to get the right value of ``"b et p"``.
    
    Parameters
    ----------
    file_B1 : str
        Base 1 file.
    file_B2 : str
        Base 2 file.
    file_prof : str
        Profile file corresponding to given bases.
    ``[opt]`` sep : str, default : ``'\\t'``
        Dataframe separator.
    ``[opt]`` output_file : ``None`` or str, default : ``None``
        Output file name, otherwise add the suffix ``"_B"`` to ``file_prof``.
    ``[opt]`` not_in_file : bool, default : ``False``
        If call comes from script function instead of user.
    
    Returns
    -------
    * ``not_in_file = False``
        none, but save output dataframe in a .dat
    * ``not_in_file = True``
        base : dataframe
            Output base dataframe.
    
    Raises
    ------
    * File not found.
    * Wrong separator or columns not found.
    """
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
        MESS_err_mess("Le fichier '{}' (profils) n'est pas interpolé, ou le séparateur '{}' est incorrect".format(file_prof,sep))
    base = pd.concat([B1[1::2],B2[1::2]])
    base.reset_index(drop=True,inplace=True)
    
    if not_in_file:
        return base
        
    if output_file == None:
        base.to_csv(file_prof[:-4]+"_B.dat", index=False, sep=sep)
    else:
        base.to_csv(output_file, index=False, sep=sep)

# Convertit le format dataframe en matrice

def TRANS_df_to_matrix(file,sep='\t',output_file="dtm.json"):
    """ [TA]\n
    Create the 'matrix' representation of a grid dataframe.
    
    Notes
    -----
    Output is in JSON format.
    
    Parameters
    ----------
    file : str
        Dataframe file.
    ``[opt]`` sep : str, default : ``'\\t'``
        Dataframe separator.
    ``[opt]`` output_file : str, default : ``"dtm.json"``
        Output file name.
    
    Raises
    ------
    * File not found.
    * Wrong separator or columns not found.
    
    See also
    --------
    ``TRANS_matrix_to_df``
    """
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

# Convertit le format matrice en dataframe

def TRANS_matrix_to_df(file,sep='\t',output_file="mtd.dat"):
    """ [TA]\n
    Create the dataframe representation of a 'matrix'.
    
    Notes
    -----
    ``sep`` is only relevant for the output.
    Weird coordinates shenanigans serves to comply with the krigind grid structure.
    
    Parameters
    ----------
    file : str
        Matrix file.
    ``[opt]`` sep : str, default : ``'\\t'``
        Output dataframe separator.
    ``[opt]`` output_file : str, default : ``"mtd.dat"``
        Output file name.
    
    Raises
    ------
    * File not found.
    * File is not a JSON.
    
    See also
    --------
    ``TRANS_df_to_matrix``
    """
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

# Convertit le format matrice en .grd pour surfer

def TRANS_matrix_to_grd(file,fmt,output_file=None):
    """ [TA]\n
    Create the .grd representation of a 'matrix'.
    Current supported format are :
    * Golden Software Surfer 6 binary
    * Golden Software Surfer 6 ascii
    * Golden Software Surfer 7 binary
    
    Notes
    -----
    .grd is compatible with *Golden Software Surfer*
    
    Parameters
    ----------
    file : str
        Matrix file.
    fmt : str, [``'surfer6bin'``, ``'surfer6ascii'``, ``'surfer7bin'``]
        Surfer format.
    ``[opt]`` output_file : ``None`` or str, default : ``None``
        Output file name. If ``None``, set to ``file + "_grd.grd"``
    
    Raises
    ------
    * File not found.
    * File is not a JSON.
    * TypeError exception in one of ``grd.py`` write functions.
    """
    try:
        with open(file, 'r') as f:
            grid_dict = json.load(f)
    except FileNotFoundError:
        MESS_err_mess('Le fichier "{}" est introuvable'.format(file))
    except json.JSONDecodeError:
        MESS_err_mess('Le fichier "{}" n\'est pas un .json'.format(file))
    
    if output_file == None:
        output_file = file[:-5] + "_grd.grd"
    
    nb_data = len(grid_dict["ncz"])
    for n in range(nb_data):
        grid = np.array(grid_dict["grid"][n])
        zmin = min(grid.flatten())
        zmax = max(grid.flatten())
        data = {'ncol' : grid_dict["pxy"][0], 'nrow' : grid_dict["pxy"][1], 'xmin' : grid_dict["ext"][0], 'xmax' : grid_dict["ext"][1], 
                'ymin' : grid_dict["ext"][2], 'ymax' : grid_dict["ext"][3], 'xsize' : grid_dict["step"][0], 'ysize' : grid_dict["step"][1], 
                'zmin' : zmin, 'zmax' : zmax, 'values' : grid, 'blankvalue' : np.inf}
        if nb_data == 1:
            filename = output_file
        else:
            spl = output_file.split(".")
            filename = spl[0]+"_"+str(n+1)+"."+spl[1]
        try:
            if fmt == 'surfer6bin':
                grd.write_surfer6bin(filename, data)
            elif fmt == 'surfer6ascii':
                grd.write_surfer6ascii(filename, data)
            elif fmt == 'surfer7bin':
                grd.write_surfer7bin(filename, data)
            else:
                MESS_err_mess('Format de fichier inconnu : {}'.format(fmt))
        except TypeError as e:
            MESS_err_mess("Erreur de type : '{}'".format(e))

# Convertit le format matrice en .grd pour surfer

def TRANS_grd_to_matrix(file_list,fmt,output_file=None):
    """ [TA]\n
    Create the 'matrix' representation of a .grd.
    Current supported format are :
    * Golden Software Surfer 6 binary
    * Golden Software Surfer 6 ascii
    * Golden Software Surfer 7 binary
    
    Notes
    -----
    .grd is compatible with *Golden Software Surfer*
    
    Parameters
    ----------
    file : str
        .grd file.
    fmt : str, [``'surfer6bin'``, ``'surfer6ascii'``, ``'surfer7bin'``]
        Surfer format.
    ``[opt]`` output_file : ``None`` or str, default : ``None``
        Output file name. If ``None``, set to ``file + "_mtx.json"``
    
    Raises
    ------
    * File not found.
    * TypeError exception in one of ``grd.py`` write functions.
    """
    data = {}
    grid = []
    ncx = []
    ncy = []
    ncz = []
    for ic,file in enumerate(file_list):
        try:
            if fmt ==  'surfer6bin':
                data = grd.read_surfer6bin(file)
            elif fmt ==  'surfer6ascii':
                data = grd.read_surfer6ascii(file)
            elif fmt ==  'surfer7bin':
                data = grd.read_surfer7bin(file)
            else:
                MESS_err_mess('Format de fichier inconnu : {}'.format(fmt))
        except TypeError as e:
            MESS_err_mess("Erreur de type : '{}'".format(e))
        except OSError as e:
            MESS_err_mess("Erreur de fichier : '{}'".format(e))
        grid.append(data['values'].tolist())
        ncx.append("x_"+str(ic+1))
        ncy.append("y_"+str(ic+1))
        ncz.append("z_"+str(ic+1))
        
    grid_save = {"grid" : grid, "ext" : [data['xmin'],data['xmax'],data['ymin'],data['ymax']], 
                 "pxy" : [data['ncol'],data['nrow']], "step" : [data['xsize'],data['ysize']], 
                 "ncx" : ncx, "ncy" : ncy, "ncz" : ncz}
    
    if output_file == None:
        output_file = file[:-4] + "_mtx.json"
    with open(output_file, "w") as f:
        json.dump(grid_save, f, indent=None, cls=MyJSONEncoder)  

# Charge et affiche des figures en .pickle

def FIG_display_fig(file_list):
    """ [TA]\n
    Reload the matplotlib figure saved as PICKLE format.
    
    Parameters
    ----------
    file_list : ``None`` or list of str
        List of pickle files. If ``None``, takes every file in the ``Output`` folder.
    
    Raises
    ------
    * File not found.
    """
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

def FIG_plot_data(file,sep='\t',col_x=None,col_y=None,col_z=None):
    """ [TA]\n
    Plots raw data from dataframe.
    
    Parameters
    ----------
    file : str
        Dataframe file.
    ``[opt]`` sep : str, default : ``'\\t'``
        Dataframe separator.
    ``[opt]`` col_x : ``None`` or list of int, default : ``None``
        Index of every X coordinates columns. If ``None``, is set to ``[0]``.
    ``[opt]`` col_y : ``None`` or list of int, default : ``None``
        Index of every Y coordinates columns. If ``None``, is set to ``[1]``.
    ``[opt]`` col_z : ``None`` or list of int, default : ``None``
        Index of every Z coordinates columns (actual data). If ``None``, takes every column that is not X nor Y.
    
    Notes
    -----
    Also handles column names with multiple substrings splitted by '|', which correspond to the grid dataframe format.
    
    Raises
    ------
    * File not found.
    * Wrong separator.
    * Column is not numeric.
    """
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
        nc_data = col_z.drop(ncy_t)
    else:
        nc_data = df.columns[col_z]
    nb_data = len(nc_data)
    nb_ecarts = len(ncx)
    nb_res = nb_data//nb_ecarts
    
    for e in range(nb_ecarts):
        fig,ax=plt.subplots(nrows=1,ncols=nb_res,figsize=(nb_res*CONFIG.fig_width//2,CONFIG.fig_height),squeeze=False)
        if multi_col:
            X = df[ncx_t]
            Y = df[ncy_t]
        else:
            X = df[ncx_t[e]]
            Y = df[ncy_t[e]]
        for r in range(nb_res):
            n = e*nb_res + r
            Z = df[nc_data[n]]
            try:
                Q5,Q95 = Z.dropna().quantile([0.05,0.95])
            except TypeError:
                MESS_err_mess("La colonne '{}' n'est pas numérique".format(nc_data[n]))
            col = ax[0][r].scatter(X,Y,marker='s',c=Z,cmap='cividis',s=6,vmin=Q5,vmax=Q95)
            plt.colorbar(col,ax=ax[0][r])
            ax[0][r].title.set_text(nc_data[n])
            ax[0][r].set_xlabel(ncx[e])
            ax[0][r].set_ylabel(ncy[e])
            ax[0][r].set_aspect('equal')
        plt.show(block=False)
        plt.pause(CONFIG.fig_render_time) # À augmenter si la figure ne s'affiche pas, sinon on pourra le baisser pour accélérer la vitesse de l'input
        plt.savefig(CONFIG.script_path+"Output/FIG_" +str(e)+'.png')
        pickle.dump(fig, open(CONFIG.script_path+"Output/FIG_" +str(e)+'.pickle', 'wb'))
        
    keep_plt_for_cmd()

# Plot en grille

def FIG_plot_grid(file):
    """ [TA]\n
    Plots raw data from 'matrix' format.
    
    Parameters
    ----------
    file : str
        Matrix file.
    
    Raises
    ------
    * File not found.
    * File is not a JSON.
    """
    try:
        with open(file, 'r') as f:
            grid_dict = json.load(f)
    except FileNotFoundError:
        MESS_err_mess('Le fichier "{}" est introuvable'.format(file))
    except json.JSONDecodeError:
        MESS_err_mess('Le fichier "{}" n\'est pas un .json'.format(file))
    
    nb_ecarts = len(grid_dict["ncx"])
    nb_res = len(grid_dict["ncz"])//nb_ecarts
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
        plt.pause(CONFIG.fig_render_time) # À augmenter si la figure ne s'affiche pas, sinon on pourra le baisser pour accélérer la vitesse de l'input
        plt.savefig(CONFIG.script_path+"Output/FIG_" +str(e)+'.png')
        pickle.dump(fig, open(CONFIG.script_path+"Output/FIG_" +str(e)+'.pickle', 'wb'))
        
    keep_plt_for_cmd()

# Plot en nuage de pts les positions des n voies

def FIG_plot_pos(file,sep='\t'):
    """ [TA]\n
    Plots positions of each coil.
    
    Parameters
    ----------
    file : str
        Dataframe file.
    ``[opt]`` sep : str, default : ``'\\t'``
        Dataframe separator.
    
    Notes
    -----
    Coil position columns must be named as such : ``[X/Y] + _int_ + [coil_id]``.\n
    Output figure can be heavy.
    
    Raises
    ------
    * File not found.
    * Wrong separator.
    * No positions for each coil.
    """
    try:
        df = pd.read_csv(file, sep=sep)
    except FileNotFoundError:
        MESS_err_mess('Le fichier "{}" est introuvable'.format(file))
    
    if len(df.columns) <= 1:
        MESS_err_mess("Le fichier n'est pas lu correctement', le séparateur {} est-il correct ?".format(repr(sep)))
    
    color = ["blue","green","orange","magenta","red","cyan","black","yellow"]
    ncx = []
    ncy = []
    cpt = 0
    while True: # Programmassion
        new_x = "X_int_"+str(cpt+1)
        new_y = "Y_int_"+str(cpt+1)
        try:
            df[new_x]
            ncx.append(new_x)
            ncy.append(new_y)
        except KeyError:
            break
        cpt += 1
    if cpt == 0:
        MESS_err_mess("Les données n'ont pas de coordonnées pour chaque voie, veuillez passer par 'CMD_init'")
    
    fig,ax=plt.subplots(nrows=1,ncols=1,figsize=(CONFIG.fig_width,CONFIG.fig_height))
    for index, row in df.iterrows():
        ax.plot(row[ncx],row[ncy],'-k')
    for i in range(cpt):
        ax.plot(df[ncx[i]],df[ncy[i]],'o',color=color[i%8],label="Bobine "+str(i+1))
    ax.set_title("Positions des bobines")
    ax.set_xlabel("X_int")
    ax.set_ylabel("Y_int")
    ax.set_aspect('equal')
    plt.legend()
    plt.show(block=False)
    plt.pause(CONFIG.fig_render_time) # À augmenter si la figure ne s'affiche pas, sinon on pourra le baisser pour accélérer la vitesse de l'input
    plt.savefig(CONFIG.script_path+"Output/FIG_pos.png")
    pickle.dump(fig, open(CONFIG.script_path+"Output/FIG_pos.pickle", 'wb'))
        
    keep_plt_for_cmd()

# Ajoute un nouvel appareil à la base en JSON

def JSON_add_device(app_name,config,nb_ecarts,freq_list,gps=True,gps_dec=[0.0,0.0],TR_l=None,TR_t=None,height=0.1,bucking_coil=0,coeff_c_ph=None,coeff_c_qu=1.0,config_angles=None,autosave=False,error_code=False):
    """ [TA]\n
    Create device with requested components, then save it in ``JSONs/Appareils.json``.\n
    TODO : Implement ``config_angles``.
    
    Notes
    -----
    Any device that shares all attributes with an existing entry will be ignored and raise a warning.
    
    Parameters
    ----------
    app_name : str
        Device name. Can be anything.
    config : str, {``"HCP"``, ``"VCP"``, ``VVCP``,``"PRP_CS"``, ``"PRP_DEM"``, ``"PAR"``, ``"COAX_H"``, ``"COAX_P"``, ``"CUS"``}
        Coil configuration.
    nb_ecarts : int
        Number of X and Y columns. The number of coils.
    freq_list : list of int
        Frequences of each coil. If all are the same, can be of length 1.
    ``[opt]`` gps : bool, default : ``True``
        If got GPS data.
    ``[opt]`` gps_dec : [float, float], default : ``[0.0,0.0]``
        Shift between the GPS antenna and the device center, on both axis. Should be ``[0,0]`` if none.
    ``[opt]`` TR_l : ``None`` or list of float, default : ``None``
        Distance between each coil and the transmitter coil, on lateral axis.
    ``[opt]`` TR_t : ``None`` or list of float, default : ``None``
        Distance between each coil and the transmitter coil, on transversal axis.
    ``[opt]`` height : float, default : ``0.1``
        Height of the device during the prospection.
    ``[opt]`` bucking_coil, default : ``0``
        Index of the bucking coil between coils (from ``1`` to ``nb_ecarts``). If none, set to 0.
    ``[opt]`` coeff_c_ph : ``None`` or list of float, default : ``None``
        Device constant given by the maker (in phase).
    ``[opt]`` coeff_c_qu : float, default : ``1.0``
        Device constant given by the maker (in quadrature).
    ``[opt]`` config_angles : ``None`` or list of [float, float], default : ``None``
        If ``config = "CUS"`` (custom), define the angles of each coil.
    ``[opt]`` autosave : bool, default : ``False``
        Saves new devices without user input.
    ``[opt]`` error_code : bool, default : ``False``
        Instead of returning the dictionary, return an error code as an int.
    
    Returns
    -------
    * ``error_code = False``
        new_app : dict
            Output dictionary.
    * ``error_code = True``
        ec : int, {``0``, ``1``}
            Exit code (1 if ``new_app`` already exists)
    
    Raises
    ------
    * Unknown ``config``.
    * Lengths of ``TR_l``, ``TR_t`` and ``coeff_c_ph`` do not match ``nb_ecarts``.
    * None of ``TR_l`` and ``TR_t`` is specified.
    * ``config_angles = None`` even though``config = "CUS"``
    * Length of ``config_angles`` does not match ``nb_ecarts``.
    * Lenght of ``gps_dec`` is not equal to 2.
    """
    app_list = {}
    with open(CONFIG.json_path+"Appareils.json", 'r') as f:
        app_list = json.load(f)
    
    ### À DÉCOMMENTER POUR RÉINITIALISER LE FICHIER ###
    app_list ={
        "app_list": []
       }
    
    config_list = ["HCP","VCP","VVCP","PRP_CS","PRP_DEM","PAR","COAX_H","COAX_P","CUS"]
    if config not in config_list:
        MESS_err_mess("La configuration choisie est inconnue ({})".format(config_list))
    if TR_t == None and TR_l == None:
        MESS_err_mess("Aucune position de bobine n'est spécifiée. Veuiller renseigner 'TR_l' ou 'TR_t'")
    if TR_l == None:
        TR_l = [0.0 for i in range(nb_ecarts)]
    if TR_t == None:
        TR_t = [0.0 for i in range(nb_ecarts)]
    if len(TR_l) != nb_ecarts:
        MESS_err_mess("Le nombre de positions l ({}) n'est pas égal au nombre de bobines ({})".format(len(TR_l),nb_ecarts))
    if len(TR_t) != nb_ecarts:
        MESS_err_mess("Le nombre de positions t ({}) n'est pas égal au nombre de bobines ({})".format(len(TR_t),nb_ecarts))
    if coeff_c_ph == None:
        coeff_c_ph = [0.0 for i in range(nb_ecarts)]
    if len(coeff_c_ph) != nb_ecarts:
        MESS_err_mess("Le taille de la constante en quadrature ({}) n'est pas égal au nombre de bobines ({})".format(len(coeff_c_ph),nb_ecarts))
    
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
    new_app["TR_l"] = TR_l
    new_app["TR_t"] = TR_t
    new_app["TR"] = [np.sqrt(TR_l[i]**2 + TR_t[i]**2) for i in range(nb_ecarts)]
    new_app["height"] = height
    new_app["freq_list"] = freq_list
    new_app["bucking_coil"] = bucking_coil
    new_app["coeff_c_ph"] = coeff_c_ph
    new_app["coeff_c_qu"] = coeff_c_qu
    
    for app in app_list["app_list"]:
        if {i:new_app[i] for i in new_app if i!='app_id'} == {i:app[i] for i in app if i!='app_id'}:
            MESS_warn_mess("Appareil ({}, {}) déjà ajouté.".format(app_name,config))
            if error_code:
                return 1
            else:
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
        
    with open(CONFIG.json_path+"Appareils.json", "w") as f:
        json.dump(app_list, f, indent=2)
    if error_code:
        return 0
    else:
        return new_app
        
# Récupère la valeur des paramètres de l'appareil dans le JSON à partir de l'uid.
# Stoppe l'exécution si il n'existe pas.

def JSON_find_device(uid):
    """ [TA]\n
    Find the requested device in ``JSONs/Appareils.json`` from ``"app_id"``.\n
    
    Parameters
    ----------
    uid : int
        Device's ``"app_id"`` value.
    
    Returns
    -------
    app : dict
        Found device.
    
    Raises
    ------
    * Unknown ``uid``.
    """
    app_list = {}
    with open(CONFIG.json_path+"Appareils.json", 'r') as f:
        app_list = json.load(f)
    
    nc = os.get_terminal_size().columns
    for app in app_list["app_list"]:
        if app["app_id"] == uid:
            JSON_print_device_selected(app,nc)
            print(success_color+"-"*nc)
            print(base_color)
            return app
    
    MESS_err_mess("L'appareil sélectionné (uid = {}) n'existe pas dans la base locale".format(uid))

# Supprime un appareil de la base

def JSON_remove_device(uid):
    """ [TA]\n
    Remove the requested device in ``JSONs/Appareils.json`` from ``"app_id"``.\n
    
    Parameters
    ----------
    uid : int
        Device's ``"app_id"`` value.
    
    Returns
    -------
    app : dict
        Found device.
    
    Raises
    ------
    * Unknown ``uid``.
    """
    app_list = {}
    with open(CONFIG.json_path+"Appareils.json", 'r') as f:
        app_list = json.load(f)
    try:
        del app_list["app_list"][uid]
    except IndexError:
        MESS_err_mess("L'appareil sélectionné (uid = {}) n'existe pas dans la base locale".format(uid))
    
    for ic, app in enumerate(app_list["app_list"]):
        app["app_id"] = ic
    
    with open(CONFIG.json_path+"Appareils.json", "w") as f:
        json.dump(app_list, f, indent=2)

# Affiche les appareils déjà enregistrés.
# La première envoie les infos à afficher à la seconde.

def JSON_print_devices(uid=None):
    """ [TA]\n
    Print the requested device in ``JSONs/Appareils.json`` from ``"app_id"``.\n
    
    Parameters
    ----------
    ``[opt]`` uid : ``None`` or int, default : ``None``
        Device's ``"app_id"`` value. If ``None``, print all.
    
    Raises
    ------
    * Unknown ``uid``.
    """
    app_list = {}
    with open(CONFIG.json_path+"Appareils.json", 'r') as f:
        app_list = json.load(f)
    
    print("")
    nc = os.get_terminal_size().columns
    if uid == None:
        for app in app_list["app_list"]:
            JSON_print_device_selected(app,nc)
    else:
        try:
            JSON_print_device_selected(next(app for app in app_list["app_list"] if app["app_id"] == uid),nc)
        except:
            MESS_err_mess("L'appareil sélectionné (uid = {}) n'existe pas dans la base locale".format(uid))
    
    print(success_color+"-"*nc)
    print(base_color)

# Affiche dans le terminal les informations relatives à un/tous les appareils de la base.

def JSON_print_device_selected(app,nc):
    """ [TA]\n
    Notes
    -----
    Subfunction of ``JSON_print_devices``\n
    """
    print(success_color+"-"*nc)
    print(type_color+"{} : ".format(app["app_id"])+title_color+"{} ({})".format(app["app_name"],app["config"]))
    print(success_low_color+"\tGPS : "+base_color+"{}".format(app["GPS"]))
    print(success_low_color+"\tNb T/R : "+base_color+"{}, ".format(app["nb_ecarts"]))
    print(success_low_color+"\tPos l : "+base_color+"{}, ".format(app["TR_l"])+success_low_color+"Pos t : "+base_color+"{}".format(app["TR_t"]))
    print(success_low_color+"\tz : "+base_color+"{}, ".format(app["height"])+success_low_color+"Frequences : "+base_color+"{}".format(app["freq_list"]))
        

# Récupère les constantes associées à l'appareil.
# Les créent si elles n'existent pas.

def JSON_add_coeff(app_data):
    """ [TA]\n
    Create dictionary with requested components about the device.\n
    If the parameters are already in the ``JSONs/Constantes.json`` file, then it simply takes the results.
    Otherwise, compute the modeling constants, then save it in the .json.\n
    
    Notes
    -----
    Computation is done by Fortran scripts.
    
    Parameters
    ----------
    app_data : dict
        Dictionary of device data.
    
    Returns
    -------
    dict_const : dict
        Dictionary with the initial parameters and the affiliated constants.
    
    Raises
    ------
    A lot, but everything is handled by ``try`` keywords.
    
    See also
    --------
    ``JSON_add_device, FORTRAN_new_const``
    """
    const_list = {}
    with open(CONFIG.json_path+"Constantes.json", 'r') as f:
       const_list = json.load(f)
    
    ### À DÉCOMMENTER POUR RÉINITIALISER LE FICHIER ###
    const_list ={}
    
    new_const = {}
    new_const["config"] = [[app_data["config"], {}]]
    new_const["config"][0][1]["TR"] = [[app_data["TR"], {}]]
    new_const["config"][0][1]["TR"][0][1]["height"] = [[app_data["height"], {}]]
    new_const["config"][0][1]["TR"][0][1]["height"][0][1]["freq_list"] = [[app_data["freq_list"], {}]]
    
    # OK j'avoue j'assume moyen cette merde mais ça marche complètement
    # On parcourt un arbre où chaque embranchement est une valeur du paramètre de l'étage.
    # La structure a comme étage de haut en bas : "config", "TR", "height", "freq_list".
    # On commence à parcourir "config". Si la config est nouvelle, on calcule les coeffs par Fortran, puis on insère une branche contenant les trois autres paramètres et en feuille les valeurs des constantes.
    # Sinon, on se rend dans la config connue, et on cherche sur "TR" etc.
    # Si à la fin on a trouvé une occurence pour chacun des paramètres, ça veut dire que les constantes ont déjà été calculées pour cette appareil. On la prend et on insère rien dans le .json.
    # On trie par ordre alpha ou croissant la base pour la lisibilité (ne change pas la vitesse de recherche).
    try:
        ic1 = [e[0] for e in const_list["config"]].index(new_const["config"][0][0])
        #print("(1)", [e[0] for e in const_list["config"]])
        new_const_part = new_const["config"][0][1]
        const_list_part = const_list["config"][ic1][1]
        try:
            ic2 = [e[0] for e in const_list_part["TR"]].index(new_const_part["TR"][0][0])
            #print("(2)", [e[0] for e in const_list_part["TR"]])
            new_const_part = new_const_part["TR"][0][1]
            const_list_part = const_list_part["TR"][ic2][1]
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
                    # Constante déjà calculée
                    new_const["config"][0][1]["TR"][0][1]["height"][0][1]["freq_list"][0][1] = const_list_part
                except ValueError:
                    new_const["config"][0][1]["TR"][0][1]["height"][0][1]["freq_list"][0][1] = FORTRAN_new_const(app_data)
                    const_list["config"][ic1][1]["TR"][ic2][1]["height"][ic3][1]["freq_list"].append(new_const_part["freq_list"][0])
                    const_list["config"][ic1][1]["TR"][ic2][1]["height"][ic3][1]["freq_list"] = \
                        sorted(const_list["config"][ic1][1]["TR"][ic2][1]["height"][ic3][1]["freq_list"], key=lambda x: "".join(str(s) for s in x[0]))
            except ValueError:
                new_const["config"][0][1]["TR"][0][1]["height"][0][1]["freq_list"][0][1] = FORTRAN_new_const(app_data)
                const_list["config"][ic1][1]["TR"][ic2][1]["height"].append(new_const_part["height"][0])
                const_list["config"][ic1][1]["TR"][ic2][1]["height"] = sorted(const_list["config"][ic1][1]["TR"][ic2][1]["height"], key=lambda x: float(x[0]))
        except ValueError:
            new_const["config"][0][1]["TR"][0][1]["height"][0][1]["freq_list"][0][1] = FORTRAN_new_const(app_data)
            const_list["config"][ic1][1]["TR"].append(new_const_part["TR"][0])
            const_list["config"][ic1][1]["TR"] = sorted(const_list["config"][ic1][1]["TR"], key=lambda x: "".join(str(s) for s in x[0])) # Petite technique pour trier des listes ;)
    except ValueError:
        new_const["config"][0][1]["TR"][0][1]["height"][0][1]["freq_list"][0][1] = FORTRAN_new_const(app_data)
        const_list["config"].append(new_const["config"][0])
        const_list["config"] = sorted(const_list["config"], key=lambda x: x[0])
    except KeyError or IndexError:
        MESS_warn_mess("Base de résultat réinitialisée")
        new_const["config"][0][1]["TR"][0][1]["height"][0][1]["freq_list"][0][1] = FORTRAN_new_const(app_data)
        const_list = new_const
    # except:
    #     MESS_err_mess("Une erreur inconnue s'est produite (JSON_add_coeff)")
           
    # Remise à un format plus lisible
    dict_const = {}
    dict_const["config"] = new_const["config"][0][0]
    dict_const["TR"] = new_const["config"][0][1]["TR"][0][0]
    dict_const["height"] = new_const["config"][0][1]["TR"][0][1]["height"][0][0]
    dict_const["freq_list"] = new_const["config"][0][1]["TR"][0][1]["height"][0][1]["freq_list"][0][0]
    dict_const["sigma_a_ph"] = new_const["config"][0][1]["TR"][0][1]["height"][0][1]["freq_list"][0][1]["sigma_a_ph"]
    dict_const["Kph_a_ph"] = new_const["config"][0][1]["TR"][0][1]["height"][0][1]["freq_list"][0][1]["Kph_a_ph"]
    dict_const["sigma_a_qu"] = new_const["config"][0][1]["TR"][0][1]["height"][0][1]["freq_list"][0][1]["sigma_a_qu"]
    dict_const["Kph_a_qu"] = new_const["config"][0][1]["TR"][0][1]["height"][0][1]["freq_list"][0][1]["Kph_a_qu"]    
        
    with open(CONFIG.json_path+"Constantes.json", "w") as f:
        json.dump(const_list, f, indent=None, cls=MyJSONEncoder)
    
    #print(dict_const)
    return dict_const

# Calcule le coefficient de l'appareil avec le calibrage à la boule.

def FORTRAN_ball_calibr(ball_file,config,TR,radius,z,x_min,x_max,sep='\t',y=0,step=5,bucking_coil=0,plot=True):
    """ [TA]\n
    Uses Fortran to estimate the device coefficient for quadrature.\n
    
    Parameters
    ----------
    ball_file : dict
        File containing the user measurements.
    config : str, {``"PRP_CS"``, ``"PRP_DEM"``, ``HCP``,``"VCP"``}
        Coil configuration.
    TR : list of int
        Distance between each coil and the transmitter coil (in cm).
    radius : int
        Radius of the aluminium ball.
    z : int
        Offset for z axis (height).
    x_min : int
        Starting position between the device and the ball. Can be negative, lower than ``x_max``.
    x_max  : int
        Ending position between the device and the ball. Can be negative, higher than ``x_min``.
    ``[opt]`` y : int, default : ``0``
        Offset for y axis (lateral).
    ``[opt]`` step : int, default : ``5``
        Distance between two consecutive measures.
    ``[opt]`` bucking_coil : int, default : ``0``
        Index of the bucking coil between coils (from ``1`` to ``len(TR)``). If none, set to 0.
    
    Notes
    -----
    Subfunction of ``FORTRAN_ball_calibr``.\n
    The indents are mandatory for the Fortran executable.\n
    Each new line (except the last one) must end by ``"\x0d\n"``, which is the Windows end of line + new line combination.\n
    All parameters must be int as float shoud not be read correctly by Fortran.\n
    If the ``config`` would be ``"VVCP"``, must instead specify ``"HCP"`` or ``"VCP"`` depending on which methode has been used in the practical file.
    
    Raises
    ------
    * Unknown configuration.
    * Fortran executable fails.
    * Unknown OS.
    * ``x_min``, ``x_max`` and ``step`` do not match ``ball_file`` content.
    
    See also
    --------
    ``FORTRAN_ball_calibr``
    """
    print(TR)
    print(sep)
    nb_ecarts = len(TR)
    config_list = ["PRP_CS","PRP_DEM","HCP","VCP"]
    if config not in config_list:
        MESS_err_mess("Méthode non implémentée pour la configuration '{}' ({})".format(config,config_list))
    fortran_folder = "Fortran/"
    cfg_file = "_boule_.cfg"
    output_file = "_boule_.dat"
    fortran_exe = "boule.exe"
    fortran_linux = "boule.out"
    os.chdir(CONFIG.script_path+fortran_folder)
    FORTRAN_constboule(cfg_file,output_file,TR,radius,z,x_min,x_max,y,step,bucking_coil)
    if OS_KERNEL == "Linux":
        error_code = os.system("./{} {}".format(fortran_linux,cfg_file))#"init_etal.txt"
    elif OS_KERNEL == "Windows":
        error_code = os.system("start {} {}".format(fortran_exe,cfg_file))
    elif OS_KERNEL == "Darwin":
        error_code = os.system("./{} -f {}".format(fortran_exe,cfg_file))
    else:
        MESS_err_mess("PAS IMPLÉMENTÉ POUR L'OS '{}'".format(OS_KERNEL))
    if error_code:
        MESS_err_mess("[Fortran] ERREUR")
    
    don = pd.read_csv(output_file,sep='\s+',skiprows=1)
    config_index = next(i for i,c in enumerate(config_list) if c == config)
    cols_th = don.iloc[:,1+nb_ecarts*config_index:1+nb_ecarts*(config_index+1)]
    don = pd.read_csv(ball_file,sep=sep)
    don.drop(don[don[don.columns[0]] < 0].index, inplace=True)
    cols_pr = don[[c for c in don.columns if "Inph" in c]]
    
    coeff = 0
    try:
        for e in range(nb_ecarts):
            c_pr = cols_pr.iloc[:,e]*1000
            c_th = cols_th.iloc[:,e]
            if plot:
                fig,ax=plt.subplots(nrows=1,ncols=1,figsize=(CONFIG.fig_width,CONFIG.fig_height))
                ax.plot(c_pr,c_th,'o')
                ax.set_title("Positions des bobines (y={}, z={})".format(y,z))
                ax.set_xlabel("Pratique")
                ax.set_ylabel("Théorique")
                plt.show()
                print(c_pr,c_th)
            lin_reg = linregress(c_pr,c_th)
            coeff += lin_reg.slope
    except ValueError:
        MESS_err_mess("Le pas et/ou le départ/arrivée en x est incorrect".format(config,config_list))
    except TypeError:
        MESS_err_mess("Problème de lecture du fichier...")
    coeff /= nb_ecarts
    
    print("coeff = {}".format(coeff))
    
    os.chdir(CONFIG.script_path)
    
# Construit le fichier d'entrée du Fortran (boule).

def FORTRAN_constboule(cfg_file,output_file,TR,radius,z,x_min,x_max,y=0,step=5,bucking_coil=0):
    """ [TA]\n
    Construct a file that contains the mandatory data for the Fortran ball calibration procedure.\n
    
    Parameters
    ----------
    cfg_file : str
        File that will contain the informations for the Fortran file.
    output_file : str
        File that will contain the dataframe of theoretical values.
    TR : list of int
        Distance between each coil and the transmitter coil (in cm).
    radius : int
        Radius of the aluminium ball.
    z : int
        Offset for z axis (height).
    x_min : int
        Starting position between the device and the ball. Can be negative, lower than ``x_max``.
    x_max  : int
        Ending position between the device and the ball. Can be negative, higher than ``x_min``.
    ``[opt]`` y : int, default : ``0``
        Offset for y axis (lateral).
    ``[opt]`` step : int, default : ``5``
        Distance between two consecutive measures.
    ``[opt]`` bucking_coil : int, default : ``0``
        Index of the bucking coil between coils (from ``1`` to ``len(TR)``). If none, set to 0.
    
    Notes
    -----
    Subfunction of ``FORTRAN_ball_calibr``.\n
    The indents are mandatory for the Fortran executable.\n
    Each new line (except the last one) must end by ``"\x0d\n"``, which is the Windows end of line + new line combination.\n
    All parameters must be int as float shoud not be read correctly by Fortran.
    
    See also
    --------
    ``FORTRAN_ball_calibr``
    """
    
    with open(cfg_file, 'w') as f:
        f.write(str(len(TR))+"\x0d\n")
        f.write(str(bucking_coil)+"\x0d\n")
        f.write(output_file+"\x0d\n")
        for e in TR:
            f.write(str(e)+"\x0d\n")
        f.write(str(y)+" "+str(x_min)+" "+str(z)+"\x0d\n")
        f.write(str(step)+" "+str(x_max)+"\x0d\n")
        f.write(str(radius)+"")

# Calcule puis ajoute les constantes liées à l'appareil choisi.

def FORTRAN_new_const(app_data,plot=True):
    """ [TA]\n
    Uses Fortran to compute a dataframe of constants values.\n
    Then estimates the coefficients of a linear of polynomial relation for each coil.
    
    Parameters
    ----------
    app_data : dict
        Dictionary of device data.
    ``[opt]`` plot : bool, default : ``False``
        Enables plotting of found linear/polynomial models.
    
    Returns
    -------
    const_dict : dict
        Dictionary of constants.
    
    Notes
    -----
    Subfunction of ``JSON_add_coeff``.\n
    macOS (``Darwin``) has not been tested yet (no Apple device).
    
    Raises
    ------
    * Fortran executable fails.
    * Unknown OS.
    
    See also
    --------
    ``JSON_add_coeff, FORTRAN_constab, CMD_coeffs_relation``
    """
    os.chdir(CONFIG.script_path)
    fortran_folder = "Fortran/"
    cfg_file = fortran_folder+"_config_.cfg"
    fortran_exe = fortran_folder+"terrainhom.exe"
    fortran_linux = fortran_folder+"terrainhom.out"
    const_dict = {"sigma_a_ph": [], "sigma_a_qu": [], "Kph_a_ph": [], "Kph_a_qu": 0}
    for e in range(app_data["nb_ecarts"]):
        FORTRAN_constab(app_data,cfg_file,e,variation=None,S_rau=1,S_eps_r=1,S_kph=0,S_kqu=0,F_rau=1001,F_eps_r=None,F_kph=0.01,F_kqu=None)
        if OS_KERNEL == "Linux":
            error_code = os.system("./{} {}".format(fortran_linux,cfg_file))
        elif OS_KERNEL == "Windows":
            error_code = os.system("start {} {}".format(fortran_exe,cfg_file))
        elif OS_KERNEL == "Darwin":
            error_code = os.system("./{} -f {}".format(fortran_exe,cfg_file))
        else:
            MESS_err_mess("PAS IMPLÉMENTÉ POUR L'OS '{}'".format(OS_KERNEL))
        if error_code:
            MESS_err_mess("[Fortran] ERREUR")
        
        don = pd.read_csv(cfg_file[:-4]+".dat",sep='\s+',header=None)
        print(don)
        
        HsHp_qu = np.array(don.iloc[:,5])
        sigma = np.array(1/don.iloc[:,0])
        saqu = CMD_coeffs_relation(HsHp_qu,sigma,m_type="linear",plot=plot)[1]
        const_dict["sigma_a_qu"].append(saqu)
        
        true_sigma = HsHp_qu * saqu
        HsHp_ph = np.array(don.iloc[:,4])
        saph = CMD_coeffs_relation(true_sigma,HsHp_ph,m_type="poly_3",plot=plot)
        const_dict["sigma_a_ph"].append(saph)
        
        true_HsHp_ph = saph[0] + true_sigma*saph[1] + (true_sigma)**2*saph[2] + (true_sigma)**3*saph[3]
        kaph = CMD_coeffs_relation(HsHp_ph,true_HsHp_ph,m_type="poly_3",plot=plot)
        const_dict["Kph_a_ph"].append(kaph)
    
    return const_dict

# Construit le fichier d'entrée du Fortran (ppt).

def FORTRAN_constab(app_data,cfg_file,e,variation=None,S_rau=1,S_eps_r=1,S_kph=0,S_kqu=0,F_rau=None,F_eps_r=None,F_kph=None,F_kqu=None):
    """ [TA]\n
    Construct a file that contains the mandatory data for the Fortran ppt procedure.\n
    
    Parameters
    ----------
    app_data : dict
        Dictionary of device data.
    cfg_file : str
        File that will contain the informations for the Fortran file.
    e : int
        Index of the chosen coil (the procedure manage one coil at a time).
    ``[opt]`` variation : ``None`` or int, default : ``None``
        Number of different values for each moving parameter. The maximum values are
            * 1 parameter : ``10000``.
            * 2 parameters : ``100``.
            * 3 parameters : ``21``.
            * 4 parameters : ``10``.
    ``[opt]`` S_rau : int, default : ``1``
        Starting value for :math:`\\rho`.
    ``[opt]`` S_eps_r : int, default : ``1``
        Starting value for :math:`\\epsilon_{r}`.
    ``[opt]`` S_kph : int, default : ``0``
        Starting value for :math:`k_{ph}`.
    ``[opt]`` S_kqu : int, default : ``0``
        Starting value for :math:`k_{qu}`.
    ``[opt]`` F_rau : ``None`` or int, default : ``None``
        Ending value for :math:`\\rho`. If ``None``, :math:`\\rho` is constant.
    ``[opt]`` F_eps_r : ``None`` or int, default : ``None``
        Ending value for :math:`\\epsilon_{r}`. If ``None``, :math:`\\epsilon_{r}` is constant.
    ``[opt]`` F_kph : ``None`` or int, default : ``None``
        Ending value for :math:`k_{ph}`. If ``None``, :math:`k_{ph}` is constant.
    ``[opt]`` F_kqu : ``None`` or int, default : ``None``
        Ending value for :math:`k_{qu}`. If ``None``, :math:`k_{qu}` is constant.
    
    Notes
    -----
    Subfunction of ``FORTRAN_new_const``.\n
    The indents are mandatory for the Fortran executable.\n
    At least one of the 4 ``F_{arg}`` should be set.\n
    TODO : Custom configuration.
    
    Raises
    ------
    * Unknown configuration.
    * Values are too big (goes beyond the maximum allocated space).
    * No parameters are marked as varying.
    * The number of computation lines goes beyond 10000.
    
    See also
    --------
    ``FORTRAN_new_const``
    """
    _Config_params = [[1.2,3.4,5.6,7.8],[0.0,0.0,0.0,90.0],[0.0,35.0,0.0,35.0],
                      [0.0,90.0,0.0,90.0],[0.0,0.0,0.0,0.0],[90.0,0.0,90.0,0.0],
                      [1.2,3.4,5.6,7.8],[1.2,3.4,5.6,7.8],[0.0,90.0,0.0,0.0],
                      [90.0,0.0,90.0,0.0]]
    
    with open(cfg_file, 'w') as f:
        f.write(" # Geometrie(s) d'appareil\n")
        f.write(" {}\n".format(1))
        try:
            config_id = next(i for i,c in enumerate(["CUS","PRP_CS","PAR","HCP","COAX_H","VCP","COAX_V","VVCP","PRP_DEM"]) if c == app_data["config"])
        except StopIteration:
            MESS_err_mess("Configuration inconnue")
        nb_spaces = 2 - len(str(config_id)) # Est toujours égal à 1 pour l'instant
        f.write(" "*nb_spaces+"{}\n".format(config_id))
        f.write(" "*(2 - len(str(int(app_data["TR"][e]))))+"{:.2f}\n".format(app_data["TR"][e]))
        f.write(" 1.00\n")
        f.write(" "*(2 - len(str(int(app_data["height"]))))+"{:.2f}\n".format(app_data["height"]))
        f.write(" "*(2 - len(str(int(app_data["height"]))))+"{:.2f}\n".format(app_data["height"]))
            
        f.write(" # Parametres utiles pour CSTM\n")
        angles = _Config_params[config_id]
        for i in range(4):
            nb_spaces = 2 - len(str(int(angles[i])))
            f.write(" "*nb_spaces+"{:.2f}\n".format(angles[i]))
        f.write(" "*(2 - len(str(int(app_data["TR_l"][e]))))+"{:.2f}\n".format(app_data["TR_l"][e]))
        f.write(" "*(2 - len(str(int(app_data["TR_t"][e]))))+"{:.2f}\n".format(app_data["TR_t"][e]))
        
        f.write(" # Tableau de frequence(s)\n")
        nb_spaces = 2 - len(str(len(app_data["freq_list"])))
        if nb_spaces < 0:
            MESS_err_mess("Le nombre de fréquences ne peut pas dépasser 99 ! (c'est beaucoup)")
        f.write(" "*nb_spaces+"{}\n".format(len(app_data["freq_list"])))
        for freq in app_data["freq_list"]:
            nb_spaces = 7 - len(str(int(freq)))
            if nb_spaces < 0:
                MESS_err_mess("La fréquences ne peut pas dépasser 9999999 Hz ! (c'est beaucoup)")
            f.write(" "*nb_spaces+"{:.2f}\n".format(freq))
        
        f.write(" # Terrain 1D\n")
        nb_var = int(F_rau!=None)+int(F_eps_r!=None)+int(F_kph!=None)+int(F_kqu!=None)
        if nb_var == 0:
            MESS_err_mess("Sélectionnez au moins un paramètre à varier {rau,eps_r,kph,kqu}")
        f.write(" "+"{}\n".format(nb_var))
        limit_var = [10000,100,21,10]
        if variation == None:
            variation = limit_var[nb_var-1]
        else:
            if variation > limit_var[nb_var-1]:
                MESS_err_mess("Le nombre d'itérations totale doit être inférieur à variation**[nb params] : {}".format(limit_var[nb_var-1]))
        nb_spaces = 5 - len(str(variation))
        f.write(" "*nb_spaces+"{}\n".format(variation))
        S_var_list = [S_rau,S_eps_r,S_kph,S_kqu]
        F_var_list = [F_rau,F_eps_r,F_kph,F_kqu]
        nb_spaces_var = [6,7,4,4]
        for ic,p in enumerate(F_var_list):
            if p != None:
                f.write(" "*3+"{}".format(ic+1))
        f.write("\n")
        for ic,p in enumerate(S_var_list):
            if ic <= 1:
                nb_spaces = nb_spaces_var[ic] - len(str(int(p)))
                if nb_spaces < 0:
                    MESS_err_mess("Valeur de départ trop grande ({})".format(p))
                f.write(" "*nb_spaces+"{:.2f}".format(p))
            else:
                f.write(" "*nb_spaces_var[ic]+"{:.5E}".format(p))
        f.write("\n")
        for ic,p in enumerate(F_var_list):
            if p != None:
                if ic <= 1:
                    nb_spaces = nb_spaces_var[ic] - len(str(int(p)))
                    if nb_spaces < 0:
                        MESS_err_mess("Valeur de départ trop grande ({})".format(p))
                    f.write(" "*nb_spaces+"{:.2f}".format(p))
                else:
                    f.write(" "*nb_spaces_var[ic]+FORTRAN_sc_notation(p,5))
            else:
                if ic <= 1:
                    nb_spaces = nb_spaces_var[ic] - len(str(int(S_var_list[ic])))
                    f.write(" "*nb_spaces+"{:.2f}".format(S_var_list[ic]))
                else:
                    f.write(" "*nb_spaces_var[ic]+FORTRAN_sc_notation(S_var_list[ic],5))
        f.write("\n")

def FORTRAN_sc_notation(n,p):
    """ [TA]\n
    Convert float to a Fortran readable scientific notation.\n
    Format : ``0.[value]E[+/-][exponent]``, example : ``0.12030E-03``.\n
    
    Parameters
    ----------
    n : float
        Float number to convert
    p : int
        Float precision.
    
    Returns
    -------
    s_res : str
        Format string 
    
    Notes
    -----
    Subfunction of ``FORTRAN_constab``.\n
    Python's scientific notation is shifted to the left and cannot be used as raw.
    """
    s = "{:.{}E}".format(n,p)
    s_res = "0."+s[0]+s[2:-5]+"E"+"{:.{}E}".format(n*10,p)[-3:]
    return s_res



