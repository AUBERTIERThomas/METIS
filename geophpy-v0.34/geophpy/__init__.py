# -*- coding: utf-8 -*-
'''
    geophpy
    -------

    The public API to geophpy.

    :copyright: Copyright 2014-2021 Lionel Darras, Philippe Marty, Quentin Vitale and contributors, see AUTHORS.
    :license: GPLv3, see LICENSE for details.

'''

from geophpy.core.io import FILE_FORMAT_DICT, FORMAT_LIST

SOFTWARE = 'GeophPy'
__software__ = SOFTWARE

VERSION = '0.33'
__version__ = VERSION

AUTHORS  = 'L. Darras (UMR5133-Archéorient), P. Marty (UMR7619-Metis) & Q. Vitale (Évhea)'
__authors__ = AUTHORS

DATE = '14/12/2021'
__date__ = DATE

DESCRIPTION = 'Tools for sub-surface geophysical survey data processing'
__description__ = DESCRIPTION

FILE_FORMAT_DICT = FILE_FORMAT_DICT # dictionary of recognized file formats

from geophpy.core import *
