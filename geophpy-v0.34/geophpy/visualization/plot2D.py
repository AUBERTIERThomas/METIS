# -*- coding: utf-8 -*-
'''
    geophpy.plotting.plot2D
    -----------------------

    Dataset display in 2-dimensions.

    :copyright: Copyright 2014-2020 L. Darras, P. Marty, Q. Vitale and contributors, see AUTHORS.
    :license: GNU GPL v3.

'''


import matplotlib.colors as colors
#import matplotlib.cm as cm
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# to get matplotlib filled markers list
from matplotlib.lines import Line2D

from six import iteritems

from mpl_toolkits.axes_grid1 import make_axes_locatable

from geophpy.core.utils import *

#from geophpy.plotting.plot import _init_figure

# to avoid using pyplot to make figure (retained in memory, could be problematic with a GUI)
#from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
#from matplotlib.figure import Figure

#from scipy.interpolate import griddata


# list of matplotlib filled marker (code from matplotlib.org)
UNFILLED_MARKERS = [m for m, func in iteritems(Line2D.markers)
                    if func != 'nothing' and m not in Line2D.filled_markers]
UNFILLED_MARKERS = sorted(UNFILLED_MARKERS,
                          key=lambda x: (str(type(x)), str(x)))[::-1]


def plot_surface(dataset, cmapname, **kwargs):
    ''' Plot dataset as a 2D surface.

    Parameters
    ----------
    dataset : :obj:`~geophpy.dataset.DataSet`
        Dastaset to display.

    cmapname : str
        Name of the colormap.

    **kwargs :
        Additional keyword arguments for display options.
        The keyword options can be found in the following table:

        fig : None or `matplotlib.figure.Figure`
            Figure to use for the plot.
            Use None (by default) to create a new figure.

        creversed :
        logscale :
        cmmin :
        cmmax :
        markersize :

        cmapdisplay : bool
            True to display a colorbar.

        labeldisplay :

        axisdisplay : bool
            True to display axis.

        pointsdisplay :
        marker : Matplotlib marker style string,
        transparent :
        rects :
        rect_color :
        points :
        rectscolor # point_color ???

        filename :

        dpi :

        transparent : bool
            If True, the axes patches will all be transparent.
            The figure patch will also be transparent unless facecolor and/or edgecolor are specified via kwargs.

            See matplotlib documentation for more information.

    '''

    # Retrieving general options
    fig = kwargs.get('fig', None)
    creversed = kwargs.get('creversed', False)
    logscale = kwargs.get('logscale', False)
    interpolation = kwargs.get('interpolation', 'none')
    cmapdisplay = kwargs.get('cmapdisplay', True)
    cmmin = kwargs.get('cmmin', None)
    cmmax = kwargs.get('cmmax', None)

    # Figure initialization
    fig, ax = _init_figure(fig=fig)  # clear an existing figure and add an empty ax

    # Reversed colormap
    cmap = _init_colormap(cmapname, creversed=creversed)

    # Logarithmic scale
    norm = _init_colorscale(logscale=logscale)

    # builds the image
    if dataset.data.z_image is not None:
        #Z = (dataset.data.z_image)          # reads the z_image of the dataset
        Z = np.copy(dataset.data.z_image)


        #Z[np.isnan(Z)] = 0
        #Z = np.ma.masked_invalid(dataset.data.z_image)
        #cm.get_cmap().set_bad(alpha=0.0)
        #cm.get_cmap().set_bad(color='red')
        #X, Y = dataset.get_xygrid()
        ### with pcolormesh, 'pixel' can be not square (rectanle), nans are handeled
        #im = ax.pcolormesh(X, Y, Z, norm=norm, cmap=cmap, vmin=cmmin, vmax=cmmax)

        x0 = dataset.info.x_min - (dataset.info.x_gridding_delta/2)
        x1 = dataset.info.x_max + (dataset.info.x_gridding_delta/2)
        y0 = dataset.info.y_min - (dataset.info.y_gridding_delta/2)
        y1 = dataset.info.y_max + (dataset.info.y_gridding_delta/2)

        im = ax.imshow(Z, extent=(x0, x1, y0, y1), interpolation=interpolation, cmap=cmap, vmin=cmmin, vmax=cmmax, norm=norm, origin='lower', aspect='auto')

    else:
        Z = np.empty([100, 100])
        im = ax.imshow(Z, interpolation=interpolation, cmap=cmap, vmin=cmmin, vmax=cmmax, norm=norm, origin='lower', aspect='auto')

    # Display options
    _apply_plot_options(dataset, ax, **kwargs)

    # Colorbar display
    #colormap = _init_colorbar(ax, im, cmapdisplay=cmapdisplay)
    colormap = _init_colorbar(fig, ax, im, cmapdisplay=cmapdisplay)


    # Forcing axis limits
    x, y = dataset.get_xyvect()
    ax.set_xlim(np.nanmin(x), np.nanmax(x))
    ax.set_ylim(np.nanmin(y), np.nanmax(y))

    # Forcing equal x and Y
    ax.set_aspect('equal')

    # Saving figure to file
    _save_figure(**kwargs)

    fig.canvas.draw()

    return fig, colormap


def plot_contour(dataset, cmapname, **kwargs):
    '''plotting in 2D-dimensions contours.

    Parameters
    ----------
    dataset : :obj:`~geophpy.dataset.DataSet`
        Dastaset to display.

    cmapname : str
        Name of the colormap.

    **kwargs :
        Additional keyword arguments for display options.
        The keyword options can be found in the following table:

        fig : None or `matplotlib.figure.Figure`
            Figure to use for the plot.
            Use None (by default) to create a new figure.

        creversed :
        logscale :
        cmmin :
        cmmax :
        markersize :

        cmapdisplay : bool
            True to display a colorbar.

        levels :

        labeldisplay :

        axisdisplay : bool
            True to display axis.

        pointsdisplay :
        marker : Matplotlib marker style string,
        rects :
        rect_color :
        points :
        rectscolor # point_color ???

        filename :


        dpi : {None, scalar > 0, 'figure'}
            The resolution in dots per inch.

        transparent : bool
            If True, the axes patches will all be transparent.
            The figure patch will also be transparent unless facecolor and/or edgecolor are specified via kwargs.

            See matplotlib documentation for more information.

    '''

   # Retrieving general options
    fig = kwargs.get('fig', None)
    creversed = kwargs.get('creversed', False)
    logscale = kwargs.get('logscale', False)
    #axisdisplay = kwargs.get('axisdisplay', None)
    cmapdisplay = kwargs.get('cmapdisplay', True)
    levels = kwargs.get('levels', None)
    cmmin = kwargs.get('cmmin', None)
    cmmax = kwargs.get('cmmax', None)

   # Figure initialization
    fig, ax = _init_figure(fig=fig)  # clear an existing figure and add an empty ax

   # Reversed colormap
    cmap = _init_colormap(cmapname, creversed=creversed)

   # Logarithmic scale
    norm = _init_colorscale(logscale=logscale)

   # Builds the graphic extent
    x_decimal_maxnb = getdecimalsnb(dataset.info.x_gridding_delta)
    y_decimal_maxnb = getdecimalsnb(dataset.info.y_gridding_delta)

    Z = (dataset.data.z_image)
    xi = np.linspace(dataset.info.x_min, dataset.info.x_max, 1 + (np.around((dataset.info.x_max-dataset.info.x_min)/dataset.info.x_gridding_delta)), endpoint=True)
    yi = np.linspace(dataset.info.y_min, dataset.info.y_max, 1 + (np.around((dataset.info.y_max-dataset.info.y_min)/dataset.info.y_gridding_delta)), endpoint=True)
    xi, yi = np.around(xi, decimals=x_decimal_maxnb), np.around(yi, decimals=y_decimal_maxnb)

    X, Y = np.meshgrid(xi, yi)                          # builds the (X, Y) gridded matrix

    x0 = dataset.info.x_min - (dataset.info.x_gridding_delta/2)
    x1 = dataset.info.x_max + (dataset.info.x_gridding_delta/2)
    y0 = dataset.info.y_min - (dataset.info.y_gridding_delta/2)
    y1 = dataset.info.y_max + (dataset.info.y_gridding_delta/2)

   ###
   ##
   # ...TBD...
   # levels can be both int or array-like in the next version of matplotlib
   # but for version 1.5 only array of values where to plot the countours
   # are allowed.
   # This transformation should hence not be necessary when the next versions
   # of matplotlib will be used.
    levels = _make_levels(levels=levels, cmmin=cmmin, cmmax=cmmax)
    if levels is not None:

        ctr = ax.contour(X, Y, Z, extent=(x0, x1, y0, y1), levels=levels, cmap=cmap, vmin=cmmin, vmax=cmmax, norm=norm, origin='lower', aspect='auto')

    else:
        ctr = ax.contour(X, Y, Z, extent=(x0, x1, y0, y1), cmap=cmap, vmin=cmmin, vmax=cmmax, norm=norm, origin='lower', aspect='auto')
   # ...TBD...
   ##
   ###

   # Display options
    _apply_plot_options(dataset, ax, **kwargs)

   # Colorbar display
    colormap = _init_colorbar(fig, ax, ctr, cmapdisplay=cmapdisplay)
##   if cmapdisplay:
##      divider = make_axes_locatable(ax)
##      cax = divider.append_axes("right", size="5%", pad=0.1)
##      #colormap = plt.colorbar(contour, cax=cax, ax=ax, ticks=[cmmin, cmmax])
##      colormap = plt.colorbar(contour, cax=cax, ax=ax, norm=norm, boundaries=[cmmin, cmmax])
##   else:
##      colormap = None

   # Forcing axis limits
    x, y = dataset.get_xyvect()
    ax.set_xlim(np.nanmin(x), np.nanmax(x))
    ax.set_ylim(np.nanmax(y), np.nanmax(y))

   # Forcing equal x and Y
    ax.set_aspect('equal')

   # Saving figure to file
    _save_figure(**kwargs)

    fig.canvas.draw()

    return fig, colormap


#def plot_contourf(dataset, cmapname, levels=None, creversed=False, fig=None, filename=None, cmmin=None, cmmax=None, cmapdisplay=True, axisdisplay=True, labeldisplay=True, pointsdisplay=False, dpi=600, transparent=False, logscale=False, rects=None, points=None, marker='+'):
def plot_contourf(dataset, cmapname, **kwargs):
    ''' Plotting in 2-D filled contours.

    Parameters
    ----------
    dataset : :obj:`~geophpy.dataset.DataSet`
        Dastaset to display.

    cmapname : str
        Name of the colormap.

    **kwargs :
        Additional keyword arguments for display options.
        The keyword options can be found in the following table:

        fig : None or `matplotlib.figure.Figure`
            Figure to use for the plot.
            Use None (by default) to create a new figure.

        creversed :
        logscale :
        cmmin :
        cmmax :
        markersize :

        cmapdisplay : bool
            True to display a colorbar.

        levels :

        labeldisplay :

        axisdisplay : bool
            True to display axis.

        pointsdisplay :
        marker : Matplotlib marker style string,
        rects :
        rect_color :
        points :
        rectscolor # point_color ???

        filename :

        dpi : {None, scalar > 0, 'figure'}
            The resolution in dots per inch.

        transparent : bool
            If True, the axes patches will all be transparent.
            The figure patch will also be transparent unless facecolor and/or edgecolor are specified via kwargs.

            See matplotlib documentation for more information.

    '''

    # Retrieving general options
    fig = kwargs.get('fig', None)
    creversed = kwargs.get('creversed', False)
    logscale = kwargs.get('logscale', False)
    axisdisplay = kwargs.get('axisdisplay', None)
    cmapdisplay = kwargs.get('cmapdisplay', True)
    levels = kwargs.get('levels', None)
    cmmin = kwargs.get('cmmin', None)
    cmmax = kwargs.get('cmmax', None)

    # Figure initialization
    fig, ax = _init_figure(fig=fig)  # clear an existing figure and add an empty ax

    # Reversed colormap
    cmap = _init_colormap(cmapname, creversed=creversed)

    # Logarithmic scale
    norm = _init_colorscale(logscale=logscale)

    # Builds the graphic
    x_decimal_maxnb = getdecimalsnb(dataset.info.x_gridding_delta)
    y_decimal_maxnb = getdecimalsnb(dataset.info.y_gridding_delta)

    Z = (dataset.data.z_image)
    xi = np.linspace(dataset.info.x_min, dataset.info.x_max, 1 + (np.around((dataset.info.x_max-dataset.info.x_min)/dataset.info.x_gridding_delta)), endpoint=True)
    yi = np.linspace(dataset.info.y_min, dataset.info.y_max, 1 + (np.around((dataset.info.y_max-dataset.info.y_min)/dataset.info.y_gridding_delta)), endpoint=True)
    xi, yi = np.around(xi, decimals=x_decimal_maxnb), np.around(yi, decimals=y_decimal_maxnb)

    X, Y = np.meshgrid(xi, yi)                          # builds the (X, Y) gridded matrix

    ax.get_xaxis().set_visible(axisdisplay)
    ax.get_yaxis().set_visible(axisdisplay)

    x0 = dataset.info.x_min-(dataset.info.x_gridding_delta/2)
    x1 = dataset.info.x_max+(dataset.info.x_gridding_delta/2)
    y0 = dataset.info.y_min-(dataset.info.y_gridding_delta/2)
    y1 = dataset.info.y_max+(dataset.info.y_gridding_delta/2)

    ###
    ##
    # ...TBD...
    # levels can be both int or array-like in the next version of matplotlib
    # but for version 1.5 only array of values where to plot the countours
    # are allowed.
    # This transformation should hence not be necessary when the next versions
    # of matplotlib will be used.
    levels = _make_levels(levels=levels, cmmin=cmmin, cmmax=cmmax)
    if levels is not None:

        ctr = ax.contourf(X, Y, Z, extent=(x0, x1, y0, y1), levels=levels, cmap=cmap, vmin=cmmin, vmax=cmmax, norm=norm, origin='lower', aspect='auto')

    else:
        ctr = ax.contourf(X, Y, Z, extent=(x0, x1, y0, y1), cmap=cmap, vmin=cmmin, vmax=cmmax, norm=norm, origin='lower', aspect='auto')

    # Display options
    _apply_plot_options(dataset, ax, **kwargs)

    # Colorbar display
    colormap = _init_colorbar(fig, ax, ctr, cmapdisplay=cmapdisplay)
##    if cmapdisplay:
##       divider = make_axes_locatable(ax)
##       cax = divider.append_axes("right", size="5%", pad=0.1)
##       #colormap = plt.colorbar(contour,cax=cax, ax=ax, norm=norm, boundaries=[cmmin, cmmax], ticks=[cmmin, cmmax])
##       colormap = plt.colorbar(contour,cax=cax, ax=ax, norm=norm, boundaries=[cmmin, cmmax])
##    else:
##       colormap = None

    # Forcing axis limits
    x, y = dataset.get_xyvect()
    ax.set_xlim(np.nanmin(x), np.nanmax(x))
    ax.set_ylim(np.nanmin(y), np.nanmax(y))

    # Forcing equal x and Y
    ax.set_aspect('equal')

    # Saving figure to file
    _save_figure(**kwargs)
    #_save_figure(filename=filename, axisdisplay=axisdisplay, cmapdisplay=cmapdisplay, dpi=dpi, transparent=transparent)

    fig.canvas.draw()

    return fig, colormap


def plot_scatter(dataset, cmapname, **kwargs):
    ''' Plotting dataset as a 2D scatter plot.

    Parameters
    ----------
    dataset : :obj:`~geophpy.dataset.DataSet`
        Dastaset to display.

    cmapname : str
        Name of the colormap.

    **kwargs :
        Additional keyword arguments for display options.
        The keyword options can be found in the following table:

        fig : None or `matplotlib.figure.Figure`
            Figure to use for the plot.
            Use None (by default) to create a new figure.

        creversed :
        logscale :
        cmmin :
        cmmax :
        markersize :

        cmapdisplay : bool
            True to display a colorbar.

        filename :

        dpi : {None, scalar > 0, 'figure'}
            The resolution in dots per inch.

        transparent : bool
            If True, the axes patches will all be transparent.
            The figure patch will also be transparent unless facecolor and/or edgecolor are specified via kwargs.

            See matplotlib documentation for more information.

    '''

    # Figure initialization
    fig = kwargs.get('fig', None)
    fig, ax = _init_figure(fig=fig)  # clear an existing figure and add an empty ax

    # Reversed colormap
    creversed = kwargs.get('creversed', False)
    cmap = _init_colormap(cmapname, creversed=creversed)

    # Logarithmic scale
    logscale = kwargs.get('logscale', False)
    norm = _init_colorscale(logscale=logscale)

    # Scatter plot
    cmmin = kwargs.get('cmmin', None)
    cmmax = kwargs.get('cmmax', None)

    # Builds the graphic
    markersize = kwargs.get('markersize', None)
    x, y, z = dataset.data.values.T
    #sc = plt.scatter(x, y, c=z, cmap=cmap, norm=norm, vmin=cmmin, vmax=cmmax, edgecolors='none')
    sc = ax.scatter(x, y, c=z, cmap=cmap, norm=norm, vmin=cmmin, vmax=cmmax, edgecolors='none', s=markersize)

    # Colorbar display
    cmapdisplay = kwargs.get('cmapdisplay', True)
    colormap = _init_colorbar(fig, ax, sc, cmapdisplay=cmapdisplay)

    # Forcing axis limits
    ax.set_xlim(np.nanmin(x), np.nanmax(x))
    ax.set_ylim(np.nanmin(y), np.nanmax(y))

    # Forcing equal x and Y
    ax.set_aspect('equal')

    # Saving figure to file
    _save_figure(**kwargs)

    fig.canvas.draw()

    return fig, colormap


def plot_postmap(dataset, **kwargs):
    ''' Plotting dataset as a 2D postmap plot.

    Parameters
    ----------
    dataset : :obj:`~geophpy.dataset.DataSet`
        Dastaset to display.

    **kwargs :
        Additional keyword arguments for display options.
        The keyword options can be found in the following table:

        fig : None or `matplotlib.figure.Figure`
            Figure to use for the plot.
            Use None (by default) to create a new figure.

        labeldisplay :

        axisdisplay : bool
            True to display axis.

        marker : Matplotlib marker style string,
        markersize :

        filename :

        dpi : {None, scalar > 0, 'figure'}
            The resolution in dots per inch.

        transparent : bool
            If True, the axes patches will all be transparent.
            The figure patch will also be transparent unless facecolor and/or edgecolor are specified via kwargs.

            See matplotlib documentation for more information.

    '''

    # Retrieving general options
    fig = kwargs.get('fig', None)
    labeldisplay = kwargs.get('labeldisplay', True)
    axisdisplay = kwargs.get('axisdisplay', None)
    marker = kwargs.get('marker', '+')
    markersize = kwargs.get('markersize', 1)

    # Figure initialization
    fig, ax = _init_figure(fig=fig)  # clear an existing figure and add an empty ax

    # Retrieving raw values
    x, y, _ = dataset.data.values.T

    # Label display
    if labeldisplay:
        ax.set_xlabel(dataset.data.fields[0])
        ax.set_ylabel(dataset.data.fields[1])

    # Axis display
    if axisdisplay:
        ax.set_title(dataset.data.fields[2])
    else:
        ax.set_title("")

    if not labeldisplay:
        ax.set_title("")

    ax.get_xaxis().set_visible(axisdisplay)
    ax.get_yaxis().set_visible(axisdisplay)

    # Scatter plot (forcing unfilled marker for readability)
    if marker not in UNFILLED_MARKERS:
        #sc = plt.scatter(x, y, facecolor='None',edgecolor='k', marker=marker)
        ax.scatter(x, y, facecolor='None', edgecolor='k', marker=marker, s=markersize)

    else:
        #sc = plt.scatter(x, y, marker=marker,edgecolor='k')
        ax.scatter(x, y, marker=marker, edgecolor='k', s=markersize)

    # Forcing axis limits
    ax.set_xlim(np.nanmin(x), np.nanmax(x))
    ax.set_ylim(np.nanmin(y), np.nanmax(y))

    # Forcing equal x and Y
    ax.set_aspect('equal')

    # Colormap display
    colormap = None

    # Saving figure to file
    _save_figure(**kwargs)

    fig.canvas.draw()

    return fig, colormap


# Already exists in plot but cannot be imported using
# from geophpy.plotting.plot import _init_figure
# for some reasons.
def _init_figure(fig=None):
    ''' Clear the given figure or return a new one and initialize an ax. '''

    # First display
    if fig is None:
        fig = plt.figure()
        #fig = Figure()
        #FigureCanvas(fig)

    # Existing display
    else:
        fig = plt.figure(fig.number, clear=True)
        #fig.clf()

    # Axes initialization
    ax = fig.add_subplot(111)

    return fig, ax


def _init_colormap(cmapname, creversed=False):
    ''' Return a matplotlib colormap object from a color map name. '''

    # Reversed colormap
    if creversed:
        cmapname = cmapname + '_r'       # adds '_r' at the colormap name to reverse it

    # Colormap object
    cmap = plt.get_cmap(cmapname)       # gets the colormap

    return cmap


def _init_colorscale(logscale=False):
    ''' Return a matplotlib linear or logarithmic colorscale norm. '''

    if logscale:
        norm = colors.LogNorm()
    else:
        norm = colors.Normalize()

    return norm


def _init_colorbar(fig, ax, plot_id, cmapdisplay=True):
    ''' Add to the given axis a colorbar for the given plot id (mappable). '''

    if cmapdisplay:
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.1)
        #colormap = plt.colorbar(plot_id, cax=cax)
        colormap = fig.colorbar(plot_id, cax=cax)

    else:
        colormap = None

    return colormap


def _save_figure(**kwargs):
    ''' Save the current figure into a file.

    Parameters
    ----------
    **kwargs :
        Keyword arguments for saving options.
        The keyword options can be found in the following table:

        filename : str
            Output file name.

        axisdisplay : bool
            True if axis are displayed.
            Will change the figure size.

        cmapdisplay : bool
            True if a colorbar is displayed.
            Will change the figure size.

        dpi : {None, scalar > 0, 'figure'}
            The resolution in dots per inch.

            See matplotlib documentation for more information.

        transparent : bool
            If True, the axes patches will all be transparent.
            The figure patch will also be transparent unless facecolor and/or edgecolor are specified via kwargs.

            See matplotlib documentation for more information.

        '''

    # Retrieving save options
    filename = kwargs.get('filename', None)
    axisdisplay = kwargs.get('axisdisplay', True)
    cmapdisplay = kwargs.get('cmapdisplay', True)
    dpi = kwargs.get('dpi', 600)
    transparent = kwargs.get('transparent', True)

    if filename is not None:
        # Plot in full picture if no axis display
        if axisdisplay is False and cmapdisplay is False:
            plt.savefig(filename, dpi=dpi, transparent=transparent, bbox_inches='tight', pad_inches=0)

        else:
            plt.savefig(filename, dpi=dpi, transparent=transparent, bbox_inches='tight')

def _make_levels(levels=None, cmmin=None, cmmax=None):
    ''' '''
    ###
    ##
    # ...TBD...
    # levels can be both int or array-like in the next version of matplotlib
    # but for version 1.5 only array of values where to plot the countours
    # are allowed.
    # This transformation should hence not be necessary when the next versions
    # of matplotlib will be used.
    if levels is not None:
        # Transforming number of contour to conttour values
        if isinstance(levels, int):
            if cmmin is None:
                vmin = np.nanmin(Z)
            else:
                vmin = cmmin

            if cmmax is None:
                vmax = np.nanmax(Z)
            else:
                vmax = cmmax

            levels = np.linspace(vmin, vmax, levels)

    return levels


def _add_points(dataset, axis, plist, color='green', marker='o', markersize=12):
    ''' Add points to the given axis. '''

    ax = axis

    for point in plist:
        # Ensuring points have 2 parameters
        if len(point) == 2:
            x, y = point

            # Ensuring points are in dataset limits
            if x < dataset.info.x_min:
                x = dataset.info.x_min
            if y < dataset.info.y_min:
                y = dataset.info.y_min

            ax.plot(x, y, color=color, linestyle='None', marker=marker, markersize=markersize, markeredgewidth=2)


def _add_rectangles(dataset, axis, rect_list, color='red'):
    ''' Add rectangles to the given axis. '''

    ax = axis

    for rect in rect_list:
        # Ensuring rectangles have 4 parameters
        if len(rect) == 4:
            x, y, w, h = rect

            # Ensuring rectangles are in dataset limits
            if x < dataset.info.x_min:
                x = dataset.info.x_min

            if (x+w) > dataset.info.x_max:
                w = dataset.info.x_max - x

            if y < dataset.info.y_min:
                y = dataset.info.y_min

            if (y+h) > dataset.info.y_max:
                h = dataset.info.y_max - y

            ax.add_patch(patches.Rectangle((x, y), w, h, fill=False, edgecolor=color))

def _add_pointsdisplay(dataset, axis, marker):
    ''' Add the dataset (raw) points position display to the given axis. '''

    ax = axis
    x = dataset.data.values[:, 0]
    y = dataset.data.values[:, 1]
    ax.plot(x, y, 'k', ms=3, linestyle='None', marker=marker)

    ax.set_xlim(dataset.info.x_min, dataset.info.x_max)
    ax.set_ylim(dataset.info.y_min, dataset.info.y_max)


def _add_gridpointsdisplay(dataset, axis, marker):
    ''' Add the dataset grid points position display to the given axis. '''

    ax = axis

    x_maxdecim = getdecimalsnb(dataset.info.x_gridding_delta)
    y_maxdecim = getdecimalsnb(dataset.info.y_gridding_delta)

    xi, yi = dataset.get_xyvect()

    xi, yi = np.around(xi, decimals=x_maxdecim), np.around(yi, decimals=y_maxdecim)
    X, Y = np.meshgrid(xi, yi)                          # builds the (X, Y) gridded matrix

    for i, _ in enumerate(X):
        ax.scatter(X[i], Y[i], s=1, c='b', marker=marker)

    ax.set_xlim(dataset.info.x_min, dataset.info.x_max)
    ax.set_ylim(dataset.info.y_min, dataset.info.y_max)


def _apply_plot_options(dataset, axis, **kwargs):
    ''' Apply the plot options to the given axis.

    Parameters
    ----------
    dataset : :obj:`~geophpy.dataset.DataSet`
        Dastaset to display.

    axis : Matplolib axis
        Axe

    **kwargs :
        Additional keyword arguments for display options.
        The keyword options can be found in the following table:

        labeldisplay
        axisdisplay
        pointsdisplay
        marker
        transparent
        rects
        rect_color
        points
        rectscolor # point_color ???

    '''

    ax = axis

    # Label display
    labeldisplay = kwargs.get('labeldisplay', True)
    if labeldisplay:
        ax.set_xlabel(dataset.data.fields[0])
        ax.set_ylabel(dataset.data.fields[1])
        ax.set_title(dataset.data.fields[2])
    else:
        ax.set_xlabel("")
        ax.set_ylabel("")
        ax.set_title("")

    # Axis display
    axisdisplay = kwargs.get('axisdisplay', True)
    ax.get_xaxis().set_visible(axisdisplay)
    ax.get_yaxis().set_visible(axisdisplay)
    #ax.get_title().set_visible(axisdisplay)

    # Gridding points display
    pointsdisplay = kwargs.get('pointsdisplay', False)
    marker = kwargs.get('marker', 'o')
    if pointsdisplay:
        _add_pointsdisplay(dataset, ax, marker)

    # Transparent display for NaNs
    transparent = kwargs.get('transparent', False)
    if transparent:
        ax.patch.set_alpha(0.0)

    # Optional rectangle display
    rects = kwargs.get('rects', None)
    rect_color = kwargs.get('rect_color', "red")
    if rects is not None:
        #xmin, xmax, ymin, ymax = dataset.get_gridextent()
        _add_rectangles(dataset, ax, rects, color=rect_color)

    # Optional point display
    points = kwargs.get('points', None)
    point_color = kwargs.get('rectscolor', "green")
    if points is not None:
        _add_points(dataset, ax, points, color=point_color, marker=marker)
