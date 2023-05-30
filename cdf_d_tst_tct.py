import csv
import numpy as np
import collections
import random
from matplotlib import pyplot as plt, rcParams
from collections import defaultdict
from palettable.colorbrewer.qualitative import Paired_12

colors = Paired_12.mpl_colors

###########################################################################
# The second part of the script analyzes the pod queue and scheduling times.
# Files have been generated from syslog files using the following command -
# python3 pods.py (taking syslog files as defined in pods.sh and temp.tr)
# Generates pod logs with the following format in d.3000 -
# Pod job89-p7xxb - SchedulerQueueTime 0.023927 SchedulingAlgorithmTime 0.000503 KubeletQueueTime 0.000363 Node "caelum-507" ExecutionTime 25.5900908177
###########################################################################
# Scheduler Algorithm and Queue times, and the execution times.
# Scheduler Algorithm and Queue times, Kubelet queue times, cumulative queue times, and the execution times.
d_sq_list=[]
d_sa_list=[]
d_kq_list=[]
d_q_list=[]
d_xt_list=[]

t_d_sq_list=[]
t_d_sa_list=[]
t_d_kq_list=[]
t_d_q_list=[]
t_d_xt_list=[]

d_job_sq_list=collections.defaultdict(float)
d_job_sa_list=collections.defaultdict(float)
d_job_kq_list=collections.defaultdict(float)
d_job_q_list=collections.defaultdict(float)
d_job_xt_list=collections.defaultdict(float)
d_job_completion_list=collections.defaultdict(float)

#Tail Tasks
t_d_job_sq_list=collections.defaultdict(float)
t_d_job_sa_list=collections.defaultdict(float)
t_d_job_kq_list=collections.defaultdict(float)
t_d_job_q_list=collections.defaultdict(float)
t_d_job_xt_list=collections.defaultdict(float)
t_d_job_completion_list=collections.defaultdict(float)

#Queue times across tasks of a job
d_job_sq_dev=collections.defaultdict(list)

d_pod_qt={}
count_tasks = collections.defaultdict(int)
#Pod job18-bl57n - SchedulerQueueTime 0.00192 SchedulingAlgorithmTime 0.000493 KubeletQueueTime 0.000207 Node "node28.sv440-128365.decentralizedsch-pg0.utah.cloudlab.us" ExecutionTime 500.37717814 NumSchedulingCycles 1 StartedAfterSec 5.45567 TAIL TASK
with open("results/pods/pods.d.10000J.400X.50N.10S.YH", 'r') as f:
    for line in f:
        if "SchedulerQueueTime" not in line:
            continue
        r = line.split()
        sq = float(r[4])
        sa = float(r[6])
        kq = float(r[8])
        xt = float(r[12])
        tc = float((line.split("TaskCompletionTime")[1]).split()[0])

        d_sq_list.append(sq)
        d_sa_list.append(sa)
        d_kq_list.append(kq)
        d_q_list.append(sq + kq)
        d_xt_list.append(xt)

        podname = r[1]
        d_pod_qt[podname] = sq + kq

        jobname = r[1].split("-")[0]
        d_job_sq_list[jobname] += sq
        d_job_sa_list[jobname] += sa
        d_job_kq_list[jobname] += kq
        d_job_q_list[jobname]  += sq + kq
        d_job_xt_list[jobname] += xt
        d_job_sq_dev[jobname].append(sq + kq)
        d_job_completion_list[jobname] += tc
        count_tasks[jobname] += 1

        if "TAIL TASK" in line:
            t_d_sq_list.append(sq)
            t_d_sa_list.append(sa)
            t_d_kq_list.append(kq)
            t_d_q_list.append(sq + kq)
            t_d_xt_list.append(xt)
            t_d_job_sq_list[jobname] += sq
            t_d_job_sa_list[jobname] += sa
            t_d_job_kq_list[jobname] += kq
            t_d_job_q_list[jobname]  += sq + kq
            t_d_job_xt_list[jobname] += xt
            t_d_job_completion_list[jobname] = tc
            #t_d_secafterepoch[jobname] = float((line.split("SecAfterEpoch")[1]).split()[0])
params = {
   'axes.labelsize': 16,
   'font.size': 16,
   'legend.fontsize': 12,
   'xtick.labelsize': 16,
   'ytick.labelsize': 16,
   'text.usetex': False,
   'figure.figsize': [6,3.4]
}
rcParams.update(params)

#CDF of tail tasks.
for jobname, num_tasks in count_tasks.items():
    d_job_sq_list[jobname] /= num_tasks
    if d_job_sq_list[jobname] > 14:
            print(jobname, "has high TST", d_job_sq_list[jobname])
    d_job_xt_list[jobname] /= num_tasks
    d_job_completion_list[jobname] /= num_tasks

fig, ax_jct = plt.subplots()
ax_jct.minorticks_off()
d_xt_list = list(d_job_xt_list.values())
d = np.sort(d_xt_list)
dp = 1. * np.arange(len(d)) / (len(d) - 1)
ax_jct.plot(d, dp, label="Average x", linestyle=':', linewidth=3, color=colors[11])
d_sq_list = list(d_job_sq_list.values())
t_d_sq_list = list(t_d_job_sq_list.values())
d = np.sort(d_sq_list)
dp = 1. * np.arange(len(d)) / (len(d) - 1)
#plt.plot(c, cp, label="Average TST per job", linestyle='-.', linewidth=2, color=colors[0])
ax_jct.plot(d, dp, label="Average TST", linestyle='-.', color=colors[9], linewidth=3)
d = np.sort(t_d_sq_list)
dp = 1. * np.arange(len(d)) / (len(d) - 1)
ax_jct.plot(d, dp, label="Tail TST", linestyle='--', color=colors[1], linewidth=3)
d_completion_list = list(d_job_completion_list.values())
t_d_completion_list = list(t_d_job_completion_list.values())
d = np.sort(d_completion_list)
dp = 1. * np.arange(len(d)) / (len(d) - 1)
ax_jct.plot(d, dp, label="Average TCT", color=colors[8], linewidth=3, linestyle='-.')
d = np.sort(t_d_completion_list)
dp = 1. * np.arange(len(d)) / (len(d) - 1)
ax_jct.plot(d, dp, label="Tail TCT", color=colors[0], linewidth=3, linestyle='--')
ax_jct.set_ylabel('CDF')
ax_jct.set_xlabel('Duration (seconds)')
legend = ax_jct.legend()
frame = legend.get_frame()
frame.set_facecolor('1.0')
frame.set_edgecolor('1.0')
ax_jct.set_ylim(0.0, 1.1)
fig.tight_layout()
fig.savefig('d_tst_tct.pdf', dpi=fig.dpi, bbox_inches='tight')


'''
fig, ax_jct = plt.subplots()
ax_jct.minorticks_off()
d_xt_list = list(d_job_xt_list.values())
d = np.sort(d_xt_list)
dp = 1. * np.arange(len(d)) / (len(d) - 1)
ax_jct.plot(d, dp, label="Average x", linestyle=':', linewidth=2, color=colors[2])
d_completion_list = list(d_job_completion_list.values())
t_d_completion_list = list(t_d_job_completion_list.values())
print("Completion times", np.percentile(d_completion_list, 50), np.percentile(d_completion_list, 90), np.percentile(d_completion_list, 99))
print("Tail Completion times", np.percentile(t_d_completion_list, 50), np.percentile(t_d_completion_list, 90), np.percentile(t_d_completion_list, 99))
d = np.sort(d_completion_list)
dp = 1. * np.arange(len(d)) / (len(d) - 1)
#plt.plot(c, cp, label="Completion Time for Tasks across Jobs", linewidth=2, color='cyan', alpha=0.5)
ax_jct.plot(d, dp, label="Average TCT", color=colors[0], alpha=0.5, linewidth=2)
d = np.sort(t_d_completion_list)
dp = 1. * np.arange(len(d)) / (len(d) - 1)
#plt.plot(c, cp, label="Completion Time for Tail Tasks across Jobs", linewidth=2, color='orange', alpha=0.5)
ax_jct.plot(d, dp, label="Tail TCT", color=colors[1], alpha=0.5, linewidth=2)
ax_jct.set_ylabel('CDF')
#ax_jct.set_xscale('log')
ax_jct.set_xlabel('Duration (seconds)')
#ax_jct.text(-0.75,-0.25, "(a) Kubernetes", size=12, ha="center", transform=ax_jct.transAxes)
print(ax_jct.get_xticks())
#plt.title('x and average and tail TST and TCT in Murmuration')
legend = ax_jct.legend()
frame = legend.get_frame()
frame.set_facecolor('1.0')
frame.set_edgecolor('1.0')
ax_jct.set_ylim(0.0, 1.1)
#plt.xticks(np.arange(0, 60001, 30000))
fig.tight_layout()
#fig.savefig('task_completion_time.pdf', dpi=fig.dpi, bbox_inches='tight')
fig.savefig('d_tct.pdf', dpi=fig.dpi, bbox_inches='tight')

fig, ax_jct = plt.subplots()
ax_jct.minorticks_off()
d_xt_list = list(d_job_xt_list.values())
d = np.sort(d_xt_list)
dp = 1. * np.arange(len(d)) / (len(d) - 1)
ax_jct.plot(d, dp, label="Average x", linestyle=':', linewidth=2, color=colors[2])
d_sq_list = list(d_job_sq_list.values())
t_d_sq_list = list(t_d_job_sq_list.values())
d = np.sort(d_sq_list)
dp = 1. * np.arange(len(d)) / (len(d) - 1)
#plt.plot(c, cp, label="Average TST per job", linestyle='-.', linewidth=2, color=colors[0])
ax_jct.plot(d, dp, label="Average TST", linestyle='-.', color=colors[0], linewidth=2)
d = np.sort(t_d_sq_list)
dp = 1. * np.arange(len(d)) / (len(d) - 1)
ax_jct.plot(d, dp, label="Tail TST", linestyle='--', color=colors[1], linewidth=2)
ax_jct.set_ylabel('CDF')
#ax_jct.set_xscale('log')
ax_jct.set_xlabel('Duration (seconds)')
#ax_jct.text(-0.75,-0.25, "(a) Kubernetes", size=12, ha="center", transform=ax_jct.transAxes)
print(ax_jct.get_xticks())
#plt.title('x and average and tail TST and TCT in Murmuration')
legend = ax_jct.legend()
frame = legend.get_frame()
frame.set_facecolor('1.0')
frame.set_edgecolor('1.0')
ax_jct.set_ylim(0.0, 1.1)
#plt.xticks(np.arange(0, 60001, 30000))
fig.tight_layout()
#fig.savefig('task_completion_time.pdf', dpi=fig.dpi, bbox_inches='tight')
print(fig.get_size_inches())
fig.savefig('d_tst.pdf', dpi=fig.dpi, bbox_inches='tight')
'''
