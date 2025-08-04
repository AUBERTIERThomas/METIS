#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 29 16:00:44 2025

@author: taubertier
"""
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

import geophpy as geo
import geophpy.emi as gemi

os.chdir("/home/taubertier/StageMETIS/2024 2025 Aubertier/fichiers donnees/CMD mini explorer 3L GPS/VCP/")
# %%

coeffs = gemi.ball_calibr("bminilo1.dat","VCP",[32,71,118],2,17,15,100,plot=False)
app_data = gemi.add_device('mini3L','VCP',3,[30000],gps=True,gps_dec=[0.25,-0.2],TR_l=[0.32,0.71,1.18],\
TR_t=[0,0,0],height=0.1,bucking_coil=0,coeff_c_ph=np.round(coeffs,4).tolist(),coeff_c_qu=[0.00599,0.0290,0.0785],save=True)
#app_data = gemi.modify_device(1,{"coeff_c_ph" : np.round(coeffs,4).tolist()})
# %%

vcp_b, vcp_p = gemi.init_process(app_data,file_list=["vcpmini-Tr.dat","vcpmini-Tr2.dat","vcpmini-Tr3.dat"],sep='\t',sup_na=False,regr=False,corr_base=False,plot=True)
# %%

vcp_p = EM_CMD.DAT_light_format(vcp_p,restr=["Inv"])
# %%

vcp_p_c = pd.concat(vcp_p)
vcp_b_c = pd.concat(vcp_b)
vcp_p_corr = EM_CMD.CMD_evol_profils(vcp_p_c.copy(),vcp_b_c,[2,3,6,7,10,11],nb_ecarts=app_data["nb_ecarts"],man_adjust=False,line=True,verif=True)[0]
# %%
vcp_p_corr_d = []
for i in range(3):
    vcp_p_corr_d.append(vcp_p_corr[vcp_p_corr["Num fich"] == i+1])

vcp_p_corr_d = EM_CMD.CMD_evol_profils(vcp_p_corr_d,[],[2,3,6,7,10,11],nb_ecarts=app_data["nb_ecarts"],auto_adjust=False,man_adjust=True,line=True)
# %%

vcp_p_corr[0] = EM_CMD.CMD_evol_profils(vcp_p_corr[0],[],[2,3,6,7,10,11],nb_ecarts=app_data["nb_ecarts"],auto_adjust=False,man_adjust=True,line=True)[0]
# %%

vcp_p_corr[1] = EM_CMD.CMD_evol_profils(vcp_p_corr[1],[],[2,3,6,7,10,11],nb_ecarts=app_data["nb_ecarts"],auto_adjust=False,man_adjust=True,line=True)[0]
# %%

fig,ax = plt.subplots(nrows=1,ncols=1,figsize=(16,9))
data_id = 0
Z = vcp_p_corr[data_id]["Inph.1[ppt]"]
Q5,Q95 = Z.quantile([0.05,0.95])
col = ax.scatter(vcp_p_corr[data_id]["X_int_1"],vcp_p_corr[data_id]["Y_int_1"],marker='s',c=Z,cmap='cividis',s=6,vmin=Q5,vmax=Q95)
plt.colorbar(col,ax=ax,shrink=0.7)
ax.set_aspect('equal')
plt.show()
# %%

ncx, ncy, nc_data, nb_data, nb_ecarts, nb_res = EM_CMD.TOOL_manage_cols(vcp_p_corr_d[0],[0,4,8],[1,5,9],[2,3,6,7,10,11])
vcp_p_front = EM_CMD.CMD_frontiere_loop(vcp_p_corr_d,ncx,ncy,nc_data,nb_data,nb_ecarts,nb_res,choice=True,plot=True)
# %%

final_list = pd.concat(vcp_p_front)
final_list.to_csv("all.dat", index=False, sep='\t')
df_grid = EM_CMD.CMD_grid([0,4,8],[1,5,9],[2,3,6,7,10,11],final_list,radius=5,step=0.5,seuil=0,only_nan=False)
# %%

final_list = pd.read_csv("all.dat", sep='\t')
for i in range(3):
    final_list[0+4*i],final_list[1+4*i] = EM_CMD.CMD_decal_posLT(final_list[0+4*i],final_list[1+4*i],final_list["Profils"],decL=-1,decT=0.)
final_list.to_csv("all.dat", index=False, sep='\t')
EM_CMD.FIG_plot_pos("all.dat")
# %%

columns = df_grid.columns
for e in range(1):
    df_voie = df_grid.filter([columns[i] for i in [0,1,2+2*e,3+2*e]], axis=1)
    df_voie.dropna(inplace=True)
    all_calibr = EM_CMD.CMD_calibration(1,[2],[3],df_voie)

# %%

all_calibr = pd.read_csv("all.dat", sep='\t')
# Très long !
all_calibr = EM_CMD.CMD_calibration(1,[3,7,11],[2,6,10],final_list[::50])
#all_calibr.to_csv("all_calibr", index=False, sep='\t')
# %%

# EM_CMD.DAT_stats(all_calibr,["sigma_1","sigma_2","sigma_3"],bins=100)
EM_CMD.DAT_stats(all_calibr,["Kph_1","Kph_2","Kph_3"],bins=100)
# EM_CMD.DAT_stats(all_calibr,["Inph.1[ppt]","Inph.2[ppt]","Inph.3[ppt]"],bins=100)
# %%

EM_CMD.FIG_plot_data(all_calibr,[0,4,8],[1,5,9],[18,20,24,26,30,32])
# %%

df_grid = EM_CMD.CMD_grid([0,4,8],[1,5,9],[18,20,24,26,30,32],all_calibr.dropna(),radius=5,step=0.5,seuil=0,only_nan=False)
# %%

os.chdir(CONFIG.data_path)
EM_CMD.TRANS_df_to_matrix(df_grid,output_file="final_grid.json")
# %%

v1 = pd.read_csv("vcpmini-Tr.dat", sep='\t')
v2 = pd.read_csv("vcpmini-Tr2.dat", sep='\t')
v3 = pd.read_csv("vcpmini-Tr3.dat", sep='\t')
final_list = pd.concat([v1,v2,v3])
EM_CMD.FIG_plot_data(final_list,[1],[0],[8,10,12])

# %%

hcp = pd.read_csv("/home/taubertier/StageMETIS/2024 2025 Aubertier/fichiers donnees/CMD mini explorer 3L GPS/HCP/all_calibr.dat", sep='\t')
EM_CMD.FIG_plot_data(all_calibr,[0,4,8],[1,5,9],[18,20,24,26,30,32])

