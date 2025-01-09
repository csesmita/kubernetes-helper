import re
from datetime import datetime, timedelta
import collections
from bisect import bisect
from matplotlib import pyplot as plt
import os
import numpy as np
from matplotlib import pyplot as plt, rcParams

params = {
   'axes.labelsize': 12,
   'font.size': 12,
   'legend.fontsize': 12,
   'xtick.labelsize': 12,
   'ytick.labelsize': 12,
   'text.usetex': False,
   'figure.figsize': [6.4,3.6]
}
rcParams.update(params)


#Time width in seconds per bucket
BUCKET_SIZE = 1

print("#################")
pattern = '\w{3}\s*\d{1,2} \d{2}:\d{2}:\d{2}'
compiled = re.compile(pattern)
pods_added = {}
add_event_string = "Add event for unscheduled pod"
fr= datetime.max
lr=datetime.min
f=""

#Compare scheduling times.
#with open('results/syslog/syslog.d.10000J.1000X.50N.10S.YH', 'r') as f:
with open('results/jrt/unsaturated/syslog.d.5000J.50X.47N.10S.YH', 'r') as f:
#with open('results/syslog/syslog.c.10000J.400X.50N.YH', 'r') as f:
    try:
        for line in f:
            if add_event_string not in line: 
                continue
            podname = line.split(add_event_string)[1].split()[1]
            pods_added[podname] = datetime.strptime(compiled.search(line).group(0),'%b %d %H:%M:%S')
            if fr > pods_added[podname]:
                fr = pods_added[podname]
            if lr < pods_added[podname]:
                lr = pods_added[podname]
    except:
        pass
#final_pods = set(pods_added.keys()).intersection(set(pods_bound.keys()))
final_pods = pods_added.keys()
num_scheduled = len(final_pods)

sched_time = (lr - fr).total_seconds()
print("File", f)
#print("First unscheduled pod add event", fr, "and last unscheduled pod add event", lr)
tasks_per_sec = num_scheduled / sched_time
print("Total Tasks Scheduled is ", num_scheduled, "in time", sched_time)
print("Average Tasks per sec" , tasks_per_sec)

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
    idx = bisect(grid, pods_added[pod])
    bins[idx] += 1

print("Num bins are ", len(bins.keys()), "with size of each bin being", BUCKET_SIZE)
max_bin_val = bins[max(bins, key=bins.get)]
min_bin_val = bins[min(bins, key=bins.get)]
#print("Max bin value is", max_bin_val)
print("Range of bin values - ", max_bin_val - min_bin_val)
#print("Max tasks per sec is", max_bin_val / BUCKET_SIZE)

num_times = 0
bin_array = []
for idx in range(max_buckets):
    bin_array.append(bins[idx])
print("Total tasks is", sum(bin_array))
print("Standard deviation is", np.std(bin_array))
print("Percentiles of bin sizes - ", np.percentile(bin_array, 50),np.percentile(bin_array, 90), np.percentile(bin_array, 99))
fig = plt.figure()
print("BIN ARRAY")
print(len(bin_array))
plt.plot(bin_array, label="Scheduling Rates Per Second")
plt.xlabel("Duration (seconds)")
#plt.xticks([0,5000,10000,15000,20000])
plt.ylim(0,200)
plt.yticks([0,50,100,150,200])
plt.ylabel("Unscheduled pods / second")
#plt.title("Rate of new unscheduled pods arriving at the scheduler")
#plt.show()
#plt.ylim(0,10000)
fig.tight_layout()
fig.savefig('pods_arrive_scheduler_50X.pdf', dpi=fig.dpi, bbox_inches='tight')
plt.close()
print("#################")
