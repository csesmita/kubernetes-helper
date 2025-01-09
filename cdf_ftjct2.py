import csv
import numpy as np
import collections
import random
from matplotlib import pyplot as plt, rcParams
from collections import defaultdict
from palettable.colorbrewer.qualitative import Pastel2_7
from bisect import bisect
import os

colors = Pastel2_7.mpl_colors
params = {
   'axes.labelsize': 14,
   #'font.size': 10,
   'legend.fontsize': 14,
   'xtick.labelsize': 14,
   'ytick.labelsize': 14,
   'text.usetex': False,
   'figure.figsize': [6.4, 3.6]
}
rcParams.update(params)

affected_jobs = [["job10"],["job8", "job11"], ["job12","job14","job16"], ["job6", "job7"]]
jct_systems = defaultdict(dict)
jct_jobids= defaultdict(dict)
dirname="./results/ft/jrt/"
for filename in os.listdir(dirname):
    affected_job_index = 0
    if "normal" in filename:
        system = 0
        affected_job_index = int((filename.split("normal"))[1]) - 1
    else:
        system = 1
        affected_job_index = int((filename.split("delete"))[1]) - 1
    with open(os.path.join(dirname, filename), 'r') as infile:
        #print("Processing", filename)
        for line in infile:
            if "has JRT" not in line:
                continue
            line = line.split()
            jobid = line[1]
            if jobid not in affected_jobs[affected_job_index]:
                continue
            jobid = int((jobid.split("job"))[1])
            if jobid not in jct_jobids.keys():
                jct_jobids[jobid] = []
            completion_time = float(line[4])
            jct_systems[system][jobid] = completion_time
            jct_jobids[jobid].append(completion_time)

print(jct_jobids)
rel_jct = []
print("Differences - ")
for jobid in jct_jobids.keys():
	rel_jct.append(100*(jct_systems[1][jobid] - jct_systems[0][jobid])/jct_systems[0][jobid])
	print(jct_systems[1][jobid] - jct_systems[0][jobid])

print("-----")
print(sum(rel_jct)/len(rel_jct))
print(np.mean(rel_jct))
print(np.median(rel_jct))
print(np.std(rel_jct))
print(min(rel_jct))
print(max(rel_jct))
'''
mean_system = {}
fig, ax1 = plt.subplots()
systems=["No Failures", "Scheduler 1 Fails"]
for system in reversed(range(len(systems))):
    mean = []
    #std = []
    jobids = []
    for jobid in sorted(jct_systems[system].keys()):
print(sum(rel_jct)/len(rel_jct))
print(sum(rel_jct)/len(rel_jct))
        mean.append(np.mean(jct_systems[system][jobid], axis=0))
        #std.append(np.std(jct_systems[system][jobid], axis=0))
        jobids.append("job" + str(jobid))
    #Plot the mean of the runs
    mean = np.array(mean)
    #std = np.array(std)
    ax1.plot(jobids, mean, label=systems[system], color=colors[system], linewidth=2,  alpha=0.5)
    #Plot the std
    #ax1.fill_between(jobids,mean+std, mean-std, facecolor=colors[system], alpha=0.4)
    mean_system[system] = mean
    print(jobids, mean)
    print(systems[system], ":50th", np.percentile(mean, 50), "99th", np.percentile(mean, 99))
ax1.set_xlabel("Job Ids")
ax1.set_ylabel("Job Completion Time (s)")
ax1.legend()
fig.savefig('ftjct_means_failed_jobs.pdf', dpi=fig.dpi, bbox_inches='tight')
'''
