#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 19 13:47:10 2025

@author: taubertier
"""

# import numpy as np
# import os
# import sys
from matplotlib import get_backend
import matplotlib.pyplot as plt
import time

tekst = get_backend()
print("Backend = ", tekst)

    
def freeze_wouw():
    fig,ax = plt.subplots(nrows=1,ncols=1,figsize=(5,5))

    ax.plot([i for i in range(100)], [i*2 for i in range(100)])
    ax.set_title("test")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_aspect('equal')
    plt.show(block=False)
    plt.pause(0.0001)

    inp = input()

    if inp == "y":
        print('\33[0;1;32m'+"ui")
    else:
        print('\33[0;1;31m'+"no")

def superglitchy_mpl():
    fig,ax = plt.subplots(nrows=1,ncols=1,figsize=(16,9))
    time.sleep(2.5)
    
freeze_wouw()