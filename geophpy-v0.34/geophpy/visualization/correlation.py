# -*- coding: utf-8 -*-
'''
    geophpy.plotting.correlation
    ----------------------------

    Module regrouping dataset correlation plots functions.

    :copyright: Copyright 2014-2019 Lionel Darras, Philippe Marty, Quentin Vitale and contributors, see AUTHORS.
    :license: GNU GPL v3.

'''

import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

import geophpy.core.processing as cproc
import geophpy.core.utils as utils
from geophpy.visualization.plot import _init_figure

import numpy as np

from scipy.signal import hilbert


def plotmap(dataset, fig=None, filename=None, method='Crosscorr',
            dpi=None, transparent=False, showenvelope=False, cmapname='jet', cmapdisplay=True):
    ''' Plot data profile-to-profile correlation map. '''

    # Figure initialization
    fig, ax = _init_figure(fig=fig)  # clear an existing figure and add an empty ax

    # Correlation map computation
    correlmap, pva1map = cproc.correlmap(dataset, method) # valfilt
    shift, shiftprf    = cproc.correlshift(correlmap, pva1map)

    # Build the image
    xmin = dataset.info.x_min   # - xdelta/2 ?
    xmax = dataset.info.x_max   # + xdelta/2 ?
    ny   = (correlmap.shape[0] + 1) // 2

    # Correlation map
    if showenvelope:
        im = ax.imshow(np.abs(hilbert(correlmap)), extent=(xmin,xmax,-ny,+ny), origin='lower', interpolation='bilinear', aspect='auto', cmap=cmapname, alpha=.99)
    else:
        im = ax.imshow(correlmap, extent=(xmin,xmax,-ny,+ny), origin='lower', interpolation='bilinear', aspect='auto', cmap=cmapname, alpha=.99)


    # Global best fit
    ax.plot([xmin,xmax], [shift,shift], 'w--', linewidth=3, alpha=.6)
    ax.plot([xmin,xmax], [shift,shift], 'k--', linewidth=2., alpha=.6)

    # Axis labels
    ax.set_title('Correlation map')
    ax.set_xlabel('Even profiles')
    ax.set_ylabel('Shift')

    # Colorbar display
    if cmapdisplay:
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.1)
        colormap = fig.colorbar(im, cax=cax)


    if filename is not None:
       plt.savefig(filename, dpi=dpi, transparent=transparent)

    return fig


def plotsum(dataset, fig=None, filename=None, method='Crosscorr', dpi=None, transparent=False,
            showenvelope=True, showfit=True):
    ''' Plot the dataset profile-to-profile correlation sum.'''

    # Figure initialization
    fig, ax = _init_figure(fig=fig)  # clear an existing figure and add an empty ax

    # Correlation map
    cormap, pva1map  = cproc.correlmap(dataset, method)
    corm             = np.zeros(cormap.shape[0])
    shift, shiftprf  = cproc.correlshift(cormap, pva1map, output=corm)

#    shift      = cproc.correlshift(cor1, pva1, output=corm)
    n               = corm.size

    # Correlation sum
    xdata = np.arange(0,n)-(n-1)//2
    ydata = np.abs(hilbert(corm))

    if showenvelope:
        ax.plot(np.arange(0,n)-(n-1)//2, np.abs(hilbert(corm)),
                'g--', linewidth=1, label='envelope')
        ax.fill_between(xdata, 0, ydata,
                        facecolor='green', alpha=0.05)

    ax.plot(np.arange(0,n)-(n-1)//2, corm,
            'b-', label='correlation')

    if showfit:
        xdata = np.arange(0,n)-(n-1)//2
        ydata = np.abs(hilbert(corm))

        popt, pcov = utils.gauss_fit(xdata, ydata)
        yfit = utils.gauss_func(xdata, popt[0], popt[1], popt[2])

        ax.plot(xdata, yfit,
                'r:', linewidth=1.5, label='fit')
    

    # Best fit location
    #ax.plot([shift, shift], [np.nanmin(corm), np.nanmax(corm)], 'k', linewidth=2)
    ax.plot([shift, shift], [np.nanmin(corm) - 0.05, np.nanmax(corm) + 0.05], 'w--', linewidth=3, alpha=.6)
    ax.plot([shift, shift], [np.nanmin(corm) - 0.05, np.nanmax(corm) + 0.05], 'k--', linewidth=2., alpha=.6)

    # Axis labels
    ax.set_title('Correlation sum')
    ax.set_xlabel('Shift')
    ax.set_ylabel('Correlation')
    
    # Upper center legend
    if showenvelope or showfit:
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles, labels)
        #ax.legend(frameon=False, loc=9, ncol=3, mode='expand')
        ax.legend(frameon=False, loc=9, ncol=3)

    if filename is not None:
       plt.savefig(filename, dpi=dpi, transparent=transparent)

    return fig
