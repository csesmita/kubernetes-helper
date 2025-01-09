import csv
import numpy as np
import collections
import random
from matplotlib import pyplot as plt, rcParams
from collections import defaultdict
from palettable.colorbrewer.qualitative import Pastel2_7
from matplotlib.ticker import FormatStrFormatter

colors = Pastel2_7.mpl_colors
# function to add value labels
def addlabels(ax, y, pos):
    for i in range(len(y)):
        ax.text(pos + i*0.35,y[i], "{:.2f}".format(y[i]), ha = 'right', fontsize='x-small', color='dimgray')

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
   'axes.labelsize': 16,
   'font.size': 16,
   'legend.fontsize': 14,
   'xtick.labelsize': 16,
   'ytick.labelsize': 16,
   'text.usetex': False,
}
rcParams.update(params)
#Show Percentiles
percentiles=['Murmuration', 'Kubernetes']
tps=['400', '1200', '2000']
x=np.arange(len(tps))
width=0.35
y_99_d=[int(np.percentile(d[200], 50)), int(np.percentile(d[600], 50)), int(np.percentile(d[1000], 50))]
y_99_c=[int(np.percentile(c[200], 50)), int(np.percentile(c[600], 50)), int(np.percentile(c[1000], 50))]
fig, ax = plt.subplots()
ax.bar(x-width/2, y_99_c, width, label="Kubernetes", color=colors[1])
ax.bar(x+width/2, y_99_d, width, label="Murmuration", color=colors[0])
labels=[(i/j) for i,j in zip(y_99_d, y_99_c)]
#addlabels(ax, y, x-width/2)
ax.set_xlabel("Tasks Per Second")
ax.set_xticks([0,1,2])
ax.set_xticklabels(tps)
rects = ax.patches[3:6]
for rect in ax.patches:
    print(rect.get_x())
#for i in range(len(y)):
for rect,label in zip(rects, labels):
    height = rect.get_height()
    #ax.text(i+ width/2, s="{:.2f}".format(y[i]), fontsize='small', color='dimgray')
    ax.text(rect.get_x() + rect.get_width() / 2, height + 5, "{:.2f}".format(label), ha="center", va="bottom")

ax.set_ylabel("$JCT$ (seconds)")
ax.set_ylim(15000, 45000)
ax.set_yticks([15000, 30000, 45000])
plt.legend(loc='upper left', ncol=2)
fig.tight_layout()
fig.savefig('jcts_50.pdf', dpi=fig.dpi, bbox_inches='tight')
