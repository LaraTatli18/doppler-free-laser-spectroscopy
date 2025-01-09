from header import *
from calibrate import calibrate

print("\n")

#load in the data
data,calibration=load("Data\Zeeman Data\data_z5\\")


d=calibrate(calibration)

GROUP_SIZE=10
N_GROUPS=N_POINTS//GROUP_SIZE

#group the data
grouped_data=group(data,N_GROUPS,GROUP_SIZE)

print("Creating first graph")

def scale_time(t):
    return 2*10**(-6)*t+-93*10**(-3)

def scale_voltage(v):
    return 400*10**(-6)*v

#layout
fig, axs = plt.subplots(2,2,figsize=(20,10))
gs = axs[1, 1].get_gridspec()
for ax in axs[0, :]:
    ax.remove()
axbig = fig.add_subplot(gs[0, :])

#add the colour bar
fig.colorbar(cm.ScalarMappable(cmap='hsv'),ax=axbig,label="Run",ticks=[1,10,20,30,40,50,60,70,80,90,100],boundaries=np.linspace(0.5,100.5,101),values=np.linspace(0,0.99,100),fraction=0.05,pad=0.03)

#the full spectrum
for i in range(100):
    spec=scale_voltage(unp.nominal_values(grouped_data[i,3000:7500]))
    col=hsv_to_rgb((i/100,0.8,0.8))
    axbig.scatter(scale_time(np.arange(3000,7500)*GROUP_SIZE),spec,s=0.2,color=col)

for i in range(100):
    spec=scale_voltage(unp.nominal_values(grouped_data[i,6100:7000]))
    col=hsv_to_rgb((i/100,0.8,0.8))
    axs[1,0].scatter(scale_time(np.arange(6100,7000)*GROUP_SIZE),spec,s=0.2,color=col)

for i in range(100):
    spec=scale_voltage(unp.nominal_values(grouped_data[i,3800:4300]))
    col=hsv_to_rgb((i/100,0.8,0.8))
    axs[1,1].scatter(scale_time(np.arange(3800,4300)*GROUP_SIZE),spec,s=0.2,color=col)

axbig.set_xlabel("time (s)")
axs[1,0].set_xlabel("time (s)")
axs[1,1].set_xlabel("time (s)")
axbig.set_ylabel("Voltage(V)")
axs[1,0].set_ylabel("Voltage(V)")
axs[1,1].set_ylabel("Voltage(V)")

fig.tight_layout()

fig.savefig("all_doppler_free.png",dpi=300)

#layout

print("combining data")
offset=[]

for i in range(100):
    spec=unp.nominal_values(grouped_data[i,3000:7500])
    peaks,properties=find_peaks(spec,prominence=1,distance=10)
    peak_order=np.argsort(properties["prominences"])
    offset.append((peaks[peak_order[-6:]]+3000)*GROUP_SIZE)




offset=np.sort(np.array(offset))


zero=np.mean(offset,axis=0)

ms=[]
cs=[]

def line(x,m,c):
    return m*x+c

for i in range(100):
    popt,pcov=curve_fit(
        f=line,
        xdata=zero,
        ydata=offset[i]
    )
    ms.append(popt[0])
    cs.append(popt[1])

def shift(t,i,ms=np.array(ms),cs=np.array(cs)):
    return (t-cs[i])/ms[i]

print("creating second graph")

fig, axs = plt.subplots(2,2,figsize=(20,10))
gs = axs[1, 1].get_gridspec()
for ax in axs[0, :]:
    ax.remove()
axbig = fig.add_subplot(gs[0, :])


for i in range(100):
    spec=unp.nominal_values(grouped_data[i,3000:7500])
    col=hsv_to_rgb((i/100,0.8,0.8))
    peaks,properties=find_peaks(spec,prominence=1)
    peak_order=np.argsort(properties["prominences"])
    offset[i]=peaks[peak_order[-1]]





ts=[]
vs=[]
for i in range(N_RUNS):
    vs+=list(unp.nominal_values(data[i]))
    ts+=list(shift(np.arange(0,N_POINTS),i))

ts=np.array(ts)
vs=np.array(vs)

order=np.argsort(ts)

ts=ts[order]
vs=vs[order]

ts=ts[3000000:7500000]
vs=vs[3000000:7500000]

bin_width=np.abs((ts[0]-ts[-1])/4500)
start=ts[0]

gts=[[]]
gvs=[[]]

for i,t in enumerate(ts):
    if t<start+bin_width:
        gts[-1].append(t)
        gvs[-1].append(vs[i])
    else:
        start+=bin_width
        gts.append([t])
        gvs.append([vs[i]])

t=[]
v=[]
for i,st in enumerate(gts):
    t.append(ufloat_from_sample(st))
    v.append(ufloat_from_sample(gvs[i]))

t=np.array(t)
v=np.array(v)

t= unp.nominal_values(d(np.array(t)-zero[3]))
t_e= unp.std_devs(d(np.array(t)-zero[3]))
v=v-v[np.argmin(unp.nominal_values(v))]
v=v/v[np.argmax(unp.nominal_values(v))]

v_e=unp.std_devs(v)
v=unp.nominal_values(v)

#plot big one
axbig.scatter(t,v,s=2)

#fitting stuff
def lorenz(x,A,x0,gamma):
    return A/((1+((x-x0)/gamma)**2))

def fit(x,*p):
    y=0
    for i in range(6):
        y+=lorenz(x,p[3*i+0],p[3*i+1],p[3*i+2])
    y+=p[18]
    return y


f=[]

p0=[0.1, 0.8250, 0.01,
    0.25, 0.84135552, 0.01364581,
    0.2, 0.85359433, 0.00662299,
    0.35, 0.8676879,  0.0093215,
    0.53, 0.88055458, 0.00800642,
    0.32, 0.9080054,  0.00888442,
    0.1]

popt,pcov=curve_fit(
    f=fit,
    xdata=t[800:1300],
    ydata=v[800:1300],
    p0=p0,
    maxfev=10**8
)

As=list(popt[0:18:3])
fs=list(popt[1:18:3])
gammas=list(popt[2:18:3])

for i in range(6):
    f.append(popt[3*i+1])
    axs[1,1].plot([f[-1],f[-1]],[0.1,0.8],linestyle='--')

p0=[0.1, -0.13, 0.01,
    0.25, -0.09, 0.01364581,
    0.2, -0.065, 0.00662299,
    0.35, -0.035,  0.0093215,
    0.53, 0, 0.00800642,
    0.32, 0.07,  0.00888442,
    0.1]

popt,pcov=curve_fit(
    f=fit,
    xdata=t[3100:4000],
    ydata=v[3100:4000],
    p0=p0,
    maxfev=10**8
)

As+=list(popt[0:18:3])
fs+=list(popt[1:18:3])
gammas+=list(popt[2:18:3])

for i in range(6):
    f.append(popt[3*i+1])
    axs[1,0].plot([f[-1],f[-1]],[0.2,1.1],linestyle='--')


axs[1,0].errorbar(x=t[3100:4000],
                  y=v[3100:4000],
                  xerr=t_e[3100:4000],
                  yerr=v_e[3100:4000],
                  linestyle='',
                  marker='.')

#axs[1,1].plot(t[800:1300],fit(t[800:1300],*popt),color='C1')
axs[1,1].scatter(t[800:1300],v[800:1300],s=2)



axbig.set_xlabel("Detuning (GHz)")
axs[1,0].set_xlabel("Detuning (GHz)")
axs[1,1].set_xlabel("Detuning (GHz)")
axbig.set_ylabel("Relative intensity")
axs[1,0].set_ylabel("Relative intensity")
axs[1,1].set_ylabel("Relative intensity")

fig.tight_layout()

fig.savefig("combined_doppler_free.png",dpi=300)

#still need to calibrate axis and align based of all peaks not just one