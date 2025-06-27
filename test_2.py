#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 23 09:57:07 2025

@author: taubertier
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import RBFInterpolator
from scipy.stats.qmc import Halton

g = 100
n = 8000

rng = np.random.default_rng()
xobs = 2*Halton(2, seed=rng).random(n) - 1
yobs = np.sum(xobs, axis=1)*np.exp(-6*np.sum(xobs**2, axis=1))
#print("xobs = ",xobs)
#print("yobs = ",yobs)
xgrid = np.mgrid[-1:1:g*1j, -1:1:g*1j]
#print("xgrid = ",xgrid)
xflat = xgrid.reshape(2, -1).T
#print("xflat = ",xflat)
yflat = RBFInterpolator(xobs, yobs)(xflat)
#print("yflat", yflat)
ygrid = yflat.reshape(g, g)
fig, ax = plt.subplots()
ax.pcolormesh(*xgrid, ygrid, vmin=-0.25, vmax=0.25, shading='gouraud')
#p = ax.scatter(*xobs.T, c=yobs, s=50, ec='k', vmin=-0.25, vmax=0.25)
#fig.colorbar(p)
plt.show()