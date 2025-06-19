#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 14 14:26:31 2025

@author: taubertier
"""

import pandas as pd
import numpy as np
import os
import sys
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.patches as ptch
import random
import gstlearn as gl
import gstlearn.plot as gp
import EM_CMD

data_path = "/home/taubertier/StageMETIS/2024 2025 Aubertier/fichiers donnees/"
data_path_c=data_path+"CMD mini explorer 3L GPS/"

os.chdir(data_path_c)

ls_nom_fich = ['hcpmini-Tr.dat','hcpmini-Tr2.dat','hcpmini-Tr3.dat']

don1 = pd.read_csv(ls_nom_fich[0],sep='\t')
don1.dropna(subset = ["Easting","Northing"],inplace=True)
don1.reset_index(drop=True,inplace=True)
don2 = pd.read_csv(ls_nom_fich[1],sep='\t')
don2.dropna(subset = ["Easting","Northing"],inplace=True)
don2.reset_index(drop=True,inplace=True)
don3 = pd.read_csv(ls_nom_fich[2],sep='\t')
don3.dropna(subset = ["Easting","Northing"],inplace=True)
don3.reset_index(drop=True,inplace=True)

const_GPS = 7
i_GPS = 2
nom_colX = "Easting"
nom_colY = "Northing"

print("??????????????????")
don1_d = EM_CMD.CMD_detect_chgt(don1)
don1_i = EM_CMD.CMD_intrp_prof(don1_d)
don1_i = EM_CMD.CMD_XY_Nan_completion(don1_i)
don1_i = EM_CMD.CMD_detect_base_pos(don1_i,2)
don_base1,don_mes1=EM_CMD.CMD_sep_BM(don1_i)
print("??????????????????")
don2_d = EM_CMD.CMD_detect_chgt(don2)
don2_i = EM_CMD.CMD_intrp_prof(don2_d)
don2_i = EM_CMD.CMD_XY_Nan_completion(don2_i)
don2_i = EM_CMD.CMD_detect_base_pos(don2_i,5)
don_base2,don_mes2=EM_CMD.CMD_sep_BM(don2_i)
#don_mes2 = EM_CMD.CMD_pts_rectif(don_mes2)
print("??????????????????")
don3_d = EM_CMD.CMD_detect_chgt(don3)
don3_i = EM_CMD.CMD_intrp_prof(don3_d)
don3_i = EM_CMD.CMD_XY_Nan_completion(don3_i)
don3_i = EM_CMD.CMD_detect_base_pos(don3_i,2)
don_base3,don_mes3=EM_CMD.CMD_sep_BM(don3_i)
print("??????????????????")

# don_mes1 = EM_CMD.CMD_evol_profils(don_mes1,don_base1,ls_nom_fich[0],const_GPS,3*i_GPS,diff=True,verif=True,line=True)
# don_mes2 = EM_CMD.CMD_evol_profils(don_mes2,don_base2,ls_nom_fich[1],const_GPS,3*i_GPS,diff=True,verif=True,line=True)
# don_mes3 = EM_CMD.CMD_evol_profils(don_mes3,don_base3,ls_nom_fich[2],const_GPS,3*i_GPS,diff=True,verif=True,line=True)

# don_mes2, done = EM_CMD.CMD_corr_data(don_mes1,don_mes2,nom_colX,nom_colY,const_GPS,3*i_GPS,m_size=20,verif=False,verif_pts=False,choice=False)
# don_mes3, done = EM_CMD.CMD_corr_data(don_mes1,don_mes3,nom_colX,nom_colY,const_GPS,3*i_GPS,m_size=20,verif=False,verif_pts=False,choice=False)
# don_mes3, done = EM_CMD.CMD_corr_data(don_mes2,don_mes3,nom_colX,nom_colY,const_GPS,3*i_GPS,m_size=20,verif=False,verif_pts=False,choice=False)
    
        
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
# don1_B1 = EM_CMD.DAT_pop_and_dec([ls_nom_B1[0]],"Time","\t",False,"",not_in_file=True)
# don1_B2 = EM_CMD.DAT_pop_and_dec([ls_nom_B2[0]],"Time","\t",False,"",not_in_file=True)
# don1_B1["b et p"], don1_B1["Base"], don1_B2["b et p"], don1_B2["Base"] = -1, 0, don1_i['b et p'].iat[-1]+1, 1
# don_base1 = pd.concat([don1_B1[1::2],don1_B2[1::2]])
# don_base1.reset_index(drop=True,inplace=True)
# don_base1 = don_base1.apply(pd.to_numeric, errors='coerce')
# #don_base1.drop(columns=["Error1[%]","Error2[%]","Error3[%]"],inplace=True)
# don2["X_int"] = don2.iloc[:,0]
# don2["Y_int"] = don2.iloc[:,1]
# don2_i = EM_CMD.CMD_detec_profil_carre(don2)
# don2_B1,don_mes2=EM_CMD.CMD_sep_BM(don2_i)
# don2_B1 = EM_CMD.DAT_pop_and_dec([ls_nom_B1[1]],"Time","\t",False,"",not_in_file=True)
# don2_B2 = EM_CMD.DAT_pop_and_dec([ls_nom_B2[1]],"Time","\t",False,"",not_in_file=True)
# don2_B1["b et p"], don2_B1["Base"], don2_B2["b et p"], don2_B2["Base"] = -1, 2, don2_i['b et p'].iat[-1]+1, 3
# don_base2 = pd.concat([don2_B1[1::2],don2_B2[1::2]])
# don_base2.reset_index(drop=True,inplace=True)
# don_base2 = don_base2.apply(pd.to_numeric, errors='coerce')
# #don_base2.drop(columns=["Error1[%]","Error2[%]","Error3[%]"],inplace=True)
# don3["X_int"] = don3.iloc[:,0]
# don3["Y_int"] = don3.iloc[:,1]
# don3_i = EM_CMD.CMD_detec_profil_carre(don3)
# don3_B1,don_mes3=EM_CMD.CMD_sep_BM(don3_i)
# don3_B1 = EM_CMD.DAT_pop_and_dec([ls_nom_B1[2]],"Time","\t",False,"",not_in_file=True)
# don3_B2 = EM_CMD.DAT_pop_and_dec([ls_nom_B2[2]],"Time","\t",False,"",not_in_file=True)
# don3_B1["b et p"], don3_B1["Base"], don3_B2["b et p"], don3_B2["Base"] = -1, 4, don2_i['b et p'].iat[-1]+1, 5
# don_base3 = pd.concat([don3_B1[1::2],don3_B2[1::2]])
# don_base3.reset_index(drop=True,inplace=True)
# don_base3 = don_base3.apply(pd.to_numeric, errors='coerce')
# #don_base3.drop(columns=["Error1[%]","Error2[%]","Error3[%]"],inplace=True)
# print(don_base1)

# const_GPS = 2
# i_GPS = 2
# nom_colX = "x[m]"
# nom_colY = "y[m]"

# don_mes1 = EM_CMD.CMD_evol_profils(don_mes1,don_base1,ls_nom_fich[0],const_GPS,3*i_GPS,diff=True,verif=True,line=True)
# don_mes2 = EM_CMD.CMD_evol_profils(don_mes2,don_base2,ls_nom_fich[1],const_GPS,3*i_GPS,diff=True,verif=True,line=True)
# don_mes3 = EM_CMD.CMD_evol_profils(don_mes3,don_base3,ls_nom_fich[2],const_GPS,3*i_GPS,diff=True,verif=True,line=True)

# #sys.exit(0)
# don_mes2, done = EM_CMD.CMD_corr_data(don_mes1,don_mes2,nom_colX,nom_colY,const_GPS,3*i_GPS,m_size=20,verif=False,verif_pts=False,choice=False)
# don_mes3, done = EM_CMD.CMD_corr_data(don_mes1,don_mes3,nom_colX,nom_colY,const_GPS,3*i_GPS,m_size=20,verif=False,verif_pts=False,choice=False)
# don_mes3, done = EM_CMD.CMD_corr_data(don_mes2,don_mes3,nom_colX,nom_colY,const_GPS,3*i_GPS,m_size=20,verif=False,verif_pts=False,choice=False)

# dl = [don_mes1,don_mes2,don_mes3]
# don_mes= pd.concat(dl)
# don_mes.reset_index(drop=True,inplace=True)

# ls_C=[const_GPS+i*i_GPS for i in range(3)]
# ls_I=[1 + const_GPS+i*i_GPS for i in range(3)]
# col_C=don_mes.columns[ls_C]
# col_I=don_mes.columns[ls_I]

# for i in range(3):
#     fig1,ax1=plt.subplots(nrows=1,ncols=2,figsize=(16,9))
#     X = don_mes['X_int']
#     Y = don_mes['Y_int']
#     Z1 = don_mes[col_C[i]]
#     Z2 = don_mes[col_I[i]]
#     Q5,Q95 = Z1.quantile([0.05,0.95])
#     col1 = ax1[0].scatter(X,Y,marker='s',c=Z1,cmap='cividis',s=6,vmin=Q5,vmax=Q95)
#     plt.colorbar(col1,ax=ax1[0],shrink=0.7,orientation ='horizontal')
#     ax1[0].title.set_text(col_C[i])
#     Q5,Q95 = Z2.quantile([0.05,0.95])
#     col2 = ax1[1].scatter(X,Y,marker='s',c=Z2,cmap='cividis',s=6,vmin=Q5,vmax=Q95)
#     plt.colorbar(col2,ax=ax1[1],shrink=0.7,orientation ='horizontal')
#     ax1[1].title.set_text(col_I[i])
#     for axc in ax1 :
#         axc.set_xlabel(nom_colX)
#         axc.set_ylabel(nom_colY)
#         axc.set_aspect('equal')
#     plt.show(block=False)
#     plt.pause(0.25)

don_mes = don_mes1[5::10]
ls_C=[const_GPS+i*i_GPS for i in range(3)]
ls_I=[1 + const_GPS+i*i_GPS for i in range(3)]
col_C=don_mes.columns[ls_C]
col_I=don_mes.columns[ls_I]
X = don_mes['X_int']
Y = don_mes['Y_int']

# # # dat = gl.Db.createFromNF(don_mes)
# # # grid = gl.DbGrid.create([100,100], [max(X)-min(X),max(Y)-min(Y)])
# # # M1 = model = gl.Model.createFromParam(gl.ECov.EXPONENTIAL, 0.1, 1.)
# # # gl.simtub(None, grid, model)
# # # #grid.display()

# # # nb = 1000
# # # data = gl.Db.createSamplingDb(grid, 0., nb, ["x1","x2","Simu"])
# # # #data.display()

# # # # gp.plot(data)
# # # # gp.decoration(title="Data Set")
# # # # gp.geometry()

# # # nmini = 5
# # # nmaxi = 10
# # # radius = 0.5
# # # neigh = gl.NeighMoving.create(False, nmaxi, radius, nmini)
# # # neigh.display()

# # # gl.leastSquares(data, grid, neigh, 1)

# # # gp.plot(grid)
# # # gp.decoration(title="Moving Average")



prec = 100
max_X = max(X)
min_X = min(X)
max_Y = max(Y)
min_Y = min(Y)
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

# Le setLocator ne marche pas si le nom de la colonne contient des catactères spéciaux : renommage par indice
for i in range(3):
    don_mes.rename(columns={col_C[i]: str(i*2), col_I[i]: str(i*2+1)},inplace=True)

dat = gl.Db_fromPandas(don_mes)
dat.setLocator("X_int",gl.ELoc.X,0)
dat.setLocator("Y_int",gl.ELoc.X,1)
dat.setLocator("0",gl.ELoc.Z)

grid = gl.DbGrid.create(x0=[min_X,min_Y],dx=[pas_X,pas_Y],nx=[prec_X,prec_Y])
#grid = gl.DbGrid.createCoveringDb(dat,nx=[prec_X,prec_Y])
grid.display()

#dat.setLocator(col_C[0],gl.ELoc.Z,1)
dat.display()

varioParamMulti = gl.VarioParam.createMultiple(ndir=2, nlag=15, dlag=15.)
vario2dir = gl.Vario(varioParamMulti)
err = vario2dir.compute(dat)

fitmod = gl.Model()
types=[gl.ECov.NUGGET, gl.ECov.EXPONENTIAL, gl.ECov.GAUSSIAN]
err = fitmod.fit(vario2dir,types=types)

res = gp.varmod(vario2dir, fitmod)

uniqueNeigh = gl.NeighUnique.create()
err = gl.kriging(dbin=dat, dbout=grid, model=fitmod, 
              neigh=uniqueNeigh,
              flag_est=True, flag_std=True, flag_varz=False,
              namconv=gl.NamingConvention("SK")
              )

fig, ax = gp.init(figsize=(16,9), flagEqual=True)
ax.raster(grid, flagLegend=True)
ax.symbol(dat, c='black')
ax.decoration(title="Simple Kriging over whole Grid")

# nmini = 3
# nmaxi = 6
# radius = 1.5
# neigh = gl.NeighMoving.create(False, nmaxi, radius, nmini)
# gl.leastSquares(dat, grid, neigh, 1)

# fig, ax = gp.init(figsize=(16,9), flagEqual=True)
# ax.raster(grid, flagLegend=True)
# ax.decoration(title="Simple Kriging over whole Grid")

# fig, ax = gp.init(figsize=(16,9), flagEqual=True)
# #print(grid.getColumn("LstSqr.0.estim"))
# X = grid.getColumn("x1")
# Y = grid.getColumn("x2")
# area = grid.getColumn("LstSqr.0.estim")
# col2 = ax.scatter(X,Y,marker='s',c=area,cmap='cividis',s=int(4000/prec))
# plt.colorbar(col2,ax=ax,shrink=0.7,orientation ='horizontal')
# for ic, val in enumerate(area):
#     if val == val:
"""
ECov, UNKNOWN,\
                         UNKNOWN,    -2, "Unknown covariance",\
                         FUNCTION,   -1, "External covariance function",\
                         NUGGET,      0, "Nugget effect",\
                         EXPONENTIAL, 1, "Exponential",\
                         SPHERICAL,   2, "Spherical",\
                         GAUSSIAN,    3, "Gaussian",\
                         CUBIC,       4, "Cubic",\
                         SINCARD,     5, "Sine Cardinal",\
                         BESSELJ,     6, "Bessel J",\
                         MATERN,      7, "Matern",\
                         GAMMA,       8, "Gamma",\
                         CAUCHY,      9, "Cauchy",\
                         STABLE,     10, "Stable",\
                         LINEAR,     11, "Linear",\
                         POWER,      12, "Power",\
                         ORDER1_GC,  13, "First Order Generalized covariance",\
                         SPLINE_GC,  14, "Spline Generalized covariance",\
                         ORDER3_GC,  15, "Third Order Generalized covariance",\
                         ORDER5_GC,  16, "Fifth Order Generalized covariance",\
                         COSINUS,    17, "Cosine",\
                         TRIANGLE,   18, "Triangle",\
                         COSEXP,     19, "Cosine Exponential",\
                         REG1D,      20, "1-D Regular",\
                         PENTA,      21, "Pentamodel",\
                         SPLINE2_GC, 22, "Order-2 Spline",\
                         STORKEY,    23, "Storkey covariance in 1-D",\
                         WENDLAND0,  24, "Wendland covariance (2,0)",\
                         WENDLAND1,  25, "Wendland covariance (3,1)",\
                         WENDLAND2,  26, "Wendland covariance (4,2)",\
                         MARKOV,     27, "Markovian covariances",\
                         GEOMETRIC,  28, "Geometric (Sphere only)",\
                         POISSON,    29, "Poisson (Sphere only)",\
                         LINEARSPH,  30, "Linear (Sphere only)"
"""
"""
EConsElem, UNKNOWN, \
                       UNKNOWN,  0, "Unknown constraint", \
                       RANGE,    1, "Range", \
                       ANGLE,    2, "Anisotropy rotation angle (degree)", \
                       PARAM,    3, "Auxiliary parameter", \
                       SILL,     4, "Sill", \
                       SCALE,    5, "Scale", \
                       T_RANGE,  6, "Tapering range", \
                       VELOCITY, 7, "Velocity (advection)", \
                       SPHEROT,  8, "Rotation angle for Sphere", \
                       TENSOR,   9, "Anisotropy Matrix term"
"""
"""
EConsType, LOWER, \
                       LOWER,   -1, "Lower Bound", \
                       DEFAULT,  0, "Default parameter", \
                       UPPER,    1, "Upper Bound", \
                       EQUAL,    2, "Equality"
"""









