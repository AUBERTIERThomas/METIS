#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 18 11:37:00 2025

@author: taubertier
"""
import numpy as np
import matplotlib.pyplot as plt
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
    
    x_2d = x[:,np.newaxis]
    r = np.random.randint(10000)
    estimator = [TheilSenRegressor(random_state=r),RANSACRegressor(random_state=r),HuberRegressor(),]
    
    best_model = None
    best_res = None
    best_mse = np.inf
    best_i = -1
    
    for i,e in enumerate(estimator):
        poly = PolynomialFeatures(3)
        model = make_pipeline(poly, e)
        model.fit(x_2d, y)
        res = model.predict(x_2d)
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
    
    x_2d = x[:,np.newaxis]
    r = np.random.randint(10000)
    estimator = [TheilSenRegressor(random_state=r),HuberRegressor(),]
    
    best_model = None
    best_res = None
    best_mse = np.inf
    best_i = -1
    
    for i,e in enumerate(estimator):
        poly = PolynomialFeatures(3)
        model = make_pipeline(poly, e)
        model.fit(x_2d, y)
        res = model.predict(x_2d)
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

def CMD_inverse_regr(X,Y):
    
    x = Y.copy()
    y = X.copy()

    coefs_list = []
    mymodel = np.poly1d(np.polyfit(x, y, 3))
    
    coefs = mymodel.c[::-1]
    coefs_list.append(coefs)
    
    x_2d = x[:,np.newaxis]
    r = np.random.randint(10000)
    estimator = [TheilSenRegressor(random_state=r),HuberRegressor(),]
    
    for i,e in enumerate(estimator):
        poly = PolynomialFeatures(3)
        model = make_pipeline(poly, e)
        model.fit(x_2d, y)
        res = model.predict(x_2d)
        mse = mean_squared_error(res, y)
        coefs = e.coef_
        coefs[0] *= 2
        coefs_list.append(coefs)
            
    return coefs_list

def coeffs_relation(X,Y,linear=True):
    
    fig,ax=plt.subplots(nrows=1,ncols=1,figsize=(8,4.5))
    ax.plot(X,Y,'+')
    if linear:
        l_r = linregress(X,Y)
        print(l_r.intercept, l_r.slope)
        ax.plot(X,l_r.intercept+X*l_r.slope,'o')
        return l_r.intercept, l_r.slope
    else:
        l = ["linear","theilsen","huber"]
        p_r = CMD_inverse_regr(X,Y)
        for i,c in enumerate(p_r):
            print(c)
            ax.plot(c[0]+c[1]*Y+c[2]*Y**2+c[3]*Y**3,Y,"o",ms=1,label=l[i])
        plt.legend()
        return p_r
        
def testouh(n,min_,max_,err_var,rc,linear=True):
    X = np.linspace(min_,max_,n)
    Y = rc[3]*X**(1/3) + rc[2]*X**(1/2) + rc[1]*X + rc[0]
    for i in range(n):
        X[i] += (np.random.normal(0,1))*err_var
        Y[i] += (np.random.normal(0,1))*err_var
    coeffs_relation(X,Y,linear=linear)


#classic_regr(500,-3,13,4,[6, 11, -14, 1.5])
#inverse_regr(500,0.1,10,3,[0, 1, 1, 20])
testouh(10000,0.1,10,3,[0, 1, 1, 20],linear=False)
