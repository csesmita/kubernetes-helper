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

dirname='/home/sv440/Android/eagle/simulation/results_new/queue_reordering/'
speedup = ['1X', '10X', '100X', '1000X']
jct_50p_schemes_per_speedup = {}
jct_99p_schemes_per_speedup = {}
system = ["fcfs-fcfs", "fcfs-srpt", "sjf-srpt", "sjfwf-srpt"]
#Each contains 5 runs.
for speedup_dir in os.listdir(dirname):
    if not os.path.isdir(os.path.join(dirname,speedup_dir)):
        continue
    #an array of 4 elements - fcfs-fcfs, fcfs-srtp, sjf-srpt, sjfwf-srpt
    jct_50p_schemes_per_speedup[speedup_dir] = defaultdict(list)
    jct_99p_schemes_per_speedup[speedup_dir] = defaultdict(list)
    sub_dir = speedup_dir + "/" + "10S" + "/" + "slots=3"
    for filename in os.listdir(os.path.join(dirname, sub_dir)):
        index = -1
        if "fcfs-fcfs" in filename:
            index = 0
        if "fcfs-srpt" in filename:
            index = 1
        if "sjf-srpt" in filename:
            index = 2
        if "sjfwf-srpt" in filename:
            index = 3
        jct=[]
        with open(os.path.join(dirname, sub_dir, filename), 'r') as infile:
            for line in infile:
                if "estimated_task_duration:" not in line:
                    continue
                line = line.split()
                completion_time = float(line[6])
                jct.append(completion_time)
        jct_50p_schemes_per_speedup[speedup_dir][index].append(np.percentile(jct, 50))
        jct_99p_schemes_per_speedup[speedup_dir][index].append(np.percentile(jct, 99))
    #print("JCT percentiles for ",num_sched_dir,"is",jct_50p_schemes_per_scheduler[num_sched_dir], jct_99p_schemes_per_scheduler[num_sched_dir])

xsize=np.arange(len(speedup))
fig, ax1 = plt.subplots()
labels=[]
width=0.15
distance = 0.75
base = []
for index in range(4):
    mean = []
    std = []
    for speedup_dir in speedup:
        mean.append(np.mean(jct_50p_schemes_per_speedup[speedup_dir][index]))
        std.append(np.std(jct_50p_schemes_per_speedup[speedup_dir][index]))
    ax1.bar(xsize*distance+width/2 + index*width, mean, yerr=std,width=width, label=system[index], color=colors[index], capsize=2)
    if index == 0:
        base = mean
    else:
        system_labels = [i/j for i,j in zip(mean,base)]
        labels.extend(system_labels)

ax1.set_xlabel("Arrival Rate")
ax1.set_ylabel("Job Completion Time (s)")
xsize = [i*distance + 4*width/2 for i in xsize]
ax1.set_xticks(xsize)
ax1.legend(ncol=4)
ax1.set_xticklabels([str(n) for n in speedup])
#Labels on other bars
rects = ax1.patches[4:15]
for rect,label in zip(rects, labels):
    height = rect.get_height()
    ax1.text(rect.get_x() + rect.get_width() / 2, height + 80, "{:.2f}".format(label), ha="center", va="bottom", fontsize='x-small')
fig.savefig('reordering_50p_vs_speedup.pdf', dpi=fig.dpi, bbox_inches='tight')
