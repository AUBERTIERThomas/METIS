#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 23 09:57:07 2025

@author: taubertier
"""

import os
import glob
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import RBFInterpolator
from scipy.stats.qmc import Halton
from scipy.stats import linregress

import EM_CMD
import CONFIG

os.chdir(CONFIG.data_path)

def CMD_evol_pseudoprof(don,nom_fich,diff=True,verif=False,line=False):
    """ [TA]\n
    Given a profile database and an associated base database, perform profile calibration by alignment of bases (bases are supposed to give the same value each time).\n
    The operation is performed by difference, but it is also possible to perform it by multiplication (ratio).\n
    It is possible to request the rectification of profile blocks if other imperfections are visible, using ``man_adjust = True``.\n
    If you only want to perform this operation, you can disable the first step using the ``auto_adjust = False``.
    
    Notes
    -----
    If used as a standalone, plots every step.\n
    If both ``man_adjust`` and ``auto_adjust`` are set to false, nothing happens.
    
    Parameters
    ----------
    don : dataframe
        Profile dataframe.
    nom_fich : str
        Profile file name. Used in plots.
    col_z : list of int
        Index of every Z coordinates columns (actual data).
    nb_ecarts : int
        Number of X and Y columns. The number of coils.
    ``[opt]`` diff : bool, default : ``True``
        Define which adjustment method (difference or ratio) is used.
    ``[opt]`` verif : bool, default : ``False``
        Enables plotting.
    ``[opt]`` line : bool, default : ``False``
        Shows lines between profiles. Makes the visualization easier.
    
    Returns
    -------
    don : dataframe
        Updated profile dataframe
    """
    global GUI_VAR_LIST
    
    X_n = "Easting"#"X_int"
    Y_n = "Northing"#"Y_int"
    nb_pts = len(don)
    
    pprof_list = []
    dist_list = []
    
    color = ["blue","green","orange","magenta","red","cyan","black","yellow"]
    if line:
        mrk = 'x-'
    else:
        mrk = 'x'
    
    lin_tab_x = np.array([[index, row[X_n]] for index, row in don.iterrows()])
    lin_tab_y = np.array([[index, row[Y_n]] for index, row in don.iterrows()])
    lin_reg_x = linregress(lin_tab_x)
    lin_reg_y = linregress(lin_tab_y)
    
    eq = [lin_reg_x.slope, lin_reg_x.intercept, lin_reg_y.slope, lin_reg_y.intercept]
    
    for index, row in don.iterrows():
        dist_list.append(np.abs(eq[2]*(row[X_n]-eq[1]) - eq[0]*(row[Y_n]-eq[3])))
    
    m1_list = []
    up = True
    for ic,d in enumerate(dist_list[:-1]):
        new_up = (d < dist_list[ic+1])
        if new_up and not up:
            m1_list.append(ic)
        up = new_up
    
    #print(m1_list)
    m2_list = []
    min_med = sorted([dist_list[i] for i in m1_list], key = lambda x: x, reverse = False)[10]*5
    
    for m in m1_list:
        #print(dist_list[m], " ", min_med)
        if dist_list[m] < min_med:
            m2_list.append(m)
    #print(m2_list)
    
    min_list = []
    diff_list = [t - s for s, t in zip(m2_list, m2_list[1:])]
    min_conseq = nb_pts//(2*len(m2_list))
    max_conseq = (2*nb_pts)//len(m2_list)
    l_min = len(m2_list)-1
    i = 0
    while i < l_min:
        d = diff_list[i]
        if d > max_conseq:
            min_list.append(m2_list[i])
            nb_new_points = int(d//max_conseq)
            print(nb_new_points, " ", m2_list[i]," ", m2_list[i+1])
            for n in range(1,nb_new_points+1):
                min_list.append(m2_list[i]+((m2_list[i+1]-m2_list[i])*n)//(nb_new_points+1))
        if d < min_conseq:
            min_list.append(m2_list[i+(dist_list[m2_list[i+1]] < dist_list[m2_list[i]])])
            i += 1
        else:
            min_list.append(m2_list[i])
        i += 1
    if i == l_min:
        min_list.append(m2_list[-1])
    
    print(min_list, " | ", len(min_list))
    don["Profil"] = 0
    l_min = len(min_list)-1
    for index, row in don.iterrows():
        ind = -1
        for ic, m in enumerate(min_list[1:]):
            if m > index:
                if m-index > index-min_list[ic]:
                    ind = ic
                else:
                    ind = ic+1
                break
        if ind == -1:
            ind = l_min
        don.loc[index,"Profil"] = ind
            
    
    index_list = range(nb_pts)
    fig,ax = plt.subplots(nrows=1,ncols=3,figsize=(CONFIG.fig_width,CONFIG.fig_height),squeeze=False)
    ax[0][0].plot(index_list,dist_list,'-')
    ax[0][0].plot([index_list[i] for i in min_list],[dist_list[i] for i in min_list],'xr')
    ax[0][1].plot(don[X_n],don[Y_n],'x')
    ax[0][1].plot([eq[0]*i+eq[1] for i in index_list],[eq[2]*i+eq[3] for i in index_list],'-k')
    ax[0][1].plot([don[X_n][index_list[i]] for i in min_list],[don[Y_n][index_list[i]] for i in min_list],'xr')
    ax[0][1].set_aspect('equal')
    ax[0][2].scatter(don[X_n],don[Y_n],marker='x',c=don["Profil"]%8, cmap='nipy_spectral')
    ax[0][2].set_aspect('equal')
    
    
    return don.copy()

nf = "cmd_GPS_survey.dat"
nf = "cmd_GPS_survey_missing_coordinates.dat"
#nf = "/home/taubertier/StageMETIS/2024 2025 Aubertier/fichiers donnees/CMD mini explorer 3L GPS/hcpmini-Tr.dat"
datah = EM_CMD.TOOL_check_time_date(nf,'\t').dropna(subset=["Easting"]).reset_index(drop=True)
hehe = CMD_evol_pseudoprof(datah,nf,diff=True,verif=False,line=False)