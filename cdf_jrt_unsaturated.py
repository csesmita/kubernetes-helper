import csv
import numpy as np
import collections
import random
from matplotlib import pyplot as plt, rcParams
from collections import defaultdict
from palettable.colorbrewer.qualitative import Pastel2_7
from bisect import bisect
import os

import matplotlib
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42


colors = Pastel2_7.mpl_colors
params = {
   'axes.labelsize': 14,
   'font.size': 12,
   'legend.fontsize': 12,
   'xtick.labelsize': 16,
   'ytick.labelsize': 16,
   'text.usetex': False,
   'figure.figsize': [4.2, 1.8]
   #'figure.figsize': [10,4.5]
}
rcParams.update(params)


systems=["Murmuration", "Kubernetes"]
linestyle=["dashed", "solid"]
#speedup = ".70X."
speedups = [".50X.", ".60X.", ".70X."]
jct_speedups = defaultdict(list)
jct_systems = defaultdict()
dirname="./results/jrt/unsaturated"
for speedup in speedups:
    for filename in os.listdir(dirname):
        if not speedup in filename:
            continue
        if "utilization." in filename or "syslog." in filename or "pods." in filename:
            continue
        if filename.startswith("c."):
            system = 1
        if filename.startswith("d."):
            system = 0
        jct=[]
        with open(os.path.join(dirname, filename), 'r') as infile:
            print(filename)
            for line in infile:
                if "has JRT" not in line:
                    continue
                line = line.split()
                completion_time = float(line[6])
                jct.append(completion_time)
        jct.sort()
        if len(jct) > 0:
            print(speedup, " - System", systems[system],np.percentile(jct,50), np.percentile(jct,100))
            jct_systems[system] = jct
            if speedup not in jct_speedups.keys():
                jct_speedups[speedup] = {}
            jct_speedups[speedup][system] = jct

    fig, ax1 = plt.subplots()
    for system in reversed(range(2)):
        a = np.sort(jct_systems[system])
        ap = 1. * np.arange(len(a)) / (len(a) - 1)
        ax1.plot(a, ap, label=systems[system], color=colors[system], linewidth=3, linestyle=linestyle[system])
    ax1.set_xlabel("Duration (seconds)")
    #ax1.set_ylabel("CDF")
    ax1.set_yticks([0.0, 0.5, 1.0])
    ax1.set_xticks([0, 25000, 50000])
    legend = ax1.legend(loc='lower right')
    frame = legend.get_frame()
    frame.set_facecolor('1.0')
    frame.set_edgecolor('1.0')
    name='undersaturated' + speedup +'pdf'
    fig.savefig(name, dpi=fig.dpi, bbox_inches='tight')

'''
## Box and whiskers plot
fig = plt.figure()

#Combine data on x-axis for box plot
data_combined_m = [jct_speedups[speedups[0]][0], jct_speedups[speedups[1]][0], jct_speedups[speedups[2]][0]]
data_combined_k = [jct_speedups[speedups[0]][1], jct_speedups[speedups[1]][1], jct_speedups[speedups[2]][1]]

colors_system_m = ['lightgreen', 'lightgreen', 'lightgreen']
colors_system_k = ['lightyellow', 'lightyellow', 'lightyellow']

box_m = plt.boxplot(data_combined_m, positions=np.array([0, 1, 2]) - 0.2, widths=0.4, labels=['60%', '70%', '80%'], patch_artist=True)
box_k = plt.boxplot(data_combined_k, positions=np.array([0, 1, 2]) + 0.2, widths=0.4, labels=['60%', '70%', '80%'], patch_artist=True)


for b, color in zip (box_m['boxes'], colors_system_m):
    b.set_facecolor(color)
for b, color in zip (box_k['boxes'], colors_system_k):
    b.set_facecolor(color)
for flier in box_m['fliers']:
    flier.set(marker='o', markerfacecolor='tab:green', markeredgecolor='tab:green',  markersize=2)
for flier in box_k['fliers']:
    flier.set(marker='o', markerfacecolor='tab:red', markeredgecolor='tab:red',  markersize=2)

# Set the y-axis label and limits
plt.ylabel("Duration (seconds)")
plt.ylim(0, 52000)
plt.legend([box_m['boxes'][0], box_k['boxes'][0]], ['Murmuration', 'Kubernetes'], loc='upper right', framealpha=0.9)

# Set the x-axis label
plt.xticks([0, 1, 2], ['100tps (60%)', '120tps (70%)', '140tps (80%)'])
plt.xlabel("Arrival Rates (Utilisation)")

# Add a title
#plt.title("JCT Distribution at lower arrival rates")

# Show grid
plt.grid()

name="combined_util.pdf"
fig.savefig(name, dpi=fig.dpi, bbox_inches='tight')
'''
