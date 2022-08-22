import csv
import numpy as np
import collections
import random
from matplotlib import pyplot as plt
from collections import defaultdict

# function to add value labels
def addlabels(y, pos):
    for i in range(len(y)):
        plt.text(i + pos,y[i], y[i], ha = 'center', Bbox = dict(facecolor = 'red', alpha =.8))

c=collections.defaultdict(list)
with open("results/jrt/c.10000J.200X.50N.YH", 'r') as f:
    for r in f:
        if "has JRT" not in r:
            continue
        r= r.split()
        jrt = float(r[4])
        c[200].append(jrt)
with open("results/jrt/c.10000J.400X.50N.YH", 'r') as f:
    for r in f:
        if "has JRT" not in r:
            continue
        r= r.split()
        jrt = float(r[4])
        c[400].append(jrt)
with open("results/jrt/c.10000J.600X.50N.YH", 'r') as f:
    for r in f:
        if "has JRT" not in r:
            continue
        r= r.split()
        jrt = float(r[4])
        c[600].append(jrt)
with open("results/jrt/c.10000J.800X.50N.YH", 'r') as f:
    for r in f:
        if "has JRT" not in r:
            continue
        r= r.split()
        jrt = float(r[4])
        c[800].append(jrt)
with open("results/jrt/c.10000J.1000X.50N.YH", 'r') as f:
    for r in f:
        if "has JRT" not in r:
            continue
        r= r.split()
        jrt = float(r[4])
        c[1000].append(jrt)

d=collections.defaultdict(list)
with open("results/jrt/d.10000J.200X.50N.10S.YH", 'r') as f:
    for r in f:
        if "has JRT" not in r:
            continue
        r= r.split()
        jrt = float(r[4])
        d[200].append(jrt)
with open("results/jrt/d.10000J.400X.50N.10S.YH", 'r') as f:
    for r in f:
        if "has JRT" not in r:
            continue
        r= r.split()
        jrt = float(r[4])
        d[400].append(jrt)
with open("results/jrt/d.10000J.600X.50N.10S.YH", 'r') as f:
    for r in f:
        if "has JRT" not in r:
            continue
        r= r.split()
        jrt = float(r[4])
        d[600].append(jrt)
with open("results/jrt/d.10000J.800X.50N.10S.YH", 'r') as f:
    for r in f:
        if "has JRT" not in r:
            continue
        r= r.split()
        jrt = float(r[4])
        d[800].append(jrt)
with open("results/jrt/d.10000J.1000X.50N.10S.YH", 'r') as f:
    for r in f:
        if "has JRT" not in r:
            continue
        r= r.split()
        jrt = float(r[4])
        d[1000].append(jrt)


#Show Percentiles
percentiles=['50', '90', '99']
x=np.arange(len(percentiles))
width=0.35
fig, ax = plt.subplots()
y= [int(np.percentile(c[200], 50)), int(np.percentile(c[200], 90)), int(np.percentile(c[200], 99))]
rects1= ax.bar(x-width/2, y, width, label="Centralized 200X",)
addlabels(y, 0)
y= [int(np.percentile(d[200], 50)), int(np.percentile(d[200], 90)), int(np.percentile(d[200], 99))]
rects2= ax.bar(x+width/2, y,  width, label="Decentralized 200X")
addlabels(y, 0)

y= [int(np.percentile(c[400], 50)), int(np.percentile(c[400], 90)), int(np.percentile(c[400], 99))]
rects1= ax.bar(x-width/2 + 4, y, width, label="Centralized 400X",)
addlabels(y,4)
y= [int(np.percentile(d[400], 50)), int(np.percentile(d[400], 90)), int(np.percentile(d[400], 99))]
rects2= ax.bar(x+width/2 + 4, y, width, label="Decentralized 400X")
addlabels(y,4)

y= [int(np.percentile(c[600], 50)), int(np.percentile(c[600], 90)), int(np.percentile(c[600], 99))]
rects1= ax.bar(x-width/2 + 8, y, width, label="Centralized 600X",)
addlabels(y,8)
y= [int(np.percentile(d[600], 50)), int(np.percentile(d[600], 90)), int(np.percentile(d[600], 99))]
rects2= ax.bar(x+width/2 + 8, y, width, label="Decentralized 600X")
addlabels(y,8)

y= [int(np.percentile(c[800], 50)), int(np.percentile(c[800], 90)), int(np.percentile(c[800], 99))]
rects1= ax.bar(x-width/2 + 12, y, width, label="Centralized 800X",)
addlabels(y,12)
y= [int(np.percentile(d[800], 50)), int(np.percentile(d[800], 90)), int(np.percentile(d[800], 99))]
rects2= ax.bar(x+width/2 + 12, y, width, label="Decentralized 800X")
addlabels(y,12)

y= [int(np.percentile(c[1000], 50)), int(np.percentile(c[1000], 90)), int(np.percentile(c[1000], 99))]
rects1= ax.bar(x-width/2 + 16, y, width, label="Centralized 1000X",)
addlabels(y,16)
y= [int(np.percentile(d[1000], 50)), int(np.percentile(d[1000], 90)), int(np.percentile(d[1000], 99))]
rects2= ax.bar(x+width/2 + 16, y, width, label="Decentralized 1000X")
addlabels(y,16)

ax.set_ylabel("JRT for Centralized and Decentralized Schedulers for Different Speedup Rates for 10000 Jobs")
ax.set_xticks([1,5,9,13,17])
ax.set_xticklabels(['200X', '400X', '600X', '800X', '1000X'])
ax.set_ylim([25000, 45000])
ax.legend()
fig.tight_layout()
plt.show()
