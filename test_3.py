#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul  2 15:31:14 2025

@author: taubertier
"""


import os
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# fich = "Fortran/test.dat"
# don = pd.read_csv(fich,sep='\s+',header=None)
# print(don)

# fig,ax = plt.subplots(nrows=1,ncols=1,figsize=(16,9),squeeze=False)
# ind = np.array([11*i+np.array([j for j in range(121)]) for i in range(11)]).flatten()
# print(ind)
# ax[0][0].plot(don.iloc[441:,2],don.iloc[441:,4],'x')

#print("{:.5E}".format(200.39279))

for i in range(50):
    print('\33[1;{}m'.format(i),i)