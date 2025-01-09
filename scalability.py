import re
from datetime import datetime, timedelta
import collections
from bisect import bisect
from matplotlib import pyplot as plt
import os

#Time width in seconds per bucket
BUCKET_SIZE = 1

fname = '/local/scratch/etcd_defaults.100Xpod.100N'
for filename in os.listdir(fname):
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
    f=""

    if filename != '10S.1cpupersched.NRL':
        continue

    #Compare scheduling times.
    with open(os.path.join(fname, filename), 'r') as f:
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
    print("Pods with add and no delete statement", len(list(set(pods_added.keys()) - set(pods_bound.keys()))))
    print("Pods with delete and no add statement", len(list(set(pods_bound.keys()) - set(pods_added.keys()))))
    final_pods = set(pods_added.keys()).intersection(set(pods_bound.keys()))
    num_scheduled = len(final_pods)

    sched_time = (l - fr).total_seconds()
    print("File", f)
    print("First unscheduled pod add event", fr, "and last unscheduled pod add event", lr)
    print("First bound pod event",b , "and last bound pod event", l)
    tasks_per_sec = num_scheduled / sched_time
    print("Total Tasks Scheduled is ", num_scheduled, "in time", sched_time)
    print("Tasks per sec" , tasks_per_sec)

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
    fig.savefig(filename + '_100X.pdf', dpi=fig.dpi, bbox_inches='tight')
    plt.close()
    print("#################")
