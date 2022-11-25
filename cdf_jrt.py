import csv
import numpy as np
import collections
import random
from matplotlib import pyplot as plt
from collections import defaultdict
from palettable.colorbrewer.qualitative import Set2_7

colors = Set2_7.mpl_colors
# function to add value labels
def addlabels(y, pos):
    for i in range(len(y)):
        #plt.text(i + pos,y[i], y[i], ha = 'center', Bbox = dict(facecolor = 'red', alpha =.8))
        plt.text(i + pos,y[i], y[i], ha = 'right', fontsize='x-small', color='dimgray')

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
yc_200= [int(np.percentile(c[200], 50)), int(np.percentile(c[200], 90)), int(np.percentile(c[200], 99))]
yd_200= [int(np.percentile(d[200], 50)), int(np.percentile(d[200], 90)), int(np.percentile(d[200], 99))]
y=[int(100*(j-i)/i) for i,j in zip(yd_200, yc_200)]
rects1= ax.bar(x-width/3 + x, y, width, label="Centralized 400 TPS", color=colors[0])
#addlabels(y, 1)
#rects2= ax.bar(x+width/2, y,  width, label="Decentralized 400 TPS", color=colors[1])
#addlabels(y, 0)

'''
y= [int(np.percentile(c[400], 50)), int(np.percentile(c[400], 90)), int(np.percentile(c[400], 99))]
rects1= ax.bar(x-width/2 + 4, y, width, label="Centralized 400X",)
addlabels(y,4)
y= [int(np.percentile(d[400], 50)), int(np.percentile(d[400], 90)), int(np.percentile(d[400], 99))]
rects2= ax.bar(x+width/2 + 4, y, width, label="Decentralized 400X")
addlabels(y,4)
'''

yc_600= [int(np.percentile(c[600], 50)), int(np.percentile(c[600], 90)), int(np.percentile(c[600], 99))]
yd_600= [int(np.percentile(d[600], 50)), int(np.percentile(d[600], 90)), int(np.percentile(d[600], 99))]
y=[int(100*(j-i)/i) for i,j in zip(yd_600, yc_600)]
rects1= ax.bar(x + 2*width/3 + x, y, width, label="Centralized 1200 TPS",color=colors[2])
#addlabels(y,2)
#rects2= ax.bar(x+width/2 + 8, y, width, label="Decentralized 1200 TPS", color=colors[3])
#addlabels(y,8)

'''
y= [int(np.percentile(c[800], 50)), int(np.percentile(c[800], 90)), int(np.percentile(c[800], 99))]
rects1= ax.bar(x-width/2 + 12, y, width, label="Centralized 800X",)
addlabels(y,12)
y= [int(np.percentile(d[800], 50)), int(np.percentile(d[800], 90)), int(np.percentile(d[800], 99))]
rects2= ax.bar(x+width/2 + 12, y, width, label="Decentralized 800X")
addlabels(y,12)
'''

yc_1000= [int(np.percentile(c[1000], 50)), int(np.percentile(c[1000], 90)), int(np.percentile(c[1000], 99))]
yd_1000= [int(np.percentile(d[1000], 50)), int(np.percentile(d[1000], 90)), int(np.percentile(d[1000], 99))]
y=[int(100*(j-i)/i) for i,j in zip(yd_1000, yc_1000)]
rects1= ax.bar(x+ 5*width/3 + x, y, width, label="Centralized 2000 TPS",color=colors[4])
#addlabels(y,3)
#rects2= ax.bar(x+width/2 + 16, y, width, label="Decentralized 2000 TPS", color=colors[5])
#addlabels(y,16)


ax.set_ylabel("Relative JCT")
plt.title("JCT in Kubernetes relative to Murmuration for Different Task Rates")
ax.set_xlabel("Percentiles")
ax.set_xticks([0+2*width/3,2+2*width/3,4+2*width/3])
#ax.set_xticklabels(['200X', '400X', '600X', '800X', '1000X'])
ax.set_xticklabels(['50th', '90th', '99th'])
#ax.set_ylim([25000, 45000])
#plt.legend(fontsize='small', ncol=2, labelspacing=0.05)
plt.legend(fontsize='small', loc='best')
fig.tight_layout()
fig.savefig('jcts.pdf', dpi=fig.dpi, bbox_inches='tight')
plt.show()
