#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 23 09:33:48 2025

@author: taubertier
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

import CONFIG
import EM_CMD

os.chdir(CONFIG.data_path)
# %%

coeffs = EM_CMD.FORTRAN_ball_calibr("bminilo1.dat","VCP",[32,71,118],2,17,15,100,plot=False)
app_data = EM_CMD.JSON_modify_device(1,{"coeff_c_ph" : np.round(coeffs,4).tolist()})
# %%

os.chdir(CONFIG.data_path)
vcp_b, vcp_p = EM_CMD.CMD_init(app_data,file_list=["vcpmini-Tr.dat","vcpmini-Tr2.dat","vcpmini-Tr3.dat"],sep='\t',sup_na=False,regr=False,corr_base=False,plot=True)
# %%

vcp_p = EM_CMD.DAT_light_format(vcp_p,restr=["Inv"])
# %%

vcp_p_corr = EM_CMD.CMD_evol_profils(vcp_p.copy(),vcp_b,[2,3,6,7,10,11],nb_ecarts=app_data["nb_ecarts"],man_adjust=True,line=True)
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

ncx, ncy, nc_data, nb_data, nb_ecarts, nb_res = EM_CMD.TOOL_manage_cols(vcp_p_corr[0],[0,4,8],[1,5,9],[2,3,6,7,10,11])
vcp_p_front = EM_CMD.CMD_frontiere_loop(vcp_p_corr,ncx,ncy,nc_data,nb_data,nb_ecarts,nb_res,choice=True,plot=True)
# %%

final_list = pd.concat(vcp_p_front)
df_grid = EM_CMD.CMD_grid([0,4,8],[1,5,9],[2,3,6,7,10,11],final_list,radius=5,step=0.5,seuil=0,only_nan=False)
# %%

columns = df_grid.columns
for e in range(1):
    df_voie = df_grid.filter([columns[i] for i in [0,1,2+2*e,3+2*e]], axis=1)
    df_voie.dropna(inplace=True)
    all_calibr = EM_CMD.CMD_calibration(1,[2],[3],df_voie)

# %%

# Très long !
all_calibr = EM_CMD.CMD_calibration(app_data,[3,7,11],[2,6,10],final_list[::])
# %%

EM_CMD.DAT_stats(all_calibr,["sigma_1","sigma_2","sigma_3"],bins=100)
EM_CMD.DAT_stats(all_calibr,["Kph_1","Kph_2","Kph_3"],bins=100)
# %%

EM_CMD.FIG_plot_data(all_calibr,[0,4,8],[1,5,9],[18,20,24,26,30,32])
# %%

df_grid = EM_CMD.CMD_grid([0,4,8],[1,5,9],[18,20,24,26,30,32],all_calibr.dropna(),radius=5,step=0.5,seuil=0,only_nan=False)
# %%

EM_CMD.TRANS_df_to_matrix(df_grid,output_file="final_grid.json")








