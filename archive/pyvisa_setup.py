import pyvisa
import time
import numpy as np
import matplotlib.pyplot as plt

rm = pyvisa.ResourceManager()
rm.list_resources() # prints the available instruments (the oscilloscope in our case)

scope = rm.open_resource("USB::0x0699::0x0412::C010259::INSTR")
print("Oscilloscope Identity:", scope.query("*IDN?")) # retrieves the identity of the oscilloscope

scope.write('header 0')
scope.write('data:encdg SRIBINARY')
scope.write('data:source CH1') # channel
scope.write('data:start 1') # first sample
record = int(scope.query('horizontal:recordlength?'))
scope.write('data:stop {}'.format(record)) # last sample
scope.write('wfmoutpre:byt_n 1') # 1 byte per sample

# acq config
scope.write('acquire:state 0') # stop
scope.write('acquire:stopafter SEQUENCE') # single
scope.write('acquire:state 1') # run
t5 = time.perf_counter()
r = scope.query('*opc?') # sync
t6 = time.perf_counter()
print('acquire time: {} s'.format(t6 - t5))

# data query
t7 = time.perf_counter()
bin_wave = scope.query_binary_values('curve?', datatype='b', container=np.array)
t8 = time.perf_counter()
print('transfer time: {} s'.format(t8 - t7))

# retrieve scaling factors
tscale = float(scope.query('wfmoutpre:xincr?'))
tstart = float(scope.query('wfmoutpre:xzero?'))
vscale = float(scope.query('wfmoutpre:ymult?')) # volts / level
voff = float(scope.query('wfmoutpre:yzero?')) # reference voltage
vpos = float(scope.query('wfmoutpre:yoff?')) # reference position (level)

# error checking
r = int(scope.query('*esr?'))
print('event status register: 0b{:08b}'.format(r))
r = scope.query('allev?').strip()
print('all event messages: {}'.format(r))

scope.close()
rm.close()

# create scaled vectors
# horizontal (time)
total_time = tscale * record
tstop = tstart + total_time
scaled_time = np.linspace(tstart, tstop, num=record, endpoint=False)
# vertical (voltage)
unscaled_wave = np.array(bin_wave, dtype='double') # data type conversion
scaled_wave = (unscaled_wave - vpos) * vscale + voff

# plotting
plt.plot(scaled_time, scaled_wave)
plt.title('channel 1') # plot label
plt.xlabel('time (seconds)') # x label
plt.ylabel('voltage (volts)') # y label
print("look for plot window...")
plt.show()

print("\nend of demonstration")
