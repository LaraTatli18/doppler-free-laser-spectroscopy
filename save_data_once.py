import pyvisa
import time
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

#tell the osciliscope how we want the data  
scope.write('header 0') # no header (i think this is the part before the columns of data that descibes the setup of the osciliscope)
scope.write('data:encdg SRIBINARY') # encode the data as signed binary with the most signigicant byte transfered first
scope.write('data:start 1') # the first data point transfered (this is 1 indexed)
scope.write('horizontal:recordlength {}'.format(N_POINTS)) # tell the osciliscope to recored n points
scope.write('data:stop {}'.format(N_POINTS)) # tell the osciliscope to transfer n points
scope.write('wfmoutpre:byt_n 1') # 1 byte per sample (this is more precise than the ac->dc converion of the osciliscope)

#just for curiosity
print("\tnumber of points:",N_POINTS)
print("\tmax sample rate:",scope.query('CONFIGuration:ANALOg:maxsamplerate?'))

#tell osciliscope to aquire the data
print("\taquiring data")
scope.write('acquire:state 0') # stop
scope.write('acquire:stopafter SEQUENCE') # single
scope.write('acquire:state 1') # run

#transfer the data to the osciliscope
print("\ttransfering data")
scope.write('data:source CH1') # read CH1
bin_wave = scope.query_binary_values('curve?', datatype='b', container=np.array)
# the data is represented as an array of signed one byte integers where the integer represents which discrete voltage level the reading is
# time values are not given instead they are assuemd to be evenly ditributed

# retrieve scaling factors
xinc = float(scope.query('wfmoutpre:xincr?'))
xzero = float(scope.query('wfmoutpre:xzero?'))
xunit = float(scope.query('wfmoutpre:xunit?'))

ymlut = float(scope.query('wfmoutpre:ymult?'))
vzero = float(scope.query('wfmoutpre:yzero?'))
yunit = float(scope.query('wfmoutpre:yunit?'))

# error checking
r = int(scope.query('*esr?'))
print('event status register: 0b{:08b}'.format(r))
r = scope.query('allev?').strip()
print('all event messages: {}'.format(r))

#close the conection
print("closing the conection")
scope.close()
rm.close()

#save the file
print("saving file to \data")
bin_wave.tofile(".\data\ch1.bin")