import csv
import numpy as np
import collections
import random
from matplotlib import pyplot as plt
from collections import defaultdict

###########################################################################
# The first part of the script analyzes the job response time.
###########################################################################
c=[]
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
with open("results/jrt/d.10000J.400X.50N.10S.YH", 'r') as f:
    for r in f:
        if "has JRT" not in r:
            continue
        r = r.split()
        jrt = float(r[4])
        d.append(jrt)

assert(len(c) == len(d))
#Show raw unsorted data
plt.plot(jobids, c, 'b', label="Centralized")
plt.plot(jobids, d, 'r--', label="Decentralized")
plt.xlabel('Job Ids')
plt.ylabel('Job Response Times Raw Data')
plt.title('JRT Raw Data')
plt.legend()
plt.show()

c=np.sort(c)
d=np.sort(d)
cp = 1. * np.arange(len(c)) / (len(c) - 1)
dp = 1. * np.arange(len(d)) / (len(d) - 1)

#Show CDF
plt.plot(c, cp, 'b', label="Centralized")
plt.plot(d, dp, 'r--', label="Decentralized")
plt.xlabel('Job Response Times')
plt.title('Job Response Times CDF')
plt.ylabel('CDF')
plt.legend()
plt.show()

print("[50,90,99] Percentiles for Centralized - ", np.percentile(c, 50), np.percentile(c, 90), np.percentile(c, 99))
print("[50,90,99] Percentiles for Decentralized - ", np.percentile(d, 50), np.percentile(d, 90), np.percentile(d, 99))

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
t_c_job_sa_list=collections.defaultdict(float)
t_c_job_xt_list=collections.defaultdict(float)

t_d_job_sq_list=collections.defaultdict(float)
t_d_job_sa_list=collections.defaultdict(float)
t_d_job_kq_list=collections.defaultdict(float)
t_d_job_q_list=collections.defaultdict(float)
t_d_job_xt_list=collections.defaultdict(float)

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

#CDF of tail tasks.
d = np.sort(t_d_q_list)
c = np.sort(t_c_sq_list)
cp = 1. * np.arange(len(c)) / (len(c) - 1)
dp = 1. * np.arange(len(d)) / (len(d) - 1)

#Show CDF
plt.plot(c, cp, 'b', label="Centralized")
plt.plot(d, dp, 'r--', label="Decentralized")
plt.xlabel('Tail Task Queue Times')
plt.title('Tail Task Queue Times CDF')
plt.ylabel('CDF')
plt.legend()
plt.show()
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
plt.plot(c_max, 'b', label="Centralized")
plt.plot(d_max,'r--', label="Decentralized")
plt.ylabel('Maximum Difference in task queue times in a job')
plt.title('Maximum Queue Time variance distribution across tasks of a job')
plt.legend()
plt.show()

### First show the percentiles of individual pods over the entire workload.
#Scheduler Queue Times vs. (Scheduler Queue + Kubelet Queue Times).
percentiles=['50', '90', '99']
x=np.arange(len(percentiles))
width=0.35
fig, ax = plt.subplots()
rects1= ax.bar(x-width/2, [np.percentile(c_sq_list, 50), np.percentile(c_sq_list, 90), np.percentile(c_sq_list, 99)], width, label="Centralized")
rects2= ax.bar(x+width/2, [np.percentile(d_q_list, 50), np.percentile(d_q_list, 90), np.percentile(d_q_list, 99)], width, label="Decentralized")
ax.set_ylabel("Percentile Scheduler and Kubelet Queue Time")
ax.set_xticks(x)
ax.set_xticklabels(percentiles)
ax.legend()
ax.bar_label(rects1, padding=3)
ax.bar_label(rects2, padding=3)
fig.tight_layout()
plt.show()
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
plt.plot(c, cp, 'b', label="Centralized")
plt.plot(d, dp, 'r--', label="Decentralized")
plt.xlabel('All Task Queue Times')
plt.title('All Task Queue Times CDF')
plt.ylabel('CDF')
plt.legend()
plt.show()

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
fig, ax = plt.subplots()
rects1= ax.bar(x-width/2, [np.percentile(c_sq_list, 50), np.percentile(c_sq_list, 90), np.percentile(c_sq_list, 99)], width, label="Centralized")
rects2= ax.bar(x+width/2, [np.percentile(d_q_list, 50), np.percentile(d_q_list, 90), np.percentile(d_q_list, 99)], width, label="Decentralized")
ax.bar_label(rects1, padding=3, fmt="%d")
ax.bar_label(rects2, padding=3, fmt="%d")
ax.set_ylabel("Percentile Scheduler and Kubelet Queue Time Per Job")
ax.set_xticks(x)
ax.set_xticklabels(percentiles)
ax.legend()
fig.tight_layout()
plt.show()
print("[50,90,99] Percentiles for Centralized Scheduler Queue Time Per Job- ", np.percentile(c_sq_list, 50), np.percentile(c_sq_list, 90), np.percentile(c_sq_list, 99))
print("[50,90,99] Percentiles for Decentralized Scheduler Queue Time Per Job- ", np.percentile(d_q_list, 50), np.percentile(d_q_list, 90), np.percentile(d_q_list, 99))

print("################")
c_sq_list = list(t_c_job_sq_list.values())
d_q_list = list(t_d_job_q_list.values())
### Next show the percentiles of individual pods over their respective jobs.
#Scheduler Queue Times vs. (Scheduler Queue + Kubelet Queue Times).
percentiles=['50', '90', '99']
x=np.arange(len(percentiles))
width=0.35
fig, ax = plt.subplots()
rects1= ax.bar(x-width/2, [np.percentile(c_sq_list, 50), np.percentile(c_sq_list, 90), np.percentile(c_sq_list, 99)], width, label="Centralized")
rects2= ax.bar(x+width/2, [np.percentile(d_q_list, 50), np.percentile(d_q_list, 90), np.percentile(d_q_list, 99)], width, label="Decentralized")
ax.bar_label(rects1, padding=3, fmt="%d")
ax.bar_label(rects2, padding=3, fmt="%d")
ax.set_ylabel("Percentile Scheduler and Kubelet Queue Time For Tail Task of Jobs")
ax.set_xticks(x)
ax.set_xticklabels(percentiles)
ax.legend()
fig.tight_layout()
plt.show()
print("[50,90,99] Percentiles for Centralized Scheduler Queue Time Per Job Tail Tasks - ", np.percentile(c_sq_list, 50), np.percentile(c_sq_list, 90), np.percentile(c_sq_list, 99))
print("[50,90,99] Percentiles for Decentralized Scheduler Queue Time Per Job Tail Tasks - ", np.percentile(d_q_list, 50), np.percentile(d_q_list, 90), np.percentile(d_q_list, 99))
print("################")


fanout = {}
running_time = {}
joblist = t_c_job_sq_list.keys()
with open("temp.tr", "r") as f:
    jobid = 0
    for row in f:
        row = row.split()
        num_tasks = int(row[1])
        est_time = float(row[2])
        jobid += 1
        jobstr = "".join(["job",str(jobid)])
        if jobstr in joblist:
            fanout[jobstr] = num_tasks
            running_time[jobstr] = est_time
'''
#Sort the tail qt times by value
fanout_list = []
running_time_list = []
lists = sorted(t_c_job_sq_list.items(), key=lambda item: item[1])
jobnames, tail_times = zip(*lists) # unpack a list of pairs into two tuples
for jobname in jobnames:
    fanout_list.append(fanout[jobname])
    running_time_list.append(running_time[jobname])
plt.plot(jobnames, tail_times, 'b', label='Tail Times')
plt.plot(jobnames, running_time_list, 'r--', label='Running Times')
plt.xlabel('Jobs')
plt.title('Jobs and Tail Times and Running Times')
plt.legend()
plt.show()

#Sort the tail qt times by value
fanout_list = []
running_time_list = []
lists = sorted(t_c_job_sq_list.items(), key=lambda item: item[1])
jobnames, tail_times = zip(*lists) # unpack a list of pairs into two tuples
for jobname in jobnames:
    fanout_list.append(fanout[jobname])
    running_time_list.append(running_time[jobname])
plt.plot(jobnames, tail_times, 'b', label='Tail Times')
plt.plot(jobnames, fanout_list, 'g--', label='Fanout')
plt.xlabel('Jobs')
plt.title('Jobs and Tail Times and Fanout')
plt.legend()
plt.show()
'''


# NAME                                                        CPU(cores)   CPU%        MEMORY(bytes)   MEMORY%     
# node1.sv440-128429.decentralizedsch-pg0.utah.cloudlab.us    35844m       56%         2656Mi          2%
c_cpu = []
d_cpu = []
with open("results/utilization/utilization.c.10000J.400X.50N.YH", 'r') as f:
    c_per_node_cpu = []
    for r in f:
        if "NAME" in r:
            if len(c_per_node_cpu) > 0:
                # Take the average of this iteration over all nodes.
                c_cpu.append(sum(c_per_node_cpu) / len(c_per_node_cpu))
                c_per_node_cpu.clear()
            continue
        if "node0" in r or "node1" in r:
            continue
        r = r.split()
        cpu = int((r[1].split("m"))[0])
        c_per_node_cpu.append(cpu)
with open("results/utilization/utilization.d.10000J.400X.50N.10S.YH", 'r') as f:
    d_per_node_cpu = []
    for r in f:
        if "NAME" in r:
            if len(d_per_node_cpu) > 0:
                # Take the average of this iteration over all nodes.
                d_cpu.append(sum(d_per_node_cpu) / len(d_per_node_cpu))
                d_per_node_cpu.clear()
            continue
        if "node0" in r or "node1" in r:
            continue
        r = r.split()
        cpu = int((r[1].split("m"))[0])
        d_per_node_cpu.append(cpu)

plt.plot(c_cpu)
plt.xlabel('Time')
plt.ylabel('Average CPU consumption across nodes')
plt.title('(C) CPU Utilization over time')
plt.show()

plt.plot(d_cpu)
plt.xlabel('Time')
plt.ylabel('Average CPU consumption across nodes')
plt.title('(D) CPU Utilization over time')
plt.show()
