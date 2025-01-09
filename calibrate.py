from header import *

def calibrate(data, graphic=False):

    GROUP_SIZE=100
    N_GROUPS=N_POINTS//GROUP_SIZE

    grouped_data=group(data, N_GROUPS, GROUP_SIZE)

    #truncate the calibration data
    i=18000
    f=75000
    truncated_grouped_data=grouped_data[:,i//GROUP_SIZE:f//GROUP_SIZE]
        
    def fit3(t,A,A_0,phi_0,phi_1,C0,C1):
        y=(A+A_0*t)*(np.sin(phi_1*t+phi_0))+(C1*t+C0)
        return y

    p03=[5.2,0, 1, 0.00044, 15, -0.0002]

    paramiters3=uarray(np.zeros((N_RUNS, len(p03))),np.zeros((N_RUNS, len(p03))))

    print(i,f)

    print(len(np.arange(i,f,GROUP_SIZE)),len(unp.nominal_values(truncated_grouped_data[0])))

    for run in range(100):
        popt,pcov=curve_fit(
            f=fit3,
            xdata=np.arange(i,f,GROUP_SIZE),
            ydata=unp.nominal_values(truncated_grouped_data[run]),
            p0=p03,
            sigma=unp.std_devs(truncated_grouped_data[run]),
            absolute_sigma=True,
            maxfev=10000000
        )
        paramiters3[run]=uncrt.correlated_values(popt,pcov)


    def fit(t,A,A_1,phi_0,phi_1,phi_2,C0,C1,C2,t_0,t_1):
    #y=A*(np.sin(phi_2*t**2+phi_1*t+phi_0))+(C2*t**2+C1*t+C0)
        y=(A+A_1*t)*np.sin(phi_0+phi_1*np.sqrt((t-t_0)**2+phi_2))+C0+C1*np.sqrt((t-t_1)**2+C2**2)
        return y

    def fite(t,A,A_1,phi_0,phi_1,phi_2,C0,C1,C2, t_0, t_1):
        return (A+A_1*t)*unp.sin(phi_0+phi_1*unp.sqrt((t-t_0)**2+phi_2))+C0+C1*unp.sqrt((t-t_1)**2+C2**2)

    p0=[5.2, 0, 4, 0.00044, 1000000, 15, -0.00038, 10000,10000,10000]
    P0=np.zeros((N_RUNS, len(p0)))
    for j in range(N_RUNS):
        P0[j]=p0

    P0[:,0]=unp.nominal_values(paramiters3[:,0])
    P0[:,1]=unp.nominal_values(paramiters3[:,1])
    #P0[:,2]=unp.nominal_values(paramiters3[:,2])
    P0[:,3]=unp.nominal_values(paramiters3[:,3])

    P0[:,5]=unp.nominal_values(paramiters3[:,4])
    P0[:,6]=unp.nominal_values(paramiters3[:,5])


    paramiters=uarray(np.zeros((N_RUNS, len(p0))),np.zeros((N_RUNS, len(p0))))

    for run in range(100):
        popt,pcov=curve_fit(
            f=fit,
            xdata=np.arange(i,f,GROUP_SIZE),
            ydata=unp.nominal_values(truncated_grouped_data[run]),
            p0=P0[run],
            sigma=unp.std_devs(truncated_grouped_data[run]),
            absolute_sigma=True,
            maxfev=1000000000
        )
        paramiters[run]=uncrt.correlated_values(popt,pcov)

        #check chi squared
        reduced_chi_squared=np.sum((fite(np.arange(i,f,GROUP_SIZE),*paramiters[run])-truncated_grouped_data[run])**2/unp.std_devs(truncated_grouped_data[run])**2)/(len(np.arange(i,f,GROUP_SIZE))-len(p0))

        if(reduced_chi_squared>2):
            print("Warning high reduced chi_squared value:",reduced_chi_squared)
        if(reduced_chi_squared<0.5):
            print("Warning low reduced chi_squared value:",reduced_chi_squared)


    L1=ufloat(0.075,0.003)
    L2=ufloat(0.37,0.002)


    p2=ufloat(0,0)
    p3=ufloat(0,0)

    for j in range(N_RUNS):
        p2+=paramiters[j,2]
        p3+=paramiters[j,3]

    p2=p2/N_RUNS
    p3=p3/N_RUNS

    def d(t,i,paramiters=paramiters):
        #return constants.c*(p2*t+p3*t**2)/(4*np.pi*(L1-L2))*10**(-9)
        phi_1=paramiters[i,3]
        phi_2=paramiters[i,4]
        t_0=paramiters[i,8]
        return phi_1*unp.sqrt((t-t_0)**2+phi_2)


    print("  Calibration Complete\n")
    return d
