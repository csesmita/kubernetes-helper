import numpy as np
from matplotlib import pyplot as plt, rcParams
from collections import defaultdict
from palettable.colorbrewer.qualitative import Set2_7
from datetime import datetime
import re
import os

colors = Set2_7.mpl_colors

def extractDateTime(timestr):
    return datetime.strptime(timestr,'%b %d %H:%M:%S')

pattern = '\w{3}\s*\d{1,2} \d{2}:\d{2}:\d{2}'
compiled = re.compile(pattern)
activePods = []
start_time = 0
#all_num_pods = []
num_pods_over_time = {}

for filename in os.listdir('/local/scratch/eva3'):
    with open(os.path.join('/local/scratch/eva3', 'node28'), 'r') as f:
        times_sampled = set()
        for r in f:
            try:
                num_pods = int(r.split("active pods")[1].split("int=")[1].split(")")[0])
            except:
                continue
            log_time = extractDateTime(compiled.search(r).group(0)).replace(year=2023).timestamp()
            print(log_time)
            if log_time in times_sampled:
                continue
            times_sampled.add(log_time)
            if start_time == 0:
                start_time = log_time
            time_elapsed = log_time - start_time
            if time_elapsed not in num_pods_over_time.keys():
                num_pods_over_time[time_elapsed] = 0
            num_pods_over_time[time_elapsed] += num_pods
            #all_num_pods.append(num_pods)
        break

for timekey in sorted(num_pods_over_time.keys()):
    print(timekey, num_pods_over_time[timekey])
    #num_pods_over_time[timekey] /= (110 * 49)
fig, ax_tail = plt.subplots()
num_pods_over_time = sorted(num_pods_over_time.items())
x,y = zip(*num_pods_over_time)
print("Active Pods' Utilization", np.percentile(y, 50), np.percentile(y, 90), np.percentile(y, 99))
l1, = ax_tail.plot(x, y, label="Number of Active Pods", linewidth=2, color=colors[0])
ax_tail.set_ylabel('Number of pods', color=colors[0])
legend = plt.legend([l1], ["Number of Active Pods"], framealpha=0.5)
frame = legend.get_frame()
frame.set_facecolor('1.0')
frame.set_edgecolor('1.0')
fig.tight_layout()
fig.savefig('kq.pdf', dpi=fig.dpi, bbox_inches='tight')
