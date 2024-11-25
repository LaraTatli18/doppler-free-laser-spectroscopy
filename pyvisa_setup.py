import pyvisa
import time

rm = pyvisa.ResourceManager()
rm.list_resources() # prints the available instruments (the oscilloscope in our case)

#my_oscilloscope = rm.open_resource("name of oscilloscope here")
#print(my_oscilloscope.query("*IDN?")) # retrieves the identity of the oscilloscope






