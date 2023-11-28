from matplotlib import pyplot as plt, rcParams
import numpy as np
from palettable.colorbrewer.qualitative import Pastel2_7
import os
from collections import defaultdict 

colors = Pastel2_7.mpl_colors
params = {
   'axes.labelsize': 14,
   #'font.size': 10,
   'legend.fontsize': 12,
   'xtick.labelsize': 14,
   'ytick.labelsize': 14,
   'text.usetex': False,
   'figure.figsize': [6.4, 3.6]
}
rcParams.update(params)

dirname='/home/sv440/Android/eagle/simulation/results_new/queue_reordering/1000X/10S/'
subdirs=["slots=0", "slots=3"]
jct_50p_per_setup = {}
jct_99p_per_setup = {}
system = ["fcfs-fcfs", "fcfs-srpt", "sjf-srpt", "lrtf-srpt", "srjf-srpt"]
#Each contains 5 runs.
for subdir in subdirs:
    #an array of 5 elements - fcfs-fcfs, fcfs-srtp, sjf-srpt, lrtf-srpt, srjf-srpt
    jct_50p_per_setup[subdir] = defaultdict(list)
    jct_99p_per_setup[subdir] = defaultdict(list)
    for filename in os.listdir(os.path.join(dirname, subdir)):
        index = -1
        if "fcfs-fcfs" in filename:
            index = 0
        if "fcfs-srpt" in filename:
            index = 1
        if "sjf-srpt" in filename:
            index = 2
        if "lrtf-srpt" in filename:
            index = 3
        if "srjf-srpt" in filename:
            index = 4
        jct=[]
        with open(os.path.join(dirname, subdir, filename), 'r') as infile:
            for line in infile:
                if "estimated_task_duration:" not in line:
                    continue
                line = line.split()
                completion_time = float(line[6])
                jct.append(completion_time)
        jct_50p_per_setup[subdir][index].append(np.percentile(jct, 50))
        jct_99p_per_setup[subdir][index].append(np.percentile(jct, 99))
    #print("JCT percentiles for ",num_sched_dir,"is",jct_50p_schemes_per_scheduler[num_sched_dir], jct_99p_schemes_per_scheduler[num_sched_dir])
size = ["Homogeneous", "Heterogeneous"]
xsize=np.arange(len(size))
fig, ax1 = plt.subplots()
labels=[]
width=0.15
distance = 0.9
error_bar_heights=[]
base = []
for index in range(5):
    mean = []
    std = []
    for subdir in jct_99p_per_setup.keys():
        mean.append(np.mean(jct_99p_per_setup[subdir][index]))
        std.append(np.std(jct_99p_per_setup[subdir][index]))
    #print(mean, std)
    ax1.bar(xsize*distance+width/2 + index*width, mean, yerr=std,width=width, label=system[index], color=colors[index], capsize=2)
    if index == 0:
        base = mean
    else:
        system_labels = [i/j for i,j in zip(mean,base)]
        labels.extend(system_labels)
        error_bar_heights.extend(std)

ax1.set_xlabel("Setup Type")
ax1.set_ylabel("Job Completion Time (s)")
xsize = [i*distance + 5*width/2 for i in xsize]
ax1.set_xticks(xsize)
ax1.set_yticks([0,60000, 120000, 180000, 240000])
ax1.legend(ncol=2, loc='upper left')
ax1.set_xticklabels([str(n) for n in size])
#Labels on other bars
rects = ax1.patches[2:10]
for rect,label, err_height in zip(rects, labels, error_bar_heights):
    height = rect.get_height() + err_height
    ax1.text(rect.get_x() + rect.get_width() / 2, height, "{:.2f}".format(label), ha="center", va="bottom", fontsize='small')
fig.savefig('reordering_99p_vs_setup_10S.pdf', dpi=fig.dpi, bbox_inches='tight')
