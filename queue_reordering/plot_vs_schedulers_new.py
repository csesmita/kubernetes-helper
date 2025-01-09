from matplotlib import pyplot as plt, rcParams
import numpy as np
from palettable.colorbrewer.qualitative import Set2_7 
import os
from collections import defaultdict 

#colors = Pastel2_7.mpl_colors
colors = Set2_7.mpl_colors
params = {
   'axes.labelsize': 14,
   #'font.size': 10,
   'legend.fontsize': 14,
   'xtick.labelsize': 14,
   'ytick.labelsize': 14,
   'text.usetex': False,
   'figure.figsize': [4.8, 3.6]
}
rcParams.update(params)

dirname='/home/sv440/Android/eagle/simulation/results_new/queue_reordering/1000X/1S/slots=3'
jct_schemes_per_scheduler = defaultdict(list)
system = ["fcfs-fcfs", "fcfs-srpt", "sjf-srpt", "lrtf-srpt", "srjf-srpt"]
#Each contains 5 runs.
for filename in os.listdir(dirname):
    #an array of 5 elements - fcfs-fcfs, fcfs-srtp, sjf-srpt, lrtf-srpt, srjf-srpt
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
    with open(os.path.join(dirname, filename), 'r') as infile:
        for line in infile:
            if "estimated_task_duration:" not in line:
                continue
            line = line.split()
            completion_time = float(line[6])
            jct.append(completion_time)
    jct_schemes_per_scheduler[index].append(jct)
fig, ax1 = plt.subplots()
labels=[]
width=0.15
distance = 0.9
base = []
for index in range(5):
    mean = np.mean(jct_schemes_per_scheduler[index], axis=0)
    std = np.std(jct_schemes_per_scheduler[index], axis=0)
    x = range(len(mean))
    #Plot the mean of the runs
    ax1.plot(x,mean, label=system[index], color=colors[index])
    #Plot the std
    ax1.fill_between(x,mean+std, mean-std, facecolor=colors[index], alpha=0.4)

ax1.set_xlabel("Jobs")
ax1.set_ylabel("Job Completion Time (10000s)")
ax1.set_xticks([0,5000, 10000])
ax1.set_yticks([0,50000,100000,150000, 200000, 250000])
ax1.set_yticklabels(['0','5', '10', '15', '20', '25'])
ax1.legend(ncol=2, loc='upper left')
fig.savefig('reordering_vs_schedulers_1S.pdf', dpi=fig.dpi, bbox_inches='tight')
