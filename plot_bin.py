import matplotlib.pyplot as plt
import numpy as np

y_data=np.fromfile("data\ch1.bin",dtype='d')
x_data=np.arange(0,len(y),1)

plt.scatter(y_data)