import csv
import numpy as np
import collections
import random
from matplotlib import pyplot as plt, rcParams
from collections import defaultdict
from palettable.colorbrewer.qualitative import Set2_7

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

c_job_sq_list=collections.defaultdict(float)
c_job_sa_list=collections.defaultdict(float)
c_job_xt_list=collections.defaultdict(float)

d_job_sq_list=collections.defaultdict(float)
d_job_sa_list=collections.defaultdict(float)
d_job_kq_list=collections.defaultdict(float)
d_job_q_list=collections.defaultdict(float)
d_job_xt_list=collections.defaultdict(float)

#Tail Tasks
t_c_job_sq_list=collections.defaultdict(float)
t_c_job_sq_list_noretry=collections.defaultdict(float)
t_c_job_sq_list_1secretry=collections.defaultdict(float)
t_c_job_sa_list=collections.defaultdict(float)
t_c_job_xt_list=collections.defaultdict(float)

t_d_job_sq_list=collections.defaultdict(float)
t_d_job_sa_list=collections.defaultdict(float)
t_d_job_kq_list=collections.defaultdict(float)
t_d_job_q_list=collections.defaultdict(float)
t_d_job_xt_list=collections.defaultdict(float)

t_c_secafterepoch = {}
t_d_secafterepoch = {}

#Queue times across tasks of a job
c_job_sq_dev=collections.defaultdict(list)
d_job_sq_dev=collections.defaultdict(list)

c_pod_qt={}
d_pod_qt={}
#Pod job18-bl57n - SchedulerQueueTime 0.00192 SchedulingAlgorithmTime 0.000493 KubeletQueueTime 0.000207 Node "node28.sv440-128365.decentralizedsch-pg0.utah.cloudlab.us" ExecutionTime 500.37717814 NumSchedulingCycles 1 StartedAfterSec 5.45567 TAIL TASK
with open("results/pods/pods.c.10000J.400X.50N.YH",'r') as f:
    for line in f:
        if "SchedulerQueueTime" not in line:
            continue
        r = line.split()
        sq = float(r[4])
        sa = float(r[6])
        xt = float(r[12])

        podname = r[1]
        c_pod_qt[podname] = sq

        c_sq_list.append(sq)
        c_sa_list.append(sa)
        c_xt_list.append(xt)

        jobname = r[1].split("-")[0]
        c_job_sq_list[jobname] += sq
        c_job_sa_list[jobname] += sa
        c_job_xt_list[jobname] += xt
        c_job_sq_dev[jobname].append(sq)
        if "TAIL TASK" in line:
            t_c_sq_list.append(sq)
            t_c_sa_list.append(sa)
            t_c_xt_list.append(xt)
            t_c_job_sq_list[jobname] += sq
            t_c_job_sa_list[jobname] += sa
            t_c_job_xt_list[jobname] += xt
            #t_c_secafterepoch[jobname] = float((line.split("SecAfterEpoch")[1]).split()[0])
with open("results/pods/pods.c.10000J.400X.50N.YH.noretry",'r') as f:
    for line in f:
        if "SchedulerQueueTime" not in line:
            continue
        r = line.split()
        sq = float(r[4])
        sa = float(r[6])
        xt = float(r[12])

        podname = r[1]
        jobname = r[1].split("-")[0]
        if "TAIL TASK" in line:
            t_c_job_sq_list_noretry[jobname] += sq
with open("results/pods/pods.c.10000J.400X.50N.YH.1secretry",'r') as f:
    for line in f:
        if "SchedulerQueueTime" not in line:
            continue
        r = line.split()
        sq = float(r[4])
        sa = float(r[6])
        xt = float(r[12])

        podname = r[1]
        jobname = r[1].split("-")[0]
        if "TAIL TASK" in line:
            t_c_job_sq_list_1secretry[jobname] += sq

with open("results/pods/pods.d.10000J.400X.50N.10S.YH", 'r') as f:
    for line in f:
        if "SchedulerQueueTime" not in line:
            continue
        r = line.split()
        sq = float(r[4])
        sa = float(r[6])
        kq = float(r[8])
        xt = float(r[12])

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
            #t_d_secafterepoch[jobname] = float((line.split("SecAfterEpoch")[1]).split()[0])

#CDF of tail tasks.
d = np.sort(t_d_q_list)
c = np.sort(t_c_sq_list)
cp = 1. * np.arange(len(c)) / (len(c) - 1)
dp = 1. * np.arange(len(d)) / (len(d) - 1)

#Show CDF
plt.plot(c, cp, 'b', label="Kubernetes")
plt.plot(d, dp, 'r--', label="Murmuration")
plt.xlabel('Tail Task Queue Times')
plt.title('Tail Task Queue Times CDF')
plt.ylabel('CDF')
plt.legend()
#plt.show()
print("################")

#Difference in queue wait times across tasks of a job.
c_max=[]
d_max=[]
for jobname in d_job_sq_dev.keys():
    tasks_sq = c_job_sq_dev[jobname]
    '''
    tasks_sq_diff = [(x - tasks_sq[0]) for x in tasks_sq]
    '''
    c_max.append(max(tasks_sq) - min(tasks_sq))
    tasks_sq = d_job_sq_dev[jobname]
    '''
    tasks_sq_diff = [(x - tasks_sq[0]) for x in tasks_sq]
    '''
    d_max.append(max(tasks_sq) - min(tasks_sq))
print("Maximum wait time variance across tasks of a job (C)", np.percentile(c_max,50), np.percentile(c_max,90), np.percentile(c_max,99))
print("Maximum wait time variance across tasks of a job (D)", np.percentile(d_max,50), np.percentile(d_max,90), np.percentile(d_max,99))
plt.plot(c_max, 'b', label="Kubernetes")
plt.plot(d_max,'r--', label="Murmuration")
plt.ylabel('Maximum Difference in task queue times in a job')
plt.title('Maximum Queue Time variance distribution across tasks of a job')
plt.legend()
#plt.show()

### First show the percentiles of individual pods over the entire workload.
#Scheduler Queue Times vs. (Scheduler Queue + Kubelet Queue Times).
percentiles=['50', '90', '99']
x=np.arange(len(percentiles))
width=0.35
fig1, ax = plt.subplots()
rects1= ax.bar(x-width/2, [np.percentile(c_sq_list, 50), np.percentile(c_sq_list, 90), np.percentile(c_sq_list, 99)], width, label="Centralized")
rects2= ax.bar(x+width/2, [np.percentile(d_q_list, 50), np.percentile(d_q_list, 90), np.percentile(d_q_list, 99)], width, label="Decentralized")
ax.set_ylabel("Percentile Scheduler and Kubelet Queue Time")
ax.set_xticks(x)
ax.set_xticklabels(percentiles)
ax.legend()
#ax.bar_label(rects1, padding=3)
#ax.bar_label(rects2, padding=3)
fig1.tight_layout()
#plt.show()
print("Number of pods evaluated (C)", len(c_sq_list), "and max wait time (C)", max(c_sq_list))
print("Number of pods evaluated (D)", len(d_q_list), "and max wait time (D)", max(d_q_list))

#CDF of total QT across all pods.
c_sq_list.sort()
d_q_list.sort()
d = np.sort(d_q_list)
c = np.sort(c_sq_list)

#assert(len(c) == len(d))

cp = 1. * np.arange(len(c)) / (len(c) - 1)
dp = 1. * np.arange(len(d)) / (len(d) - 1)
plt.plot(c, cp, 'b', label="Kubernetes")
plt.plot(d, dp, 'r--', label="Murmuration")
plt.xlabel('All Task Queue Times')
plt.title('All Task Queue Times CDF')
plt.ylabel('CDF')
plt.legend()
#plt.show()

print("[50,90,99] Percentiles for Centralized Scheduler Queue Time- ", np.percentile(c_sq_list, 50), np.percentile(c_sq_list, 90), np.percentile(c_sq_list, 99))
#print("[50,90,99] Percentiles for Decentralized Scheduler Queue Time- ", np.percentile(d_sq_list, 50), np.percentile(d_sq_list, 90), np.percentile(d_sq_list, 99))
#print("[50,90,99] Percentiles for Decentralized Kubelet Queue Time- ", np.percentile(d_kq_list, 50), np.percentile(d_kq_list, 90), np.percentile(d_kq_list, 99))
print("[50,90,99] Percentiles for Decentralized Scheduler and Kubelet Queue Time- ", np.percentile(d_q_list, 50), np.percentile(d_q_list, 90), np.percentile(d_q_list, 99))
print("################")


c_sq_list = list(c_job_sq_list.values())
d_q_list = list(d_job_q_list.values())
### Next show the percentiles of individual pods over their respective jobs.
#Scheduler Queue Times vs. (Scheduler Queue + Kubelet Queue Times).
percentiles=['50', '90', '99']
x=np.arange(len(percentiles))
width=0.35
fig1, ax = plt.subplots()
rects1= ax.bar(x-width/2, [np.percentile(c_sq_list, 50), np.percentile(c_sq_list, 90), np.percentile(c_sq_list, 99)], width, label="Centralized")
rects2= ax.bar(x+width/2, [np.percentile(d_q_list, 50), np.percentile(d_q_list, 90), np.percentile(d_q_list, 99)], width, label="Decentralized")
#ax.bar_label(rects1, padding=3, fmt="%d")
#ax.bar_label(rects2, padding=3, fmt="%d")
ax.set_ylabel("Percentile Scheduler and Kubelet Queue Time Per Job")
ax.set_xticks(x)
ax.set_xticklabels(percentiles)
ax.legend()
fig1.tight_layout()
#plt.show()
print("[50,90,99] Percentiles for Centralized Scheduler Queue Time Per Job- ", np.percentile(c_sq_list, 50), np.percentile(c_sq_list, 90), np.percentile(c_sq_list, 99))
print("[50,90,99] Percentiles for Decentralized Scheduler Queue Time Per Job- ", np.percentile(d_q_list, 50), np.percentile(d_q_list, 90), np.percentile(d_q_list, 99))


print("################")
###########################################################################
# The first part of the script analyzes the job response time.
###########################################################################
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
with open("results/jrt/d.10000J.400X.50N.10S.YH", 'r') as f:
    for r in f:
        if "has JRT" not in r:
            continue
        r = r.split()
        jrt = float(r[4])
        d.append(jrt)
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

print("JRT Percentiles - c", np.percentile(c,50), np.percentile(c,99))
print("JRT Percentiles - c_noretry", np.percentile(c_noretry,50), np.percentile(c_noretry,99))
print("JRT Percentiles - c_1secretry", np.percentile(c_1secretry,50), np.percentile(c_1secretry,99))
print("JRT Percentiles - d", np.percentile(d,50), np.percentile(d,99))

assert(len(c) == len(d))
#Show raw unsorted data
plt.plot(jobids, c, 'b', label="Centralized")
plt.plot(jobids, d, 'r--', label="Decentralized")
plt.xlabel('Job Ids')
plt.ylabel('Job Response Times Raw Data')
plt.title('JRT Raw Data')
plt.legend()
#plt.show()

c=np.sort(c)
c_1secretry=np.sort(c_1secretry)
c_noretry=np.sort(c_noretry)
d=np.sort(d)
cp = 1. * np.arange(len(c)) / (len(c) - 1)
cp_noretry = 1. * np.arange(len(c_noretry)) / (len(c_noretry) - 1)
cp_1secretry = 1. * np.arange(len(c_1secretry)) / (len(c_1secretry) - 1)
dp = 1. * np.arange(len(d)) / (len(d) - 1)
#Show CDF
#fig, (ax1, ax2) = plt.subplots(1,2)
fig, ax1 = plt.subplots()
ax1.plot(c, cp, 'b', label="Kubernetes", color=colors[0], linewidth=3)
ax1.plot(c_noretry, cp_noretry, 'b', label="Kubernetes w/ no retry", color=colors[4], linewidth=3, linestyle='dashdot')
ax1.plot(c_1secretry, cp_1secretry, 'b', label="Kubernetes w/ 1s retry", color=colors[5], linewidth=3, linestyle='dotted')
ax1.plot(d, dp, linestyle='--', label="Murmuration", color=colors[1], linewidth=3)
ax1.set_xlabel('Job Completion Times (s)')
ax1.set_ylabel('CDF')
#ax1.set_xticks(ticks=[0,10000,20000,30000,40000,50000,60000], labels=["0","10","20","30","40","50","60"])
#ax1.title.set_text("JCT Comparison")
legend = ax1.legend()
frame = legend.get_frame()
frame.set_facecolor('1.0')
frame.set_edgecolor('1.0')
fig.tight_layout()
fig.savefig('c_d_jct.pdf', dpi=fig.dpi, bbox_inches='tight')

print("[50,90,99] Percentiles for Centralized - ", np.percentile(c, 50), np.percentile(c, 90), np.percentile(c, 99))
print("[50,90,99] Percentiles for Centralized w/ no retry- ", np.percentile(c_noretry, 50), np.percentile(c_noretry, 90), np.percentile(c_noretry, 99))
print("[50,90,99] Percentiles for Centralized w/ 1s retry- ", np.percentile(c_1secretry, 50), np.percentile(c_1secretry, 90), np.percentile(c_1secretry, 99))
print("[50,90,99] Percentiles for Decentralized - ", np.percentile(d, 50), np.percentile(d, 90), np.percentile(d, 99))



c_sq_list = list(t_c_job_sq_list.values())
c_sq_list_noretry = list(t_c_job_sq_list_noretry.values())
c_sq_list_1secretry = list(t_c_job_sq_list_1secretry.values())
d_q_list = list(t_d_job_q_list.values())
c=np.sort(c_sq_list)
c_noretry=np.sort(c_sq_list_noretry)
c_1secretry=np.sort(c_sq_list_1secretry)
d=np.sort(d_q_list)
cp = 1. * np.arange(len(c)) / (len(c) - 1)
cp_noretry = 1. * np.arange(len(c_noretry)) / (len(c_noretry) - 1)
cp_1secretry = 1. * np.arange(len(c_1secretry)) / (len(c_1secretry) - 1)
dp = 1. * np.arange(len(d)) / (len(d) - 1)
fig, ax_jct = plt.subplots()
ax_jct.plot(c, cp, label="Kubernetes", linewidth=3, color=colors[0])
ax_jct.plot(c_noretry, cp_noretry, label="Kubernetes w/ no retry queue", linestyle='dashdot', linewidth=3, color=colors[4])
ax_jct.plot(c_1secretry, cp_1secretry, label="Kubernetes w/ 1s retry period", linestyle='dotted', linewidth=3, color=colors[5])
ax_jct.plot(d, dp, label="Murmuration", linestyle='--', linewidth=3, color=colors[1])
ax_jct.set_ylabel('CDF')
#ax_jct.set_xscale('log')
ax_jct.set_xlabel('Wait times (s)')
#ax_jct.text(-0.75,-0.25, "(a) Kubernetes", size=12, ha="center", transform=ax_jct.transAxes)
#plt.title('x and average and tail TST and TCT in Murmuration')
legend = ax_jct.legend()
frame = legend.get_frame()
frame.set_facecolor('1.0')
frame.set_edgecolor('1.0')
ax_jct.set_ylim(0.0, 1.1)
#plt.xticks(np.arange(0, 60001, 30000))
fig.tight_layout()
#fig.savefig('task_completion_time.pdf', dpi=fig.dpi, bbox_inches='tight')
fig.savefig('c_d_twt.pdf', dpi=fig.dpi, bbox_inches='tight')
print("Wait time Kubernetes", np.percentile(c,50), np.percentile(c,90), np.percentile(c,99))
print("Wait time Kubernetes w/ no retry", np.percentile(c_noretry,50), np.percentile(c_noretry,90), np.percentile(c_noretry,99))
print("Wait time Kubernetes w/ 1s retry", np.percentile(c_1secretry,50), np.percentile(c_1secretry,90), np.percentile(c_1secretry,99))
print("Wait time Murmuration", np.percentile(d,50), np.percentile(d,90), np.percentile(d,99))
'''
### Next show the percentiles of individual pods over their respective jobs.
#Scheduler Queue Times vs. (Scheduler Queue + Kubelet Queue Times).
percentiles=['50', '90', '99']
systems=['Kubernetes', 'Murmuration']
x=np.arange(len(systems))
width=0.35
#fig, ax = plt.subplots()
#rects1= ax2.bar(x-width/2, [np.percentile(c_sq_list, 50), np.percentile(c_sq_list, 90), np.percentile(c_sq_list, 99)], width, label="Centralized", color=colors[0])
rects1= ax2.bar(x-width/3 + x, [np.percentile(c_sq_list, 50), np.percentile(d_q_list, 50)], width, label="50th %ile", color=colors[0])
rects2= ax2.bar(x+2*width/3 + x, [np.percentile(c_sq_list, 90), np.percentile(d_q_list, 90)], width, label="90th %ile", color=colors[1])
rects3= ax2.bar(x+5*width/3 + x, [np.percentile(c_sq_list, 99), np.percentile(d_q_list, 99)], width, label="99th %ile", color=colors[2])
#rects2= ax2.bar(x+width/2, [np.percentile(d_q_list, 50), np.percentile(d_q_list, 90), np.percentile(d_q_list, 99)], width, label="Decentralized", color=colors[1])
#ax.bar_label(rects1, padding=3, fmt="%d")
#ax.bar_label(rects2, padding=3, fmt="%d")
ax2.set_ylabel("Wait times (s)")
#ax2.title.set_text("(TST + w2s) comparison for tail tasks")
ax2.set_xticks([2*width/3, 2+2*width/3])
#ax2.set_yticks(ticks=[0,5000,10000,15000,20000,25000,30000], labels=["0","5","10","15","20","25","30"])
ax2.set_xticklabels(systems)
ax2.legend()
fig.tight_layout()
#plt.show()
fig.savefig('cdf_tail_400X_b.pdf', dpi=fig.dpi, bbox_inches='tight')
print(fig.get_size_inches())
print("[50,90,99] Percentiles for Centralized Scheduler Queue Time Per Job Tail Tasks - ", np.percentile(c_sq_list, 50), np.percentile(c_sq_list, 90), np.percentile(c_sq_list, 99))
print("[50,90,99] Percentiles for Decentralized Scheduler Queue Time Per Job Tail Tasks - ", np.percentile(d_q_list, 50), np.percentile(d_q_list, 90), np.percentile(d_q_list, 99))
print("################")
'''

'''
# NAME                                                        CPU(cores)   CPU%        MEMORY(bytes)   MEMORY%     
# node1.sv440-128429.decentralizedsch-pg0.utah.cloudlab.us    35844m       56%         2656Mi          2%
c_cpu = []
d_cpu = []
dc_cpu = {}
dd_cpu = {}
with open("results/utilization/utilization.c.10000J.400X.50N.YH", 'r') as f:
    c_per_node_cpu = []
    start_time = 0
    for r in f:
        if "NAME" in r:
            if len(c_per_node_cpu) > 0:
                # Take the average of this iteration over all nodes.
                cpu_avg = sum(c_per_node_cpu) / len(c_per_node_cpu)
                c_cpu.append(cpu_avg)
                c_per_node_cpu.clear()
                dc_cpu[start_time] = cpu_avg 
                start_time += 120
            continue
        if "node0" in r or "node1" in r:
            continue
        r = r.split()
        cpu = int((r[1].split("m"))[0])
        c_per_node_cpu.append(cpu)

with open("results/utilization/utilization.d.10000J.400X.50N.10S.YH", 'r') as f:
    d_per_node_cpu = []
    start_time = 0
    for r in f:
        if "NAME" in r:
            if len(d_per_node_cpu) > 0:
                # Take the average of this iteration over all nodes.
                cpu_avg = sum(d_per_node_cpu) / len(d_per_node_cpu)
                d_cpu.append(cpu_avg)
                d_per_node_cpu.clear()
                dd_cpu[start_time] = cpu_avg
                start_time += 120
            continue
        if "node0" in r or "node1" in r:
            continue
        r = r.split()
        cpu = int((r[1].split("m"))[0])
        d_per_node_cpu.append(cpu)

print("CPU Utilization in C", np.percentile(c_cpu, 50), np.percentile(c_cpu, 90), np.percentile(c_cpu, 99))
print("CPU Utilization in D", np.percentile(d_cpu, 50), np.percentile(d_cpu, 90), np.percentile(d_cpu, 99))
# Arrange secafterepoch in ascending order.
sorted_t_c_secafterepoch = sorted(t_c_secafterepoch.items(), key=lambda item: item[1])
tail_c_time_sorted = []
dtail_c_time_sorted = {}
jobnames, tail_secafterepoch = zip(*sorted_t_c_secafterepoch) # unpack a list of pairs into two tuples
for jobname in jobnames:
    tail_c_time_sorted.append(t_c_job_sq_list[jobname])
    tail_time = t_c_secafterepoch[jobname]
    dtail_c_time_sorted[tail_time] = t_c_job_sq_list[jobname]

sorted_t_d_secafterepoch = sorted(t_d_secafterepoch.items(), key=lambda item: item[1])
tail_d_time_sorted = []
dtail_d_time_sorted = {}
jobnames, tail_secafterepoch = zip(*sorted_t_d_secafterepoch) # unpack a list of pairs into two tuples
for jobname in jobnames:
    tail_d_time_sorted.append(t_d_job_q_list[jobname])
    tail_time = t_d_secafterepoch[jobname]
    dtail_d_time_sorted[tail_time] = t_d_job_q_list[jobname]

dc_cpu = sorted(dc_cpu.items())
dtail_c_time_sorted = sorted(dtail_c_time_sorted.items())
x,y = zip(*dc_cpu)
plt.plot(x, y, label="(C) CPU Utilization")
x,y=zip(*dtail_c_time_sorted)
plt.plot(x,y, label="(C) Tail Latencies")
dd_cpu = sorted(dd_cpu.items())
dtail_d_time_sorted = sorted(dtail_d_time_sorted.items())
x,y = zip(*dd_cpu)
plt.plot(x,y, label="(D) CPU Utilization")
x,y=zip(*dtail_d_time_sorted)
plt.plot(x,y, label="(D) Tail Latencies")
plt.xlabel('Time')
plt.title('Comparison of CPU Utilization and Tail Latencies over time in C and D')
plt.legend()
plt.show()
'''
