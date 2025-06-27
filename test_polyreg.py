#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 18 11:37:00 2025

@author: taubertier
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve
from scipy.stats import linregress
from sklearn.linear_model import (
    HuberRegressor,
    LinearRegression,
    RANSACRegressor,
    TheilSenRegressor,
)
from sklearn.metrics import mean_squared_error
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures

import CONFIG
import EM_CMD

v = [1, 2, 3, 4]
#v = [-4, 3, 1, 150]
#v = [-2, 5, -10, 20]
#v = [-9, 10, 15, 15]
#v = [0, -5, -9, 2]

def classic_regr(n,min_,max_,err_var,rc):
    
    l = ["linear","theilsen","ransac","huber"]
    print(rc)
    print("--- ---")
    old_x = np.linspace(min_,max_,n)
    old_y = rc[3]*old_x**3 + rc[2]*old_x**2 + rc[1]*old_x + rc[0]
    x = old_x.copy()
    y = old_y.copy()
    for i in range(n):
        x[i] += (np.random.normal(0,1))*err_var
        y[i] += (np.random.normal(0,1))*err_var
    
    coefs_list = []
    fig,ax=plt.subplots(nrows=1,ncols=2,figsize=(8,4.5))
    ax[0].plot(x,y,'+')
    
    mymodel = np.poly1d(np.polyfit(x, y, 3))
    
    ax[0].plot(x, mymodel(x))
    ax[0].plot(old_x,old_y,'--')
    coefs = mymodel.c[::-1]
    print(l[0])
    print(coefs)
    diff = [(coefs[i]-rc[i]) for i in range(4)]
    score = sum([np.abs(d) for d in diff])
    print("diff = ",score)
    print()
    coefs_list.append(coefs)
    
    xd = x[:,np.newaxis]
    r = np.random.randint(10000)
    estimator = [TheilSenRegressor(random_state=r),RANSACRegressor(random_state=r),HuberRegressor(),]
    
    best_model = None
    best_res = None
    best_mse = np.inf
    best_i = -1
    
    for i,e in enumerate(estimator):
        poly = PolynomialFeatures(3)
        model = make_pipeline(poly, e)
        model.fit(xd, y)
        res = model.predict(xd)
        mse = mean_squared_error(res, y)
        if i in [1]:
            coefs = e.estimator_.coef_
            coefs[0] = rc[0]
        else:
            coefs = e.coef_
            coefs[0] *= 2
        print(l[i+1])
        print(coefs)
        diff = [(coefs[i]-rc[i]) for i in range(4)]
        score = sum([np.abs(d) for d in diff])
        print("diff = ",score)
        print("mse = ",mse)
        print()
        coefs_list.append(coefs)
        if mse < best_mse:
            best_model = e
            best_res = res
            best_mse = mse
            best_i = i
    #pppp = best_model.get_metadata_routing()
    #print(pppp)
    #sys.exit(0)
    print(best_i)
    
    ax[0].plot(x,best_res,"o",ms=2)
    ax[0].set_title("Modèles bruts")
    
    ax[1].plot(old_x,old_y,'--')
    for i,c in enumerate(coefs_list):
        ax[1].plot(x,c[0]+c[1]*x+c[2]*x*x+c[3]*x*x*x,"o",ms=1,label=l[i])
        
    
    plt.legend()
    ax[1].set_title("Vrai équation")


def inverse_regr(n,min_,max_,err_var,rc):
    
    l = ["linear","theilsen","huber"]
    print(rc)
    print("--- ---")
    old_x = np.linspace(min_,max_,n)
    old_y = rc[3]*old_x**(1/3) + rc[2]*old_x**(1/2) + rc[1]*old_x + rc[0]
    x = old_y.copy()
    y = old_x.copy()
    for i in range(n):
        x[i] += (np.random.normal(0,1))*err_var
        y[i] += (np.random.normal(0,1))*err_var
    
    coefs_list = []
    final_coefs_list = []
    fig,ax=plt.subplots(nrows=1,ncols=2,figsize=(8,4.5))
    ax[0].plot(y,x,'+')    
    mymodel = np.poly1d(np.polyfit(x, y, 3))
    
    ax[0].plot(old_x,old_y,'--')
    coefs = mymodel.c[::-1]
    print(l[0])
    final_coefs = [np.sign(c)*(np.abs(c)**(1/(i+1))) for i,c in enumerate(coefs)]
    print(final_coefs)
    print()
    coefs_list.append(coefs)
    final_coefs_list.append(final_coefs)
    
    xd = x[:,np.newaxis]
    r = np.random.randint(10000)
    estimator = [TheilSenRegressor(random_state=r),HuberRegressor(),]
    
    best_model = None
    best_res = None
    best_mse = np.inf
    best_i = -1
    
    for i,e in enumerate(estimator):
        poly = PolynomialFeatures(3)
        model = make_pipeline(poly, e)
        model.fit(xd, y)
        res = model.predict(xd)
        mse = mean_squared_error(res, y)
        coefs = e.coef_
        coefs[0] *= 2
        print(l[i+1])
        final_coefs = [np.sign(c)*(np.abs(c)**(1/(i+1))) for i,c in enumerate(coefs)]
        print(final_coefs)
        print("mse = ",mse)
        print()
        coefs_list.append(coefs)
        final_coefs_list.append(final_coefs)
        if mse < best_mse:
            best_model = e
            best_res = res
            best_mse = mse
            best_i = i
    #pppp = best_model.get_metadata_routing()
    #print(pppp)
    #sys.exit(0)
    print(best_i)
    
    ax[0].plot(best_res,x,"o",ms=2)
    ax[0].set_title("Modèles bruts")
    
    ax[1].plot(old_x,old_y,'--')
    for i,c in enumerate(coefs_list):
        ax[1].plot(c[0]+c[1]*x+c[2]*x**2+c[3]*x**3,x,"o",ms=1,label=l[i])
    #for i,c in enumerate(final_coefs_list):
    #    ax[1].plot(c[0]*x+c[1]*x**(1/2)+c[2]*x**(1/3),x,"o",ms=1,label=l[i])
        
    
    plt.legend()
    ax[1].set_title("Vrai équation")

def CMD_inverse_regr(X,Y,choice):
    
    x = Y.copy()
    y = X.copy()

    coefs_list = []
    xd = x[:,np.newaxis]
    if choice:
        mymodel = np.poly1d(np.polyfit(x, y, 3))
        
        coefs = mymodel.c[::-1]
        coefs_list.append(coefs)
        
        r = np.random.randint(10000)
        estimator = [TheilSenRegressor(random_state=r),HuberRegressor(),]
    else:
        estimator = [HuberRegressor()]
    
    for i,e in enumerate(estimator):
        poly = PolynomialFeatures(3)
        model = make_pipeline(poly, e)
        model.fit(xd, y)
        coefs = e.coef_
        coefs[0] *= 2
        coefs_list.append(coefs)
            
    return coefs_list

def CMD_mse(X,Y,c):
    
    new_Y = c[0] + c[1]*X + c[2]*X**(1/2) + c[3]*X**(1/3)
    mse = sum(np.abs(new_Y - Y))
    return mse
    

def CMD_convergence_inv_poly(X,Y,nb_pts,nb_tours=1000,force_fin=25,verif=False,verif_plus=False):
    
    coef_list = [float(min(X)), float((max(Y)-min(Y))/(max(X)-min(X))), 0, 0]
    current_coef = 3
    diff_y = max(Y)-min(Y)
    fin = False
    fin_mse = diff_y/5
    print("fin : ",fin_mse)
    best_mse = np.inf
    best_cl = coef_list.copy()
    cpt = 0
    while not fin:
        for i in range(nb_tours):
            mse = CMD_mse(X,Y,coef_list)
            r = np.random.randint(4)
            coef_list, mse = CMD_convergence_inv_step(X,Y,coef_list,mse,current_coef,verif=verif_plus)
            current_coef = r
            if best_mse > mse:
                best_mse = mse
                best_cl = coef_list.copy()
            cpt += 1
            if verif:
                print(cpt," ",mse," ",current_coef)
        print(best_mse)
        if best_mse < fin_mse or cpt >= nb_tours*force_fin:
            fin = True
    print(cpt," ",fin_mse," ",best_mse)
    return best_cl
    
def CMD_convergence_inv_step(X,Y,coef_list,mse,cc,verif=False):
               
    cl_cpy = coef_list.copy()
    sign = True
    fin = False
    prev_mse = mse
    step = 1
    while not fin:
        mse = CMD_mse(X,Y,cl_cpy)
        if verif:
            print("[",cc,"] ",prev_mse," ",mse," ",step)
        if mse > prev_mse:
            sign = not sign
            step /= 2
            r = np.random.random()
            if r > np.exp(-(mse/prev_mse)*3):
                cl_cpy[cc] = coef_list[cc]
            else:
                prev_mse = mse
                coef_list[cc] = cl_cpy[cc]
        else:
            prev_mse = mse
            coef_list[cc] = cl_cpy[cc]
        cl_cpy[cc] += (int(not sign) - int(sign))*step
        if step < 0.01:
            fin = True
    return coef_list, prev_mse

def coeffs_relation(X,Y,linear,choice,conv,nb_conv=50):
    
    fig,ax=plt.subplots(nrows=1,ncols=1,figsize=(CONFIG.fig_width,CONFIG.fig_height))
    ax.plot(X,Y,'+',label="Points initiaux")
    ax.set_xlabel(r"signal(ph)")
    ax.set_ylabel(r"$\sigma$")
    if linear:
        l_r = linregress(X,Y)
        print(l_r.intercept, l_r.slope)
        ax.plot(X,l_r.intercept+X*l_r.slope,'o',ms=1,label="Régression linéaire")
        ax.set_title("Modèle linéaire VS nuage de points")
        plt.legend()
        return [l_r.intercept, l_r.slope]
    else:
        if choice:
            l = ["linear","theilsen","huber"]
        else:
            l = ["huber"]
        p_r = CMD_inverse_regr(X,Y,choice)
        p_rx = []
        for i,c in enumerate(p_r):
            print(c)
            p_rx.append(c[0]+c[1]*Y+c[2]*Y**2+c[3]*Y**3)
            ax.plot(p_rx[i],Y,"o",ms=1,label=l[i])
        ax.set_title("Modèles VS nuage de points")
        plt.legend()
        plt.show(block=False)
        plt.pause(0.25)
        if choice:
            correct = False
            while correct == False:
                if EM_CMD.GUI:
                    EM_CMD.MESS_input_GUI(["Quel modèle choisir ?","","~r~ linear","~r~ theilsen ~!~","~r~ huber"])
                    try:
                        inp = EM_CMD.GUI_VAR_LIST[0]
                    except:
                        EM_CMD.MESS_warn_mess("Veuillez sélectionner un réponse")
                        continue
                else:
                    EM_CMD.MESS_input_mess(["Quel modèle choisir ?","","0 : linear","1 : theilsen","2 : huber"])
                    inp = input()
                try:
                    inp = int(inp)
                    model = p_rx[inp]
                    correct = True
                except ValueError:
                    EM_CMD.MESS_warn_mess("Réponse non reconnue !")
                except IndexError:
                    EM_CMD.MESS_warn_mess("Le modèle {} n'existe pas !".format(inp))
            plt.close(fig)
        else:
            model = p_r[0][0]+p_r[0][1]*Y+p_r[0][2]*Y**2+p_r[0][3]*Y**3
        
        nb_pts = len(Y)
        if conv:
            mc = len(Y)/(nb_conv**2)
            npc_l = np.array([int(mc*i**2) for i in range(nb_conv)])
            print(npc_l)
            X_c = model[npc_l]
            Y_c = Y[npc_l]
            fc = CMD_convergence_inv_poly(X_c,Y_c,nb_conv)
        else:
            npc_l = np.array([0,nb_pts//3,2*nb_pts//3,nb_pts-1])
            X_c = model[npc_l]
            X_c_l = np.array([[1,xi,xi**(1/2),xi**(1/3)] for xi in X_c])
            Y_c = Y[npc_l]
            fc = np.linalg.solve(X_c_l, Y_c)
        
        X_plot = np.linspace(min(model),max(model),100)
        fig,ax=plt.subplots(nrows=1,ncols=1,figsize=(CONFIG.fig_width,CONFIG.fig_height))
        ax.plot(model,Y,"o",ms=4,label="Estimation")
        ax.plot(X_plot,fc[0]+fc[1]*X_plot+fc[2]*X_plot**(1/2)+fc[3]*X_plot**(1/3),"-",label="Modèle inverse")
        #ax.plot(v[0]+v[1]*X_plot+v[2]*X_plot**(1/2)+v[3]*X_plot**(1/3), X_plot,"-",label="symétrique")
        ax.plot(X_plot, v[0]+v[1]*X_plot+v[2]*X_plot**(1/2)+v[3]*X_plot**(1/3),"-",label="techniquement le vrai")
        ax.set_title("Allure de la relation")
        ax.set_xlabel(r"signal(ph)")
        ax.set_ylabel(r"$\sigma$")
        plt.legend()
        plt.show(block=False)
        plt.pause(0.25)
        print(fc)
        return fc
        
def testouh(n,min_,max_,err_var,rc,linear=True,choice=False,conv=False):
    X = np.linspace(min_,max_,n)
    Y = rc[3]*X**(1/3) + rc[2]*X**(1/2) + rc[1]*X + rc[0]
    fact = (max(Y)-min(Y))/(max(X)-min(X))
    for i in range(n):
        X[i] += (np.random.normal(0,1))*err_var
        Y[i] += (np.random.normal(0,1))*err_var*fact
    coeffs_relation(X,Y,linear,choice,conv)


classic_regr(500,-3,13,1,[6, 11, -14, 1.5])
#inverse_regr(500,0.1,10,3,[0, 1, 1, 20])
#testouh(10000,0.1,5,0.4,v,linear=False,choice=False,conv=True)
