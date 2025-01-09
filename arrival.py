import matplotlib.pyplot as plt
import sys
from math import ceil
import numpy as np
from palettable.colorbrewer.qualitative import Set2_7
from matplotlib import pyplot as plt, rcParams

colors = Set2_7.mpl_colors
params = {
   'axes.labelsize': 12,
   'font.size': 12,
   'legend.fontsize': 12,
   'xtick.labelsize': 12,
   'ytick.labelsize': 12,
   'text.usetex': False,
   #'figure.figsize': [10, 3]
}
rcParams.update(params)

num_workloads = len(sys.argv[1:])
fig=plt.figure()
for i in range(num_workloads):
    arrival = []
    f = open(sys.argv[i+1], 'r')
    start_time = 0
    for row in f:
        row = row.split(' ')
        next_time = float(row[0])
        arrival.append(next_time - start_time)
        start_time = next_time
    f.close()
    d = np.sort(arrival)
    dp = 1. * np.arange(len(d)) / (len(d) - 1)
    #Show CDF
    plt.plot(d, dp, label=sys.argv[1+i], color=colors[i])
    print("50th percentile: ",  np.percentile(arrival, 50))
    print("90th percentile: ",  np.percentile(arrival, 90))
    print("99th percentile: ",  np.percentile(arrival, 99))

plt.xlabel('Inter-Arrival Delay (s)')
plt.ylabel('CDF')
plt.xscale('log')
plt.minorticks_off()
plt.legend()
fig.tight_layout()
fig.savefig('arrivals.pdf', dpi=fig.dpi, bbox_inches='tight')

