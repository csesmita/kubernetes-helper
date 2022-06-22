import csv
import numpy as np
import collections
import random
from matplotlib import pyplot as plt

###########################################################################
# The first part of the script analyzes the job response time.
###########################################################################

c=[]
d=[]
jobids=[]
jobid = 0
with open("results/jrt/c.5000J.200X.19N", 'r') as f:
    for r in f:
        if "has JRT" not in r:
            continue
        r= r.split()
        c.append(float(r[4]))
        jobid += 1
        jobids.append(jobid)
with open("results/jrt/d.5000J.200X.19N.10S", 'r') as f:
    for r in f:
        if "has JRT" not in r:
            continue
        r = r.split()
        d.append(float(r[4]))
c=np.sort(c)
d=np.sort(d)

assert(len(c) == len(d))

cp = 1. * np.arange(len(c)) / (len(c) - 1)
dp = 1. * np.arange(len(d)) / (len(d) - 1)

#Show raw data
plt.plot(jobids, c, 'b', label="Centralized")
plt.plot(jobids, d, 'r--', label="Decentralized")
plt.xlabel('Job Ids')
plt.ylabel('Job Response Times Raw Data')
plt.title('JRT Raw Data')
plt.legend()
plt.show()

#Show CDF
plt.plot(c, cp, 'b', label="Centralized")
plt.plot(d, dp, 'r--', label="Decentralized")
plt.xlabel('Job Response Times')
plt.title('Job Response Times CDF')
plt.ylabel('CDF')
plt.legend()
plt.show()

#Show Histogram
q25, q75 = np.percentile(d, [25,75])
width = 2 * (q75 - q25) * len(d) ** (-1/3)
bins = round( (max(d) - min(d)) / width)
plt.hist(c, density=True, bins=bins, label="Centralized")
plt.hist(d, density=True, bins=bins, label="Decentralized")
plt.ylabel('Probability')
plt.xlabel('Job Response Time Histogram')
plt.title('Job Response Time Histogram')
plt.legend()
plt.show()

#Show percentiles as bar
percentiles=['50', '90', '99']
plt.bar(percentiles, [np.percentile(c, 50), np.percentile(c, 90), np.percentile(c, 99)], label="Centralized")
plt.bar(percentiles, [np.percentile(d, 50), np.percentile(d, 90), np.percentile(d, 99)], label="Decentralized")
plt.ylabel("Percentile Job Response Times")
plt.title("Percentile Job Response Times")
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

# Scheduler Algorithm and Queue times, Kubelet queue times, cumulative queue times, and the execution times.
d_sq_list=[]
d_sa_list=[]
d_kq_list=[]
d_q_list=[]
d_xt_list=[]

c_job_sq_list=collections.defaultdict(float)
c_job_sa_list=collections.defaultdict(float)
c_job_xt_list=collections.defaultdict(float)

d_job_sq_list=collections.defaultdict(float)
d_job_sa_list=collections.defaultdict(float)
d_job_kq_list=collections.defaultdict(float)
d_job_q_list=collections.defaultdict(float)
d_job_xt_list=collections.defaultdict(float)
with open("results/pods/c.5000", 'r') as f:
    for r in f:
        if "SchedulerQueueTime" not in r:
            continue
        r = r.split()
        sq = float(r[4])
        sa = float(r[6])
        xt = float(r[12])

        c_sq_list.append(sq)
        c_sa_list.append(sa)
        c_xt_list.append(xt)		

        jobname = r[1].split("-")[0]
        c_job_sq_list[jobname] += sq
        c_job_sa_list[jobname] += sa
        c_job_xt_list[jobname] += xt

with open("results/pods/d.5000", 'r') as f:
    for r in f:
        if "SchedulerQueueTime" not in r:
            continue
        r = r.split()
        sq = float(r[4])
        sa = float(r[6])
        kq = float(r[8])
        xt = float(r[12])

        d_sq_list.append(sq)
        d_sa_list.append(sa)
        d_kq_list.append(kq)
        d_xt_list.append(xt)
        d_q_list.append(sq + kq)

        jobname = r[1].split("-")[0]
        d_job_sq_list[jobname] += sq
        d_job_sa_list[jobname] += sa
        d_job_kq_list[jobname] += kq
        d_job_q_list[jobname]  += sq + kq
        d_job_xt_list[jobname] += xt

### First show the percentiles of individual pods over the entire workload.
#Scheduler Queue Times vs. (Scheduler Queue + Kubelet Queue Times).
percentiles=['50', '90', '99']
x=np.arange(len(percentiles))
width=0.35
fig, ax = plt.subplots()
rects1= ax.bar(x-width/2, [np.percentile(c_sq_list, 50), np.percentile(c_sq_list, 90), np.percentile(c_sq_list, 99)], width, label="Centralized")
rects2= ax.bar(x+width/2, [np.percentile(d_q_list, 50), np.percentile(d_q_list, 90), np.percentile(d_q_list, 99)], width, label="Decentralized")
ax.bar_label(rects1, padding=3)
ax.bar_label(rects2, padding=3)
ax.set_ylabel("Percentile Scheduler and Kubelet Queue Time")
ax.set_xticks(x,percentiles)
ax.legend()
fig.tight_layout()
plt.show()

#Scheduler Algorithm Times
percentiles=['50', '90', '99']
x=np.arange(len(percentiles))
width=0.35
fig, ax = plt.subplots()
rects1= ax.bar(x-width/2, [np.percentile(c_sa_list, 50), np.percentile(c_sa_list, 90), np.percentile(c_sa_list, 99)], width, label="Centralized")
rects2= ax.bar(x+width/2, [np.percentile(d_sa_list, 50), np.percentile(d_sa_list, 90), np.percentile(d_sa_list, 99)], width, label="Decentralized")
ax.bar_label(rects1, padding=3)
ax.bar_label(rects2, padding=3)
ax.set_ylabel("Percentile Scheduler Algorithm Time")
ax.set_xticks(x,percentiles)
ax.legend()
fig.tight_layout()
plt.show()

#Execution Time - Should match since this comes from the workload
percentiles=['50', '90', '99']
x=np.arange(len(percentiles))
width=0.35
fig, ax = plt.subplots()
rects1= ax.bar(x-width/2, [np.percentile(c_xt_list, 50), np.percentile(c_xt_list, 90), np.percentile(c_xt_list, 99)], width, label="Centralized")
rects2= ax.bar(x+width/2, [np.percentile(c_xt_list, 50), np.percentile(c_xt_list, 90), np.percentile(c_xt_list, 99)], width, label="Decentralized")
ax.bar_label(rects1, padding=3)
ax.bar_label(rects2, padding=3)
ax.set_ylabel("Percentile Execution Time")
ax.set_xticks(x,percentiles)
ax.legend()
fig.tight_layout()
plt.show()

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
ax.bar_label(rects1, padding=3, fmt="%f")
ax.bar_label(rects2, padding=3, fmt="%f")
ax.set_ylabel("Percentile Scheduler and Kubelet Queue Time Per Job")
ax.set_xticks(x,percentiles)
ax.legend()
fig.tight_layout()
plt.show()

c_sa_list = list(c_job_sa_list.values())
d_sa_list = list(d_job_sa_list.values())
#Scheduler Algorithm Times
percentiles=['50', '90', '99']
x=np.arange(len(percentiles))
width=0.35
fig, ax = plt.subplots()
rects1= ax.bar(x-width/2, [np.percentile(c_sa_list, 50), np.percentile(c_sa_list, 90), np.percentile(c_sa_list, 99)], width, label="Centralized")
rects2= ax.bar(x+width/2, [np.percentile(d_sa_list, 50), np.percentile(d_sa_list, 90), np.percentile(d_sa_list, 99)], width, label="Decentralized")
ax.bar_label(rects1, padding=3, fmt="%f")
ax.bar_label(rects2, padding=3, fmt="%f")
ax.set_ylabel("Percentile Scheduler Algorithm Time Per Job")
ax.set_xticks(x,percentiles)
ax.legend()
fig.tight_layout()
plt.show()

c_xt_list = list(c_job_xt_list.values())
d_xt_list = list(d_job_xt_list.values())
#Execution Time - Should match since this comes from the workload
percentiles=['50', '90', '99']
x=np.arange(len(percentiles))
width=0.35
fig, ax = plt.subplots()
rects1= ax.bar(x-width/2, [np.percentile(c_xt_list, 50), np.percentile(c_xt_list, 90), np.percentile(c_xt_list, 99)], width, label="Centralized")
rects2= ax.bar(x+width/2, [np.percentile(d_xt_list, 50), np.percentile(d_xt_list, 90), np.percentile(d_xt_list, 99)], width, label="Decentralized")
ax.bar_label(rects1, padding=3, fmt="%f")
ax.bar_label(rects2, padding=3, fmt="%f")
ax.set_ylabel("Percentile Execution Time Per Job")
ax.set_xticks(x,percentiles)
ax.legend()
fig.tight_layout()
plt.show()

