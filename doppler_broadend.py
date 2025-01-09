from header import *
from calibrate import calibrate

print("\n")

#load in the data
data,calibration=load("Data\data_broad_nopump\\")

d=calibrate(calibration)

GROUP_SIZE=100
N_GROUPS=N_POINTS//GROUP_SIZE

#group the data
grouped_data=group(data,N_GROUPS,GROUP_SIZE)

def binorm(t,a1,m1,s1,a2,m2,s2,c):
    return a1*np.exp(-(t-m1)**2/(2*s1**2))+a2*np.exp(-(t-m2)**2/(2*s2**2))+c

i=30000//GROUP_SIZE
f=75000//GROUP_SIZE

ds=(d(np.arange(i,f)))

p0=[-70,40000/GROUP_SIZE,8000/GROUP_SIZE,-60,70000/GROUP_SIZE,8000/GROUP_SIZE,50]

popts=np.zeros((N_RUNS,len(p0)))

for j,run in enumerate(unp.nominal_values(grouped_data[:,i:f])):
    popt,pcov=curve_fit(
            f=binorm,
            xdata=unp.nominal_values(ds),
            ydata=run,
            p0=p0,
            #sigma=unp.std_devs(grouped_calibration[run,i:f]),
            #absolute_sigma=True
        )

    popts[j]=popt

params=uarray(np.mean(popts,axis=0),np.std(popts,axis=0,ddof=1)/np.sqrt(N_RUNS))

def y(x):
    return (x*80*10**(-6)+33.7800*10**(-3))/(params[6]*80*10**(-6)+33.7800*10**(-3))


Is=y(grouped_data[0,i:f])
plt.errorbar(x=unp.nominal_values(ds),
             xerr=unp.std_devs(ds),
             y=unp.nominal_values(Is),
             yerr=unp.std_devs(Is),
             marker='.',
             linestyle='')
plt.plot(unp.nominal_values(ds),unp.nominal_values(y(binorm(np.arange(i,f),*popts[0]))),color='C1',zorder=10)
plt.xlabel("Detuning (GHz)")
plt.ylabel("Relative intensity")
plt.savefig("doppler_broadend_spectrum.png",dpi=600)

#print

