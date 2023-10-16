import csv
import numpy as np
import collections
import random
from matplotlib import pyplot as plt, rcParams
from collections import defaultdict
from palettable.colorbrewer.qualitative import Set2_7
from bisect import bisect

colors = Set2_7.mpl_colors
params = {
   'axes.labelsize': 16,
   'font.size': 16,
   'legend.fontsize': 10,
   'xtick.labelsize': 16,
   'ytick.labelsize': 16,
   'text.usetex': False,
   'figure.figsize': [6.8, 3.6]
}
rcParams.update(params)

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
with open("results/pods/pods.c.10000J.400X.50N.YH.2",'r') as f:
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

#CDF of tail tasks.
for jobname, num_tasks in count_tasks.items():
    c_job_sq_list[jobname] /= num_tasks
    c_job_xt_list[jobname] /= num_tasks
    c_job_completion_list[jobname] /= num_tasks
#fig, (ax_jct, ax_tail)= plt.subplots(1,2)
fig, ax_jct = plt.subplots()
ax_jct.minorticks_off()
c_xt_list = list(c_job_xt_list.values())
c = np.sort(c_xt_list)
cp = 1. * np.arange(len(c)) / (len(c) - 1)
ax_jct.plot(c, cp, label="Average x", linestyle=':', linewidth=2, color=colors[2])
#Take the list of average task completions per job. Sort them. Plot as CDF.
c_sq_list = list(c_job_sq_list.values())
t_c_sq_list = list(t_c_job_sq_list.values())
c = np.sort(c_sq_list)
cp = 1. * np.arange(len(c)) / (len(c) - 1)
ax_jct.plot(c, cp, label="Average TST", linestyle='-.', color=colors[0])
c_completion_list = list(c_job_completion_list.values())
t_c_completion_list = list(t_c_job_completion_list.values())
c = np.sort(c_completion_list)
cp = 1. * np.arange(len(c)) / (len(c) - 1)
ax_jct.plot(c, cp, label="Average TCT", color=colors[0], alpha=0.5)
c = np.sort(t_c_sq_list)
cp = 1. * np.arange(len(c)) / (len(c) - 1)
ax_jct.plot(c, cp, label="Tail TST", linestyle='--', color=colors[1])
c = np.sort(t_c_completion_list)
cp = 1. * np.arange(len(c)) / (len(c) - 1)
ax_jct.plot(c, cp, label="Tail TCT", color=colors[1], alpha=0.5)
ax_jct.set_ylabel('CDF')
ax_jct.set_xlabel('Duration (seconds)')


c=[]
c_1secretry=[]
c_noretry=[]
d=[]
jobids=[]
jobid = 0 
with open("results/jrt/c.10000J.400X.50N.YH", 'r') as f:
    for r in f:
        if "has JRT" not in r:
            continue
        r= r.split()
        jrt = float(r[4])
        c.append(jrt)
        jobid += 1
        jobids.append(jobid)
with open("results/jrt/c.10000J.400X.50N.YH.noretry", 'r') as f:
    for r in f:
        if "has JRT" not in r:
            continue
        r= r.split()
        jrt = float(r[4])
        c_noretry.append(jrt)

with open("results/jrt/c.10000J.400X.50N.YH.1secretry", 'r') as f:
    for r in f:
        if "has JRT" not in r:
            continue
        r= r.split()
        jrt = float(r[4])
        c_1secretry.append(jrt)

c=np.sort(c)
c_1secretry=np.sort(c_1secretry)
c_noretry=np.sort(c_noretry)
cp = 1. * np.arange(len(c)) / (len(c) - 1)
cp_noretry = 1. * np.arange(len(c_noretry)) / (len(c_noretry) - 1)
cp_1secretry = 1. * np.arange(len(c_1secretry)) / (len(c_1secretry) - 1)

ax_jct.plot(c, cp, 'b', label="JCT - Kubernetes", color=colors[6], linewidth=3)
ax_jct.plot(c_noretry, cp_noretry, 'b', label="JCT - Kubernetes (no retry)", color=colors[4], linewidth=3, linestyle='dashdot')
ax_jct.plot(c_1secretry, cp_1secretry, 'b', label="JCT - Kubernetes (1s retry)", color=colors[5], linewidth=3, linestyle='dotted')


legend = ax_jct.legend()
frame = legend.get_frame()
frame.set_facecolor('1.0')
frame.set_edgecolor('1.0')
ax_jct.set_ylim(0.0, 1.1)
ax_jct.set_xticks([0,20000,40000,60000])
fig.tight_layout()
fig.savefig('fig2_merged.pdf', dpi=fig.dpi, bbox_inches='tight')
