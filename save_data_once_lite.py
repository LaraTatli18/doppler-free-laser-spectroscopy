import pyvisa
import numpy as np
import matplotlib.pyplot as plt

#the number of data points to collect
N_POINTS=5000000

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

#tell the osciliscope what data we would like
scope.write('data:source CH1') # read CH1
scope.write('data:start 1') # the first data point transfered (this is 1 indexed)
scope.write('data:stop {}'.format(N_POINTS)) # tell the osciliscope to transfer n points
scope.write('wfmoutpre:byt_nr 1') # 1 bytes per sample this beats the acuracy of the osciliscope 
scope.write('header 1') # turns on the waveform data

#get the waveform data
waveform_data=scope.query('WFMOutpre?')

#get the actual data
scope.query_binary_values('curve?', datatype='i', container=np.array)
# the data is represented as an array of signed two byte integers where the integer represents which discrete voltage level the reading is
# time values are not given instead they are assuemd to be evenly ditributed

# error checking
r = int(scope.query('*esr?'))
print('event status register: 0b{:08b}'.format(r))
r = scope.query('allev?').strip()
print('all event messages: {}'.format(r))

#close the conection
print("closing the conection")
scope.close()
rm.close()

#save the binary data 
print("saving file to \data")
bin_wave.tofile("data\ch1.bin")

#save the scaling data in seperate value so that we can convert later
f = open("data\paramiters.txt", "a")
f.write(waveform_data)
f.close()