import csv
import numpy as np
import collections
import random
from matplotlib import pyplot as plt, rcParams
from collections import defaultdict
from palettable.colorbrewer.qualitative import Set2_7
from matplotlib.ticker import FormatStrFormatter

colors = Set2_7.mpl_colors
# function to add value labels
def addlabels(y, pos):
    for i in range(len(y)):
        #plt.text(i + pos,y[i], y[i], ha = 'center', Bbox = dict(facecolor = 'red', alpha =.8))
        plt.text(i + i*pos,y[i], "{:.2f}".format(y[i]), ha = 'right', fontsize='x-small', color='dimgray')

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

params = {
   'axes.labelsize': 10,
   'font.size': 10,
   'legend.fontsize': 10.5,
   'xtick.labelsize': 10,
   'ytick.labelsize': 10,
   'text.usetex': False,
   #'figure.figsize': [19.2, 4.8]
}
rcParams.update(params)
#Show Percentiles
percentiles=['50', '90', '99']
tps=['400', '1200', '2000']
x=np.arange(len(tps))
width=0.35
fig, ax = plt.subplots()
yc_50= [int(np.percentile(c[200], 50)), int(np.percentile(c[600], 50)), int(np.percentile(c[1000], 50))]
yd_50= [int(np.percentile(d[200], 50)), int(np.percentile(d[600], 50)), int(np.percentile(d[1000], 50))]
y=[((j)/i) for i,j in zip(yd_50, yc_50)]
rects1= ax.bar(x-width/3 + x, y, width, label="50th %ile", color=colors[0])
#addlabels(y, width)
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

yc_90= [int(np.percentile(c[200], 90)), int(np.percentile(c[600], 90)), int(np.percentile(c[1000], 90))]
yd_90= [int(np.percentile(d[200], 90)), int(np.percentile(d[600], 90)), int(np.percentile(d[1000], 90))]
y=[((j)/i) for i,j in zip(yd_90, yc_90)]
rects1= ax.bar(x + 2*width/3 + x, y, width, label="90th %ile",color=colors[2])
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

yc_99= [int(np.percentile(c[200], 99)), int(np.percentile(c[600], 99)), int(np.percentile(c[1000], 99))]
yd_99= [int(np.percentile(d[200], 99)), int(np.percentile(d[600], 99)), int(np.percentile(d[1000], 99))]
y=[((j)/i) for i,j in zip(yd_99, yc_99)]
rects1= ax.bar(x+ 5*width/3 + x, y, width, label="99th %ile",color=colors[4])
#addlabels(y,3)
#rects2= ax.bar(x+width/2 + 16, y, width, label="Decentralized 2000 TPS", color=colors[5])
#addlabels(y,16)


ax.set_ylabel("Relative JCT")
ax.grid(visible=True, axis='y', which='major')
plt.title("JCT in Kubernetes relative to Murmuration")
ax.set_xlabel("Tasks Per Second")
ax.set_xticks([0+2*width/3,2+2*width/3,4+2*width/3])
#ax.set_xticklabels(['200X', '400X', '600X', '800X', '1000X'])
ax.set_xticklabels(['400', '1200', '2000'])
#ax.set_ylim([25000, 45000])
ax.set_yticks([1.0])
ax.set_yticks([0.5, 1.0, 1.5], minor=True)
ax.tick_params(axis = 'y', which = 'both', labelsize = 10)
ax.yaxis.set_minor_formatter(FormatStrFormatter("%.1f"))
#plt.legend(fontsize='small', ncol=2, labelspacing=0.05)
plt.legend(fontsize='small', loc='best')
fig.tight_layout()
fig.savefig('jcts.pdf', dpi=fig.dpi, bbox_inches='tight')
plt.show()
