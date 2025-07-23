#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 23 09:33:48 2025

@author: taubertier
"""

import os
import matplotlib.pyplot as plt
import pandas as pd

import CONFIG
import EM_CMD

os.chdir(CONFIG.data_path)
# %%

EM_CMD.FORTRAN_ball_calibr("bminihi2.dat","HCP",[32,71,118],3,27,15,100)