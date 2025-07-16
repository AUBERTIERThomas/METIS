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

fich = "Fortran/test.dat"
don = pd.read_csv(fich,sep='\s+',header=None)
print(don)

fig,ax = plt.subplots(nrows=1,ncols=1,figsize=(16,9),squeeze=False)
ind = np.array([11*i+np.array([j for j in range(121)]) for i in range(11)]).flatten()
print(ind)
#ax[0][0].plot(don.iloc[441:,2],don.iloc[441:,4],'x')
#ax[0][0].plot(don.iloc[:,5],1/don.iloc[:,0],'x')
ax[0][0].plot(1/don.iloc[:,0],don.iloc[:,4],'x')
f = np.array(don.iloc[:,4])
c = [0.000999000999000999, 0.014038191122300208, 0, -0.03125]
#ax[0][0].plot(f,c[0]+f*c[1]+f*f*c[2]+f*f*f*c[3],'x')


# for i in range(50):
#     print('\33[1;{}m'.format(i),i)
