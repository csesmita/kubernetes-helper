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
   'figure.figsize': [6, 3.4]
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
print("Median Kubernetes Average TCT", np.percentile(c_completion_list, 50))
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
fig.tight_layout()
#fig.savefig('task_completion_time.pdf', dpi=fig.dpi, bbox_inches='tight')
print(fig.dpi)
fig.savefig('c_d_tail_tc_a.pdf', dpi=fig.dpi, bbox_inches='tight')
print("Scheduler Queue time across all tasks of jobs", np.percentile(c_sq_list,50), np.percentile(c_sq_list,90), np.percentile(c_sq_list,99))
print("Scheduler Queue time across tail tasks of jobs", np.percentile(t_c_sq_list,50), np.percentile(t_c_sq_list,90), np.percentile(t_c_sq_list,99))
print("Completion time across all tasks", np.percentile(c_completion_list,50), np.percentile(c_completion_list,90), np.percentile(c_completion_list,99))
print("Completion time across tail tasks", np.percentile(t_c_completion_list,50), np.percentile(t_c_completion_list,90), np.percentile(t_c_completion_list,99))
print("Execution time of tasks", np.percentile(c_xt_list,50), np.percentile(c_xt_list,90), np.percentile(c_xt_list,99))
print("################")

# NAME                                                        CPU(cores)   CPU%        MEMORY(bytes)   MEMORY%     
# node1.sv440-128429.decentralizedsch-pg0.utah.cloudlab.us    35844m       56%         2656Mi          2%
c_cpu = []
d_cpu = []
dc_cpu = {}
dd_cpu = {}
c_per_node_cpup = []
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
        cpup = int((r[2].split("%"))[0])
        c_per_node_cpu.append(cpu)
        c_per_node_cpup.append(cpup)

print("CPU Utilization in C", np.percentile(c_cpu, 50), np.percentile(c_cpu, 90), np.percentile(c_cpu, 99))
print("CPU% Utilization in C", np.percentile(c_per_node_cpup, 50), np.percentile(c_per_node_cpup, 90), np.percentile(c_per_node_cpup, 99))

# Arrange tasks according to when they entered the scheduler queue.
sorted_t_c_queueaddtime = sorted(t_c_queueaddtime.items(), key=lambda item: item[1])
dtail_c_time_sorted = {}
jobnames, tail_queueaddtime = zip(*sorted_t_c_queueaddtime) # unpack a list of pairs into two tuples
#Bucketize dtail_c_time_sorted to get 50th/99th tail latency per interval period.
BUCKET_SIZE=10
start_time=0
end_time=60000
max_buckets = int(end_time / BUCKET_SIZE) + 1
#grid shows the start time of the bucket at that index.
grid=[start_time + n*BUCKET_SIZE for n in range(max_buckets)]
#bins stores sq times of tail tasks that got added to sq at that bucket index.
bins=collections.defaultdict(list)
#Tails of these jobs arrived in ascending order.
s = {}
for jobname in jobnames:
    tailtaskqueueaddtime = t_c_queueaddtime[jobname]
    idx = bisect(grid, tailtaskqueueaddtime)
    #dtail_c_time_sorted[tailtaskqueueaddtime] = t_c_job_sq_list[jobname]
    bins[idx].append(t_c_job_sq_list[jobname])
for idx in list(range(max_buckets)):
    if len(bins[idx]) == 0:
        continue
    dtail_c_time_sorted[grid[idx]] =  np.percentile(bins[idx], 99)
    s[grid[idx]] = len(bins[idx])

fig, ax_tail = plt.subplots()
ax_tail2 = ax_tail.twinx()
dc_cpu = sorted(dc_cpu.items())
dtail_c_time_sorted = sorted(dtail_c_time_sorted.items())
x,y = zip(*dc_cpu)
print("Max cpu utilization", max(y))
l1, = ax_tail.plot(x, y, label="CPU Utilization on Workers", linewidth=2, color=colors[0])
ax_tail.set_xticks(np.arange(0, 60001, 30000))
ax_tail.set_xlabel('Duration in logarithmic scale (seconds)')
ax_tail.set_xscale('log')
#ax_tail.set_ylim(0, 100)
ax_tail.set_ylabel('CPU (millicores)', color=colors[0])
#time, tail latency
x,y=zip(*dtail_c_time_sorted)
s1 = [2*s[n] for n in x]
l2 = ax_tail2.scatter(x,y, marker = 'o', label="Tail Latencies", s=s1, color=colors[1])
z = np.polyfit(x, y, 2)
p = np.poly1d(z)
#l3= ax_tail2.plot(x, p(x), color=colors[2], linestyle="--")
ax_tail2.set_ylabel('Tail TST (seconds)', color=colors[1])
ax_tail2.set_ylim(0, 40000)
ax_tail2.set_yticks(np.arange(0, 50000 , 10000))    
ax_tail2.set_xscale('log')
#ax_tail.text(0.5,-0.4, "(b)", size=12, ha="center", transform=ax_tail.transAxes)
#legend = plt.legend([l1, l2, l3], ["Average CPU Utilization on Workers", "99th %ile Tail Task Scheduler Times", "Trend Line for Tail Task Scheduler Times"])
legend = plt.legend([l1, l2], ["Average CPU Utilization on Nodes", "99th %ile Tail TST"], framealpha=0.5)
frame = legend.get_frame()
frame.set_facecolor('1.0')
frame.set_edgecolor('1.0')
fig.tight_layout()
fig.savefig('c_d_tail_tc_u.pdf', dpi=fig.dpi, bbox_inches='tight')
#plt.title('Comparison of CPU Utilization and Tail Latencies over time')
#plt.show()

###Distributed Scheduler
# Scheduler Algorithm and Queue times, and the execution times.
tct = []
w2x = []
tail_tct = []
#29.0950625  estimated_task_duration:  19  by_def:  0  total_job_running_time:  29.0015 job_start: 0.09356249999999999 job_end: 29.0950625 average TCT 19.0950625 tail TCT 29.0950625
#with open("/home/sv440/Android/eagle/simulation/results/sparrow_tail/s.14.10X.tail_analysis",'r') as f:
with open("/home/sv440/Android/eagle/simulation/results_new/jct/sparrow/YH/s.10000M",'r') as f:
    for line in f:
        if "Total time elapsed in the DC" in line:
            continue
        tct.append(float((line.split("average TCT")[1]).split()[0]))
        tail_tct.append(float((line.split("tail TCT")[1]).split()[0]))
        w2x.append(float((line.split("average w2x")[1]).split()[0]))

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

#Take the list of average task completions per job. Sort them. Plot as CDF.
fig, ax_tail = plt.subplots()
ax_tail.minorticks_off()
print("Median Sparrow Average TCT", np.percentile(tct, 50))
c = np.sort(tct)
cp = 1. * np.arange(len(c)) / (len(c) - 1)
ax_tail.plot(c, cp, label="Average TCT", linewidth=3, color=colors[0], alpha=0.75)
c = np.sort(tail_tct)
cp = 1. * np.arange(len(c)) / (len(c) - 1)
ax_tail.plot(c, cp, label="Tail TCT", linewidth=3, color=colors[1])
c = np.sort(w2x)
cp = 1. * np.arange(len(c)) / (len(c) - 1)
ax_tail.plot(c, cp, label="Average w2x", linewidth=3, color=colors[3], alpha=0.75)
c_xt_list = list(c_job_xt_list.values())
c = np.sort(c_xt_list)
cp = 1. * np.arange(len(c)) / (len(c) - 1)
ax_tail.plot(c, cp, label="Average TST", linestyle=':', linewidth=2, color=colors[2])
ax_tail.set_xlabel('Duration (seconds)')
#ax_tail.text(0.5,-0.25, "(b) Sparrow", size=12, ha="center", transform=ax_tail.transAxes)
#ax_tail.set_xscale('log')
#ax_tail.set_xticks([1.e-02, 1.e+00, 1.e+02, 1.e+04])
ax_tail.set_xlim(0, 60001)
ax_tail.minorticks_off()
legend = ax_tail.legend()
frame = legend.get_frame()
frame.set_facecolor('1.0')
frame.set_edgecolor('1.0')
ax_tail.set_ylim(0.0, 1.1)
ax_tail.set_ylabel('CDF')
fig.tight_layout()
#fig.savefig('c_tail_tc_util.pdf', dpi=fig.dpi, bbox_inches='tight')
fig.savefig('c_d_tail_tc_b.pdf', dpi=fig.dpi, bbox_inches='tight')
