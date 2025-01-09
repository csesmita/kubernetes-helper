import re
from datetime import datetime, timedelta
import collections
from bisect import bisect
from matplotlib import pyplot as plt
import os
import numpy as np
#Time width in seconds per bucket
BUCKET_SIZE = 1

pattern = '\d{2}\d{2} \d{2}:\d{2}:\d{2}\.\d{6}'
compiled = re.compile(pattern)
pods_bound = {}
pods_deleted = {}
bind_event_string = "Attempting to bind pod to node"
delete_event_string = "Delete event for scheduled pod"
f=""

#Compare scheduling times.
with open('results/jrt/unsaturated/syslog.c.5000J.50X.47N.YH', 'r') as f:
    for line in f:
        if bind_event_string not in line and delete_event_string not in line:
            continue
        if bind_event_string in line:
            podname = line.split(bind_event_string)[1].split()[1]
            pods_bound[podname] = datetime.strptime(compiled.search(line).group(0),'%m%d %H:%M:%S.%f')
        if delete_event_string in line:
            podname = line.split(delete_event_string)[1].split()[1]
            pods_deleted[podname] = datetime.strptime(compiled.search(line).group(0),'%m%d %H:%M:%S.%f')
            continue

print("Pods with delete and no bind statement", len(list(set(pods_deleted.keys()) - set(pods_bound.keys()))))
print("Pods with bind and no delete statement", len(list(set(pods_bound.keys()) - set(pods_deleted.keys()))))
final_pods = set(pods_bound.keys()).intersection(set(pods_deleted.keys()))

start = datetime.max
finish = datetime.min
pod_run_time = []
for pod in final_pods:
    assert(pods_bound[pod] < pods_deleted[pod])
    pod_run_time.append((pods_deleted[pod] - pods_bound[pod]).total_seconds())
    if start > pods_bound[pod]:
        start = pods_bound[pod]
    if finish < pods_deleted[pod]:
        finish = pods_deleted[pod]

#start = start.total_seconds()
#finish = finish.total_seconds()

print(np.median(pod_run_time), np.percentile(pod_run_time, 90))

'''
num_scheduled = len(final_pods)

total_time = (fb - ld).total_seconds()
#print("File", f)
#print("First unscheduled pod add event", fr, "and last unscheduled pod add event", lr)
#print("First bound pod event",b , "and last bound pod event", l)
#tasks_per_sec = num_scheduled / sched_time
#print("Total Tasks Scheduled is ", num_scheduled, "in time", sched_time)
#print("Tasks per sec" , tasks_per_sec)

#######################################################################
###BINNED CALCULATIONS#################################################
#######################################################################

interval=timedelta(seconds=BUCKET_SIZE)
start=fb
max_buckets = int(total_time / BUCKET_SIZE) + 1
grid=[start+n*interval for n in range(max_buckets)]
bins=collections.defaultdict(int)
for pod in final_pods:
    #Add to the bucket that indicates how many were scheduled
    idx = bisect(grid, pods_bound[pod])
    bins[idx] += 1

print("Num bins are ", len(bins.keys()), "with size of each bin being", BUCKET_SIZE)
max_bin_val = bins[max(bins, key=bins.get)]
print("Max bin value is", max_bin_val)
print("Max tasks per sec is", max_bin_val / BUCKET_SIZE)

bin_array = []
for idx in range(max_buckets):
    bin_array.append(bins[idx])
print("Total tasks is", sum(bin_array))

fig = plt.figure()
plt.plot(bin_array, label="Scheduling Rates Per Second")
#plt.show()
plt.ylim(0,10000)
fig.tight_layout()
fig.savefig(filename + '_200X.pdf', dpi=fig.dpi, bbox_inches='tight')
plt.close()
'''
