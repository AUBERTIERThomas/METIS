#!/usr/bin/env python],[
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 21 15:00:57 2025

@author: taubertier
"""

import os
import matplotlib.pyplot as plt
import pandas as pd

import CONFIG
import EM_CMD

os.chdir(CONFIG.data_path)
# %%

a1 = EM_CMD.CMD_init(0,file_list=["aravo1.dat"],sep='\t',sup_na=False,regr=False,corr_base=False,no_base=True,plot=True)[1][0]
a2 = EM_CMD.CMD_init(0,file_list=["aravo2_1.dat"],sep='\t',sup_na=False,regr=False,corr_base=False,no_base=True)[1][0]
a3 = EM_CMD.CMD_init(0,file_list=["aravo3.dat"],sep='\t',sup_na=False,regr=False,corr_base=False,no_base=True)[1][0]
a4 = EM_CMD.CMD_init(0,file_list=["aravo4.dat"],sep='\t',sup_na=False,regr=False,corr_base=False,no_base=True)[1][0]
a5 = EM_CMD.CMD_init(0,file_list=["aravo5.dat"],sep='\t',sup_na=False,regr=False,corr_base=False,no_base=True)[1][0]
a6 = EM_CMD.CMD_init(0,file_list=["aravo6.dat"],sep='\t',sup_na=False,regr=False,corr_base=False,no_base=True,pseudo_prof=True,l_p=[])[1][0]
a22 = EM_CMD.CMD_init(0,file_list=["aravo22.dat"],sep='\t',sup_na=False,regr=False,corr_base=False,no_base=True,pseudo_prof=True,\
                l_p=[[4993710.01,294875.01],[4993710.01,294930.01],[4993875.01,294930.01],[4993875.01,295020.01],[4993775.01,295020],[4993775.01,294950.01]])[1][0]
a31 = EM_CMD.CMD_init(0,file_list=["aravo31.dat"],sep='\t',sup_na=False,regr=False,corr_base=False,no_base=True,pseudo_prof=True,\
                l_p=[[4993700,294690],[4993650,294755],[4993640,294890],[4993740,294990],[4993665,294850],[4993720,294840]])[1][0]
a221= EM_CMD.CMD_init(0,file_list=["aravo221.dat"],sep='\t',sup_na=False,regr=False,corr_base=False,no_base=True,pseudo_prof=True,\
                l_p=[[4993805,294810],[4993645,294870]])[1][0]
# %%

df_list = EM_CMD.DAT_light_format([a1,a2,a3,a4,a5,a6,a22,a31,a221],restr=["Inv"])
# %%

df_list = EM_CMD.CMD_evol_profils(df_list,[],[2,3,6,7,10,11],nb_ecarts=3,base_adjust=False,man_adjust=True,line=True)
# %%

uwu = EM_CMD.CMD_evol_profils([df_list[0]],[],[2,3,6,7,10,11],nb_ecarts=3,base_adjust=False,man_adjust=True,line=True)[0]
# %%

df_list[0] = uwu
# %%

uwu = EM_CMD.CMD_evol_profils([df_list[2]],[],[2,3,6,7,10,11],nb_ecarts=3,base_adjust=False,man_adjust=True,line=True)[0]
# %%

df_list[2] = uwu
# %%

uwu = EM_CMD.CMD_evol_profils([df_list[3]],[],[2,3,6,7,10,11],nb_ecarts=3,base_adjust=False,man_adjust=True,line=True)[0]
# %%

df_list[3] = uwu
# %%

uwu = EM_CMD.CMD_evol_profils([df_list[4]],[],[2,3,6,7,10,11],nb_ecarts=3,base_adjust=False,man_adjust=True,line=True)[0]
# %%

df_list[4] = uwu
# %%

uwu = EM_CMD.CMD_evol_profils([df_list[5]],[],[2,3,6,7,10,11],nb_ecarts=3,base_adjust=False,man_adjust=True,line=True)[0]
# %%

df_list[5] = uwu
# %%

uwu = EM_CMD.CMD_evol_profils([df_list[7]],[],[2,3,6,7,10,11],nb_ecarts=3,base_adjust=False,man_adjust=True,line=True)[0]
# %%

df_list[7] = uwu
# %%

uwu = EM_CMD.CMD_evol_profils([df_list[8]],[],[2,3,6,7,10,11],nb_ecarts=3,base_adjust=False,man_adjust=True,line=True)[0]
# %%

df_list[8] = uwu
# %%

ncx, ncy, nc_data, nb_data, nb_ecarts, nb_res = EM_CMD.TOOL_manage_cols(df_list[0],[0,4,8],[1,5,9],[2,3,6,7,10,11])
# %%

a4_c = df_list[3]
# %%

a1_c = EM_CMD.CMD_frontiere_loop([a4_c,df_list[0]],ncx,ncy,nc_data,nb_data,nb_ecarts,nb_res,choice=True,plot=True)[1]
# %%

a2_c = EM_CMD.CMD_frontiere_loop([a1_c,df_list[1]],ncx,ncy,nc_data,nb_data,nb_ecarts,nb_res,choice=True,plot=True)[1]
# %%

a3_c = EM_CMD.CMD_frontiere_loop([a1_c,df_list[2]],ncx,ncy,nc_data,nb_data,nb_ecarts,nb_res,choice=True,plot=True)[1]
# %%

a5_c = EM_CMD.CMD_frontiere_loop([a4_c,df_list[4]],ncx,ncy,nc_data,nb_data,nb_ecarts,nb_res,choice=True,plot=True)[1]
# %%

a6_c = EM_CMD.CMD_frontiere_loop([a1_c,df_list[5]],ncx,ncy,nc_data,nb_data,nb_ecarts,nb_res,choice=True,plot=True,nb=100,verif_pts=False)[1]
# %%

a22_c = EM_CMD.CMD_frontiere_loop([a1_c,df_list[6]],ncx,ncy,nc_data,nb_data,nb_ecarts,nb_res,choice=True,plot=True)[1]
# %%

a31_c = EM_CMD.CMD_frontiere_loop([a6_c,df_list[7]],ncx,ncy,nc_data,nb_data,nb_ecarts,nb_res,choice=True,plot=True,verif_pts=True)[1]
# %%

a221_c = EM_CMD.CMD_frontiere_loop([a4_c,df_list[8]],ncx,ncy,nc_data,nb_data,nb_ecarts,nb_res,choice=True,plot=True,verif_pts=True)[1]
# %%

final_list = pd.concat([a1_c,a2_c,a3_c,a4_c,a5_c,a6_c,a22_c,a31_c,a221_c])
EM_CMD.CMD_grid([0,4,8],[1,5,9],[2,3,6,7,10,11],[final_list],radius=0,step=1.5,seuil=0.5,only_nan=False)










