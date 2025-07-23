#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  5 10:53:05 2025

@author: taubertier
"""

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Variables à modifier pour rentrer les paramètres de votre config

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


### === Chemins === ###
# datapath : Chemin contenant les fichiers de données (pour éviter de le recopier à chaque fois)
# json_path : Chemin contenant les bases d'appareils/de constantes
# script_path : Chemin contenant les fichiers .py CMD (et le reste de l'infrastructure)
#data_path = "/home/taubertier/StageMETIS/2024 2025 Aubertier/fichiers donnees/donnees SG/2018_CMDm/2018_CMDm_zone1_test/"
#data_path = "/home/taubertier/StageMETIS/2024 2025 Aubertier/fichiers donnees/donnees SG/2018_CMD/2018_CMD_zone2_test/"
data_path = "/home/taubertier/StageMETIS/2024 2025 Aubertier/fichiers donnees/CMD mini explorer 3L GPS/"
#data_path = "/home/taubertier/StageMETIS/2024 2025 Aubertier/fichiers donnees/CMD explorer GPS/HCP/"
#data_path = "/home/taubertier/StageMETIS/2024 2025 Aubertier/fichiers donnees/Divers/"
#data_path = "/home/taubertier/StageMETIS/2024 2025 Aubertier/fichiers donnees/cmd_aravo/cmd/"
json_path = "/home/taubertier/StageMETIS/2024 2025 Aubertier/JSONs/"
script_path = "/home/taubertier/StageMETIS/2024 2025 Aubertier/CMD_code/"
### =============== ###

### === Précisions === ###
prec_coos = 4 # Précision (chiffres après la virgule) des données "coordonnées" [4]
prec_data = 2 # Précision (chiffres après la virgule) des données "mesures" [2]
### ================== ###

### === MatPlotLib === ###
fig_width = 16 # Largeur des figures mpl [16]
fig_height = 9 # Hauteur des figures mpl [9]
fig_render_time = 0.25 # Temps (en s) consacré à charger la figure (uniquement celles en cours d'exécution) [0.25]
### ================== ###

### === Tkinter === ###
ver = "7" # Version du programme appelé par l'interface

sc_name = ":1" # Valeur obtenue avec la commande "echo $DISPLAY"
tk_width = 1920 # Largeur des fenêtres principales [1920]
tk_height = 1080 # Hauteur des fenêtres principales [1080]
tk_width_mpl = tk_width*0.52 # Largeur des figures (images) [tk_width*0.52]
tk_height_mpl = tk_height*0.82 # Hauteur des figures (images) [tk_height*0.82]

tk_b_font_size = -26 # Taille de la police des boutons (négatif = meilleur rendu) [-26]
### =============== ###

### === Options interface graphique === ###
keep_prev_ui = False # Garder les fenêtres ouvertes [False]
keep_cmd = False # Garder le terminal ouvert [False]
show_raw_figs = True # Afficher les figures mpl [True]
clear_old_outputs = True # Effacer les anciens résultats [True]
ui_popups = True # Activer les fenêtres graphiques pour les choix, via lancement par "GraphicInterface.py" [True]
blocking_figs = False # Laisse les figures mpl monopoliser l'exécution (sont interactives mais bloquent le programme) [False]

ui_popups_from_cmd = False # Activer les fenêtres graphiques pour les choix, via lancement terminal. Ignoré par "ui_popups" sinon [False]
ui_popups_shutdown = True # Terminer l'exécution si la fenêtre de choix est fermée, sinon la relance [True]
### =================================== ###

### === Couleurs === ###
no_blink = False # Retirer l'effet clignotant du texte (pas toujours compatible avec le shell) [False]
### ================ ###

### === Warnings === ###
no_warnings = True # Ne plus afficher les warnings externes au code (ceux des librairies) [True]
### ================ ###



