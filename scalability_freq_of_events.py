import re
from datetime import datetime, timedelta
import collections
from bisect import bisect
from matplotlib import pyplot as plt
import numpy as np

#10sec per bucket
BUCKET_SIZE = 1

pattern = '\d{2}\d{2} \d{2}:\d{2}:\d{2}\.\d{6}'
compiled = re.compile(pattern)
pods_deleted = {}
#delete_event_string = "Delete event for scheduled pod"
bind_event_string = "Attempting to bind pod to node"
#failed_event_string = "Unable to schedule pod; no fit; waiting"
fr= datetime.max
l=datetime.min
f=""

#Compare scheduling times.
with open("./results/jrt/unsaturated/syslog.c.5000J.50X.47N.YH",'r') as f:
    for line in f:
        if bind_event_string not in line:
            continue
        podname = line.split(bind_event_string)[1].split()[1]
        pods_deleted[podname] = datetime.strptime(compiled.search(line).group(0),'%m%d %H:%M:%S.%f')
        if fr > pods_deleted[podname]:
            fr= pods_deleted[podname]
        if l < pods_deleted[podname]:
            l = pods_deleted[podname]
 
total_time = (l - fr).total_seconds()
#total_time = 22320
print("First", fr, "last", l, "interval seconds = ", total_time)

#######################################################################
###BINNED CALCULATIONS#################################################
#######################################################################

interval=timedelta(seconds=BUCKET_SIZE)
start=fr
max_buckets = int(total_time / BUCKET_SIZE) + 1
grid=[start+n*interval for n in range(max_buckets)]
bins=collections.defaultdict(int)
for pod in pods_deleted.keys():
    #Add pods to the correct bucket
    idx = bisect(grid, pods_deleted[pod])
    bins[idx] += 1

bin_array = []
for idx in range(max_buckets):
    bin_array.append(bins[idx])

print("Stats - ", np.median(bin_array))

fig = plt.figure()
plt.plot(bin_array, label="Scheduling Rates Per Second")
fig.tight_layout()
#plt.ylim(0,60)
#plt.xlim(0,25000)
fig.savefig('attempting_pod_bind.pdf', dpi=fig.dpi, bbox_inches='tight')
plt.close()
