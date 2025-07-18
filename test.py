#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 25 11:57:49 2025

@author: taubertier
"""

import pandas as pd
import numpy as np
import os
import sys
import matplotlib.pyplot as plt
import matplotlib.patches as ptch
import random
import EM_CMD


# data_path = "/home/taubertier/StageMETIS/2024 2025 Aubertier/fichiers donnees/"
# data_path_c=data_path+"CMD mini explorer 3L GPS/"

# os.chdir(data_path_c)

# ls_nom_fich = ['hcpmini-Tr.dat','hcpmini-Tr2.dat','hcpmini-Tr3.dat']

# don1 = pd.read_csv(ls_nom_fich[0],sep='\t')
# don1.dropna(subset = ["Easting","Northing"],inplace=True)
# don1.reset_index(drop=True,inplace=True)
# don2 = pd.read_csv(ls_nom_fich[1],sep='\t')
# # don2.dropna(subset = ["Easting","Northing"],inplace=True)
# # don2.reset_index(drop=True,inplace=True)
# don3 = pd.read_csv(ls_nom_fich[2],sep='\t')
# don3.dropna(subset = ["Easting","Northing"],inplace=True)
# don3.reset_index(drop=True,inplace=True)


# def CMD_evol_profils_mult(don,bas,nom_fich,start,nb_data,verif=False):
    
#     prof_deb = don['Profil'].iat[0]
#     prof_fin = don['Profil'].iat[-1]
#     base_deb = bas['Base'].iat[0]
#     base_fin = bas['Base'].iat[-1]
#     prof_l = prof_fin-prof_deb+1
#     base_l = base_fin-base_deb+1
    
#     col_names = don.columns[start:start+nb_data]
    
#     prof_med = np.array([[0.0]*(prof_fin-prof_deb+1)]*nb_data)
#     base_med = np.array([[0.0]*(base_fin-base_deb+1)]*nb_data)
#     prof_bp = []
#     base_bp = []
#     index_list = []
    
#     color = ["blue","green","orange"]
#     for i in range(prof_l):
#         prof = don[don["Profil"] == i+prof_deb]
#         prof_bp.append(prof['b et p'].iat[0])
#         index_list.append(prof.index[0])
#         for j in range(nb_data):
#             prof_med[j,i] = prof[col_names[j]].median()
#     index_list.append(None)
#     #print(index_list)
#     for i in range(base_l):
#         base = bas[bas["Base"] == i+base_deb]
#         base_bp.append(base['b et p'].iat[0])
#         for j in range(nb_data):
#             base_med[j,i] = base[col_names[j]].median()
#     print(base_med)
#     if verif:
#         fig,ax=plt.subplots(nrows=1,ncols=2,figsize=(18,9))
#         for j in range(nb_data):
#             ax[j%2].plot(prof_bp,prof_med[j]/max(prof_med[j]),'x-',label=col_names[j]+" (profil)",color=color[int(j/2)])
#             ax[j%2].plot(base_bp,base_med[j]/max(base_med[j]),'o-',label=col_names[j]+" (base)",color=color[int(j/2)])
#         ax[0].set_xlabel("Profil")
#         ax[1].set_xlabel("Profil")
#         ax[0].set_ylabel("Valeur en prop. du max")
#         ax[1].set_ylabel("Valeur en prop. du max")
#         # ax[0].set_ylim([0.4, 1])
#         # ax[1].set_ylim([0.9, 1])
#         fig.suptitle(nom_fich+" (données de base)")
#         ax[0].legend()
#         ax[1].legend()
#         plt.show()

#     for i in range(prof_l):
#         prof = don[don["Profil"] == i+prof_deb]
#         r = prof["b et p"].iat[0]
#         k = 0
#         while k < base_l and base_bp[k] < r:
#             k = k+1
        
#         av = k-1
#         ap = k
#         if k == 0:
#             av = 0
#             fact = 0
#         elif k == base_l:
#             ap = base_l-1
#             fact = 1
#         else:
#             fact = (r-base_bp[av])/(base_bp[ap]-base_bp[av])
#         for j in range(nb_data):
#             new_val = prof[col_names[j]]/(fact*base_med[j,ap] + (1-fact)*base_med[j,av])
#             if index_list[i+1] != None:
#                 temp = don.loc[index_list[i+1]][col_names[j]]
#             don.loc[index_list[i]:index_list[i+1], col_names[j]] = new_val
#             if index_list[i+1] != None:
#                 don.loc[index_list[i+1], col_names[j]] = temp
            
#     for i in range(prof_l):
#         prof = don[don["Profil"] == i+prof_deb]
#         for j in range(nb_data):
#             prof_med[j,i] = prof[col_names[j]].median()
    
#     if verif:
#         fig,ax=plt.subplots(nrows=1,ncols=2,figsize=(18,9))
#         for j in range(nb_data):
#             ax[j%2].plot(prof_bp,prof_med[j]/max(prof_med[j]),'x-',label=col_names[j]+" (profil)",color=color[int(j/2)])
#         ax[0].set_xlabel("Profil")
#         ax[1].set_xlabel("Profil")
#         ax[0].set_ylabel("Valeur en prop. du max")
#         ax[1].set_ylabel("Valeur en prop. du max")
#         # ax[0].set_ylim([0.4, 1])
#         # ax[1].set_ylim([0.9, 1])
#         fig.suptitle(nom_fich+" (données redressées)")
#         ax[0].legend()
#         ax[1].legend()
#         plt.show()
    
#     return don.copy()

# # print("??????????????????")
# # don1_d = EM_CMD.CMD_detect_chgt(don1)
# # don1_i = EM_CMD.CMD_intrp_prof(don1_d)
# # don1_i = EM_CMD.CMD_XY_Nan_completion(don1_i)
# # don1_i = EM_CMD.CMD_detect_base_pos(don1_i,2)
# # don_base1,don_mes1=EM_CMD.CMD_sep_BM(don1_i)
# # print("??????????????????")
# # don2_d = EM_CMD.CMD_detect_chgt(don2)
# # don2_i = EM_CMD.CMD_intrp_prof(don2_d)
# # don2_i = EM_CMD.CMD_XY_Nan_completion(don2_i)
# # don2_i = EM_CMD.CMD_detect_base_pos(don2_i,5)
# # don_base2,don_mes2=EM_CMD.CMD_sep_BM(don2_i)
# # #don_mes2 = EM_CMD.CMD_pts_rectif(don_mes2)
# # print("??????????????????")
# # don3_d = EM_CMD.CMD_detect_chgt(don3)
# # don3_i = EM_CMD.CMD_intrp_prof(don3_d)
# # don3_i = EM_CMD.CMD_XY_Nan_completion(don3_i)
# # don3_i = EM_CMD.CMD_detect_base_pos(don3_i,2)
# # don_base3,don_mes3=EM_CMD.CMD_sep_BM(don3_i)
# # print("??????????????????")

# # EM_CMD.CMD_corr_data(don_mes1,don_mes2,verif=False,verif_pts=True)
# # EM_CMD.CMD_corr_data(don_mes1,don_mes3,verif=False,verif_pts=True)
# # EM_CMD.CMD_corr_data(don_mes2,don_mes3,verif=False,verif_pts=True)

# # ab6=don_mes2[don_mes2.columns[0]]
# # ordo=don_mes2[don_mes2.columns[1]]
# # plt.plot(ab6,ordo,'+-k')
# # ab6=don_base2[don_base2.columns[0]]
# # ordo=don_base2[don_base2.columns[1]]
# # plt.plot(ab6,ordo,'+-r')

# # n = 6000
# # p = 6000
# # nb_front = 50
# # a = 1.2
# # b = 0.8

# # x1 = [random.random()*9.5 for i in range(n)]
# # y1 = [random.random()*20 for i in range(n)]
# # x2 = [random.random()*9.5+10.5 for i in range(p)]
# # y2 = [random.random()*20 for i in range(p)]
# # c1 = [a*x1[i] + b*y1[i] for i in range(n)]
# # c2 = [a*x2[i] + b*y2[i] for i in range(p)]
# # print(sum(c1)/n)
# # print(sum(c2)/p)

# # # plt.plot(x1,y1,'+r')
# # # plt.plot(x2,y2,'+b')

# # plt.figure(0)
# # scat = plt.scatter(x1+x2,y1+y2,marker='8',s=14,c=c1+c2,cmap='cividis')
# # plt.colorbar(scat)

# # c2 = [0.2*i+20 for i in c2]

# # plt.figure(1)
# # scat = plt.scatter(x1+x2,y1+y2,marker='8',s=14,c=c1+c2,cmap='cividis')
# # plt.colorbar(scat)

# # sig1 = np.std(c1)
# # sig2 = np.std(c2)

# # diff = 0
# # ec = 1
# # for j in range(n):
# #     diff = diff + c1[j] - c2[j]
# # diff /= n
# # ec = sig1/sig2

# # plt.figure(2)
# # scat = plt.scatter(x1+x2,y1+y2,marker='8',s=14,c=c1+([i*ec + diff for i in c2]),cmap='cividis')
# # plt.colorbar(scat)

# # i_excl = []
# # j_excl = []
# # for i in range(nb_front):
# #     i_min,j_min,d = EM_CMD.CMD_appr_border(x1,x2,y1,y2,n-1,p-1,i_excl,j_excl)
# #     # print("i = ",i_min)
# #     # print("j = ",j_min)
# #     i_excl.append(i_min)
# #     j_excl.append(j_min)
# #     # plt.plot(x1[i_min],y1[i_min],'ok')
# #     # plt.plot(x2[j_min],y2[j_min],'om')
    
# # # diff = 0
# # # for j in range(nb_front):
# # #     diff = diff + c1[i_excl[j]] - c2[j_excl[j]]
# # # diff /= nb_front
    
# # # plt.figure(2)
# # # scat = plt.scatter(x1+x2,y1+y2,marker='8',s=14,c=c1+([i + diff for i in c2]),cmap='cividis')
# # # plt.colorbar(scat)

# # sig1 = np.std([c1[i] for i in i_excl])
# # sig2 = np.std([c2[j] for j in j_excl])

# # diff = 0
# # ec = 1
# # ec = sig1/sig2
# # for j in range(nb_front):
# #     diff = diff + c1[i_excl[j]] - c2[j_excl[j]]*ec
# # diff /= nb_front
# # print("diff = ",diff)
# # print("ec = ",ec)

# # plt.figure(3)
# # scat = plt.scatter(x1+x2,y1+y2,marker='8',s=14,c=c1+([i*ec + diff for i in c2]),cmap='cividis')
# # plt.colorbar(scat)
# # plt.show()

# # don_to_corr = [i for i in range(1,10)]
# # don_corr = [0]
# # is_corr_done = False
# # while is_corr_done == False:
# #     for i in don_corr:
# #         for j in don_to_corr:
# #             print("i -> ",don_corr," et j -> ",don_to_corr)
# #             done = random.random()
# #             if done > 0.5:
# #                 don_to_corr.remove(j)
# #                 don_corr.append(j)
# #         don_corr.remove(i)
# #         if len(don_to_corr) == 0:
# #             is_corr_done = True
# #     if len(don_corr) == 0:
# #         EM_CMD.CMD_warn_mess("Certains jeux de données n'ont pas pu être ajustés. Sont-ils tous frontaliers ?")
# #         is_corr_done = True
    

# # x = np.linspace(0.8,5,500)
# # fig,ax=plt.subplots(nrows=1,ncols=1,figsize=(16,9))
# # ax.plot(x, 5-1/x**2, label = "valeur de l'appareil")
# # ax.set_xlabel(r'$Temps$')
# # ax.set_ylabel(r"$Valeur$")
# # ax.set_aspect('equal')
# # ax.set_title(r"Évolution d'une même donnée prospectée en fonction du temps")
# # plt.legend()
# # plt.show()

# import numpy as np
# def func(x, y):
#     return x*(1-x)*np.cos(4*np.pi*x) * np.sin(4*np.pi*y**2)**2

# grid_x, grid_y = np.mgrid[0:1:100j, 0:1:200j]
# print(grid_x)

# rng = np.random.default_rng()
# points = rng.random((1000, 2))
# values = func(points[:,0], points[:,1])

# from scipy.interpolate import griddata
# grid_z0 = griddata(points, values, (grid_x, grid_y), method='nearest')
# grid_z1 = griddata(points, values, (grid_x, grid_y), method='linear')
# grid_z2 = griddata(points, values, (grid_x, grid_y), method='cubic')

# import matplotlib.pyplot as plt
# plt.subplot(221)
# plt.imshow(func(grid_x, grid_y).T, extent=(0,1,0,1), origin='lower')
# plt.plot(points[:,0], points[:,1], 'k.', ms=1)
# plt.title('Original')
# plt.subplot(222)
# plt.imshow(grid_z0.T, extent=(0,1,0,1), origin='lower')
# plt.title('Nearest')
# plt.subplot(223)
# plt.imshow(grid_z1.T, extent=(0,1,0,1), origin='lower')
# plt.title('Linear')
# plt.subplot(224)
# plt.imshow(grid_z2.T, extent=(0,1,0,1), origin='lower')
# plt.title('Cubic')
# plt.gcf().set_size_inches(6, 6)
# plt.show()

# fig,ax=plt.subplots(nrows=1,ncols=1,figsize=(8,4.5))

# cl = [0,0.33,1,2,4]
# color = ["y","r","m","b","g"]
# radius = 4

# x = np.linspace(-radius,radius,101)
# for i,c in enumerate(cl):
#     y = ((1+radius-np.abs(x))/(1+radius))**c
#     ax.plot(x,y,'-', label = r"coeff = ${}$".format(c), color = color[i])
# plt.legend()
# plt.show()

nomfich=nomfich2
donnees=pd.read_csv(nomfich,sep='\t')

ind_aux=donnees[donnees['Date'].isna()].index

# la liste des indiceq de début de profil est celle des changement de profil
# auxquels on ajoute 1
# il faut ensuite éliminer le dernier et rajouter 0 au début
ind_deb=ind_aux+1
ind_deb=ind_deb.drop(ind_deb[-1]).insert(0,0)

# pour l'indice de fin, la manip est plus légère
ind_fin=ind_aux-1

# on a alors le nombre de points par profil (contrôle qualité, il ne devrait
# pas y avoir de grande différence, sauf explication notées sur le carnet
# de terrain)

nb_pt_prof=ind_fin-ind_deb+1

TxRx6L=np.array((0.2,0.33,0.5,0.72,1.03,1.5))
decal6L=np.round(TxRx6L/2.-0.75,3)
TxRx3L=np.array((0.32,0.71,1.18))
decal3L=np.round(TxRx3L/2.-0.59,3)

# ici on utilise le décalage correspondant à l'appareil utilisé

decal=decal6L
TxRx=TxRx6L

nbvoie=len(TxRx)
# cette boucle permet de calculer la position du centre de l'appareil à
# partir du fichier non interpolé mais pas avec le GPS
# il faut le prendre en compte (à faire, surement avec la 
# détection de la colonne altitude) 
try:
    del(X_fin,Y_fin)
except:
    print('première exécution du script')
pass

for i in range(len(ind_aux)):
    xd,xf=donnees['x[m]'].loc[ind_deb[i]],donnees['x[m]'].loc[ind_aux[i]]
    yd,yf=donnees['y[m]'].loc[ind_deb[i]],donnees['y[m]'].loc[ind_aux[i]]
    if (xd!=xf) :
        xaux=np.linspace(xd,xf,nb_pt_prof[i])
    else:
        xaux=np.full((nb_pt_prof[i],),xd)
    pass
    if (yd!=yf) :
        yaux=np.linspace(yd,yf,nb_pt_prof[i])
    else:
        yaux=np.full((nb_pt_prof[i],),yd)
    pass
    try :
        X_fin=np.append(X_fin,xaux)
    except :
        X_fin=np.copy(xaux)
    pass
    try:
        Y_fin=np.append(Y_fin,yaux)
    except :
        Y_fin=np.copy(yaux)
    pass
pass
















        

