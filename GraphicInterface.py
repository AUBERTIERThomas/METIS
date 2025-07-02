#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 22 13:32:00 2025

@author: taubertier
"""

import tkinter as tk
import tkinter.ttk as ttk
import subprocess
import os
import glob
import matplotlib.pyplot as plt
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,NavigationToolbar2Tk)
import numpy as np
import pickle
from PIL import Image, ImageTk
import warnings

import CONFIG

""" ATTENTION : Pour que les figures suite aux affichages tkinter marchent correctement, il faut changer le backend de matplotlib dans les options de spyder :
    Outils -> Préférences -> Console IPython -> Graphiques -> Sortie Graphique : Tk ou Automatique"""

# --- Variables de couleur en héxa

d_gray = ["#b0b0b0","#b8b8b8"]
l_gray = ["#c8c8c8","#d0d0d0"]
l_blue = ["#6080a0","#6484b0"]

# --- Variables de paramètres globaux
keep_prev_ui = CONFIG.keep_prev_ui
keep_cmd = CONFIG.keep_cmd
show_raw_figs = CONFIG.show_raw_figs
clear_old_outputs = CONFIG.clear_old_outputs
ui_popups = CONFIG.ui_popups
blocking_figs = CONFIG.blocking_figs

if CONFIG.no_warnings:
    warnings.filterwarnings("ignore")

def LOAD_root(title,mm=False):
    """ [TA]\n
    Create an instance of tkinter window, load components common top all instances.
    
    Parameters
    ----------
    title : str
        Window name (shown at the top).
    
    Returns
    -------
    root : tkinter.Tk
        Window instance
    canvas : tkinter.Canvas
        Canvas object that contains most of the graphic components.
    bg_im : tkinter.PhotoImage
        Loaded background image.
    button_im : tkinter.PhotoImage
        Loaded button sprite.
    settings_im : tkinter.PhotoImage
        Loaded settings button sprite.

    Notes
    -----
    The ``.zoom`` method can only expand the image by an integer value.
    For this reason, all sprites needs to be at least smaller than their expected size on the canvas.
    Very small sprites (such as 20x20 resolution) are thus more lenient for scaling operations.
    """
    root = tk.Tk(screenName=CONFIG.sc_name)
    root.geometry(str(CONFIG.tk_width)+"x"+str(CONFIG.tk_height))
    root.title(title)
        
    canvas = tk.Canvas(root, width = CONFIG.tk_width, height = CONFIG.tk_height)
    canvas.pack(fill = "both", expand = True)
    
    bg_zoom = max(-(-CONFIG.tk_width // 640),-(-CONFIG.tk_height // 360))
    if mm:
        bg_im = tk.PhotoImage(master = canvas, file = r"Images/METIS_BG.png").zoom(bg_zoom,bg_zoom)
        canvas.create_image( CONFIG.tk_width, 0, image = bg_im, anchor = "ne")
    else:
        bg_im = tk.PhotoImage(master = canvas, file = r"Images/Neutral_BG.png").zoom(bg_zoom,bg_zoom)
        canvas.create_image( CONFIG.tk_width//2, CONFIG.tk_height//2, image = bg_im, anchor = "center")
    
    button_im = tk.PhotoImage(master = canvas, file = r"Images/ayaya.png").zoom(10,10)
    settings_im = tk.PhotoImage(master = canvas, file = r"Images/Settings.png").zoom(3,3)
    
    return root, canvas, bg_im, button_im, settings_im

# Fenêtre du menu principal

def GUI_main_menu():

    root, canvas, bg_im, button_im, settings_im = LOAD_root("Main menu",mm=True)
    
    def on_CMD_button_pressed():
        if not keep_prev_ui:
            root.destroy()
        GUI_main_CMD()
    
    def on_CMDEX_button_pressed():
        if not keep_prev_ui:
            root.destroy()
        GUI_main_CMDEX()
    
    def on_JSON_button_pressed():
        if not keep_prev_ui:
            root.destroy()
        GUI_main_JSON()
    
    def on_DAT_button_pressed():
        if not keep_prev_ui:
            root.destroy()
        GUI_main_DAT() 
    
    def on_other_button_pressed():
        if not keep_prev_ui:
            root.destroy()
        GUI_main_other()
    
    canvas.create_rectangle(CONFIG.tk_width//2-425, CONFIG.tk_height-575, CONFIG.tk_width//2+425, CONFIG.tk_height-25, fill="#d6c09f", width=0)
    b1 = tk.Button(canvas, text = "CMD", font=('Terminal', 40, 'bold'), compound="center", image = button_im, command=on_CMD_button_pressed)
    b1_c = canvas.create_window( CONFIG.tk_width//2-150,CONFIG.tk_height-550, anchor = "n",window = b1)
    b2 = tk.Button(canvas, text = "CMDEX", font=('Terminal', 40, 'bold'), compound="center", image = button_im, command=on_CMDEX_button_pressed)
    b2_c = canvas.create_window( CONFIG.tk_width//2+150,CONFIG.tk_height-550, anchor = "n",window = b2)
    b3 = tk.Button(canvas, text = "JSON", font=('Terminal', 40, 'bold'), compound="center", image = button_im, command=on_JSON_button_pressed)
    b3_c = canvas.create_window( CONFIG.tk_width//2-300,CONFIG.tk_height-250, anchor = "n",window = b3)
    b4 = tk.Button(canvas, text = "DAT", font=('Terminal', 40, 'bold'), compound="center", image = button_im, command=on_DAT_button_pressed)
    b4_c = canvas.create_window( CONFIG.tk_width//2,CONFIG.tk_height-250, anchor = "n",window = b4)
    b5 = tk.Button(canvas, text = "Divers", font=('Terminal', 40, 'bold'), compound="center", image = button_im, command=on_other_button_pressed)
    b5_c = canvas.create_window( CONFIG.tk_width//2+300,CONFIG.tk_height-250, anchor = "n",window = b5)
    ba = tk.Button(root, text = 'Aide', font=('Terminal', 20, 'bold'), compound="center", command=lambda : EXEC_help())
    ba_c = canvas.create_window( 25,CONFIG.tk_height-100, anchor = "nw",window = ba)
    bs = tk.Button(root, image = settings_im, command=EXEC_settings)
    bs_c = canvas.create_window( 25, 25, anchor = "nw",window = bs)
    bi = tk.Button(root, text = '?', font=('Terminal', 20, 'bold'), compound="center", command=EXEC_g_infos)
    bi_c = canvas.create_window( 25,CONFIG.tk_height-50, anchor = "nw",window = bi)
    bc = tk.Button(root, text = 'Crédits', font=('Terminal', 20, 'bold'), compound="center", command=EXEC_credits)
    bc_c = canvas.create_window( CONFIG.tk_width-145,CONFIG.tk_height-50, anchor = "nw",window = bc)
    
    root.mainloop()

# -----------------------------------------------------------------------------------
# --- Fonctions pour les fenêtres graphiques des différentes classes de commandes ---
# -----------------------------------------------------------------------------------

def GUI_main_CMD():

    root, canvas, bg_im, button_im, settings_im = LOAD_root("CMD menu")
    
    def on_return_button_pressed():
        if not keep_prev_ui:
            root.destroy()
        GUI_main_menu()
    
    def on_kd_button_pressed():
        if not keep_prev_ui:
            root.destroy()
        GUI_CMD_exec_known_device()
    
    def on_nd_button_pressed():
        if not keep_prev_ui:
            root.destroy()
        GUI_CMD_exec_new_device()
    
    canvas.create_rectangle(CONFIG.tk_width//2-275, CONFIG.tk_height-375, CONFIG.tk_width//2+275, CONFIG.tk_height-125, fill="#d9c09c", width=0)
    b1 = tk.Button(root, text = 'CMD_exec_\nknown_device', font=('Terminal', CONFIG.tk_b_font_size, 'bold'), compound="center", image = button_im, command=on_kd_button_pressed)
    b1_c = canvas.create_window( CONFIG.tk_width//2-150,CONFIG.tk_height-350, anchor = "n",window = b1)
    b2 = tk.Button(root, text = 'CMD_exec_\nnew_device', font=('Terminal', CONFIG.tk_b_font_size, 'bold'), compound="center", image = button_im, command=on_nd_button_pressed)
    b2_c = canvas.create_window( CONFIG.tk_width//2+150,CONFIG.tk_height-350, anchor = "n",window = b2)
    br = tk.Button(root, text = 'Retour', font=('Terminal', CONFIG.tk_b_font_size, 'bold'), compound="center", command=on_return_button_pressed)
    br_c = canvas.create_window( 50,25, anchor = "nw",window = br)
    bs = tk.Button(root, image = settings_im, command=EXEC_settings)
    bs_c = canvas.create_window( CONFIG.tk_width-85,25, anchor = "nw",window = bs)
    
    root.mainloop()

def GUI_main_CMDEX():

    root, canvas, bg_im, button_im, settings_im = LOAD_root("CMDEX menu")
    
    def on_return_button_pressed():
        if not keep_prev_ui:
            root.destroy()
        GUI_main_menu()
    
    def on_i_button_pressed():
        if not keep_prev_ui:
            root.destroy()
        GUI_CMDEX_init()
    
    def on_ep_button_pressed():
        if not keep_prev_ui:
            root.destroy()
        GUI_CMDEX_evol_profils()
    
    def on_f_button_pressed():
        if not keep_prev_ui:
            root.destroy()
        GUI_CMDEX_frontiere()
    
    def on_k_button_pressed():
        if not keep_prev_ui:
            root.destroy()
        GUI_CMDEX_grid()
      
    canvas.create_rectangle(CONFIG.tk_width//2-275, CONFIG.tk_height-575, CONFIG.tk_width//2+275, CONFIG.tk_height-25, fill="#d9c09c", width=0)
    b1 = tk.Button(root, text = 'CMDEX_init', font=('Terminal', CONFIG.tk_b_font_size, 'bold'), compound="center", image = button_im, command=on_i_button_pressed)
    b1_c = canvas.create_window( CONFIG.tk_width//2-150,CONFIG.tk_height-550, anchor = "n",window = b1)
    b2 = tk.Button(root, text = 'CMDEX_\nevol_profils', font=('Terminal', CONFIG.tk_b_font_size, 'bold'), compound="center", image = button_im, command=on_ep_button_pressed)
    b2_c = canvas.create_window( CONFIG.tk_width//2+150,CONFIG.tk_height-550, anchor = "n",window = b2)
    b3 = tk.Button(root, text = 'CMDEX_\nfrontiere', font=('Terminal', CONFIG.tk_b_font_size, 'bold'), compound="center", image = button_im, command=on_f_button_pressed)
    b3_c = canvas.create_window( CONFIG.tk_width//2-150,CONFIG.tk_height-250, anchor = "n",window = b3)
    b4 = tk.Button(root, text = 'CMDEX_grid', font=('Terminal', CONFIG.tk_b_font_size, 'bold'), compound="center", image = button_im, command=on_k_button_pressed)
    b4_c = canvas.create_window( CONFIG.tk_width//2+150,CONFIG.tk_height-250, anchor = "n",window = b4)
    br = tk.Button(root, text = 'Retour', font=('Terminal', CONFIG.tk_b_font_size, 'bold'), compound="center", command=on_return_button_pressed)
    br_c = canvas.create_window( 50,25, anchor = "nw",window = br)
    bs = tk.Button(root, image = settings_im, command=EXEC_settings)
    bs_c = canvas.create_window( CONFIG.tk_width-85,25, anchor = "nw",window = bs)
    
    root.mainloop()

def GUI_main_JSON():

    root, canvas, bg_im, button_im, settings_im = LOAD_root("JSON menu")
    
    def on_return_button_pressed():
        if not keep_prev_ui:
            root.destroy()
        GUI_main_menu()
    
    def on_pd_button_pressed():
        if not keep_prev_ui:
            root.destroy()
        GUI_JSON_print_devices()
    
    def on_ad_button_pressed():
        if not keep_prev_ui:
            root.destroy()
        GUI_JSON_add_devices()
    
    def on_rd_button_pressed():
        if not keep_prev_ui:
            root.destroy()
        GUI_JSON_remove_devices()
    
    canvas.create_rectangle(CONFIG.tk_width//2-425, CONFIG.tk_height-375, CONFIG.tk_width//2+425, CONFIG.tk_height-125, fill="#d9c09c", width=0)
    b1 = tk.Button(root, text = 'JSON_print_\ndevices', font=('Terminal', CONFIG.tk_b_font_size, 'bold'), compound="center", image = button_im, command=on_pd_button_pressed)
    b1_c = canvas.create_window( CONFIG.tk_width//2-300,CONFIG.tk_height-350, anchor = "n",window = b1)
    b2 = tk.Button(root, text = 'JSON_add_\ndevice', font=('Terminal', CONFIG.tk_b_font_size, 'bold'), compound="center", image = button_im, command=on_ad_button_pressed)
    b2_c = canvas.create_window( CONFIG.tk_width//2,CONFIG.tk_height-350, anchor = "n",window = b2)
    b3 = tk.Button(root, text = 'JSON_remove_\ndevice', font=('Terminal', CONFIG.tk_b_font_size, 'bold'), compound="center", image = button_im, command=on_rd_button_pressed)
    b3_c = canvas.create_window( CONFIG.tk_width//2+300,CONFIG.tk_height-350, anchor = "n",window = b3)
    br = tk.Button(root, text = 'Retour', font=('Terminal', CONFIG.tk_b_font_size, 'bold'), compound="center", command=on_return_button_pressed)
    br_c = canvas.create_window( 50,25, anchor = "nw",window = br)
    bs = tk.Button(root, image = settings_im, command=EXEC_settings)
    bs_c = canvas.create_window( CONFIG.tk_width-85,25, anchor = "nw",window = bs)
    
    root.mainloop()

def GUI_main_DAT():

    root, canvas, bg_im, button_im, settings_im = LOAD_root("DAT menu")
    
    def on_return_button_pressed():
        if not keep_prev_ui:
            root.destroy()
        GUI_main_menu()
    
    def on_cd_button_pressed():
        if not keep_prev_ui:
            root.destroy()
        GUI_DAT_change_date()
    
    def on_pad_button_pressed():
        if not keep_prev_ui:
            root.destroy()
        GUI_DAT_pop_and_dec()
    
    def on_sc_button_pressed():
        if not keep_prev_ui:
            root.destroy()
        GUI_DAT_switch_cols()
        
    def on_rc_button_pressed():
        if not keep_prev_ui:
            root.destroy()
        GUI_DAT_remove_cols()
    
    def on_rd_button_pressed():
        if not keep_prev_ui:
            root.destroy()
        GUI_DAT_remove_data()
    
    def on_mmc_button_pressed():
        if not keep_prev_ui:
            root.destroy()
        GUI_DAT_min_max_col()
    
    def on_lf_button_pressed():
        if not keep_prev_ui:
            root.destroy()
        GUI_DAT_light_format()
    
    def on_cs_button_pressed():
        if not keep_prev_ui:
            root.destroy()
        GUI_DAT_change_sep()
    
    def on_fb_button_pressed():
        if not keep_prev_ui:
            root.destroy()
        GUI_DAT_fuse_bases()
    
    canvas.create_rectangle(CONFIG.tk_width//2-725, CONFIG.tk_height-575, CONFIG.tk_width//2+725, CONFIG.tk_height-25, fill="#d9c09c", width=0)
    b1 = tk.Button(root, text = 'DAT_change_\ndate', font=('Terminal', CONFIG.tk_b_font_size, 'bold'), compound="center", image = button_im, command=on_cd_button_pressed)
    b1_c = canvas.create_window( CONFIG.tk_width//2-600,CONFIG.tk_height-550, anchor = "n",window = b1)
    b2 = tk.Button(root, text = 'DAT_pop_\nand_dec', font=('Terminal', CONFIG.tk_b_font_size, 'bold'), compound="center", image = button_im, command=on_pad_button_pressed)
    b2_c = canvas.create_window( CONFIG.tk_width//2-300,CONFIG.tk_height-550, anchor = "n",window = b2)
    b3 = tk.Button(root, text = 'DAT_switch_\ncols', font=('Terminal', CONFIG.tk_b_font_size, 'bold'), compound="center", image = button_im, command=on_sc_button_pressed)
    b3_c = canvas.create_window( CONFIG.tk_width//2,CONFIG.tk_height-550, anchor = "n",window = b3)
    b4 = tk.Button(root, text = 'DAT_remove_\ncols', font=('Terminal', CONFIG.tk_b_font_size, 'bold'), compound="center", image = button_im, command=on_rc_button_pressed)
    b4_c = canvas.create_window( CONFIG.tk_width//2+300,CONFIG.tk_height-550, anchor = "n",window = b4)
    b5 = tk.Button(root, text = 'DAT_remove_\ndata', font=('Terminal', CONFIG.tk_b_font_size, 'bold'), compound="center", image = button_im, command=on_rd_button_pressed)
    b5_c = canvas.create_window( CONFIG.tk_width//2+600,CONFIG.tk_height-550, anchor = "n",window = b5)
    b6 = tk.Button(root, text = 'DAT_min_\nmax_col', font=('Terminal', CONFIG.tk_b_font_size, 'bold'), compound="center", image = button_im, command=on_mmc_button_pressed)
    b6_c = canvas.create_window( CONFIG.tk_width//2-450,CONFIG.tk_height-250, anchor = "n",window = b6)
    b7 = tk.Button(root, text = 'DAT_light_\nformat', font=('Terminal', CONFIG.tk_b_font_size, 'bold'), compound="center", image = button_im, command=on_lf_button_pressed)
    b7_c = canvas.create_window( CONFIG.tk_width//2-150,CONFIG.tk_height-250, anchor = "n",window = b7)
    b8 = tk.Button(root, text = 'DAT_change_\nsep', font=('Terminal', CONFIG.tk_b_font_size, 'bold'), compound="center", image = button_im, command=on_cs_button_pressed)
    b8_c = canvas.create_window( CONFIG.tk_width//2+150,CONFIG.tk_height-250, anchor = "n",window = b8)
    b9 = tk.Button(root, text = 'DAT_fuse_\nbases', font=('Terminal', CONFIG.tk_b_font_size, 'bold'), compound="center", image = button_im, command=on_fb_button_pressed)
    b9_c = canvas.create_window( CONFIG.tk_width//2+450,CONFIG.tk_height-250, anchor = "n",window = b9)
    br = tk.Button(root, text = 'Retour', font=('Terminal', CONFIG.tk_b_font_size, 'bold'), compound="center", command=on_return_button_pressed)
    br_c = canvas.create_window( 50,25, anchor = "nw",window = br)
    bs = tk.Button(root, image = settings_im, command=EXEC_settings)
    bs_c = canvas.create_window( CONFIG.tk_width-85,25, anchor = "nw",window = bs)
    
    root.mainloop()

def GUI_main_other():

    root, canvas, bg_im, button_im, settings_im = LOAD_root("Divers menu")
    
    def on_return_button_pressed():
        if not keep_prev_ui:
            root.destroy()
        GUI_main_menu()
    
    def on_TRANS_dtm_button_pressed():
        if not keep_prev_ui:
            root.destroy()
        GUI_TRANS_df_to_matrix()
    
    def on_TRANS_mtd_button_pressed():
        if not keep_prev_ui:
            root.destroy()
        GUI_TRANS_matrix_to_df()
    
    def on_TRANS_mtg_button_pressed():
        if not keep_prev_ui:
            root.destroy()
        GUI_TRANS_matrix_to_grd()
    
    def on_TRANS_gtm_button_pressed():
        if not keep_prev_ui:
            root.destroy()
        GUI_TRANS_grd_to_matrix()
    
    def on_FIG_df_button_pressed():
        if not keep_prev_ui:
            root.destroy()
        GUI_FIG_display_fig()
    
    def on_FIG_pd_button_pressed():
        if not keep_prev_ui:
            root.destroy()
        GUI_FIG_plot_data()
    
    def on_FIG_pg_button_pressed():
        if not keep_prev_ui:
            root.destroy()
        GUI_FIG_plot_grid()
    
    def on_FIG_pp_button_pressed():
        if not keep_prev_ui:
            root.destroy()
        GUI_FIG_plot_pos()
    
    def on_EXEC_button_pressed():
        if not keep_prev_ui:
            root.destroy()
        GUI_EXEC()
    
    canvas.create_rectangle(CONFIG.tk_width//2-725, CONFIG.tk_height-575, CONFIG.tk_width//2+725, CONFIG.tk_height-25, fill="#d9c09c", width=0)
    b1 = tk.Button(root, text = 'TRANS_df_\nto_matrix', font=('Terminal', CONFIG.tk_b_font_size, 'bold'), compound="center", image = button_im, command=on_TRANS_dtm_button_pressed)
    b1_c = canvas.create_window( CONFIG.tk_width//2-450,CONFIG.tk_height-550, anchor = "n",window = b1)
    b2 = tk.Button(root, text = 'TRANS_\nmatrix_to_df', font=('Terminal', CONFIG.tk_b_font_size, 'bold'), compound="center", image = button_im, command=on_TRANS_mtd_button_pressed)
    b2_c = canvas.create_window( CONFIG.tk_width//2-150,CONFIG.tk_height-550, anchor = "n",window = b2)
    b3 = tk.Button(root, text = 'TRANS_\nmatrix_to_grd', font=('Terminal', CONFIG.tk_b_font_size, 'bold'), compound="center", image = button_im, command=on_TRANS_mtg_button_pressed)
    b3_c = canvas.create_window( CONFIG.tk_width//2+150,CONFIG.tk_height-550, anchor = "n",window = b3)
    b4 = tk.Button(root, text = 'TRANS_grd_\nto_matrix', font=('Terminal', CONFIG.tk_b_font_size, 'bold'), compound="center", image = button_im, command=on_TRANS_gtm_button_pressed)
    b4_c = canvas.create_window( CONFIG.tk_width//2+450,CONFIG.tk_height-550, anchor = "n",window = b4)
    b5 = tk.Button(root, text = 'FIG_display_\nfig', font=('Terminal', CONFIG.tk_b_font_size, 'bold'), compound="center", image = button_im, command=on_FIG_df_button_pressed)
    b5_c = canvas.create_window( CONFIG.tk_width//2-600,CONFIG.tk_height-250, anchor = "n",window = b5)
    b6 = tk.Button(root, text = 'FIG_plot_\ndata', font=('Terminal', CONFIG.tk_b_font_size, 'bold'), compound="center", image = button_im, command=on_FIG_pd_button_pressed)
    b6_c = canvas.create_window( CONFIG.tk_width//2-300,CONFIG.tk_height-250, anchor = "n",window = b6)
    b7 = tk.Button(root, text = 'FIG_plot_\ngrid', font=('Terminal', CONFIG.tk_b_font_size, 'bold'), compound="center", image = button_im, command=on_FIG_pg_button_pressed)
    b7_c = canvas.create_window( CONFIG.tk_width//2,CONFIG.tk_height-250, anchor = "n",window = b7)
    b8 = tk.Button(root, text = 'FIG_plot_\npos', font=('Terminal', CONFIG.tk_b_font_size, 'bold'), compound="center", image = button_im, command=on_FIG_pp_button_pressed)
    b8_c = canvas.create_window( CONFIG.tk_width//2+300,CONFIG.tk_height-250, anchor = "n",window = b8)
    b9 = tk.Button(root, text = 'EXEC', font=('Terminal', int(CONFIG.tk_b_font_size*1.5), 'bold'), compound="center", image = button_im, command=on_EXEC_button_pressed)
    b9_c = canvas.create_window( CONFIG.tk_width//2+600,CONFIG.tk_height-250, anchor = "n",window = b9)
    br = tk.Button(root, text = 'Retour', font=('Terminal', CONFIG.tk_b_font_size, 'bold'), compound="center", command=on_return_button_pressed)
    br_c = canvas.create_window( 50,25, anchor = "nw",window = br)
    bs = tk.Button(root, image = settings_im, command=EXEC_settings)
    bs_c = canvas.create_window( CONFIG.tk_width-85,25, anchor = "nw",window = bs)
    
    root.mainloop()

# ------------------------------------------------------------------------
# --- Fonctions pour les fenêtres graphiques des différentes commandes ---
# ------------------------------------------------------------------------
    
def GUI_CMD_exec_known_device(from_EXEC=None):
        
    root, canvas, bg_im, button_im, settings_im = LOAD_root("CMD_exec_known_device")

    label_list = ["uid","file_list","file_list_rev","sep","output_file","output_file_base","light_restr","split","sup_na","regr","corr_base","choice"]
    type_list = ["int","str[]","str[]","str","str","str","str[]","bool","bool","bool","bool","bool"]
    default_list = ["*","None","None",'\\t',"\"res.dat\"","\"res_B.dat\"","None","False","True","False","True","False"]
    
    EXEC_display_variables(root, canvas, button_im, settings_im, label_list, type_list, default_list, "CMD_exec_known_device", "CMD_", "Traitement CMD (appareil enregistré)", GUI_main_CMD, from_EXEC)
    
    root.mainloop()

def GUI_CMD_exec_new_device(from_EXEC=None):

    root, canvas, bg_im, button_im, settings_im = LOAD_root("CMD_exec_new_device")

    label_list = ["app_name","config","nb_ecarts","freq_list","GPS","GPS_dec","TR_l","TR_t","height","bucking_coil","coeff_construct","file_list","file_list_rev","sep","output_file","output_file_base","light_restr","split","sup_na","regr","corr_base","choice"]
    type_list = ["str","str","int","float[]","bool","float[]","float[]","float[]","float","int","float","str[]","str[]","str","str","str","str[]","bool","bool","bool","bool","bool"]
    default_list = ["*","*","*","*","True","[0.0,0.0]","array of 0.0","array of 0.0","0.1","0","1.0","None","None",'\\t',"\"res.dat\"","\"res_B.dat\"","None","False","True","False","True","False"]
    
    EXEC_display_variables(root, canvas, button_im, settings_im, label_list, type_list, default_list, "CMD_exec_new_device", "CMD_", "Traitement CMD (nouvel appareil)", GUI_main_CMD, from_EXEC)
    
    root.mainloop()

def GUI_CMDEX_init(from_EXEC=None):

    root, canvas, bg_im, button_im, settings_im = LOAD_root("CMDEX_init")

    label_list = ["uid","file_list","sep","sup_na","regr","corr_base"]
    type_list = ["int","str[]","str","bool","bool","bool"]
    default_list = ["*","None",'\\t',"True","False","True"]
    
    EXEC_display_variables(root, canvas, button_im, settings_im, label_list, type_list, default_list, "CMDEX_init", "CMDEX_i_", "Interpolation, décalage et complétion", GUI_main_CMDEX, from_EXEC)
    
    root.mainloop()

def GUI_CMDEX_evol_profils(from_EXEC=None):

    root, canvas, bg_im, button_im, settings_im = LOAD_root("CMDEX_evol_profils")

    label_list = ["file_prof_list","file_base_list","col_z","sep","replace","output_file_list","nb_ecarts","diff","auto_adjust","man_adjust","line"]
    type_list = ["str[]","str[]","int[]","str","bool","str[]","int","bool","bool","bool","bool"]
    default_list = ["*","*","*",'\\t',"False","None","1","True","True","False","False"]
    
    EXEC_display_variables(root, canvas, button_im, settings_im, label_list, type_list, default_list, "CMDEX_evol_profils", "CMDEX_ep_", "Étalonnage par base et/ou manuel", GUI_main_CMDEX, from_EXEC)
    
    root.mainloop()

def GUI_CMDEX_frontiere(from_EXEC=None):

    root, canvas, bg_im, button_im, settings_im = LOAD_root("CMDEX_frontiere")

    label_list = ["col_x","col_y","col_z","file_list","sep","output_file","choice"]
    type_list = ["int[]","int[]","int[]","str[]","str","str","bool"]
    default_list = ["*","*","*","None",'\\t',"\"frt.dat\"","False"]
    
    EXEC_display_variables(root, canvas, button_im, settings_im, label_list, type_list, default_list, "CMDEX_frontiere", "CMDEX_f_", "Étalonnage des frontières", GUI_main_CMDEX, from_EXEC)
    
    root.mainloop()

def GUI_CMDEX_grid(from_EXEC=None):

    root, canvas, bg_im, button_im, settings_im = LOAD_root("CMDEX_grid")

    label_list = ["col_x","col_y","col_z","file_list","sep","output_file","m_type","radius","prec","seuil","i_method","no_crop","all_models","plot_pts","matrix"]
    type_list = ["int[]","int[]","int[]","str[]","str","str","str","int","int","float","str","bool","bool","bool","bool"]
    default_list = ["*","*","*","None",'\\t',"None","None","0","100","0.0","None","False","False","False","False"]
    
    EXEC_display_variables(root, canvas, button_im, settings_im, label_list, type_list, default_list, "CMDEX_grid", "CMDEX_g_", "Mise en grille des données", GUI_main_CMDEX, from_EXEC)
    
    root.mainloop()

def GUI_JSON_print_devices(from_EXEC=None):

    root, canvas, bg_im, button_im, settings_im = LOAD_root("JSON_print_devices")

    label_list = ["uid"]
    type_list = ["int"]
    default_list = ["None"]
    
    EXEC_display_variables(root, canvas, button_im, settings_im, label_list, type_list, default_list, "JSON_print_devices", "", "Liste des appareils enregistrés", GUI_main_JSON, from_EXEC)
    
    root.mainloop()

def GUI_JSON_add_devices(from_EXEC=None):

    root, canvas, bg_im, button_im, settings_im = LOAD_root("JSON_add_devices")

    label_list = ["app_name","config","nb_ecarts","freq_list","GPS","GPS_dec","TR_l","TR_t","height","bucking_coil","coeff_construct"]
    type_list = ["str","str","int","float[]","bool","float[]","float[]","float[]","float","int","float"]
    default_list = ["*","*","*","*","True","[0.0,0.0]","array of 0.0","array of 0.0","0.1","0","1.0"]
    
    EXEC_display_variables(root, canvas, button_im, settings_im, label_list, type_list, default_list, "JSON_add_devices", "", "Ajouter un appareil", GUI_main_JSON, from_EXEC)
    
    root.mainloop()

def GUI_JSON_remove_devices(from_EXEC=None):

    root, canvas, bg_im, button_im, settings_im = LOAD_root("JSON_remove_devices")

    label_list = ["uid"]
    type_list = ["int"]
    default_list = ["None"]
    
    EXEC_display_variables(root, canvas, button_im, settings_im, label_list, type_list, default_list, "JSON_remove_devices", "", "Supprimer un appareil enregistré", GUI_main_JSON, from_EXEC)
    
    root.mainloop()

def GUI_DAT_change_date(from_EXEC=None):

    root, canvas, bg_im, button_im, settings_im = LOAD_root("DAT_change_date")

    label_list = ["file_list","date_str","sep","replace","output_file_list"]
    type_list = ["str[]","str","str","bool","str[]"]
    default_list = ["*","*","\\t","False","None"]
    
    EXEC_display_variables(root, canvas, button_im, settings_im, label_list, type_list, default_list, "DAT_change_date", "", "Changement de la date d'un fichier .dat", GUI_main_DAT, from_EXEC)
    
    root.mainloop()

def GUI_DAT_pop_and_dec(from_EXEC=None):

    root, canvas, bg_im, button_im, settings_im = LOAD_root("DAT_pop_and_dec")

    label_list = ["file_list","colsup","sep","replace","output_file_list"]
    type_list = ["str[]","str","str","bool","str[]"]
    default_list = ["*","*","\\t","False","None"]
    
    EXEC_display_variables(root, canvas, button_im, settings_im, label_list, type_list, default_list, "DAT_pop_and_dec", "", "Suppression d'une colonne surnuméraire dans un fichier .dat", GUI_main_DAT, from_EXEC)
    
    root.mainloop()

def GUI_DAT_switch_cols(from_EXEC=None):

    root, canvas, bg_im, button_im, settings_im = LOAD_root("DAT_switch_cols")

    label_list = ["file_list","col_a","col_b","sep","replace","output_file_list"]
    type_list = ["str[]","str","str","str","bool","str[]"]
    default_list = ["*","*","*","\\t","False","None"]
    
    EXEC_display_variables(root, canvas, button_im, settings_im, label_list, type_list, default_list, "DAT_switch_cols", "", "Inversion de deux colonnes dans un fichier .dat", GUI_main_DAT, from_EXEC)
    
    root.mainloop()

def GUI_DAT_remove_cols(from_EXEC=None):

    root, canvas, bg_im, button_im, settings_im = LOAD_root("DAT_remove_cols")

    label_list = ["file_list","colsup_list","keep","sep","replace","output_file_list"]
    type_list = ["str[]","str[]","bool","str","bool","str[]"]
    default_list = ["*","*","False","\\t","False","None"]
    
    EXEC_display_variables(root, canvas, button_im, settings_im, label_list, type_list, default_list, "DAT_remove_cols", "", "Suppression de colonnes dans un fichier .dat", GUI_main_DAT, from_EXEC)
    
    root.mainloop()

def GUI_DAT_remove_data(from_EXEC=None):

    root, canvas, bg_im, button_im, settings_im = LOAD_root("DAT_remove_data")

    label_list = ["file_list","colsup_list","i_min","i_max","sep","replace","output_file_list"]
    type_list = ["str[]","str[]","int","int","str","bool","str[]"]
    default_list = ["*","*","*","*","\\t","False","None"]
    
    EXEC_display_variables(root, canvas, button_im, settings_im, label_list, type_list, default_list, "DAT_remove_data", "", "Suppression de données (valeurs) dans un fichier .dat", GUI_main_DAT, from_EXEC)
    
    root.mainloop()

def GUI_DAT_min_max_col(from_EXEC=None):

    root, canvas, bg_im, button_im, settings_im = LOAD_root("DAT_min_max_col")

    label_list = ["file_list","col_list","sep","n"]
    type_list = ["str[]","str[]","str","int"]
    default_list = ["*","*","\\t","10"]
    
    EXEC_display_variables(root, canvas, button_im, settings_im, label_list, type_list, default_list, "DAT_min_max_col", "", "Affichage des données extrêmes", GUI_main_DAT, from_EXEC)
    
    root.mainloop()

def GUI_DAT_light_format(from_EXEC=None):

    root, canvas, bg_im, button_im, settings_im = LOAD_root("DAT_light_format")

    label_list = ["file_list","sep","replace","output_file_list","nb_ecarts","restr"]
    type_list = ["str[]","str","bool","str[]","bool","str[]"]
    default_list = ["*","\\t","False","None","3","[]"]
    
    EXEC_display_variables(root, canvas, button_im, settings_im, label_list, type_list, default_list, "DAT_light_format", "", "Mise en format standard d'un fichier .dat", GUI_main_DAT, from_EXEC)
    
    root.mainloop()

def GUI_DAT_change_sep(from_EXEC=None):

    root, canvas, bg_im, button_im, settings_im = LOAD_root("DAT_change_sep")

    label_list = ["file_list","sep","newsep","replace","output_file_list"]
    type_list = ["str[]","str","str","bool","str[]"]
    default_list = ["*","*","*","False","None"]
    
    EXEC_display_variables(root, canvas, button_im, settings_im, label_list, type_list, default_list, "DAT_change_sep", "", "Changement du séparateur dans un fichier .dat", GUI_main_DAT, from_EXEC)
    
    root.mainloop()

def GUI_DAT_fuse_bases(from_EXEC=None):

    root, canvas, bg_im, button_im, settings_im = LOAD_root("DAT_fuse_bases")

    label_list = ["file_B1","file_B2","file_prof","sep","output_file"]
    type_list = ["str","str","str","str","str"]
    default_list = ["*","*","*","\\t","None"]
    
    EXEC_display_variables(root, canvas, button_im, settings_im, label_list, type_list, default_list, "DAT_fuse_bases", "", "Fusion de bases B1 et B2 dans un même fichier .dat", GUI_main_DAT, from_EXEC)
    
    root.mainloop()

def GUI_TRANS_df_to_matrix(from_EXEC=None):

    root, canvas, bg_im, button_im, settings_im = LOAD_root("TRANS_df_to_matrix")

    label_list = ["file","sep","output_file"]
    type_list = ["str","str","str"]
    default_list = ["*","\\t","dtm.json"]
    
    EXEC_display_variables(root, canvas, button_im, settings_im, label_list, type_list, default_list, "TRANS_df_to_matrix", "", "Changement de format, de dataframe (.dat) à matrice (.json)", GUI_main_other, from_EXEC)
    
    root.mainloop()

def GUI_TRANS_matrix_to_df(from_EXEC=None):

    root, canvas, bg_im, button_im, settings_im = LOAD_root("TRANS_matrix_to_df")

    label_list = ["file","sep","output_file"]
    type_list = ["str","str","str"]
    default_list = ["*","\\t","mtd.dat"]
    
    EXEC_display_variables(root, canvas, button_im, settings_im, label_list, type_list, default_list, "TRANS_matrix_to_df", "", "Changement de format, de matrice (.json) à dataframe (.dat)", GUI_main_other, from_EXEC)
    
    root.mainloop()

def GUI_TRANS_matrix_to_grd(from_EXEC=None):

    root, canvas, bg_im, button_im, settings_im = LOAD_root("TRANS_matrix_to_grd")

    label_list = ["file","fmt","output_file"]
    type_list = ["str","str","str"]
    default_list = ["*","*","None"]
    
    EXEC_display_variables(root, canvas, button_im, settings_im, label_list, type_list, default_list, "TRANS_matrix_to_grd", "", "Changement de format, de matrice (.json) à Surfer (.grd)", GUI_main_other, from_EXEC)
    
    root.mainloop()

def GUI_TRANS_grd_to_matrix(from_EXEC=None):

    root, canvas, bg_im, button_im, settings_im = LOAD_root("TRANS_grd_to_matrix")

    label_list = ["file_list","fmt","output_file"]
    type_list = ["str[]","str","str"]
    default_list = ["*","*","None"]
    
    EXEC_display_variables(root, canvas, button_im, settings_im, label_list, type_list, default_list, "TRANS_grd_to_matrix", "", "Changement de format, de Surfer (.grd) à matrice (.json)", GUI_main_other, from_EXEC)
    
    root.mainloop()

def GUI_FIG_display_fig(from_EXEC=None):

    root, canvas, bg_im, button_im, settings_im = LOAD_root("FIG_display_fig")

    label_list = ["file_list"]
    type_list = ["str[]"]
    default_list = ["None"]
    
    EXEC_display_variables(root, canvas, button_im, settings_im, label_list, type_list, default_list, "FIG_display_fig", None, "Affichage interactif de figures en .pickle", GUI_main_other, from_EXEC)
    
    root.mainloop()

def GUI_FIG_plot_data(from_EXEC=None):

    root, canvas, bg_im, button_im, settings_im = LOAD_root("FIG_plot_data")

    label_list = ["file","sep","col_x","col_y","col_z"]
    type_list = ["str","str","int[]","int[]","int[]"]
    default_list = ["*","\\t","[0]","[1]","None"]
    
    EXEC_display_variables(root, canvas, button_im, settings_im, label_list, type_list, default_list, "FIG_plot_data", "FIG_", "Affichage et enregistrement de figures (nuage de points)", GUI_main_other, from_EXEC)
    
    root.mainloop()

def GUI_FIG_plot_grid(from_EXEC=None):

    root, canvas, bg_im, button_im, settings_im = LOAD_root("FIG_plot_grid")

    label_list = ["file"]
    type_list = ["str"]
    default_list = ["*"]
    
    EXEC_display_variables(root, canvas, button_im, settings_im, label_list, type_list, default_list, "FIG_plot_grid", "FIG_", "Affichage et enregistrement de figures (grille)", GUI_main_other, from_EXEC)
    
    root.mainloop()

def GUI_FIG_plot_pos(from_EXEC=None):

    root, canvas, bg_im, button_im, settings_im = LOAD_root("FIG_plot_pos")

    label_list = ["file","sep"]
    type_list = ["str","str"]
    default_list = ["*","\\t"]
    
    EXEC_display_variables(root, canvas, button_im, settings_im, label_list, type_list, default_list, "FIG_plot_pos", "FIG_pos", "Affichage des positions pour chaque bobine", GUI_main_other, from_EXEC)
    
    root.mainloop()

def GUI_EXEC():

    root, canvas, bg_im, button_im, settings_im = LOAD_root("EXEC")

    label_list = ["file"]
    type_list = ["str"]
    default_list = ["_cmd_.txt"]
    
    EXEC_display_variables(root, canvas, button_im, settings_im, label_list, type_list, default_list, "EXEC", "", "Lancement de fonction via fichier .txt", GUI_main_other, None)
    
    root.mainloop()

# Exécute la commande d'aide

def EXEC_help(help_name=None):
    
    if help_name == None:
        os.system("gnome-terminal -e 'bash -c \"python3 Traitement_CMD_v"+CONFIG.ver+".py; exec bash\"'")
    else:
        os.system("gnome-terminal -e 'bash -c \"python3 Traitement_CMD_v"+CONFIG.ver+".py CMD_help "+str(help_name)+"; exec bash\"'")

def EXEC_settings():
    
    s_w = 700
    s_h = 400
    root = tk.Tk(screenName=CONFIG.sc_name)
    root.geometry(str(s_w)+"x"+str(s_h))
    root.title("OPTIONS")
        
    canvas = tk.Canvas(root, width = CONFIG.tk_width, height = CONFIG.tk_height)
    canvas.pack(fill = "both", expand = True)
    
    global keep_prev_ui
    global keep_cmd
    global show_raw_figs
    global clear_old_outputs
    global ui_popups
    global blocking_figs
    
    def update_global_vars():
        global keep_prev_ui
        global keep_cmd
        global show_raw_figs
        global clear_old_outputs
        global ui_popups
        global blocking_figs
        keep_prev_ui = c1.instate(['selected'])
        keep_cmd = c2.instate(['selected'])
        show_raw_figs = c3.instate(['selected'])
        clear_old_outputs = c4.instate(['selected'])
        ui_popups = c5.instate(['selected'])
        blocking_figs = c6.instate(['selected'])
    
    c1 = ttk.Checkbutton(master = canvas, command=update_global_vars)
    if keep_prev_ui:
        c1.state(['!alternate','selected'])
    else:
        c1.state(['!alternate','!selected'])
    canvas.create_window( 30, 20, anchor = "nw", window = c1)
    canvas.create_text( 55, 20, font=('Times', -20, 'bold'), text = "garder les fenêtres ouvertes", anchor = "nw", fill='black')
    c2 = ttk.Checkbutton(master = canvas, command=update_global_vars)
    if keep_cmd:
        c2.state(['!alternate','selected'])
    else:
        c2.state(['!alternate','!selected'])
    canvas.create_window( 30, 45, anchor = "nw", window = c2)
    canvas.create_text( 55, 45, font=('Times', -20, 'bold'), text = "garder le terminal ouvert", anchor = "nw", fill='black')
    c3 = ttk.Checkbutton(master = canvas, command=update_global_vars)
    if show_raw_figs:
        c3.state(['!alternate','selected'])
    else:
        c3.state(['!alternate','!selected'])
    canvas.create_window( 30, 70, anchor = "nw", window = c3)
    canvas.create_text( 55, 70, font=('Times', -20, 'bold'), text = "afficher les figures mpl", anchor = "nw", fill='black')
    c4 = ttk.Checkbutton(master = canvas, command=update_global_vars)
    if clear_old_outputs:
        c4.state(['!alternate','selected'])
    else:
        c4.state(['!alternate','!selected'])
    canvas.create_window( 30, 95, anchor = "nw", window = c4)
    canvas.create_text( 55, 95, font=('Times', -20, 'bold'), text = "effacer les anciens résultats (conseillé)", anchor = "nw", fill='black')
    c5 = ttk.Checkbutton(master = canvas, command=update_global_vars)
    if ui_popups:
        c5.state(['!alternate','selected'])
    else:
        c5.state(['!alternate','!selected'])
    canvas.create_window( 30, 120, anchor = "nw", window = c5)
    canvas.create_text( 55, 120, font=('Times', -20, 'bold'), text = "activer les fenêtres graphiques pour les choix", anchor = "nw", fill='black')
    c6 = ttk.Checkbutton(master = canvas, command=update_global_vars)
    if blocking_figs:
        c6.state(['!alternate','selected'])
    else:
        c6.state(['!alternate','!selected'])
    canvas.create_window( 30, 145, anchor = "nw", window = c6)
    canvas.create_text( 55, 145, font=('Times', -20, 'bold'), text = "activer les fenêtres graphiques bloquantes", anchor = "nw", fill='black')
    
    br = tk.Button(root, text = 'Valider', font=('Terminal', CONFIG.tk_b_font_size, 'bold'), compound="center", command=root.destroy)
    br_c = canvas.create_window( s_w//2-55, s_h-50, anchor = "nw",window = br)
        
# Gère l'affichage des éléments des fenêtres de fonctions
        
def EXEC_display_variables(root, canvas, button_im, settings_im, label_list, type_list, default_list, func_name, func_prefix, func_descr, prev_window, from_EXEC):
    
    title_l = len(func_descr)//2
    canvas.create_rectangle(CONFIG.tk_width//2-title_l*25, 5, CONFIG.tk_width//2+title_l*25, 50, fill=l_gray[1], width=0)
    canvas.create_text( CONFIG.tk_width//2, 20, font=('Times', 30, 'bold'), text = func_descr, anchor = "center", fill="black")
    
    var_list = [None for i in range(len(label_list))]
    
    canvas.create_rectangle(35, 120, 145, 145, fill=l_blue[0], width=0)
    canvas.create_rectangle(145, 120, 345, 145, fill=l_blue[1], width=0)
    canvas.create_rectangle(345, 120, 595, 145, fill=l_blue[0], width=0)
    canvas.create_rectangle(595, 120, 725, 145, fill=l_blue[1], width=0)
    canvas.create_text( 40, 125, font=('Times', -20, 'bold'), text = "Type", anchor = "nw", fill="black")
    canvas.create_text( 145, 125, font=('Times', -20, 'bold'), text = "Variable", anchor = "nw", fill="black")
    canvas.create_text( 345, 125, font=('Times', -20, 'bold'), text = "Valeur", anchor = "nw", fill="black")
    canvas.create_text( 595, 125, font=('Times', -20, 'bold'), text = "Défaut", anchor = "nw", fill="black")
    
    opt_start = default_list.count("*")
    for i in range(len(label_list)):
        canvas.create_rectangle(35, 145+25*i, 145, 170+25*i, fill=d_gray[i%2], width=0)
        canvas.create_rectangle(145, 145+25*i, 345, 170+25*i, fill=l_gray[i%2], width=0)
        canvas.create_rectangle(345, 145+25*i, 595, 170+25*i, fill=d_gray[i%2], width=0)
        canvas.create_rectangle(595, 145+25*i, 725, 170+25*i, fill=l_gray[i%2], width=0)
        canvas.create_text( 40, 150+25*i, font=('Times', -20, 'bold'), text = type_list[i], anchor = "nw", fill='purple')
        if type_list[i] == "bool":
            var_list[i] = ttk.Checkbutton(master = root, variable = var_list[i])
            if from_EXEC == None:
                if default_list[i] == "True":
                    var_list[i].state(['!alternate','selected'])
                else:
                    var_list[i].state(['!alternate','!selected'])
            else:
                if EXEC_get_param(from_EXEC[opt_start:],label_list[i]).lower() in ["true","t","1"]:
                    var_list[i].state(['!alternate','selected'])
                else:
                    var_list[i].state(['!alternate','!selected'])
        else:
            v = tk.StringVar()
            if from_EXEC == None:
                v.set("")
            else:
                if i < opt_start:
                    v.set(from_EXEC[i][:-1])
                else:
                    v.set(EXEC_get_param(from_EXEC[opt_start:],label_list[i]))
            var_list[i] = tk.Entry(master = root, textvariable = v, width=33)
            var_list[i].insert(0, v.get())
        canvas.create_window( 350, 150+25*i, anchor = "nw", window = var_list[i])
        if i < opt_start:
            l_color = "blue"
            d_color = "red"
        else:
            l_color = "#006cc9"
            d_color = "green"
        canvas.create_text( 150, 150+25*i, font=('Times', -20, 'bold'), text = label_list[i], anchor = "nw", fill=l_color)
        canvas.create_text( 600, 150+25*i, font=('Times', -20, 'bold'), text = default_list[i], anchor = "nw", fill=d_color)
        
    def on_return_button_pressed():
        if not keep_prev_ui:
            root.destroy()
        prev_window()

    def on_run_button_pressed():
        EXEC_launch_command(func_name,var_list,label_list,default_list,func_prefix)
    
    def on_refresh_button_pressed():
        EXEC_refresh_data(root, canvas, func_prefix)
    
    def on_clear_button_pressed():
        EXEC_clear_all_figs()
            
    b1 = tk.Button(root, text = 'RUN', font=('Terminal', 50, 'bold'), compound="center", image = button_im, command=on_run_button_pressed)
    b1_c = canvas.create_window( 25,CONFIG.tk_height-225, anchor = "nw",window = b1)
    if func_prefix not in ["",None]:
        b2 = tk.Button(root, text = 'Afficher\nle résultat', font=('Terminal', CONFIG.tk_b_font_size, 'bold'), compound="center", image = button_im, command=on_refresh_button_pressed)
        b2_c = canvas.create_window( 265,CONFIG.tk_height-225, anchor = "nw",window = b2)
        if show_raw_figs:
            b3 = tk.Button(root, text = 'Fermer\nles figures', font=('Terminal', CONFIG.tk_b_font_size, 'bold'), compound="center", image = button_im, command=on_clear_button_pressed)
            b3_c = canvas.create_window( 505,CONFIG.tk_height-225, anchor = "nw",window = b3)
    br = tk.Button(root, text = 'Retour', font=('Terminal', CONFIG.tk_b_font_size, 'bold'), compound="center", command=on_return_button_pressed)
    br_c = canvas.create_window( 25,25, anchor = "nw",window = br)
    ba = tk.Button(root, text = 'Aide', font=('Terminal', CONFIG.tk_b_font_size, 'bold'), compound="center", command=lambda : EXEC_help(func_name))
    ba_c = canvas.create_window( 25,CONFIG.tk_height-275, anchor = "nw",window = ba)
    bs = tk.Button(root, image = settings_im, command=EXEC_settings)
    bs_c = canvas.create_window( CONFIG.tk_width-85,25, anchor = "nw",window = bs)

def EXEC_get_param(fe,l):
    for v in fe:
        s = v[:-1].split("=")
        if s[0] == l:
            return s[1]
    return ""

# Affiche des informations générales

def EXEC_g_infos():
    
    s_w = 700
    s_h = 400
    root = tk.Tk(screenName=CONFIG.sc_name)
    root.geometry(str(s_w)+"x"+str(s_h))
    root.title("INFOS")
        
    canvas = tk.Canvas(root, width = CONFIG.tk_width, height = CONFIG.tk_height)
    canvas.pack(fill = "both", expand = True)
    
    canvas.create_text( 55, 20, font=('Times', -20, 'bold'), text = "Bienvenue sur l'interface graphique du traitement CMD !", anchor = "nw", fill='black')
    canvas.create_text( 55, 70, font=('Times', -20, 'bold'), text = "Les fonctions sont divisées par catégories :", anchor = "nw", fill='black')
    canvas.create_text( 55, 95, font=('Times', -20, 'bold'), text = "CMD -> Traitement général, avec de nombreuses étapes", anchor = "nw", fill='#606000')
    canvas.create_text( 55, 120, font=('Times', -20, 'bold'), text = "CMDEX -> Morceau de traitement, dédié à une tâche spécifique", anchor = "nw", fill='#606000')
    canvas.create_text( 55, 145, font=('Times', -20, 'bold'), text = "JSON -> Gestion des appareils enregistrés (Appareil.json)", anchor = "nw", fill='#606000')
    canvas.create_text( 55, 170, font=('Times', -20, 'bold'), text = "DAT -> Manipulations sur fichier .dat", anchor = "nw", fill='#606000')
    canvas.create_text( 55, 195, font=('Times', -20, 'bold'), text = "Divers -> Autres fonctions (affichage, changement de format...)", anchor = "nw", fill='#606000')
    canvas.create_text( 55, 245, font=('Times', -20, 'bold'), text = "Pour plus d'informations, veuillez consulter l'aide", anchor = "nw", fill='brown')
    
    br = tk.Button(root, text = 'Valider', font=('Terminal', CONFIG.tk_b_font_size, 'bold'), compound="center", command=root.destroy)
    br_c = canvas.create_window( s_w//2-70, s_h-50, anchor = "nw",window = br)

# Affiche les crédits

def EXEC_credits():
    
    s_w = 700
    s_h = 250
    root = tk.Tk(screenName=CONFIG.sc_name)
    root.geometry(str(s_w)+"x"+str(s_h))
    root.title("CRÉDITS")
        
    canvas = tk.Canvas(root, width = CONFIG.tk_width, height = CONFIG.tk_height)
    canvas.pack(fill = "both", expand = True)
    
    canvas.create_text( s_w//2, 20, font=('Times', -20, 'bold'), text = "Développé par Thomas AUBERTIER", anchor = "n", fill='black')
    canvas.create_text( s_w//2, 45, font=('Times', -20, 'bold'), text = "Stage METIS / ÉVEHA International", anchor = "n", fill='black')
    canvas.create_text( s_w//2, 70, font=('Times', -20, 'bold'), text = "thomas.aubertier@etu.sorbonne-universite.fr", anchor = "n", fill='#006cc9')
    canvas.create_text( s_w//2, 120, font=('Times', -20, 'bold'), text = "Basé sur les travaux de Julien THIESSON", anchor = "n", fill='brown')
    canvas.create_text( s_w//2, 145, font=('Times', -20, 'bold'), text = "-- 2025 --", anchor = "n", fill='red')
    
    br = tk.Button(root, text = 'Valider', font=('Terminal', CONFIG.tk_b_font_size, 'bold'), compound="center", command=root.destroy)
    br_c = canvas.create_window( s_w//2-70, s_h-50, anchor = "nw",window = br)

# Exécute la fonction spécifiée

def EXEC_launch_command(func_name,var_list,label_list,default_list,func_prefix):
    
    if func_name == "EXEC":
        if var_list:
            file_name = "_cmd_.txt"
        else:
            file_name = str(var_list[0].get()).split("=")[1]
        with open("EXEC/"+file_name, 'r') as cmd_file:
            fn = cmd_file.readlines()
            if not fn or fn[0][:-1] in ["","0","EXEC","CMD_help"]:
                print("Fonction inutile pour l'interface graphique")
                return None
            ef = fn[0][:-1]
            globals()['GUI_'+ef](from_EXEC=fn[1:])
        return None
    
    param_list = ""
    for ic, v in enumerate(var_list):
        try:
            var_value = str(v.get())
        except:
            var_value = str(v.instate(['selected']))
        if var_value != "" :
            if default_list[ic] == "*": # Paramètre obligatoire
                param_list += " " + var_value
            else:                       # Paramètre optionel
                param_list += " " + label_list[ic] + "=" + var_value
    
    gui_mode = [" GraphicUIn't"," GraphicUI"]
    if func_prefix == None:
        gui_mode = [" GraphicUIn't GraphicUI_ignore"," GraphicUI GraphicUI_ignore"]
    command_to_execute = "python3 Traitement_CMD_v"+CONFIG.ver+".py " + func_name + param_list + gui_mode[int(ui_popups)]
    print(command_to_execute)
    if func_prefix != None and clear_old_outputs:
        os.system("rm -f Output/"+func_prefix+"*")
    if keep_cmd or func_prefix == None or func_prefix == "":
        os.system("gnome-terminal -e 'bash -c \"" + command_to_execute + "; exec bash\"'")
    else:
        os.system("gnome-terminal -e '" + command_to_execute + "'")

# Affiche les figures résultat de la commande

def EXEC_refresh_data(root, canvas, prefix):
    
    os.chdir(CONFIG.script_path)
    fig_list = sorted(glob.glob("Output/"+prefix+"*.pickle"))
    im_list = sorted(glob.glob("Output/"+prefix+"*.png"))
    t = len(fig_list)
    b_l = []
    fig_l = []
    im_l = []
    #canvas.pack_forget()
    label = tk.Label(root)
    label.place(x=750, y=150)
    for ic in range(t):
        if show_raw_figs:
            figx = pickle.load(open(fig_list[ic], 'rb'))
        
        # size = figx.get_size_inches()
        # rescale = min(dim_max_fig/size[0], dim_max_fig/size[1])
        # figx.set_figwidth(size[0]*rescale)
        # figx.set_figheight(size[1]*rescale)
        plt.show(block=blocking_figs)
        plt.pause(0.25)
        # fig_l.append(tk.Tk(screenName=CONFIG.sc_name))
        # fig_l[ic].title('Figure '+str(ic+1))
        
        # figcanvas = tk.Canvas(canvas, width = CONFIG.tk_width_mpl, height = CONFIG.tk_height_mpl)
        # figcanvas.place(x=750, y=150)
        im = Image.open(im_list[ic])
        im_width, im_height = im.size
        rescale = min(CONFIG.tk_width_mpl/im_width, CONFIG.tk_height_mpl/im_height)
        #im = canvas.create_image( 750, 150, image = button_im, anchor = "nw")
        im_l.append(ImageTk.PhotoImage(im.resize((int(im_width*rescale), int(im_height*rescale))), master = root))
        # figcanvastkagg = FigureCanvasTkAgg(figx, master=fig_l[ic])
        # figcanvastkagg.get_tk_widget().place(x=750, y=150)
        # figcanvastkagg.get_tk_widget().pack(side = tk.BOTTOM, expand = False)
        
        # toolbar = NavigationToolbar2Tk(figcanvastkagg, fig_l[ic], pack_toolbar=False)
        # toolbar.update()
        # toolbar.pack()
        
        b = tk.Button(root, text = str(ic+1), font=('System', 50, 'bold'), command=lambda ic=ic: EXEC_show_fig(label,im_l,ic))
        b_l.append(canvas.create_window( 750 + 110*ic, 60, anchor = "nw",window = b))
        
    canvas.pack()
    if im_l:
        EXEC_show_fig(label,im_l,0)

# Change la figure à afficher

def EXEC_show_fig(label,im_l,ic):
    
    # for im in im_list:
    #     im.pack_forget()
    #     #f.withdraw()
    # im_list[ic].pack()
    #f.deiconify()
    #canvas.tag_raise(im)
    #im.tkraise()
    #canvas.pack()
    #print(ic, " est visible !")
    # for i in range(3):
    #     print(im_l[i])
    # print(im_l[ic]," ",ic)
    label.config(image=im_l[ic])

# Change la figure à afficher

def EXEC_clear_all_figs():
    
    plt.close('all')
    
GUI_main_menu()
















