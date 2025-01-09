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
d_tct = []
d_tail_tct = []
d_tail_tct_by_x = []
#29.0950625  estimated_task_duration:  19  by_def:  0  total_job_running_time:  29.0015 job_start: 0.09356249999999999 job_end: 29.0950625 average TCT 19.0950625 tail TCT 29.0950625
with open("/home/sv440/Android/eagle/simulation/results/sparrow_tail/s.14.10X.tail_analysis",'r') as f:
    for line in f:
        if "Total time elapsed in the DC" in line:
            continue
        d_tct.append(float((line.split("average TCT")[1]).split()[0]))
        d_tail_tct_this = float((line.split("tail TCT")[1]).split()[0])
        d_tail_tct.append(d_tail_tct_this)
        est = float((line.split("estimated_task_duration:")[1]).split()[0])
        if est > 0:
            d_tail_tct_by_x.append(d_tail_tct_this / est)

c_tct = []
c_tail_tct = []
c_tail_tct_by_x = []
with open("results/pods/pods.c.10000J.400X.50N.YH.2",'r') as f:
    for line in f:
        if "SchedulerQueueTime" not in line:
            continue
        r = line.split()
        sq = float(r[4])
        sa = float(r[6])
        xt = float(r[12])
        tc = float((line.split("TaskCompletionTime")[1]).split()[0])
        c_tct.append(tc)

        if "TAIL TASK" in line:
            c_tail_tct_by_x.append(tc / xt)
            c_tail_tct.append(tc)

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
c = np.sort(c_tail_tct_by_x)
cp = 1. * np.arange(len(c)) / (len(c) - 1)
plt.plot(c, cp, label="Kubernetes TCT/x per job", linewidth=2, color=colors[0], alpha=0.5, marker='d', markersize=3)
c = np.sort(d_tail_tct_by_x)
cp = 1. * np.arange(len(c)) / (len(c) - 1)
plt.plot(c, cp, label="Sparrow TCT/x per job", linewidth=2, color=colors[1], alpha=0.5, marker='o', markersize=3)
plt.xlabel('Duration in logarithmic scale (seconds)')
plt.ylabel('CDF')
plt.xscale('log')
legend = plt.legend()
frame = legend.get_frame()
frame.set_facecolor('1.0')
frame.set_edgecolor('1.0')
plt.ylim(0.0, 1.1)
#plt.xticks(np.arange(0, 60001, 30000))
#plt.show()
fig.tight_layout()
fig.savefig('cd_compare.pdf', dpi=fig.dpi, bbox_inches='tight')
