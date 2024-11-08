import numpy as np
import matplotlib.pyplot as plt

xs=np.linspace(-3,3,1000)
yas=1-np.exp(-xs**2)
ybs=yas+0.6*np.exp(-(10*xs)**2)

fig, axs = plt.subplots(3,sharey=True)
axs[0].plot(xs, yas)
axs[1].plot(xs, ybs)
axs[2].plot(xs, ybs-yas)

for ax in axs:
	ax.set_xticks([])
	ax.set_yticks([])

fig.supxlabel("Frequency")
fig.supylabel("Intensity")

plt.savefig("example graph.png")