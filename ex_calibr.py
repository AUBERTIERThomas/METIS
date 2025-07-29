#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 22 14:09:28 2025

@author: taubertier
"""

import os
import matplotlib.pyplot as plt
import pandas as pd

import CONFIG
import EM_CMD

os.chdir(CONFIG.data_path)
# %%

all_calibr = EM_CMD.CMD_calibration(0,[3,7,11],[2,6,10],file_list=["all.dat"])
# %%

all_sans_sigma = EM_CMD.CMD_calibration(0,[3,7,11],[2,6,10],file_list=["all.dat"])
# %%

fig,ax = plt.subplots(nrows=1,ncols=3,figsize=(20,5))

for i in range(3):
    ax[i].plot(all_calibr["Kph_"+str(i+1)],all_sans_sigma["Kph_"+str(i+1)],"x")
    ax[i].set_title("Voix "+str(i+1))
    ax[i].set_xlabel("avec sig")
    ax[i].set_ylabel("sans sig")
    ax[i].set_aspect('equal')
# %%

EM_CMD.DAT_stats(all_calibr,["Kph_1","Kph_2","Kph_3"])

# Conversion en liste si 'file_list' ne l'est pas
# Chargement de l'appareil si 'uid' est l'indice dans la base 'Appareils.json'
# Concaténation si nécessaire avant traitement
# Chargement des données
# Numérotation des fichiers
# Si la colonne 'X_int' existe déjà, le fichier est déjà interpolé (on l'ignore)
# GPS ou non
# On calcule le nombre de colonnes absentes avant les données (Cond/Inph) parmi celles potentielles.
# Initialisation des colonnes position et données
# Affichage des nom des fichiers traîtés, si on les a en entrée
# Si au moins un fichier est à traîter, on effectue les étapes
# Si le fichier contient des données temporelles
# Détection profils et interpolation des positions répétées
# Si le fichier ne contient pas de base, on ne considère que des profils
# Suppression ou completion des données manquantes
# Si aucun profil n'a pu être détecté (pas de saut temporel, prospection continue), on utilise un autre algo de complétion
# Si la prospection est continue (détection ou précisé par l'utilisateur), on cherche à construire des pseudo-profils
# Sélection dynamique
# Si on veut juste prendre la droite de régression comme référence
# Si on prend une liste de segments
# Séparation base/profil en fonction des colonnes "Base" et "Profil". La base peut être vide
# Nom des colonnes de données
# Synthèse de chaque base en une seule ligne
# Traitements individuels : on prend un fichier à la fois
# Régression des profils pas droits (toujours dynamique)
# Étalonnage par base (pas de manuel depuis cette fonction)
# Décalage des positions par voies
# Nom des colonnes de données, si tous les fichiers sont interpolés
# Plot du résultat, en séparant chaque voie
# Enregistrement de la figure (en image + pickle)
# Résultat enregistré en .dat (option)
# Sortie des dataframes (option)