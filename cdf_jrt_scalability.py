import csv
import numpy as np
import collections
import random
from matplotlib import pyplot as plt
from collections import defaultdict

width=0.33
# function to add value labels
def addlabels(y, pos):
    for i in range(len(y)):
        plt.text(i -width + pos,y[i], y[i], ha = 'center', Bbox = dict(facecolor = 'red', alpha =.8))

d=collections.defaultdict(list)
with open("results/jrt/d.10000J.1000X.50N.10S.YH", 'r') as f:
    for r in f:
        if "has JRT" not in r:
            continue
        r= r.split()
        jrt = float(r[4])
        d[10].append(jrt)
with open("results/jrt/d.10000J.1000X.50N.20S.YH", 'r') as f:
    for r in f:
        if "has JRT" not in r:
            continue
        r= r.split()
        jrt = float(r[4])
        d[20].append(jrt)
with open("results/jrt/d.10000J.1000X.50N.50S.YH", 'r') as f:
    for r in f:
        if "has JRT" not in r:
            continue
        r= r.split()
        jrt = float(r[4])
        d[50].append(jrt)

#Show Percentiles
percentiles=['50', '90', '99']
x=np.arange(len(percentiles))
fig, ax = plt.subplots()
y= [int(np.percentile(d[10], 50)), int(np.percentile(d[10], 90)), int(np.percentile(d[10], 99))]
rects1= ax.bar(x-width, y, width, label="Decentralized 10S",)
addlabels(y, 0)
y= [int(np.percentile(d[20], 50)), int(np.percentile(d[20], 90)), int(np.percentile(d[20], 99))]
rects2= ax.bar(x, y,  width, label="Decentralized 20S")
addlabels(y, width)
y= [int(np.percentile(d[50], 50)), int(np.percentile(d[50], 90)), int(np.percentile(d[50], 99))]
rects1= ax.bar(x+(width), y, width, label="Decentralized 50S",)
addlabels(y,2*width)

ax.set_ylabel("JRT for Different Number of Schedulers for X1000 Speedup for 10000 Jobs")
ax.set_xticks([0,1,2])
ax.set_xticklabels(['50th', '90th', '99th'])
ax.set_ylim([25000, 45000])
ax.legend()
fig.tight_layout()
plt.show()
