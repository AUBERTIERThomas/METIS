#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 15 09:26:41 2025

@author: taubertier
"""

import pandas as pd
import numpy as np
import os
import sys
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import random
import EM_CMD

data_path = "/home/taubertier/StageMETIS/2024 2025 Aubertier/fichiers donnees/"
data_path_c=data_path+"CMD mini explorer 3L GPS/"

os.chdir(data_path_c)

# ls_nom_fich = ['hcpmini-Tr.dat','hcpmini-Tr2.dat','hcpmini-Tr3.dat']

# don1 = pd.read_csv(ls_nom_fich[0],sep='\t')
# don1.dropna(subset = ["Easting","Northing"],inplace=True)
# don1.reset_index(drop=True,inplace=True)
# don2 = pd.read_csv(ls_nom_fich[1],sep='\t')
# don2.dropna(subset = ["Easting","Northing"],inplace=True)
# don2.reset_index(drop=True,inplace=True)
# don3 = pd.read_csv(ls_nom_fich[2],sep='\t')
# don3.dropna(subset = ["Easting","Northing"],inplace=True)
# don3.reset_index(drop=True,inplace=True)
don_tot = pd.read_csv("res.dat",sep='\t')

const_GPS = 7
i_GPS = 2
nom_colX = "Easting"
nom_colY = "Northing"

# print("??????????????????")
# don1_d = EM_CMD.CMD_detect_chgt(don1)
# don1_i = EM_CMD.CMD_intrp_prof(don1_d)
# don1_i = EM_CMD.CMD_XY_Nan_completion(don1_i)
# don1_i = EM_CMD.CMD_detect_base_pos(don1_i,2)
# don_base1,don_mes1=EM_CMD.CMD_sep_BM(don1_i)
# print("??????????????????")
# don2_d = EM_CMD.CMD_detect_chgt(don2)
# don2_i = EM_CMD.CMD_intrp_prof(don2_d)
# don2_i = EM_CMD.CMD_XY_Nan_completion(don2_i)
# don2_i = EM_CMD.CMD_detect_base_pos(don2_i,5)
# don_base2,don_mes2=EM_CMD.CMD_sep_BM(don2_i)
# don_mes2 = EM_CMD.CMD_pts_rectif(don_mes2)
# print("??????????????????")
# don3_d = EM_CMD.CMD_detect_chgt(don3)
# don3_i = EM_CMD.CMD_intrp_prof(don3_d)
# don3_i = EM_CMD.CMD_XY_Nan_completion(don3_i)
# don3_i = EM_CMD.CMD_detect_base_pos(don3_i,2)
# don_base3,don_mes3=EM_CMD.CMD_sep_BM(don3_i)
# print("??????????????????")

        
# data_path = "/home/taubertier/StageMETIS/2024 2025 Aubertier/fichiers donnees/donnees SG/2018_CMDm/2018_CMDm_zone1_test/"

# os.chdir(data_path)

# ls_nom_fich = ['Pas18_CMDm_sq1.dat','Pas18_CMDm_sq2.dat','Pas18_CMDm_sq4.dat']
# ls_nom_B1 = ['Pas18_CMDm_sq1_B1.dat','Pas18_CMDm_sq2_B1.dat','Pas18_CMDm_sq4_B1.dat']
# ls_nom_B2 = ['Pas18_CMDm_sq1_B2.dat','Pas18_CMDm_sq2_B2.dat','Pas18_CMDm_sq4_B2.dat']
# don1 = pd.read_csv(ls_nom_fich[0],sep=',')
# don2 = pd.read_csv(ls_nom_fich[1],sep=',')
# don3 = pd.read_csv(ls_nom_fich[2],sep=',')

# don1["X_int"] = don1.iloc[:,0]
# don1["Y_int"] = don1.iloc[:,1]
# don1_i = EM_CMD.CMD_detec_profil_carre(don1)
# don1_B1,don_mes1=EM_CMD.CMD_sep_BM(don1_i)
# don2["X_int"] = don2.iloc[:,0]
# don2["Y_int"] = don2.iloc[:,1]
# don2_i = EM_CMD.CMD_detec_profil_carre(don2)
# don2_B1,don_mes2=EM_CMD.CMD_sep_BM(don2_i)
# don3["X_int"] = don3.iloc[:,0]
# don3["Y_int"] = don3.iloc[:,1]
# don3_i = EM_CMD.CMD_detec_profil_carre(don3)
# don3_B1,don_mes3=EM_CMD.CMD_sep_BM(don3_i)

# const_GPS = 2
# i_GPS = 2
# nom_colX = "x[m]"
# nom_colY = "y[m]"

#dl = [don_mes1,don_mes2,don_mes3]
#dl = [don_mes1[::20],don_mes2[::20],don_mes3[::20]]
#dl = [don_mes1[::5]]
#don_mes= pd.concat(dl)
# don_mes = don_tot[::10]
# don_mes.reset_index(drop=True,inplace=True)
# ls_C=[const_GPS+i*i_GPS for i in range(3)]
# ls_I=[1 + const_GPS+i*i_GPS for i in range(3)]
# ls_T=[const_GPS+i for i in range(6)]
# col_C=don_mes.columns[ls_C]
# col_I=don_mes.columns[ls_I]
# col_T=don_mes.columns[ls_T]
# X = don_mes['X_int']
# Y = don_mes['Y_int']
# nb_data = i_GPS*3

# EM_CMD.CMD_dat_to_grid(don_mes,"X_int","Y_int",col_T,radius=5,prec=200,tol=0.5,only_nan=False,verif=True)

   
    

