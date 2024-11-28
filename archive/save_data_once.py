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

#tell the osciliscope how we want the data  
scope.write('header 0') # no header (i think this is the part before the columns of data that descibes the setup of the osciliscope)
scope.write('data:encdg SRIBINARY') # encode the data as signed binary with the most signigicant byte transfered first (the order of the bytes doesnt matter because we are only using one byte)
scope.write('data:start 1') # the first data point transfered (this is 1 indexed)
scope.write('horizontal:recordlength {}'.format(N_POINTS)) # tell the osciliscope to recored n points
scope.write('data:stop {}'.format(N_POINTS)) # tell the osciliscope to transfer n points
scope.write('wfmoutpre:byt_n 1') # 1 bytes per sample this is the acuracy of the osciliscope 

#just for curiosity
print("\tnumber of points:",N_POINTS)
print("\tmax sample rate:",scope.query('CONFIGuration:ANALOg:maxsamplerate?'))

#tell osciliscope to aquire the data
print("\taquiring data")
scope.write('acquire:state 0') # stop
scope.write('acquire:stopafter SEQUENCE') # single
scope.write('acquire:state 1') # run

r = scope.query('*opc?')

#transfer the data to the osciliscope
print("\ttransfering data")
scope.write('data:source CH1') # read CH1
bin_wave = scope.query_binary_values('curve?', datatype='i', container=np.array)
# the data is represented as an array of signed one byte integers where the integer represents which discrete voltage level the reading is
# time values are not given instead they are assuemd to be evenly ditributed

# retrieve scaling factors
xzero = str(scope.query('wfmoutpre:xzero?'))
xincr = str(scope.query('wfmoutpre:xincr?'))
xunit = str(scope.query('wfmoutpre:xunit?'))

yzero = str(scope.query('wfmoutpre:yzero?'))
ymult = str(scope.query('wfmoutpre:ymult?'))
yunit = str(scope.query('wfmoutpre:yunit?'))

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
f = open("data\scaling_paramiters.txt", "a")
f.write("xzero: "+xzero)
f.write("\nxincr: "+xincr)
f.write("\nxunit: "+xunit)
f.write("\nyzero: "+yzero)
f.write("\nymult: "+ymult)
f.write("\nyunit: "+yunit)
f.close()