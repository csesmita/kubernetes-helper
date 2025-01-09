import re
from datetime import datetime, timedelta
import collections
from bisect import bisect
from matplotlib import pyplot as plt
import os
import numpy as np
from matplotlib import pyplot as plt, rcParams
from palettable.colorbrewer.qualitative import Set2_7
import matplotlib

matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42

colors = Set2_7.mpl_colors

params = {
   'axes.labelsize': 12,
   'font.size': 12,
   'legend.fontsize': 10,
   'xtick.labelsize': 12,
   'ytick.labelsize': 12,
   'text.usetex': False,
   'figure.figsize': [4.8, 1.8]
}
rcParams.update(params)


#Time width in seconds per bucket
BUCKET_SIZE = 1

pattern = '\w{3}\s*\d{1,2} \d{2}:\d{2}:\d{2}'
compiled = re.compile(pattern)
add_event_string = "Add event for unscheduled pod"

#files = ['results/jrt/unsaturated/syslog.d.5000J.50X.47N.10S.YH', 'results/jrt/unsaturated/syslog.d.5000J.60X.47N.10S.YH', 'results/jrt/unsaturated/syslog.d.5000J.70X.47N.10S.YH', 'results/syslog/syslog.c.10000J.200X.50N.2.YH', 'results/syslog/syslog.c.10000J.400X.50N.YH', 'results/syslog/syslog.c.10000J.600X.50N.YH', 'results/syslog/syslog.d.10000J.800X.50N.10S.YH', 'results/syslog/syslog.d.10000J.1000X.50N.10S.YH']
files = ['results/syslog/syslog.c.10000J.400X.50N.YH', 'results/jrt/unsaturated/syslog.d.5000J.50X.47N.10S.YH', 'results/syslog/syslog.d.10000J.1000X.50N.10S.YH', 'results/syslog/syslog.d.10000J.800X.50N.10S.YH']
rates = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
#names = ['50X', '60X', '70X', '200X', '400X', '600X', '800X', '1000X']
names = ['400X', '50X', '1000X', '800X']

style = [(0, (3, 5, 1, 5, 1, 5)), 'solid', 'dotted', (0, (5, 10)), 'dashed', (0, (5, 5)), 'dashdot', (5, (10, 3))]

fig = plt.figure()
for fidx in range(len(files)):
    filename = files[fidx]
    rate = rates[fidx]
    name = names[fidx]
    #Compare scheduling times.
    pods_added = {}
    fr= datetime.max
    lr=datetime.min
    f=""
    with open(filename, 'r') as f:
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
    final_pods = pods_added.keys()
    num_scheduled = len(final_pods)

    sched_time = (lr - fr).total_seconds()
    print("#################")
    print("File", filename)
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
        idx = bisect(grid, pods_added[pod])
        bins[idx] += 1

    #print("Num bins are ", len(bins.keys()), "with size of each bin being", BUCKET_SIZE)
    max_bin_val = bins[max(bins, key=bins.get)]
    min_bin_val = bins[min(bins, key=bins.get)]
    #print("Max bin value is", max_bin_val)
    print("Range:", max_bin_val - min_bin_val, "average:", tasks_per_sec)
    #print("Max tasks per sec is", max_bin_val / BUCKET_SIZE)


    ###############################################################
    bin_array = []
    for idx in range(max_buckets):
        bin_array.append(bins[idx])
    #print("Total tasks is", sum(bin_array))
    #print("Standard deviation is", np.std(bin_array))
    print("Percentiles of bin sizes - ", np.percentile(bin_array, 50),np.percentile(bin_array, 90), np.percentile(bin_array, 99))
    #print("BIN ARRAY")
    #print(len(bin_array))
    a = np.sort(bin_array)
    b = 1. * np.arange(len(a)) / (len(a) - 1)
    plt.plot(a,b, color=colors[fidx % 7], linewidth=2.5, linestyle=style[fidx], label=rate, markevery=[-1], marker='x', markersize=10, markerfacecolor=colors[fidx % 7],markeredgecolor=colors[fidx % 7])
    #plt.xticks([0,5000,10000,15000,20000])
    #plt.ylim(0,200)
    #plt.ylabel("CDF")
    #plt.ylim(0,10000)
plt.legend(ncol=4, loc='center right')
plt.xticks([0,100,200, 300, 400])
plt.yticks([0.0, 0.5, 1.0])
plt.ylim(0,1.1)
plt.xlabel("Unscheduled pods / second")
#plt.title("Arrival rate of unscheduled pods")
fig.tight_layout()
fig.savefig('pods_arrive_scheduler.pdf', dpi=fig.dpi, bbox_inches='tight')
plt.close()
