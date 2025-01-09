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
c_sq_list=[]
c_sa_list=[]
c_xt_list=[]

t_c_sq_list=[]
t_c_sa_list=[]
t_c_xt_list=[]

c_job_sq_list=collections.defaultdict(float)
c_job_sa_list=collections.defaultdict(float)
c_job_xt_list=collections.defaultdict(float)
c_job_completion_list=collections.defaultdict(float)

#Tail Tasks
t_c_job_sq_list=collections.defaultdict(float)
t_c_job_sa_list=collections.defaultdict(float)
t_c_job_xt_list=collections.defaultdict(float)
t_c_job_completion_list=collections.defaultdict(float)

t_c_queueaddtime = {}

c_pod_qt={}
count_tasks = collections.defaultdict(int)
#Pod job18-bl57n - SchedulerQueueTime 0.00192 SchedulingAlgorithmTime 0.000493 KubeletQueueTime 0.000207 Node "node28.sv440-128365.decentralizedsch-pg0.utah.cloudlab.us" ExecutionTime 500.37717814 NumSchedulingCycles 1 StartedAfterSec 5.45567 TAIL TASK
with open("results/pods/pods.c.5000J.200X.20N.YH",'r') as f:
    for line in f:
        if "SchedulerQueueTime" not in line:
            continue
        r = line.split()
        sq = float(r[4])
        sa = float(r[6])
        xt = float(r[12])
        tc = float((line.split("TaskCompletionTime")[1]).split()[0])

        podname = r[1]
        c_pod_qt[podname] = sq

        c_sq_list.append(sq)
        c_sa_list.append(sa)
        c_xt_list.append(xt)

        jobname = r[1].split("-")[0]
        c_job_sq_list[jobname] += sq
        c_job_sa_list[jobname] += sa
        c_job_xt_list[jobname] += xt
        c_job_completion_list[jobname] += tc
        count_tasks[jobname] += 1
        if "TAIL TASK" in line:
            t_c_sq_list.append(sq)
            t_c_sa_list.append(sa)
            t_c_xt_list.append(xt)
            t_c_job_sq_list[jobname] += sq
            t_c_job_sa_list[jobname] += sa
            t_c_job_xt_list[jobname] += xt
            t_c_queueaddtime[jobname] = float((line.split("QueueAddTime")[1]).split()[0])
            t_c_job_completion_list[jobname] = tc
'''
#CDF of tail tasks.
c = np.sort(t_c_sq_list)
cp = 1. * np.arange(len(c)) / (len(c) - 1)
#Show CDF
fig = plt.plot(c, cp, label="Queue Time for Tail Tasks")
c = np.sort(c_sq_list)
cp = 1. * np.arange(len(c)) / (len(c) - 1)
plt.plot(c, cp, label="Queue Time for All Tasks")
plt.xlabel('Queue Times')
plt.title('Scheduler Queue Times across Tasks')
plt.ylabel('CDF')
plt.legend()
#plt.show()
'''
print("Scheduler Queue time across all tasks", np.percentile(c_sq_list,50), np.percentile(c_sq_list,90), np.percentile(c_sq_list,99))
print("Scheduler Queue time across tail tasks", np.percentile(t_c_sq_list,50), np.percentile(t_c_sq_list,90), np.percentile(t_c_sq_list,99))
print("################")

params = {
   'axes.labelsize': 12,
   'font.size': 12,
   'legend.fontsize': 12,
   'xtick.labelsize': 12,
   'ytick.labelsize': 12,
   'text.usetex': False,
   #'figure.figsize': [10, 3.5]
}
rcParams.update(params)
#CDF of tail tasks.
for jobname, num_tasks in count_tasks.items():
    c_job_sq_list[jobname] /= num_tasks
    c_job_xt_list[jobname] /= num_tasks
    c_job_completion_list[jobname] /= num_tasks
#fig, (ax_jct, ax_tail)= plt.subplots(1,2)
fig, ax_jct = plt.subplots()
ax_jct.minorticks_off()
#print("Fig size", fig.get_size_inches())
c_xt_list = list(c_job_xt_list.values())
c = np.sort(c_xt_list)
cp = 1. * np.arange(len(c)) / (len(c) - 1)
ax_jct.plot(c, cp, label="Average x", linestyle=':', linewidth=2, color=colors[2])
#Take the list of average task completions per job. Sort them. Plot as CDF.
c_sq_list = list(c_job_sq_list.values())
t_c_sq_list = list(t_c_job_sq_list.values())
c = np.sort(c_sq_list)
cp = 1. * np.arange(len(c)) / (len(c) - 1)
#plt.plot(c, cp, label="Average TST per job", linestyle='-.', linewidth=2, color=colors[0])
ax_jct.plot(c, cp, label="Average TST", linestyle='-.', color=colors[0])
c_completion_list = list(c_job_completion_list.values())
t_c_completion_list = list(t_c_job_completion_list.values())
c = np.sort(c_completion_list)
cp = 1. * np.arange(len(c)) / (len(c) - 1)
#plt.plot(c, cp, label="Completion Time for Tasks across Jobs", linewidth=5, color='cyan', alpha=0.5)
ax_jct.plot(c, cp, label="Average TCT", color=colors[0], alpha=0.5)
c = np.sort(t_c_sq_list)
cp = 1. * np.arange(len(c)) / (len(c) - 1)
ax_jct.plot(c, cp, label="Tail TST", linestyle='--', color=colors[1])
c = np.sort(t_c_completion_list)
cp = 1. * np.arange(len(c)) / (len(c) - 1)
#plt.plot(c, cp, label="Completion Time for Tail Tasks across Jobs", linewidth=5, color='orange', alpha=0.5)
ax_jct.plot(c, cp, label="Tail TCT", color=colors[1], alpha=0.5)
ax_jct.set_ylabel('CDF')
#ax_jct.set_xscale('log')
ax_jct.set_xlabel('Duration (seconds)')
#ax_jct.text(-0.75,-0.25, "(a) Kubernetes", size=12, ha="center", transform=ax_jct.transAxes)
print(ax_jct.get_xticks())
#plt.title('Scheduler Queue Wait Times and Task Completion Times Aggregated Over Jobs')
legend = ax_jct.legend()
frame = legend.get_frame()
frame.set_facecolor('1.0')
frame.set_edgecolor('1.0')
ax_jct.set_ylim(0.0, 1.1)
#plt.xticks(np.arange(0, 60001, 30000))
#plt.show()
#fig.tight_layout()
#fig.savefig('task_completion_time.pdf', dpi=fig.dpi, bbox_inches='tight')
print(fig.dpi)
fig.savefig('c.pdf', dpi=fig.dpi, bbox_inches='tight')
print("Scheduler Queue time across all tasks of jobs", np.percentile(c_sq_list,50), np.percentile(c_sq_list,90), np.percentile(c_sq_list,99))
print("Scheduler Queue time across tail tasks of jobs", np.percentile(t_c_sq_list,50), np.percentile(t_c_sq_list,90), np.percentile(t_c_sq_list,99))
print("Completion time across all tasks", np.percentile(c_completion_list,50), np.percentile(c_completion_list,90), np.percentile(c_completion_list,99))
print("Completion time across tail tasks", np.percentile(t_c_completion_list,50), np.percentile(t_c_completion_list,90), np.percentile(t_c_completion_list,99))
print("Execution time of tasks", np.percentile(c_xt_list,50), np.percentile(c_xt_list,90), np.percentile(c_xt_list,99))
print("################")
