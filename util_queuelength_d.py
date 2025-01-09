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
   'axes.labelsize': 12,
   'font.size': 12,
   'legend.fontsize': 12,
   'xtick.labelsize': 12,
   'ytick.labelsize': 12,
   'text.usetex': False,
   'figure.figsize': [6, 3.4]
}
rcParams.update(params)

pod_qt = {}
q_list= []
t_q_list= []
t_c_queueaddtime = {}
t_c_job_q_list=collections.defaultdict(float)
with open("results/pods/pods.d.10000J.400X.50N.10S.YH",'r') as f:
    for line in f:
        if "SchedulerQueueTime" not in line:
            continue
        r = line.split()
        sq = float(r[4])
        kq = float(r[8])
        podname = r[1]
        pod_qt[podname] = sq + kq
        q_list.append(sq + kq)
        if "TAIL TASK" in line:
            t_q_list.append(sq + kq)
            jobname = r[1].split("-")[0]
            t_c_job_q_list[jobname] += sq + kq
            t_c_queueaddtime[jobname] = float((line.split("QueueAddTime")[1]).split()[0])

# NAME                                                        CPU(cores)   CPU%        MEMORY(bytes)   MEMORY%     
# node1.sv440-128429.decentralizedsch-pg0.utah.cloudlab.us    35844m       56%         2656Mi          2%
c_cpu = []
d_cpu = []
dc_cpu = {}
dd_cpu = {}
with open("results/utilization/utilization.d.10000J.400X.50N.10S.YH", 'r') as f:
    d_per_node_cpu = []
    d_per_node_cpup = []
    start_time = 0
    for r in f:
        if "NAME" in r:
            if len(d_per_node_cpu) > 0:
                # Take the average of this iteration over all nodes.
                cpu_avg = sum(d_per_node_cpu) / len(d_per_node_cpu)
                d_cpu.append(cpu_avg)
                d_per_node_cpu.clear()
                dc_cpu[start_time] = cpu_avg 
                start_time += 120
            continue
        if "node0" in r or "node1" in r:
            continue
        r = r.split()
        cpu = int((r[1].split("m"))[0])
        cpup = int((r[2].split("%"))[0])
        d_per_node_cpu.append(cpu)
        d_per_node_cpup.append(cpup)

print("CPU Utilization in D", np.percentile(d_cpu, 50), np.percentile(d_cpu, 90), np.percentile(d_cpu, 99))
print("CPU% Utilization in D", np.percentile(d_per_node_cpup, 50), np.percentile(d_per_node_cpup, 90), np.percentile(d_per_node_cpup, 99))

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
    bins[idx].append(t_c_job_q_list[jobname])
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
fig.savefig('d_tail_u.pdf', dpi=fig.dpi, bbox_inches='tight')
#plt.title('Comparison of CPU Utilization and Tail Latencies over time')
#plt.show()
