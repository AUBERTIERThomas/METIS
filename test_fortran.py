#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  4 16:39:21 2025

@author: taubertier
"""

import os
import glob
import sys
import ctypes as ct

script_path = "/home/taubertier/StageMETIS/2024 2025 Aubertier/Code python JT/"

# import the shared library
fortlib = ct.CDLL(script_path+'/testatata.so') 

# Specify arguments and result types
fortlib.sum2.argtypes = [ct.POINTER(ct.c_double)]
fortlib.sum2.restype = ct.c_double

# Create a double and pass it to Fotran (by reference)
a = ct.c_double(5)
b = fortlib.sum2(ct.byref(a))
print(b)