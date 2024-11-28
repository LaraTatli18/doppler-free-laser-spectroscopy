import pyvisa
import numpy as np
import time
import matplotlib.pyplot as plt

#the number of data points to collect
N_POINTS=5000000
N_MEASUREMENTS=100

#prints a tupple of all conected devices
rm = pyvisa.ResourceManager()
rl=rm.list_resources()
print("connected devices:",rl)

adress = rl[0] #"USB::0x0699::0x0412::C010259::INSTR"

#connect to the osciliscope
print("attempting to conect to",adress)
scope = rm.open_resource(adress)
print("succesfully conected to", scope.query("*IDN?"))

#get the data
print("getting data")

#calculate the period
r = scope.query('*opc?')
print("trig freq =", scope.query('trigger:frequency?')[18:].strip())
frequency=float(scope.query('trigger:frequency?')[18:].strip())
T=1/frequency

print("period =", T)
print("freq =", frequency)

T=0.2
print("\testimated time:", T*N_MEASUREMENTS)
for i in range(N_MEASUREMENTS):
    print("\ttaking {}th measurement".format(i))

    #wait for one period so that we know its fresh data
    time.sleep(T)

    #measure CH1 data
    scope.write('data:source CH1')
    scope.write('data:start 1')
    scope.write('horizontal:recordlength {}'.format(N_POINTS))
    scope.write('data:stop {}'.format(N_POINTS))
    scope.write('wfmoutpre:byt_nr 1')
    scope.write('header 1')

    waveform_data=scope.query('WFMOutpre?')
    bin_wave=scope.query_binary_values('curve?', datatype='i', container=np.array)
    
    bin_wave.tofile("data\ch1_{}.bin".format(i))

    f = open("data\ch1_paramiters.txt", "a")
    f.write(waveform_data)
    f.close()

    #measure CH2 data
    scope.write('data:source CH2')
    scope.write('data:start 1')
    scope.write('horizontal:recordlength {}'.format(N_POINTS))
    scope.write('data:stop {}'.format(N_POINTS))
    scope.write('wfmoutpre:byt_nr 1')
    scope.write('header 1')

    waveform_data=scope.query('WFMOutpre?')
    scope.query_binary_values('curve?', datatype='i', container=np.array)

    bin_wave.tofile("data\ch2_{}.bin".format(i))

    f = open("data\ch2_paramiters.txt", "a")
    f.write(waveform_data)
    f.close()

    


#close the conection
print("closing the conection")
scope.close()
rm.close()