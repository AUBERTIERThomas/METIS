# -*- coding: utf-8 -*-
'''
   geophpy.emi.operation
   -------------------------

   DataSet Object electromagnetic operations routines.

   :copyright: Copyright 2014-2025 Lionel Darras, Philippe Marty, Quentin Vitale and contributors, see AUTHORS.
   :license: GNU GPL v3.
'''

import pandas as pd

import geophpy.core.operation as goper
import geophpy.__config__ as CONFIG

def synth_base(don,nc_data,CMDmini=True):
    """
    Resume each base by one single line.\n
    It contains all data pointed by ``nc_data``, its profile/base index and its time.\n
    Does not return a single dataframe, is managed by ``init``.
    
    Parameters
    ----------
    don : dataframe
        Active base dataframe.
    nc_data : list of str
        Names of every conductivity and inphase columns, ordered two by two.
    ``[opt]`` CMDmini : bool, default : ``True``
        If bases were taken in the air (device's 0). 
    
    Returns
    -------
    pd_num_fich : pd.Series
        ``"File_id"`` column (file order).
    pd_bp : pd.Series
        ``"B+P"`` column (base + profile index).
    pd_tps : pd.Series
        ``"Seconds"`` column (base + profile index).
    * ``CMDmini = True``
        pd_inf : pd.Series
            Data columns for lowest values (device's 0).
    * ``CMDmini = False``
        pd_valmd : pd.Series
            Data columns for average values, since all points are on the ground.
    
    Notes
    -----
    Subfunction of ``init``.\n
    If ``CMDmini = False``, the result will not give enough information to remove
    the device's 0, although the variations between bases will stand.
    
    See also
    --------
    ``init, evol_profiles``
    """
    # Division des colonnes entre conductivité et inphase
    cond_data = nc_data[::2]
    inph_data = nc_data[1::2]
    
    # Vérification de format
    if not('Base' in don.columns) :
        raise KeyError("Call 'detect_base_pos' before this procedure.")
    if not('Seconds' in don.columns) :
        don['Seconds'] = goper.set_time(don)
    
    # Calcul des quantiles pour diviser la base entre haut et bas
    # On utilise la conductivité pour faire la différence
    num_base=don['Base'].unique()
    num_base=num_base[num_base>0]    
    ls_num_fich,ls_bp,ls_tps,ls_val=[],[],[],[]
    for n_base in num_base :
        ind_c=don.index[don['Base']==n_base]
        tps_c=don.loc[ind_c,'Seconds'].median()
        Q5=don.loc[ind_c,cond_data].quantile(0.05)
        Q95=don.loc[ind_c,cond_data].quantile(0.95)
        valb_c=(Q95+Q5)/2.
        ls_num_fich.append(don.loc[ind_c[0],"File_id"])
        ls_bp.append(don.loc[ind_c[0],"B+P"])
        ls_tps.append(tps_c),ls_val.append(valb_c)
    
    # Association de la moyenne des valeurs en haut pour chaque base
    pd_valmd=pd.concat(ls_val,axis=1)
    ls_sup,ls_inf=[],[]
    for n_base in num_base :
        ind_c=don.index[don['Base']==n_base]
        seuil=pd_valmd[n_base-1]
        ls_s,ls_i=[],[]
        for ic,sc in enumerate(seuil) :
            dat_c=don.loc[ind_c,cond_data[ic]].copy()
            dat_i=don.loc[ind_c,inph_data[ic]].copy()
            ind1=dat_c.index[dat_c>sc]
            ind2=dat_c.index[dat_c<sc]
            ls_s.append(dat_c.loc[ind1].median())     
            ls_i.append(dat_c.loc[ind2].median())
            ls_s.append(dat_i.loc[ind1].median())     
            ls_i.append(dat_i.loc[ind2].median())
        
        
        
        ls_sup.append(pd.Series(ls_s))
        ls_inf.append(pd.Series(ls_i))
    
    # Mise au bon format
    pd_sup=pd.concat(ls_sup,axis=1).round(CONFIG.prec_data)
    pd_inf=pd.concat(ls_inf,axis=1).round(CONFIG.prec_data)
    pd_sup.index=nc_data
    pd_inf.index=nc_data 
    pd_num_fich=pd.Series(ls_num_fich)  
    pd_bp=pd.Series(ls_bp)     
    pd_tps=pd.Series(ls_tps).round(CONFIG.prec_data)
    
    # Si l'appareil a pu être soulevé ou non
    if CMDmini :
        return(pd_num_fich,pd_bp,pd_tps,pd_inf)
    else :
        return(pd_num_fich,pd_bp,pd_tps,pd_valmd)