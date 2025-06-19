# -*- coding: utf-8 -*-
"""
Created on Sat Feb 13 17:32:15 2021

@author: thiesson
"""

# programme pour lecture données CMD 
# à faire :
# - des figures propres (échelle de couleur, échelle graphique
# titre, nord) pour avoir un rendu surfer like
# à noter, peut être que Surfer à une API python maintnenant ça permettrait
# de ne pas avoir à tout refaire
# - faire les différents choix (CMDmini3L,mini6L et CMDexpl) qui entrainerait
# des changements automatiques (utilisation d'un dictionnaire avec les listes?)
# - un code de repositionnement intelligent (avec détection des profils de 
# plusieurs manière possible, par le Temps ou par les changements de direction)
# le code de repositionnement fonctionne pour :
# CMD6L acquisition par profils avec GPS (nomrep3)

# Le code doit être testé avec :
# CMD3L acquisition par profils sans GPS (nomrep1)
# CMD6L acquisition par profils sans GPS (nomrep2)

# on base le traitement avec GPS sur les données de limeil brévannes (nomrep3)
# dedans il y a également des bases ...

import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import matplotlib.patches as ptch
import matplotlib.collections as collec
import scipy.interpolate as intrp
os.chdir('C:/Data_equivalent/programmation/python/CMD')
import EM_CMD


# fonction qui effectue le décalage longitudinal et transverse
# par rapport au sens de déplacement
# X,Y et profs sont de pandas.series
# une amélioration serait de le faire avec la courbe paramètrique enveloppe
# issue du cercle de centre la courbe trajectoire

def decal_posLT(X,Y,profs,decL=0.,decT=0.):
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

def detec_base(don_c, seuil,trace=True):
    
    don_int=don_c.copy()
    if 'X_int' in don_int.columns:
        ls_coord=['X_int','Y_int']
    else :
        ls_coord=['Northing','Easting']
        print ('Attention, la détection est plus fiable avec les données\
interpolées')
    if  'b et p' in don_int.columns:
        nom_col='b et p'
    else : 
        print("veuillez faire la détection de changements et ou profils \
avant d'exécuter ce sous programme")
        return (don_mes)
    
    don_aux=don_int.groupby(nom_col)[ls_coord].mean().round(2)

    if trace : 
        fig, ax=plt.subplots(nrows=1,ncols=1)
    
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

    if trace :
        cercle=ptch.Circle((xb,yb),seuil,ec='r',fc='#FFFFFF00')
        ax.add_patch(cercle)
    
    don_int['Base']=0
    for ic,ib in enumerate(ls_base):
        ind_c=don_int.index[don_int[nom_col]==ib]
        don_int.loc[ind_c,'Base']=ic+1
    don_int['Profil']=0        
    for ic,ip in enumerate(ls_prof):
        ind_c=don_int.index[don_int[nom_col]==ip]
        don_int.loc[ind_c,'Profil']=ic+1
        
      
    return(don_int.copy())
       

nomrep1="C:/Data_equivalent/prospection/Tournoisis_Amelie_Laurent/\
2024/CMD miniexplorer/VCP"
nomrep2="C:/Data_equivalent/prospection/Tournoisis_Amelie_Laurent/\
2024/CMD miniexplorer/HCP"
nomrep3="C:/Data_equivalent/prospection/Tournoisis_Amelie_Laurent/\
2024/cmd explorer/HCP"
nomrep4="C:/Data_equivalent/prospection/Tournoisis_Amelie_Laurent/\
2024/cmd explorer/VCP"
nomrep5="C:/Data_equivalent/prospection/Tournoisis_Amelie_Laurent/\
2024/CMD miniexplorer/VVCP"
nomrep=nomrep4
nomreppos=nomrep4
nomfichpos=nomreppos+'/'+'tcmd.dat'

os.chdir(nomrep)

# il faut gérer différentes choses comme la recherche de base ou la présence
# d'un GPS. C'est le rôle des booléens suivants
# qu'on pourra traduire sous forme d'interface si nécessaire
if nomrep in (nomrep1,nomrep2):
    acq_GPS=True
    acq_PtPt=False
    CMD6L=False
    CMD3L=True
    CMDex=False
    Base=True
    init_geom=False
elif nomrep in (nomrep5,) :
    acq_GPS=True
    acq_PtPt=True
    CMD6L=False
    CMD3L=True
    CMDex=False
    Base=True
    init_geom=False
else :
    acq_GPS=True
    acq_PtPt=False
    CMD6L=False
    CMD3L=False
    CMDex=True
    Base=True
    init_geom=False


# ici on a les différents paramètre des différentes géométries
# on pourrait utiliser un dictionnaire

TxRx6L=np.array((0.2,0.33,0.5,0.72,1.03,1.5))
decal6L=np.round(TxRx6L/2.-0.75,3)
TxRx3L=np.array((0.32,0.71,1.18))
decal3L=np.round(TxRx3L/2.-0.59,3)
TxRxex=np.array((1.5,2.4,4.6))
decalex=np.round(TxRxex/2.-2.3,3)

    
#à modifier en fonction de la configuration de prospection 
#décalage entre antenne GPS et centre de l'appareil    
dec_tete_app=np.array((0.4,))

if CMD6L :
    nb_voies=len(decal6L)
    dec_para=decal6L
    if acq_GPS : 
        dec_perp=dec_tete_app
        if len(dec_perp)==1 :
            dec_perp=np.tile(dec_perp,nb_voies)
        else:
            if len(dec_perp)!=nb_voies :
                print('attention,la taille du décalage doit être 1 ou ',\
                      nb_voies,\
                          '\nOn prend la première valeur du tableau fourni')
                dec_perp=np.tile(dec_perp[0],nb_voies)
            pass
        pass
    pass
    TxRx=TxRx6L
    init_geom=True
pass
if CMD3L:
    nb_voies=len(decal3L)
    dec_para=decal3L
    if acq_GPS : 
        dec_perp=dec_tete_app
        if len(dec_perp)==1 :
            dec_perp=np.tile(dec_perp,nb_voies)
        else:
            if len(dec_perp)!=nb_voies :
                print('attention,la taille du décalage doit être 1 ou ',\
                      nb_voies,\
                          '\nOn prend la première valeur du tableau fourni')
                dec_perp=np.tile(dec_perp[0],nb_voies)
            pass
        pass
    pass
    TxRx=TxRx3L
    init_geom=True
pass
if CMDex:
    nb_voies=len(decalex)
    dec_perp=decalex
    if acq_GPS : 
        dec_para=dec_tete_app
        if len(dec_para)==1 :
            dec_para=np.tile(dec_para,nb_voies)
        else:
            if len(dec_para)!=nb_voies :
                print('attention,la taille du décalage doit être 1 ou ',\
                      nb_voies,\
                          '\nOn prend la première valeur du tableau fourni')
                dec_para=np.tile(dec_para[0],nb_voies)
            pass
        pass
    pass
    TxRx=TxRxex
    init_geom=True
pass
if not(init_geom) :
    print('pas d''initialisation, arrêt du script')
    exit()
pass
    
# initialisaiton de la liste de fichiers VCP pour concaténation 

ls_nomfich=os.listdir()
# VCP mini
if nomrep==nomrep1 : 
    ls_nomf=[ls_nomfich[3],ls_nomfich[7],ls_nomfich[11]]
    ls_date=['10/14/2024','10/14/2024','10/16/2024']

# HCP mini
if nomrep==nomrep2 :
    ls_nomf=[ls_nomfich[2],ls_nomfich[6],ls_nomfich[10]]
    ls_date=['10/15/2024','10/15/2024','10/17/2024']

# HCP expl
if nomrep==nomrep3 : 
    ls_nomf=[ls_nomfich[4],]
    ls_date=['10/15/2024',]

# VCP expl
if nomrep==nomrep4 : 
    ls_nomf=[ls_nomfich[7],]
    ls_date=['10/16/2024',]
#VVCP mini
if nomrep==nomrep5 : 
    ls_nomf=[ls_nomfich[3],]
    ls_date=['10/16/2024',]

# concaténation si nécessaire avant traitement
ls_pd=[]

for ic,f in enumerate(ls_nomf) :
    ls_pd.append(pd.read_csv(f,sep='\t'))
    ls_pd[-1]['Num fich']=ic+1
    
if acq_GPS :
    #si DGPS i_GPS=3 si GPS i_GPS=1
    i_GPS=3
    nom_colX='Northing'
    nom_colY='Easting'
else :
    i_GPS=0
    nom_colX='x[m]'
    nom_colY='y[m]'
pass

xp=pd.read_csv(nomfichpos,sep='\t')[nom_colX]
yp=pd.read_csv(nomfichpos,sep='\t')[nom_colY]

if CMD6L :
     if acq_PtPt :
         ls_C=[4+i_GPS,7+i_GPS,10+i_GPS,13+i_GPS,16+i_GPS,19+i_GPS]
         ls_I=[5+i_GPS,8+i_GPS,11+i_GPS,14+i_GPS,17+i_GPS,20+i_GPS]
     else :
         ls_C=[4+i_GPS,6+i_GPS,8+i_GPS,10+i_GPS,12+i_GPS,14+i_GPS]
         ls_I=[5+i_GPS,7+i_GPS,9+i_GPS,11+i_GPS,13+i_GPS,15+i_GPS]

else:
     if acq_PtPt :
         ls_C=[4+i_GPS,7+i_GPS,10+i_GPS]
         ls_I=[5+i_GPS,8+i_GPS,11+i_GPS]
     else:
         ls_C=[4+i_GPS,6+i_GPS,8+i_GPS]
         ls_I=[5+i_GPS,7+i_GPS,9+i_GPS]
pass

for ic,don_c in enumerate (ls_pd) :
    print('fichier de données n°{}'.format(ic+1))
    col_C=don_c.columns[ls_C]
    print(don_c[col_C].describe())
    col_I=don_c.columns[ls_I]
    print(don_c[col_I].describe())
    don_c['Date']=ls_date[ic]

    
    
don_raw=pd.concat(ls_pd)
col_C=don_raw.columns[ls_C]
col_I=don_raw.columns[ls_I]
don_raw.index=np.arange(don_raw.shape[0])
don_raw['temps (s)']=EM_CMD.CMD_time(don_raw)

# On gère les prospections faites des jours différents
for ic,date_c in enumerate(don_raw['Date'].unique()) :
    if ic>0 :
        ind_d =don_raw.index[don_raw['Date']==date_c]
        don_raw.loc[ind_d,'temps (s)']=don_raw.loc[ind_d,'temps (s)']+ic*86400
    

# vérification de la bonne détection des chagement (base ou profil
# dans la prospection)
don_c=EM_CMD.CMD_detect_chgt(don_raw,verif=True)

# interpolation des positions

don_int=EM_CMD.CMD_intrp_prof(don_c)


# Séparation base profil
if nomrep == nomrep1 : seuil_c=0.5
if nomrep == nomrep2 : seuil_c=2
if nomrep == nomrep3 : seuil_c=0.5
if nomrep == nomrep4 :seuil_c=0.5

#seuil_c=0.5
don_int=detec_base(don_int,seuil_c)




    
#don_c=EM_CMD.CMD_detect_basec(don_c,seuil=seuil_c)
#don_c=EM_CMD.CMD_num_prof(don_c)

ind_mes=don_c.index[don_int['Profil']!=0]
ind_base=don_c.index[don_int['Base']!=0]



# on affiche les points de mesure sans repositionnement ni interpolation
fig1,ax1=plt.subplots(nrows=1,ncols=2,figsize=(9.,6.))
X=don_c.loc[ind_mes,'X_int']
Y=don_c.loc[ind_mes,'Y_int']
Z1=don_c.loc[ind_mes,col_C[1]]
Z2=don_c.loc[ind_mes,col_I[0]]
Q5,Q95=Z1.quantile([0.05,0.95])
col1=ax1[0].scatter(X,Y,marker='s',c=Z1,cmap='cividis',s=12,vmin=Q5,vmax=Q95)
plt.colorbar(col1,ax=ax1[0],shrink=0.7,orientation ='horizontal')
Q5,Q95=Z2.quantile([0.05,0.95])
col2=ax1[1].scatter(X,Y,marker='s',c=Z2,cmap='cividis',s=8,vmin=Q5,vmax=Q95)
plt.colorbar(col2,ax=ax1[1],shrink=0.7,orientation ='horizontal')
for axc in ax1 :
    axc.set_aspect('equal')
    #axc.scatter(xp,yp,c='red')
    
    
#fin de lecture du fichier

# détermination des paramètres de base

col_par=col_I.append(col_C)
base_tps,base_sup,base_inf=EM_CMD.CMD_synthBase(don_int,col_par,CMDmini=True)
###
if nomrep==nomrep1:
    base_ht=base_sup
    base_bs=base_inf
if nomrep==nomrep2:
    base_ht=base_inf
    base_bs=base_sup

nb_param=base_ht.shape[0]
nb_base=base_ht.shape[1]
num_base=don_int['Base'].unique()
num_base.sort()
num_base=num_base[1:]
# tracé de vérification des bases déterminées

for ic,num_b in enumerate(num_base):
    plt.figure()
    param=col_I[0]
    ind_c=don_int.index[don_int['Base']==num_b]
    ab6=don_int.loc[ind_c,'temps (s)']
    ab6b=base_tps.loc[num_b-1]
    ordob=base_ht.loc[param,num_b-1]
    try : 
        ordoc=base_bs.loc[param,num_b-1]
    except :
        'pas de base en bas'
        ordoc=base_ht.loc[param,num_b-1]
        ordoc=ordoc/1.5
    ordo=don_int.loc[ind_c,param]
    plt.plot(ab6,ordo,'+-')
    plt.plot(ab6b,ordob,'o r')
    plt.plot(ab6b,ordoc,'o g')


#calcul des valeurs interpolées de bases pour correction (linéaire)        
col_par=col_I

for num_b in num_base[:-1]:
    ind_d=don_int.index[don_int['Base']==num_b][-1]
    ind_f=don_int.index[don_int['Base']==num_b+1][0]
    cond1=don_int['temps (s)']>don_int.loc[ind_d,'temps (s)']
    cond2=don_int['temps (s)']<don_int.loc[ind_f,'temps (s)']

    ind_t=don_int.index[np.logical_and(cond1,cond2)]
    tf=don_int.loc[ind_t,'temps (s)']
    tb1,tb2=base_tps[[num_b-1,num_b]]
    for param in col_par :
        valb1,valb2=base_ht.loc[param,[num_b-1,num_b]]
        don_int.loc[ind_t,param+'_corrB']=np.interp(tf,[tb1,tb2],[valb1,valb2])
    
#vérification

plt.figure()
for param in col_par :
    plt.plot(don_int['temps (s)'],don_int[param],'+ k')
    plt.plot(don_int['temps (s)'],don_int[param+'_corrB'],'--b')




# partie spécifique CMD explorer

don_base,don_mes=EM_CMD.CMD_sep_BM(don_int)

# analyse de la base
# marche pour CMD mini et CMD expl
X=don_base['X_int']
Y=don_base['Y_int']


fig1,ax1=plt.subplots(nrows=2,ncols=3,figsize=(9.,6.))
col_par=col_C.append(col_I)
Tps=don_base['temps (s)']
num_base=don_base['Base'].unique()
for nbc in num_base :
    indc=don_base.index[don_base['Base']==nbc]
    tps_c=Tps.loc[indc]
    for ic,par in enumerate(col_par) :
        axc=ax1.flatten()[ic]
        val_c=don_base.loc[indc,par]
        med_c=val_c.median()
        #axc.plot(tps_c,val_c)
        axc.scatter(tps_c.median(),med_c,marker='o',c='r',s=30)
        axc.set_title(par)

Tps=don_mes['temps (s)']
num_mes=don_mes['Profil'].unique()
for nmc in num_mes :
    indc=don_mes.index[don_mes['Profil']==nmc]
    tps_c=Tps.loc[indc]
    for ic,par in enumerate(col_par) :
        axc=ax1.flatten()[ic]
        val_c=don_mes.loc[indc,par]
        med_c=val_c.median()
        #axc.plot(tps_c,val_c)
        axc.scatter(tps_c.median(),med_c,marker='s',c='b',s=25)
        axc.set_title(par)


fig1,ax1=plt.subplots(nrows=2,ncols=3,figsize=(9.,6.))
X=don_mes['X_int']
Y=don_mes['Y_int']

col_par=col_C.append(col_I)

for ic,param in enumerate(col_par):
    
    axc=ax1.flatten()[ic]
    tnc=don_mes[param]
     
    Q5,Q95=tnc.quantile([0.05,0.95])

    col0=axc.scatter(X,Y,marker='s',c=tnc,cmap='cividis',s=12,vmin=Q5,vmax=Q95)
    plt.colorbar(col0,ax=axc,shrink=0.7,orientation ='horizontal')
    axc.set_aspect('equal')
  

# partie spécifique CMD mini explorer    
# après avoir calculé et corrigé les valeur de base, on peut s'en affranchir
# et ne travailler que sur les mesures

don_base,don_mes=EM_CMD.CMD_sep_BM(don_int)

#• on visualise la carte après correction

fig1,ax1=plt.subplots(nrows=2,ncols=3,figsize=(9.,6.))
X=don_mes['X_int']
Y=don_mes['Y_int']
col_par=col_I

for ic,param in enumerate(col_par):
    tnc=don_mes[param]
    t=don_mes[param]-don_mes[param+'_corrB']
    
    Q5,Q95=tnc.quantile([0.05,0.95])

    col0=ax1[0,ic].scatter(X,Y,marker='s',c=tnc,cmap='cividis',s=12,vmin=Q5,vmax=Q95)
    plt.colorbar(col0,ax=ax1[0,ic],shrink=0.7,orientation ='horizontal')
    Q5,Q95=t.quantile([0.05,0.95])
    col1=ax1[1,ic].scatter(X,Y,marker='s',c=t,cmap='cividis',s=12,vmin=Q5,vmax=Q95)
    plt.colorbar(col1,ax=ax1[1,ic],shrink=0.7,orientation ='horizontal')
    ax1[0,ic].set_title('Voie {}'.format(ic+1))
    
for axc in ax1.flatten() :
    axc.set_aspect('equal')
    
fig1.text(0.05,0.7,'avant\ncorrection')
fig1.text(0.05,0.35,'après\ncorrection')

# on applique les décalages supplémentaires associés à la configuration de la
# prospection
if nomrep in (nomrep1,nomrep2) :
    decL=0.25 # (positif si en avant négatif sinon)
    decT=-0.2 # (positif si à babord négatif si à tribord)

if nomrep in (nomrep3,nomrep4) :
    decL=0.35
    decT=0.2

ls_prof=don_mes['Profil'].unique()

#on repositionne au bon endroit
Xc3,Yc3=decal_posLT(don_mes['X_int'],don_mes['Y_int'],don_mes['Profil']\
                  ,decL,decT)

if nomrep in (nomrep1,nomrep2) :    
    Xc2,Yc2=decal_posLT(Xc3,Yc3,don_mes['Profil'],-1*decal3L[1],0)
    Xc1,Yc1=decal_posLT(Xc3,Yc3,don_mes['Profil'],-1*decal3L[0],0)

    
if nomrep in (nomrep3,nomrep4) :    
    Xc2,Yc2=decal_posLT(Xc3,Yc3,don_mes['Profil'],0,decalex[1])
    Xc1,Yc1=decal_posLT(Xc3,Yc3,don_mes['Profil'],0,decalex[0])

don_mes['X_v1']=np.round(Xc1,2)
don_mes['Y_v1']=np.round(Yc1,2)
don_mes['X_v2']=np.round(Xc2,2)
don_mes['Y_v2']=np.round(Yc2,2)
don_mes['X_v3']=np.round(Xc3,2)
don_mes['Y_v3']=np.round(Yc3,2)
    
#tracé de vérification

fig2,ax2=plt.subplots(nrows=1,ncols=1)

X=don_mes['X_int']
Y=don_mes['Y_int']


ax2.plot(X,Y,'+ k',label ='originaux')    
ax2.plot(Xc3,Yc3,'+ r',label='décalés v3')
ax2.plot(Xc2,Yc2,'+ g',label='décalés v2')
ax2.plot(Xc1,Yc1,'+ b',label='décalés v1')
ax2.legend()
ax2.set_aspect('equal')

# si c'est OK alors on sauve dans un fichier pour faire la représentation
# dans un autre script
nomreps='traitement'
os.makedirs(nomreps, exist_ok=True)
os.chdir(nomreps)

col_v1=['X_v1', 'Y_v1','Inph.1[ppt]','Inph.1[ppt]_corrB','Cond.1[mS/m]',\
        'Profil','Num fich','Altitude']
col_v2=['X_v2', 'Y_v2','Inph.2[ppt]','Inph.2[ppt]_corrB','Cond.2[mS/m]',\
        'Profil','Num fich','Altitude']
col_v3=['X_v3', 'Y_v3','Inph.3[ppt]','Inph.3[ppt]_corrB','Cond.3[mS/m]',\
        'Profil','Num fich','Altitude']
ls_col=[col_v1,col_v2,col_v3]

if nomrep==nomrep1 :
    nomfs='VCPmini'

if nomrep==nomrep2 :
    nomfs='HCPmini'

if nomrep==nomrep3 :
    nomfs='HCPexpl'

if nomrep==nomrep4 :
    nomfs='VCPexpl'

for ic,col_c in enumerate(ls_col):
    pd_s=don_mes.loc[:,col_c].copy()
    nomfs_c=nomfs+'_v{:02d}'.format(ic+1)+'.dat'
    pd_s.to_csv(nomfs_c,index=False)
    
    





# on parcourt les numéro de fich pour ajouter des décalages si nécessaire

dec_ph=np.arange(0.05,0.071,0.005)
numfich=3
for dec in dec_ph :
    fig1,ax1=plt.subplots(nrows=1,ncols=3,figsize=(9.,6.))
    X=don_mes[nom_colX]
    Y=don_mes[nom_colY]
    indf=don_mes.index[don_mes['Num fich']==numfich]
    for ic,param in enumerate(col_par):
        t=don_mes[param]-don_mes[param+'_corrB']
        t.loc[indf]=t.loc[indf]+dec
        Q5,Q95=t.quantile([0.05,0.95])
        col1=ax1[ic].scatter(X,Y,marker='s',c=t,cmap='cividis',s=12,vmin=Q5,vmax=Q95)
        plt.colorbar(col1,ax=ax1[ic],shrink=0.7,orientation ='horizontal')
        ax1[ic].set_title('Voie {}'.format(ic+1))
        
    fig1.suptitle('Décalage = {}'.format(dec))
    
# le décalage après correction de base VCP mini est de 0,065 entre 1,2 et 3
# on initialise également les coefficients pour arriver en ppm
# à mettre dans une fonction étalonnage ave cmot clef qui fait al transformation


if nomrep==nomrep1 :
    dec=[0.065,0.065,0.065]
    ls_coef_cond_CMD=[[0.00591,0.0281,0.0745],[0.00599,0.0290,0.0785]][0]
    ls_coeff_ppt_ppm=[2029,1635,1400]
    
    
# coefficient établi avec les codes 1D
# valeur pour CMD 3L à 10 cm d'altitude en VCP
ls_kph_ppm=[1e5/303907.5,1e5/444428.,1e5/477585.]
# valeur pour CMD 3L à 4 cm d'altitude en VCP (posé sur le sol)
#ls_kph_ppm=[1e5/455376.6,1e5/489365.,1e5/495247.]
# coefficient établi avec les codes 1D
# valeur pour CMD 3L à 10 cm d'altitude en HCP
#ls_kph_ppm=[1e5/47901.3,1e5/347132.,1e5/438506.5]
    
# on fait la correction sur la prospection
col_par=col_I
numfich=3
indf=don_mes.index[don_mes['Num fich']==numfich]
for ic,param in enumerate(col_par):
    t=don_mes[param]-don_mes[param+'_corrB']
    t.loc[indf]=t.loc[indf]+dec[ic]
    don_mes[param+'_bcor']=t

# on récupéère les données avec leurs positions interpolées

don_mes2=EM_CMD.CMD_intrp_prof(don_mes)

fig1,ax1=plt.subplots(nrows=1,ncols=3,figsize=(9.,6.))
X1=don_mes2['X_int']
Y1=don_mes2['Y_int']

col_par=['Inph.1[ppt]_bcor', 'Inph.2[ppt]_bcor',
'Inph.3[ppt]_bcor']
for ic,param in enumerate(col_par):
    tnc=don_mes2[param]
    Q5,Q95=tnc.quantile([0.05,0.95])
    col0=ax1[ic].scatter(X1,Y1,marker='.',c=tnc,cmap='cividis',s=12,vmin=Q5,vmax=Q95)
    plt.colorbar(col0,ax=ax1[ic],shrink=0.7,orientation ='horizontal')

for axc in ax1 :
    axc.set_aspect('equal')

# on complète les données en X et Y si nécessaire
X_int2,Y_int2=EM_CMD.CMD_XY_Nan_completion_old(don_mes2.loc[:,'X_int'].copy(),\
                                don_mes2.loc[:,'Y_int'].copy())

fig2,ax2=plt.subplots(nrows=1,ncols=1)

ax2.plot(X_int2,Y_int2,'o r')    
ax2.plot(X1,Y1,'+ k')

don_mes2.loc[:,'X_int']=X_int2
don_mes2.loc[:,'Y_int']=Y_int2

# on nettoie le fichier pour n'avoir plus que les colonnes utiles après tous
# les prétraitements nécessaires (correction base, correciton cond sur phase
# interpolation, recalage de prospection d'un jour à l'autre)

# les colonnes qui restent sont donc normalement 
# 'X_int', 'Y_int', 'profil', 'condv1','conv2','condv3',kph1,kph2,kph3 
col_utiles=don_mes2.columns[[-2,-1,]].append(col_I.append(col_C))
don_mes3=don_mes2.loc[:,col_utiles].copy()    
don_mes3['Profil']=don_mes2['Profil']

# réaliser les fonctions de décalages (dans le sens de l'avancement
#  et perpendiculairement )    
# l'algo semble marcher mais il faut sans doute faire quelque chose 
# pour les fin de profils
# faire un algo par profil


decL=-0.2 # (positif si en avant négatif sinon)
decP=-0.25 # (positif si à babord négatif si à tribord)
ls_prof=don_mes3['Profil'].unique()

#on repositionne au bon endroit
Xc3,Yc3=decal_posLT(don_mes3['X_int'],don_mes3['Y_int'],don_mes3['Profil']\
                  ,0.2,-0.25)
    
Xc2,Yc2=decal_posLT(Xc3,Yc3,don_mes3['Profil'],-1*decal3L[1],0)
Xc1,Yc1=decal_posLT(Xc3,Yc3,don_mes3['Profil'],-1*decal3L[0],0)

fig2,ax2=plt.subplots(nrows=1,ncols=1)

# ls_Xc=[]
# ls_Yc=[]

# for prof in ls_prof:
#     ind_c=don_mes3.index[don_mes3['Profil']==prof]
#     X=don_mes3.loc[ind_c,'X_int'].copy()
#     Y=don_mes3.loc[ind_c,'Y_int'].copy()
#     DX=X.diff()
#     DY=Y.diff()
#     DX1=DX.copy()
#     DY1=DY.copy()
#     DX.iloc[0:-1]=DX.iloc[1:]      
#     DY.iloc[0:-1]=DY.iloc[1:]
#     DX1.iloc[0]=DX1.iloc[1]
#     DY1.iloc[0]=DY1.iloc[1]
#     DR=np.sqrt(DX*DX+DY*DY)       
#     DR1=np.sqrt(DX1*DX1+DY1*DY1)
#     CDir=(DX/DR+DX1/DR1)/2.
#     SDir=(DY/DR+DY1/DR1)/2.
#     decX=CDir*decL-SDir*decP
#     decY=SDir*decL+CDir*decP
#     X1=X+decX
#     Y1=Y+decY
#     ls_Xc.append(X1)
#     ls_Yc.append(Y1)
   
# Xc=pd.concat(ls_Xc) 
# Yc=pd.concat(ls_Yc)   
X=don_mes3['X_int']
Y=don_mes3['Y_int']



ax2.plot(X,Y,'+ k',label ='originaux')    
ax2.plot(Xc3,Yc3,'+ r',label='décalés v3')
ax2.plot(Xc2,Yc2,'+ g',label='décalés v2')
ax2.plot(Xc1,Yc1,'+ b',label='décalés v1')
ax2.legend()
ax2.set_aspect('equal')


# mis eau propre des fichiers prétraité et sauvegarde
os.makedirs('don_corr', exist_ok=True)
os.chdir(nomrep+'/don_corr')
nomf='CMD_VCP_mini'

don_v1=pd.DataFrame()
don_v2=pd.DataFrame()
don_v3=pd.DataFrame()


ls_don=[don_v1,don_v2,don_v3]
ls_X=[Xc1,Xc2,Xc3]
ls_Y=[Yc1,Yc2,Yc3]
for ic,don_c in enumerate(ls_don) :
    don_c['X']=ls_X[ic]
    don_c['Y']=ls_Y[ic]
    don_c['Profil']=don_mes3['Profil']
    don_c['inph_c']=don_mes3['Inph.'+str(ic+1)+'[ppt]']
    don_c['Cond_c']=don_mes3['Cond.'+str(ic+1)+'[mS/m]']
    don_c.to_csv(nomf+'_v'+str(ic+1)+'.dat',index=False)

         
    
   
    

    
    
# on repère la nécessiter d'interpoler parce que la différence entre les points
# successifs est nulle. en théorie, la valeur initiale est celle du segment
# sur lequel se trouve le point et la valeur finale est celle du changement
# donc si l'on repère tous les DR=0 (<=> les points consécutifs ont les mêmes
# coordonnées)
# en complément, les points qui ont un DR non nul sont normalement les débuts
# des segments.
# le seul bémol ce sont les points en fin de profil. Car le point suivant n'est 
# PAS sur le même segment, ils faut donc les détecter et les traiter
# différement

ind_a_garder=(don_c.index[DR!=0]+1)[:-1]
ind_a_garder=ind_a_garder.insert(0,0)
nb_pts=ind_a_garder.diff()-1

ind_a_int1=don_c.index[DR==0]
ls_intrpX,ls_intrpY=[],[]
for ic,ind_f in enumerate(ind_a_garder[1:]):
    Xdeb,Ydeb=X[ind_a_garder[ic]],Y[ind_a_garder[ic]]
    Xfin,Yfin=X[ind_f],Y[ind_f]
    nb_pt=nb_pts[ic+1]
#    print("début : ({},{}) - fin : ({},{}),\n\
# Nombre de points à interpoler : {}".format(Xdeb,Ydeb,Xfin,Yfin,nb_pt))
    ls_intrpX.append(np.linspace(Xdeb,Xfin,int(nb_pt)+2)[:-1])
    ls_intrpY.append(np.linspace(Ydeb,Yfin,int(nb_pt)+2)[:-1])
    
X_int1=np.concatenate(ls_intrpX)
Y_int1=np.concatenate(ls_intrpY)

#on vérifie que l'interpolation c'est bien passée
fig2,ax2=plt.subplots(nrows=1,ncols=1)

ax2.plot(X,Y,'o r')
ax2.plot(X_int1,Y_int1,'+ k')
ax2.set_aspect('equal')




   

    

# sauvegarde à la volée après réinterpolation
SauvessGPS=pd.DataFrame()
SauvessGPS['X']=don_ass[nom_colX]
SauvessGPS['Y']=don_ass[nom_colY]

for i_voie in range(nb_voies):
    nom_col_C,nom_col_K='Cond_V'+str(i_voie+1),'Kph_V'+str(i_voie+1)
    SauvessGPS[nom_col_C]=don_ass[nom_cond[i_voie]]
    SauvessGPS[nom_col_K]=don_ass[nom_inph[i_voie]]
pass
nomfichs='limeil2705.dat'
SauvessGPS.to_csv(nomfichs,sep='\t',index=False)


#------------------------------------------------------------------------------
# la section suivante gère l'interpolation avec GPS proprement
# sans GPS, la gestion est faite au moment de l'extration des données (gestion
# plus simple des débuts et fin de profils)
# Gestion de l'interpolation propre (en particulier pour les fins de profils)
# à la fin de cette boucle on a donc les position des centres de Tx Rx
# corrigées pour chacunes des voies de l'appareil


tab_etiq=don_ass['étiquette'].unique()
i_etiq=0
for etiq in tab_etiq:
    ind_cour=don_ass['étiquette']==etiq
    Xc=don_ass.loc[ind_cour].iloc[:,1]
    Yc=don_ass.loc[ind_cour].iloc[:,0]
    DX=Xc.diff()
    DX[0]=0
    DY=Yc.diff()
    DY[0]=0
    DR=np.sqrt(DX*DX+DY*DY)
   
    ind_a_int=DR==0
# le début du profil a toujours une coordonnées GPS correcte
    ind_a_int[0]=False
    ind_deb_fin=np.logical_not(ind_a_int)
    
# ici il faut gérer le fait que les points GPS sont rarement à la fin de
# chaque profil.
# on doit donc reporter la direction et les écatements du morceau
# précédent sur le dernier Tronçon
# il faut maintenant interpoler entre les positions pour obtenir les positions
# de chaque point et gérer la fin des profils (avec la différence
# entre l'indice du dernier point de référence et du dernier point du profil)
    
    ind_d=Xc[ind_deb_fin].index
    ind_f=Xc[ind_deb_fin].index
    ind_f=ind_f.drop(ind_f[0])
    depass=False
    if Xc.index[-1]!=ind_d[-1]:
        ind_f=ind_f.insert(len(ind_f),Xc.index[-1])
        depass=True
    pass
    n=len(ind_d)-1
  
    for i_int in range(n):
        i_d,i_f=ind_d[i_int],ind_f[i_int]
        nb=i_f-i_d+1
        if i_int>0 :
            X_cour=np.append (X_cour,np.linspace(Xc[i_d],Xc[i_f],nb)[1:])
            Y_cour=np.append (Y_cour,np.linspace(Yc[i_d],Yc[i_f],nb)[1:])
        else:
            X_cour=np.linspace(Xc[i_d],Xc[i_f],nb)
            Y_cour=np.linspace(Yc[i_d],Yc[i_f],nb)
        pass
    pass
    if depass :
        pasX=np.diff(X_cour)[-1]
        pasY=np.diff(Y_cour)[-1]
        nb=ind_f[-1]-ind_d[-1]
        for i in range(nb):
            X_cour=np.append(X_cour,X_cour[-1]+pasX)
            Y_cour=np.append(Y_cour,Y_cour[-1]+pasY)
        pass
    pass
    
# détermination des cosinus et sinus directeur
   
    DX1=np.diff(X_cour)
    DY1=np.diff(Y_cour)
    DR1=np.sqrt(DX1*DX1+DY1*DY1)
       
    Cdir=DX1/DR1
    Cdir=np.append(Cdir,Cdir[-1])

    Sdir=DY1/DR1
    Sdir=np.append(Sdir,Sdir[-1])

# on peut décomposer le décalage total de la mesure par rapport à la position
# données dans le fichier entre :
# - un décalage parallèle à la direction d'avancement (positif dans le sens 
#               d'avancement négatif sinon)
# - un décalage perpendiculaire à la direction d'avancement (positif  à 90°
#               sens trigonomètrique du vecteur d'avancement négatif sinon)

    Xtv=np.tile(X_cour,nb_voies).reshape(nb_voies,\
                                                  len(X_cour)).T
    Ytv=np.tile(Y_cour,nb_voies).reshape(nb_voies,\
                                                  len(Y_cour)).T
    for i_c in range(len(Cdir)):
        Xtv[i_c,:]=Xtv[i_c,:]+Cdir[i_c]*dec_para+Sdir[i_c]*dec_perp
        Ytv[i_c,:]=Ytv[i_c,:]+Sdir[i_c]*dec_para-Cdir[i_c]*dec_perp
    pass

# à ce stade, on a pour le profil les bonnes valeurs de position pour
# chaque voie
    if i_etiq>0 :
        Xfin=np.append(Xfin,Xtv,axis=0)
        Yfin=np.append(Yfin,Ytv,axis=0)
    else:
        Xfin=Xtv.copy()
        Yfin=Ytv.copy()
    pass
    i_etiq+=1
pass

# on a donc maintenant les positions correctes pour toutes les voies
# il faut maintenant passer à l'interpolation des données puis au tracé propre
# ou à l'écriture pour surfer

# écriture
#On crée un dataframe de sauvegarde
Sauvegarde=pd.DataFrame()
for i_voie in range(nb_voies):
    nom_col_X,nom_col_Y='X_v'+str(i_voie+1),'Y_v'+str(i_voie+1)
    nom_col_C,nom_col_K='Cond_V'+str(i_voie+1),'Kph_V'+str(i_voie+1)
    Sauvegarde[nom_col_X]=Xfin[:,i_voie]
    Sauvegarde[nom_col_Y]=Yfin[:,i_voie]
    Sauvegarde[nom_col_C]=don_ass[nom_cond[i_voie]]
pass
nomfichs='limeil_cond.dat'
Sauvegarde.to_csv(nomfichs,sep='\t')

# détermination des statistiques d'écart entre valeurs succesives
# on peut le faire sur la voie 6, les autres sont pareil à un décalage prêt

X,Y=np.round(Xfin[:,5],2),np.round(Yfin[:,5],2)
DX,DY=np.diff(X),np.diff(Y)
DR=np.round(np.sqrt(DX*DX+DY*DY),2)
RgX,RgY=X.max()-X.min(),Y.max()-Y.min()
print('quelques informations sur la répartitions spatiales des données')
print('moyenne des écarts des points successifs : ',DR.mean())
print('Min,Q1,médiane,Q3, max :\n', np.quantile(DR,(0,0.25,0.5,0.75,1)))
print('étendue en X : ',RgX,'\nétendue en Y : ',RgY)
print('nombre de points finaux si :')
for Q in np.quantile(DR,(0.25,0.5,0.75)):
    m_c=Q/2.
    print('maille = ',m_c,' (X:',str(RgX/m_c),'; Y:',str(RgY/m_c),\
                                     ' ; totX*Y:',str(RgX/m_c*RgX/m_c),')')
pass
# la valeur est à fixer en fonction des valeurs précédentes
maille=0.25
print('Xmin :',X.min(),'Xmax :',X.max())
print('Ymin :',Y.min(),'Ymax :',Y.max())

#idem pour le smin et max des coordonnées

x_min,x_max=461169.5,461251.0
y_min,y_max=5399728.0,5399924.5
print('np_ptx :',(x_max-x_min)/maille)
print('np_pty :',(y_max-y_min)/maille)

nbp_x=327
nbp_y=787
X_gr,Y_gr=np.mgrid[x_min:x_max:np.complex(0,nbp_x),\
                   y_min:y_max:np.complex(0,nbp_y)]
    
tab_arriv=np.array([X_gr.flatten(),Y_gr.flatten()]).T
XYd=np.array([X,Y]).T
# on détrmine tous les points de la grille qui sont à moins de D0 des points
# de mesures 
D0=0.25
D1=1.95
i_pt=0
for x_c,y_c in XYd :
    r_c=np.sqrt((tab_arriv[:,0]-x_c)**2+(tab_arriv[:,1]-y_c)**2)
    i_D0=r_c<=D0
    i_D1=np.logical_and(r_c>D0,r_c<=D1)
    if i_pt>0 :
        ind_D0=np.logical_or(ind_D0,i_D0)
        ind_D1=np.logical_or(ind_D1,i_D1)
    else:
        ind_D0=i_D0.copy()
        ind_D1=i_D1.copy()
    pass
    i_pt+=1
pass
# l'indice ci desosus indique les point interpolés les plus proches des points
# de mesure, il faut s'en servir pour ne définir que les min et max de chaque
# ensuite si il n'y pas de min ou de max sur une ligne, alors il faudra
# ses coordonnées en fonciton des min et max interpoler

ind_prosp_near=ind_D0.reshape(X_gr.shape)
ind_prosp_cub=ind_D1.reshape(X_gr.shape)
ind_prosp=np.logical_or(ind_prosp_near,ind_prosp_cub)
ind_pas_int=np.logical_not(ind_prosp)

X_prosp,Y_prosp=X_gr[ind_prosp].copy(),Y_gr[ind_prosp].copy()

ls_Xr=list()
for Y in np.unique(Y_prosp):
    ind_Y_X=Y_prosp==Y
    ls_Xr.append((X_prosp[ind_Y_X].min(),X_prosp[ind_Y_X].max()))
pass

# la détection d'enveloppe marche plus ou moins
# Il y a des ratés soit sur l'interpolation entre point soit pour leur
# détection on part sur uen solution moins élégante (et qu'il faudra changer)
# la définition des grilles avec D0 et D1. ça marche grossièrement mais les
# bords de prospection sont mal défini
# X maximum (le sens de parcours n'est pas bon)
# ls_Xrb=[ls_Xr[0],]
# ls_Xmn=[ls_Xr[0][0],]
# ls_Xmx=[ls_Xr[0][1],]

# nb_prof_X=len(ls_Xr)
# i_x=0

# while(i_x <=(nb_prof_X-2)):
#     i_suiv=1
#     x_mna=ls_Xr[i_x][0]
#     x_mnab=x_mna.copy()
#     x_mn=ls_Xr[i_x+i_suiv][0]
#     braquet=0
#     while (braquet <3):
#         if (x_mn>=x_mnab) :
#             if (braquet<=1) :
#                 braquet=1
#             else:
#                 braquet=3
#             pass
#         else :
#             if (braquet<1):
#                 break
#             else:
#                 braquet=2
#             pass           
#         pass
#         i_suiv+=1
#         if (i_x+i_suiv)>=nb_prof_X-1 :
#             x_mn=ls_Xr[i_x+i_suiv][0]
#             break
#         else:
#             x_mnab=x_mn.copy()
#             x_mn=ls_Xr[i_x+i_suiv][0]
#         pass
#     pass
#     if i_suiv>1:
#         for i in range(i_suiv-1):
#             x_mnc=((i+1)*x_mnab+(i_suiv-i)*x_mna)/(i_suiv+1)
#             ls_Xmn.append(x_mnc)
#         pass
#         i_suiv=i_suiv-1
#     else:
#         ls_Xmn.append(x_mn)
#     pass
#     if (i_x+i_suiv)<nb_prof_X-2 :
#         i_x+=i_suiv
#     else:
#         break
#     pass
# pass
# ls_Xmn.append(ls_Xr[-1][0])
# i_x=0
# while(i_x <=(nb_prof_X-2)):
#     i_suiv=1
#     x_mxa=ls_Xr[i_x][1]
#     x_mxab=x_mxa.copy()
#     x_mx=ls_Xr[i_x+i_suiv][1]
#     braquet=0
#     while (braquet <3):
#         if (x_mx<=x_mxab) :
#             if (braquet<1) : 
#                 braquet=1
#             else :
#                 braquet=3
#             pass
#         else :
#             if (braquet<1):
#                 break
#             else:
#                 braquet=2
#             pass            
#         pass
#         i_suiv+=1
#         if (i_x+i_suiv)>=nb_prof_X-1 :
#             x_mx=ls_Xr[i_x+i_suiv][1]
#             break
#         else:
#             x_mxab=x_mx.copy()
#             x_mx=ls_Xr[i_x+i_suiv][1]
#         pass
#     pass
#     if i_suiv>1:
#         for i in range(i_suiv-1):
#             x_mxc=((i+1)*x_mxab+(i_suiv-i)*x_mxa)/(i_suiv+1)
#             ls_Xmx.append(x_mxc)
#         pass
#         i_suiv=i_suiv-1
#     else:
#         ls_Xmx.append(x_mx)
#     pass
#     if (i_x+i_suiv)<nb_prof_X-2 :
#         i_x+=i_suiv
#     else:
#         break
#     pass
# pass
# ls_Xmx.append(ls_Xr[-1][1])

# plutôt que d efair eune détection a posteriori (ce qui ne marche pas bien 
# pour le moment) on va essayer de donner des indice aux points (genre avec D0
# et D1) pour définir que si ni l'un ni l'autre alors Nan OK le 15/04/2021



# i_y=0
# for Y in np.unique(Y_prosp):
#     plt.plot(ls_Xr[i_y][0],Y,'+ b')
#     plt.plot(ls_Xr[i_y][1],Y,'+ r')
#     plt.plot(ls_Xmn[i_y],Y,'. b')
#     plt.plot(ls_Xmx[i_y],Y,'. r')
#     i_y+=1
# pass
# plt.gca().set_aspect('equal')
    

    

Zd=don_ass[nom_cond[5]]
grid_near=intrp.griddata(XYd,Zd,(X_gr,Y_gr),method='nearest')
grid_cub=intrp.griddata(XYd,Zd,(X_gr,Y_gr),method='cubic')
grid=grid_near.copy()
grid[ind_prosp_cub]=grid_cub[ind_prosp_cub]
grid[ind_pas_int]=np.nan
grid_aux=grid_near.copy()
grid_aux[np.logical_not(np.logical_or(ind_prosp_near,ind_prosp_cub))]=np.nan   

Zmin,Q05,Q95,Zmax=np.quantile(Zd,(0.,0.05,0.95,1.))
nb_lvl=16
ech_val=np.linspace(Q05,Q95,nb_lvl)
ech_val=np.insert(np.append(ech_val,Zmax),0,Zmin)
figa,axa=plt.subplots(nrows=1,ncols=1)
axa.contourf(X_gr,Y_gr,grid_aux,levels=ech_val,cmap='cividis',vmin=Q05,vmax=Q95)
axa.set_aspect('equal')


# fonction médiane sur une fenêtre
D_fen_X=3
D_fen_Y=3
nb_x,nb_y=X_gr.shape

