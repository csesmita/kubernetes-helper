import csv
import numpy as np
import collections
import random
from matplotlib import pyplot as plt, rcParams
from collections import defaultdict
from palettable.colorbrewer.qualitative import Set2_7
from bisect import bisect
import os

colors = Set2_7.mpl_colors
params = {
   'axes.labelsize': 14,
   #'font.size': 10,
   'legend.fontsize': 14,
   'xtick.labelsize': 14,
   'ytick.labelsize': 14,
   'text.usetex': False,
   'figure.figsize': [6.4, 3.6]
}
rcParams.update(params)


jct_systems = defaultdict(list)
dirname="./results/ft/jrt/"
for filename in os.listdir(dirname):
    if "normal" in filename:
        system = 0
    else:
        system = 1
    jct=[]
    with open(os.path.join(dirname, filename), 'r') as infile:
        for line in infile:
            if "has JRT" not in line:
                continue
            line = line.split()
            completion_time = float(line[4])
            jct.append(completion_time)
    jct.sort()
    if len(jct) > 0:
        print("Processing", filename)
        jct_systems[system].append(jct)

fig, ax1 = plt.subplots()
systems=["No Failures", "Scheduler 1 Fails"]
for system in reversed(range(len(systems))):
    mean = np.mean(jct_systems[system], axis=0)
    std = np.std(jct_systems[system], axis=0)
    print(systems[system], "50th:",np.percentile(jct_systems[system],50),"99th:",np.percentile(jct_systems[system],99))
    print(mean)
    x = range(len(mean))
    #Plot the mean of the runs
    ax1.plot(x,mean, label=systems[system], color=colors[system], linewidth=2,  alpha=0.5, marker=">")
    #Plot the std
    ax1.fill_between(x,mean+std, mean-std, facecolor=colors[system], alpha=0.4)
ax1.set_xlabel("Number of Jobs")
ax1.set_ylabel("Job Completion Time (seconds)")
ax1.set_xlim(0)
#ax1.set_yticks([0,200, 400, 600])
ax1.legend()
fig.savefig('ftjct.pdf', dpi=fig.dpi, bbox_inches='tight')
