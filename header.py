import uncertainties as u
import numpy as np
import uncertainties.unumpy as unp
import numpy as np
import matplotlib.pyplot as plt
import uncertainties.unumpy as unp
import uncertainties as uncrt
from uncertainties import ufloat
from uncertainties.unumpy import uarray
from scipy.optimize import curve_fit
from scipy.signal import find_peaks
import scipy.constants as constants
from matplotlib.colors import hsv_to_rgb
import matplotlib.cm as cm


N_POINTS=100000
N_RUNS=100

def load(directory):
    print("Loading Files")
    #Load in the data to an array where the first index is the run and the second(last) index is the sample
    data=np.zeros((N_RUNS,N_POINTS))
    for i in range(N_RUNS):
        data[i]=np.fromfile(directory+"ch1_{}.bin".format(i),dtype='int8')

    calibration=np.zeros((N_RUNS,N_POINTS))
    for i in range(N_RUNS):
        calibration[i]=np.fromfile(directory+"ch2_{}.bin".format(i),dtype='int8')

    return data, calibration

def group(data, N_GROUPS, GROUP_SIZE):
    print("Grouping Data")
    grouped_data=uarray(np.zeros((N_RUNS,N_GROUPS)),np.zeros((N_RUNS,N_GROUPS)))

    for run in range(N_RUNS):
        for group in range(N_GROUPS):
            sample=data[run,group*GROUP_SIZE:(group+1)*GROUP_SIZE]
            grouped_data[run,group]=u.ufloat(np.mean(sample),np.sqrt(np.std(sample)**2/GROUP_SIZE+1/(12*GROUP_SIZE**2)))
        
    return grouped_data
        
    
def ufloat_from_sample(sample):
    return u.ufloat(np.mean(sample),np.std(sample)/np.sqrt(len(sample)))

def scale_time(directory):

    #load in x axis scale factors
    ch1=np.loadtxt(directory+"ch1_paramiters.txt",dtype=str,delimiter=';',usecols=(9,10,11))
    ch2=np.loadtxt(directory+"ch2_paramiters.txt",dtype=str,delimiter=';',usecols=(9,10,11))
    
    #check them
    for run in ch1:
        assert(run[0]=='XUNIT "s"')
        assert(run[1]==ch1[0,1])
        assert(run[2]==ch1[0,2])

    for run in ch2:
        assert(run[0]=='XUNIT "s"')
        assert(run[1]==ch1[0,1])
        assert(run[2]==ch1[0,2])

    #return correct function
    xincr=float(ch1[0,1][6:])
    xzero=float(ch1[0,2][6:])

    def s(t,xzero=xzero,xincr=xincr):
        return xzero+xincr*t
    
    return s

def scale_ch2voltage(directory):

    #load in x axis scale factors
    ch2=np.loadtxt(directory+"ch2_paramiters.txt",dtype=str,delimiter=';',usecols=(13,14,16))

    for run in ch2:
        assert(run[0]=='YUNIT "V"')
        assert(run[1]==ch2[0,1])
        assert(run[2]==ch2[0,2])

    #return correct function
    xincr=float(ch2[0,1][6:])
    xzero=float(ch2[0,2][6:])

    def s(t,xzero=xzero,xincr=xincr):
        return xzero+xincr*t
    
    return s

from lmfit import create_params
from lmfit import minimize
from lmfit import Parameters

def detuning(x,data,uncertainty):
    def model(params,x,order):
        A=0.
        phi=0.
        C=0.
        for o in range(order[0]+1):
            A+=params[f'A{o}']*x**o
        for o in range(order[1]+1):
            phi+=params[f'phi{o}']*x**o
        for o in range(order[2]+1):
            C+=params[f'C{o}']*x**o

        return A*np.cos(phi)+C

    def residual(params, x, data, uncertainty, model):

        modelv = model(params,x)

        return (data-modelv) / uncertainty

    linear = lambda params,x: model(params=params,x=x,order=(1,1,1))
    quadratic = lambda params,x: model(params=params,x=x,order=(2,2,2))
    cubic = lambda params,x: model(params=params,x=x,order=(3,3,3))

    def quartic(params,x):

        A0=params['A0']
        A1=params['A1']
        A2=params['A2']
        A3=params['A3']
        A4=params['A4']

        phi0=params['phi0']
        phi1=params['phi1']
        phi2=params['phi2']
        phi3=params['phi3']
        phi4=params['phi4']

        C0=params['C0']
        C1=params['C1']
        C2=params['C2']
        C3=params['C3']
        C4=params['C4']

        if phi4==0:
            return 10000

        return (A0 + A1*x + A2*x**2 + A3*x**3 +A4*x**4) * np.cos((phi0 + phi1*x + phi2*x**2 + phi3*x**3 +phi4*x**4)) + (C0 + C1*x + C2*x**2 + C3*x**3 +C4*x**4)
    
    params = create_params(A0=5, A1=0, A2=0, A3=0, A4=0,phi0=1, phi1 =23.4, phi2=0, phi3=0, phi4=0, C0 = 10, C1=-7, C2=0, C3=0,C4=0)

    def heat(params):
        hot_params=(params).copy()
        dict=params.valuesdict()
        for name,ovalue in dict.items():
            hot_params[name].set(value=ovalue*np.random.normal(1,0.02))
        
        return hot_params
    
    p1=params.copy()
    p1['A2'].set(vary=False)
    p1['A3'].set(vary=False)
    p1['A4'].set(vary=False)
    p1['phi2'].set(vary=False)
    p1['phi3'].set(vary=False)
    p1['phi4'].set(vary=False)
    p1['C2'].set(vary=False)
    p1['C3'].set(vary=False)
    p1['C4'].set(vary=False)
    out1 = minimize(residual, p1, args=(x, data, uncertainty, linear))

    p2=heat(out1.params)
    p2['A2'].set(vary=True)
    p2['phi2'].set(vary=True)
    p2['C2'].set(vary=True)
    out2 = minimize(residual, p2, args=(x, data, uncertainty, quadratic))

    p3=heat(out2.params)
    p3['A3'].set(vary=True)
    p3['phi3'].set(vary=True)
    p3['C3'].set(vary=True)
    out3 = minimize(residual, p3, args=(x, data, uncertainty, cubic))

    p4=heat(out3.params)
    p4['A4'].set(vary=True)
    p4['phi4'].set(vary=True)
    p4['C4'].set(vary=True)
    out4 = minimize(residual, p4, args=(x, data, uncertainty, quartic))

    def phi(x, params=out4.params):
        phi0=params['phi0']
        phi1=params['phi1']
        phi2=params['phi2']
        phi3=params['phi3']
        phi4=params['phi4']

        return phi0 + phi1*x + phi2*x**2 + phi3*x**3 +phi4*x**4
    
    return phi