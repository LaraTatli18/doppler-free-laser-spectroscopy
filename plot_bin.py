import matplotlib.pyplot as plt
import numpy as np

y_data=np.fromfile("data\ch1.bin",dtype='int8')
x_data=np.arange(0,len(y_data),1)

print(len(y_data))

plt.scatter(x_data,y_data)

plt.show()