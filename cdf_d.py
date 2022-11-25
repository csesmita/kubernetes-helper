import csv
import numpy as np
import collections
import random
from matplotlib import pyplot as plt, rcParams
from collections import defaultdict
from palettable.colorbrewer.qualitative import Set2_7
from bisect import bisect

colors = Set2_7.mpl_colors

###########################################################################
# The second part of the script analyzes the pod queue and scheduling times.
# Files have been generated from syslog files using the following command -
# python3 pods.py (taking syslog files as defined in pods.sh and temp.tr)
# Generates pod logs with the following format in d.3000 -
# Pod job89-p7xxb - SchedulerQueueTime 0.023927 SchedulingAlgorithmTime 0.000503 KubeletQueueTime 0.000363 Node "caelum-507" ExecutionTime 25.5900908177
###########################################################################
# Scheduler Algorithm and Queue times, and the execution times.
tct = []
tail_tct = []
#29.0950625  estimated_task_duration:  19  by_def:  0  total_job_running_time:  29.0015 job_start: 0.09356249999999999 job_end: 29.0950625 average TCT 19.0950625 tail TCT 29.0950625
with open("/home/sv440/Android/eagle/simulation/s.14.10X.tail_analysis",'r') as f:
    for line in f:
        if "Total time elapsed in the DC" in line:
            continue
        tct.append(float((line.split("average TCT")[1]).split()[0]))
        tail_tct.append(float((line.split("tail TCT")[1]).split()[0]))

count_tasks = collections.defaultdict(int)
c_job_xt_list=collections.defaultdict(float)
with open("results/pods/pods.c.10000J.400X.50N.YH.2",'r') as f:
    for line in f:
        if "SchedulerQueueTime" not in line:
            continue
        r = line.split()
        xt = float(r[12])
        jobname = r[1].split("-")[0]
        c_job_xt_list[jobname] += xt
        count_tasks[jobname] += 1

for jobname, num_tasks in count_tasks.items():
    c_job_xt_list[jobname] /= num_tasks

params = {
   'axes.labelsize': 8,
   'font.size': 8,
   'legend.fontsize': 8.5,
   'xtick.labelsize': 8,
   'ytick.labelsize': 8,
   'text.usetex': False,
   'figure.figsize': [6, 3.6]
}
rcParams.update(params)

#CDF of tail tasks.
fig = plt.figure()
#Take the list of average task completions per job. Sort them. Plot as CDF.
c = np.sort(tct)
cp = 1. * np.arange(len(c)) / (len(c) - 1)
plt.plot(c, cp, label="TCT averaged per job", linewidth=2, color=colors[0], alpha=0.5, marker='d', markersize=3)
c = np.sort(tail_tct)
cp = 1. * np.arange(len(c)) / (len(c) - 1)
plt.plot(c, cp, label="Tail TCT", linewidth=2, color=colors[1], alpha=0.5, marker='o', markersize=3)
c_xt_list = list(c_job_xt_list.values())
c = np.sort(c_xt_list)
cp = 1. * np.arange(len(c)) / (len(c) - 1)
plt.plot(c, cp, label="Total task execution times averaged per job", linestyle=':', linewidth=2, color=colors[2])
plt.xlabel('Time Elapsed [seconds]')
plt.ylabel('CDF')
legend = plt.legend()
frame = legend.get_frame()
frame.set_facecolor('1.0')
frame.set_edgecolor('1.0')
plt.ylim(0.0, 1.1)
plt.xticks(np.arange(0, 60001, 30000))
#plt.show()
fig.tight_layout()
fig.savefig('sparrow_task_completion_time.pdf', dpi=fig.dpi, bbox_inches='tight')
print("Completion time across all tasks", np.percentile(tct,50))
print("Completion time across tail tasks", np.percentile(tail_tct, 50))
