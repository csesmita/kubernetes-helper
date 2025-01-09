from matplotlib import pyplot as plt, rcParams
import numpy as np
from palettable.colorbrewer.qualitative import Pastel2_7
import os
from collections import defaultdict 

colors = Pastel2_7.mpl_colors
params = {
   'axes.labelsize': 10,
   'font.size': 10,
   'legend.fontsize': 10,
   'xtick.labelsize': 10,
   'ytick.labelsize': 10,
   'text.usetex': False,
   'figure.figsize': [7.2, 3.6]
}
rcParams.update(params)

dirname='results/jct/'
system = ["Default Kubernetes", "Murmuration fcfs-fcfs", "Murmuration fcfs-srpt", "Murmuration sjf-srpt", "Murmuration sjfwf-srpt"]

fig, ax1 = plt.subplots()
for filename in os.listdir(dirname):
    with open(os.path.join(dirname, filename), 'r') as infile:
        index = -1
        if filename == "c.10000J.1000X.50N.YH":
            index = 0
        if filename == "d.10000J.1000X.50N.10S.YH":
            index = 1
        if filename == "d.10000J.1000X.50N.10S.YH.srpt":
            index = 2
        if filename == "d.10000J.1000X.50N.10S.YH.sjf-srpt":
            index = 3
        if filename == "d.10000J.1000X.50N.10S.YH.sjfwf-srpt":
            index = 4
        jct=[]
        for line in infile:
            if "has JRT" not in line:
                continue
            line = line.split()
            completion_time = float(line[6])
            jct.append(completion_time)
        jct = np.sort(jct)
        jct_ratio = 1. * np.arange(len(jct)) / (len(jct) - 1)
        ax1.plot(jct, jct_ratio, label=system[index], linewidth=2, color=colors[index])
        print(system[index], "JCT percentiles", np.percentile(jct, 50), np.percentile(jct, 99))

ax1.set_xlabel("Duration (s)")
ax1.set_ylabel("Job Completion Time (s)")
ax1.legend()
fig.savefig('cdf.pdf', dpi=fig.dpi, bbox_inches='tight')
