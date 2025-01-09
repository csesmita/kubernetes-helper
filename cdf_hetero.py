import csv
import numpy as np
import collections
import random
from matplotlib import pyplot as plt, rcParams
from collections import defaultdict
from palettable.colorbrewer.qualitative import Set2_7

colors = Set2_7.mpl_colors
###########################################################################
# The first part of the script analyzes the job response time.
###########################################################################
c=[]
d=[]
jobids=[]
jobid = 0
discardjobs=[]
for i in range(1,501):
	discardjobs.append("job"+str(i))
with open("results/hetero/jrt/c.2000J.1000X.50N.YH", 'r') as f:
    for r in f:
        if "has JRT" not in r:
            continue
        r= r.split()
        jobname = r[1]
        if jobname in discardjobs:
            continue
        jrt = float(r[4])
        c.append(jrt)
        jobid += 1
        jobids.append(jobid)
with open("results/hetero/jrt/d.2000J.1000X.50N.10S.YH.hetero", 'r') as f:
    for r in f:
        if "has JRT" not in r:
            continue
        r = r.split()
        jobname = r[1]
        if jobname in discardjobs:
            continue
        jrt = float(r[4])
        d.append(jrt)
params = {
   'axes.labelsize': 12,
   'font.size': 12,
   'legend.fontsize': 12,
   'xtick.labelsize': 12,
   'ytick.labelsize': 12,
   'text.usetex': False,
   #'figure.figsize': [10, 3]
}
rcParams.update(params)

assert(len(c) == len(d))
#Show raw unsorted data
fig, ax = plt.subplots()
ax.plot(jobids, c, 'b', label="Centralized")
ax.plot(jobids, d, 'r--', label="Decentralized")
ax.set_xlabel('Job Ids')
ax.set_ylabel('Job Response Times Raw Data')
ax.set_title('JRT Raw Data')
ax.legend()
fig.savefig('cdf_hetero.pdf', dpi=fig.dpi, bbox_inches='tight')

print(np.percentile(c,50))
print(np.percentile(d,50))
