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

def CMD_detec_pseudoprof(don,X_n,Y_n,l_p=None,tn=10,tn_c=20,min_conseq=8,verif=False):
    """ [TA]\n
    Given a database with continuous timestamps, estimate profiles by finding one point (called `center`) per profile, possibly at the center.\n
    Each prospection point is then assigned to the closest center in term of index to form pseudo-profiles.\n
    By default, perform a linear regression and select the closest points as centers. For more flexibility, one can set a range of points which will create segments with ``l_p``.
    
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
    """
    for label in ["Profile","Base","b et p"]:
        try:
            don.drop(columns=label)
        except:
            pass
    
    try:
        don[X_n], don[Y_n]
    except KeyError:
        EM_CMD.MESS_err_mess('Les colonnes "{}" et/ou "{}" n\'existent pas'.format(X_n,Y_n))
    
    nb_pts = len(don)
    regr = (l_p == None)
    
    pprof_list = []
    dist_list = []
    
    if regr:
        lin_tab_x = np.array([[index, row[X_n]] for index, row in don.iterrows()])
        lin_tab_y = np.array([[index, row[Y_n]] for index, row in don.iterrows()])
        lin_reg_x = linregress(lin_tab_x)
        lin_reg_y = linregress(lin_tab_y)
        
        eq = [lin_reg_x.slope, lin_reg_x.intercept, lin_reg_y.slope, lin_reg_y.intercept]
        
        for index, row in don.iterrows():
            dist_list.append(np.abs(eq[2]*(row[X_n]-eq[1]) - eq[0]*(row[Y_n]-eq[3])))
    else:
        l_p = np.array(l_p)
        if len(l_p) < 2:
            EM_CMD.MESS_err_mess("Le vecteur de points 'l_p' doit au moins en contenir 2 pour créer un segment")
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
        ax[0][0].plot([index_list[i] for i in min_list],[dist_list[i] for i in min_list],'xr',label="Minimums locaux")
        ax[0][0].set_xlabel("Indice")
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
        plt.pause(0.25)
    
    return don.copy()

nf = "cmd_GPS_survey.dat"
l_p = None
#nf = "cmd_GPS_survey_missing_coordinates.dat"
#l_p=[[4913755,597380],[4913780,597332],[4913840,597311]]
#nf = "/home/taubertier/StageMETIS/2024 2025 Aubertier/fichiers donnees/CMD mini explorer 3L GPS/hcpmini-Tr.dat"
#nf = "/home/taubertier/StageMETIS/2024 2025 Aubertier/fichiers donnees/donnees SG/2018_CMDm/2018_CMDm_zone1/Pas18_CMDm_sq1.dat"
#l_p = None
datah = EM_CMD.TOOL_check_time_date(nf,'\t').dropna(subset=["Easting"]).reset_index(drop=True)
hehe = CMD_detec_pseudoprof(datah,"Easting","Northing",l_p=l_p,verif=True)
