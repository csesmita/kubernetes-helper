import re
from datetime import datetime, timedelta
import collections
from bisect import bisect
from matplotlib import pyplot as plt, rcParams
import os
from palettable.colorbrewer.qualitative import Set2_7

colors = Set2_7.mpl_colors
params = {
   'axes.labelsize': 14,
   'font.size': 14,
   'legend.fontsize': 14,
   'xtick.labelsize': 14,
   'ytick.labelsize': 14,
   'text.usetex': False,
   'figure.figsize': [6, 3.4],
}
rcParams.update(params)

#Time width in seconds per bucket
BUCKET_SIZE = 1

#Compare scheduling times.
with open('10S.100X.1C', 'r') as f:
    print("#################")
    pattern = '\d{2}\d{2} \d{2}:\d{2}:\d{2}\.\d{6}'
    compiled = re.compile(pattern)
    pods_added = {}
    pods_bound = {}
    add_event_string = "Add event for unscheduled pod"
    bind_event_string = "Attempting to bind pod to node"
    fr= datetime.max
    lr=datetime.min
    b=datetime.max
    l=datetime.min
    for line in f:
        if add_event_string not in line and bind_event_string not in line:
            continue
        if add_event_string in line:
            podname = line.split(add_event_string)[1].split()[1]
            pods_added[podname] = datetime.strptime(compiled.search(line).group(0),'%m%d %H:%M:%S.%f')
            if fr > pods_added[podname]:
                fr = pods_added[podname]
            if lr < pods_added[podname]:
                lr = pods_added[podname]
            continue
        if bind_event_string in line:
            podname = line.split(bind_event_string)[1].split()[1]
            pods_bound[podname] = datetime.strptime(compiled.search(line).group(0),'%m%d %H:%M:%S.%f')
            if b > pods_bound[podname]:
                b = pods_bound[podname]
            if l < pods_bound[podname]:
                l = pods_bound[podname]
final_pods = set(pods_added.keys()).intersection(set(pods_bound.keys()))
num_scheduled = len(final_pods)
sched_time = (l - fr).total_seconds()
tasks_per_sec = num_scheduled / sched_time

#######################################################################
###BINNED CALCULATIONS#################################################
#######################################################################

interval=timedelta(seconds=BUCKET_SIZE)
start=fr
max_buckets = int(sched_time / BUCKET_SIZE) + 1
grid=[start+n*interval for n in range(max_buckets)]
bins=collections.defaultdict(int)
for pod in final_pods:
    #Add to the bucket that indicates how many were scheduled
    idx = bisect(grid, pods_bound[pod])
    bins[idx] += 1

max_bin_val = bins[max(bins, key=bins.get)]
bin_array_10S_100X_1C = []
for idx in range(max_buckets):
    bin_array_10S_100X_1C.append(bins[idx])

with open('10S.500X.1C', 'r') as f:
    print("#################")
    pattern = '\d{2}\d{2} \d{2}:\d{2}:\d{2}\.\d{6}'
    compiled = re.compile(pattern)
    pods_added = {}
    pods_bound = {}
    add_event_string = "Add event for unscheduled pod"
    bind_event_string = "Attempting to bind pod to node"
    fr= datetime.max
    lr=datetime.min
    b=datetime.max
    l=datetime.min
    for line in f:
        if add_event_string not in line and bind_event_string not in line:
            continue
        if add_event_string in line:
            podname = line.split(add_event_string)[1].split()[1]
            pods_added[podname] = datetime.strptime(compiled.search(line).group(0),'%m%d %H:%M:%S.%f')
            if fr > pods_added[podname]:
                fr = pods_added[podname]
            if lr < pods_added[podname]:
                lr = pods_added[podname]
            continue
        if bind_event_string in line:
            podname = line.split(bind_event_string)[1].split()[1]
            pods_bound[podname] = datetime.strptime(compiled.search(line).group(0),'%m%d %H:%M:%S.%f')
            if b > pods_bound[podname]:
                b = pods_bound[podname]
            if l < pods_bound[podname]:
                l = pods_bound[podname]
final_pods = set(pods_added.keys()).intersection(set(pods_bound.keys()))
num_scheduled = len(final_pods)
sched_time = (l - fr).total_seconds()
tasks_per_sec = num_scheduled / sched_time

#######################################################################
###BINNED CALCULATIONS#################################################
#######################################################################

interval=timedelta(seconds=BUCKET_SIZE)
start=fr
max_buckets = int(sched_time / BUCKET_SIZE) + 1
grid=[start+n*interval for n in range(max_buckets)]
bins=collections.defaultdict(int)
for pod in final_pods:
    #Add to the bucket that indicates how many were scheduled
    idx = bisect(grid, pods_bound[pod])
    bins[idx] += 1

max_bin_val = bins[max(bins, key=bins.get)]
bin_array_10S_500X_1C = []
for idx in range(max_buckets):
    bin_array_10S_500X_1C.append(bins[idx])

#Compare scheduling times.
with open('50S.500X.1C', 'r') as f:
    print("#################")
    pattern = '\d{2}\d{2} \d{2}:\d{2}:\d{2}\.\d{6}'
    compiled = re.compile(pattern)
    pods_added = {}
    pods_bound = {}
    add_event_string = "Add event for unscheduled pod"
    bind_event_string = "Attempting to bind pod to node"
    fr= datetime.max
    lr=datetime.min
    b=datetime.max
    l=datetime.min
    for line in f:
        if add_event_string not in line and bind_event_string not in line:
            continue
        if add_event_string in line:
            podname = line.split(add_event_string)[1].split()[1]
            pods_added[podname] = datetime.strptime(compiled.search(line).group(0),'%m%d %H:%M:%S.%f')
            if fr > pods_added[podname]:
                fr = pods_added[podname]
            if lr < pods_added[podname]:
                lr = pods_added[podname]
            continue
        if bind_event_string in line:
            podname = line.split(bind_event_string)[1].split()[1]
            pods_bound[podname] = datetime.strptime(compiled.search(line).group(0),'%m%d %H:%M:%S.%f')
            if b > pods_bound[podname]:
                b = pods_bound[podname]
            if l < pods_bound[podname]:
                l = pods_bound[podname]
final_pods = set(pods_added.keys()).intersection(set(pods_bound.keys()))
num_scheduled = len(final_pods)
sched_time = (l - fr).total_seconds()
tasks_per_sec = num_scheduled / sched_time

#######################################################################
###BINNED CALCULATIONS#################################################
#######################################################################

interval=timedelta(seconds=BUCKET_SIZE)
start=fr
max_buckets = int(sched_time / BUCKET_SIZE) + 1
grid=[start+n*interval for n in range(max_buckets)]
bins=collections.defaultdict(int)
for pod in final_pods:
    #Add to the bucket that indicates how many were scheduled
    idx = bisect(grid, pods_bound[pod])
    bins[idx] += 1

max_bin_val = bins[max(bins, key=bins.get)]
bin_array_50S_500X_1C = []
for idx in range(max_buckets):
    bin_array_50S_500X_1C.append(bins[idx])
with open('10S.500X.5C', 'r') as f:
    print("#################")
    pattern = '\d{2}\d{2} \d{2}:\d{2}:\d{2}\.\d{6}'
    compiled = re.compile(pattern)
    pods_added = {}
    pods_bound = {}
    add_event_string = "Add event for unscheduled pod"
    bind_event_string = "Attempting to bind pod to node"
    fr= datetime.max
    lr=datetime.min
    b=datetime.max
    l=datetime.min
    for line in f:
        if add_event_string not in line and bind_event_string not in line:
            continue
        if add_event_string in line:
            podname = line.split(add_event_string)[1].split()[1]
            pods_added[podname] = datetime.strptime(compiled.search(line).group(0),'%m%d %H:%M:%S.%f')
            if fr > pods_added[podname]:
                fr = pods_added[podname]
            if lr < pods_added[podname]:
                lr = pods_added[podname]
            continue
        if bind_event_string in line:
            podname = line.split(bind_event_string)[1].split()[1]
            pods_bound[podname] = datetime.strptime(compiled.search(line).group(0),'%m%d %H:%M:%S.%f')
            if b > pods_bound[podname]:
                b = pods_bound[podname]
            if l < pods_bound[podname]:
                l = pods_bound[podname]
final_pods = set(pods_added.keys()).intersection(set(pods_bound.keys()))
num_scheduled = len(final_pods)
sched_time = (l - fr).total_seconds()
tasks_per_sec = num_scheduled / sched_time

#######################################################################
###BINNED CALCULATIONS#################################################
#######################################################################

interval=timedelta(seconds=BUCKET_SIZE)
start=fr
max_buckets = int(sched_time / BUCKET_SIZE) + 1
grid=[start+n*interval for n in range(max_buckets)]
bins=collections.defaultdict(int)
for pod in final_pods:
    #Add to the bucket that indicates how many were scheduled
    idx = bisect(grid, pods_bound[pod])
    bins[idx] += 1

max_bin_val = bins[max(bins, key=bins.get)]
bin_array_10S_500X_5C = []
for idx in range(max_buckets):
    bin_array_10S_500X_5C.append(bins[idx])


with open('300S.100X.1C', 'r') as f:
    print("#################")
    pattern = '\d{2}\d{2} \d{2}:\d{2}:\d{2}\.\d{6}'
    compiled = re.compile(pattern)
    pods_added = {}
    pods_bound = {}
    add_event_string = "Add event for unscheduled pod"
    bind_event_string = "Attempting to bind pod to node"
    fr= datetime.max
    lr=datetime.min
    b=datetime.max
    l=datetime.min
    for line in f:
        if add_event_string not in line and bind_event_string not in line:
            continue
        if add_event_string in line:
            podname = line.split(add_event_string)[1].split()[1]
            pods_added[podname] = datetime.strptime(compiled.search(line).group(0),'%m%d %H:%M:%S.%f')
            if fr > pods_added[podname]:
                fr = pods_added[podname]
            if lr < pods_added[podname]:
                lr = pods_added[podname]
            continue
        if bind_event_string in line:
            podname = line.split(bind_event_string)[1].split()[1]
            pods_bound[podname] = datetime.strptime(compiled.search(line).group(0),'%m%d %H:%M:%S.%f')
            if b > pods_bound[podname]:
                b = pods_bound[podname]
            if l < pods_bound[podname]:
                l = pods_bound[podname]
final_pods = set(pods_added.keys()).intersection(set(pods_bound.keys()))
num_scheduled = len(final_pods)
sched_time = (l - fr).total_seconds()
tasks_per_sec = num_scheduled / sched_time

#######################################################################
###BINNED CALCULATIONS#################################################
#######################################################################

interval=timedelta(seconds=BUCKET_SIZE)
start=fr
max_buckets = int(sched_time / BUCKET_SIZE) + 1
grid=[start+n*interval for n in range(max_buckets)]
bins=collections.defaultdict(int)
for pod in final_pods:
    #Add to the bucket that indicates how many were scheduled
    idx = bisect(grid, pods_bound[pod])
    bins[idx] += 1

max_bin_val = bins[max(bins, key=bins.get)]
bin_array_300S_100X_1C = []
for idx in range(max_buckets):
    bin_array_300S_100X_1C.append(bins[idx])



fig = plt.figure()
plt.plot(bin_array_10S_500X_1C, label="10 schedulers", color=colors[0])
plt.plot(bin_array_50S_500X_1C, label="50 schedulers", color=colors[1])
plt.plot(bin_array_300S_100X_1C, label="300 schedulers", color=colors[2])
plt.ylabel("Scheduling throughput")
plt.xlabel("Time (seconds)")
#plt.xticks([0, 200, 400, 600, 800])
plt.ylim(0,16000)
plt.xlim(0,8000)
fig.tight_layout()
plt.legend()
fig.savefig('varying_sched.pdf', dpi=fig.dpi, bbox_inches='tight')
print("#################")

fig = plt.figure()
plt.plot(bin_array_10S_500X_1C, label="1 core/scheduler", color=colors[0])
plt.plot(bin_array_10S_500X_5C, label="5 cores/scheduler", color=colors[1])
plt.ylabel("Scheduling throughput")
plt.xlabel("Time (seconds)")
#plt.xticks([0, 200, 400, 600, 800])
plt.ylim(0,16000)
plt.xlim(0,8000)
fig.tight_layout()
plt.legend()
fig.savefig('varying_cpu.pdf', dpi=fig.dpi, bbox_inches='tight')
print("#################")

fig = plt.figure()
plt.plot(bin_array_10S_100X_1C, label="100X pods", color=colors[0])
plt.plot(bin_array_10S_500X_1C, label="500X pods", color=colors[1])
plt.ylabel("Scheduling throughput")
plt.xlabel("Time (seconds)")
#plt.xticks([0, 200, 400, 600, 800])
plt.ylim(0,16000)
plt.xlim(0,8000)
fig.tight_layout()
plt.legend()
fig.savefig('varying_rate.pdf', dpi=fig.dpi, bbox_inches='tight')
print("#################")
