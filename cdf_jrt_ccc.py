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
with open("results/jrt/c.1800J.1000X.35N.CCc", 'r') as f:
    for r in f:
        if "has JRT" not in r:
            continue
        r= r.split()
        jrt = float(r[4])
        c[1000].append(jrt)
d=collections.defaultdict(list)
with open("results/jrt/d.1800J.1000X.35N.10S.CCc", 'r') as f:
    for r in f:
        if "has JRT" not in r:
            continue
        r= r.split()
        jrt = float(r[4])
        d[1000].append(jrt)

params = {
   'axes.labelsize': 14,
   'font.size': 14,
   'legend.fontsize': 14,
   'xtick.labelsize': 14,
   'ytick.labelsize': 14,
   'text.usetex': False,
}
rcParams.update(params)
#Show Percentiles
percentiles=['Murmuration', 'Kubernetes']
tps=['2000']
x=np.arange(len(tps))
width=0.35
y_99_d=[int(np.percentile(d[1000], 99))]
y_99_c=[int(np.percentile(c[1000], 99))]
fig, ax = plt.subplots()
ax.bar(x+width/2, y_99_c, width, label="Kubernetes", color=colors[0])
ax.bar(x-width/2, y_99_d, width, label="Murmuration", color=colors[1])
y_d = [int(np.percentile(d[1000], 99))]
y_c = [int(np.percentile(c[1000], 99))]
labels=[((j)/i) for i,j in zip(y_d, y_c)]
#addlabels(ax, y, x-width/2)
ax.set_xlabel("Tasks Per Second")
ax.set_xticks([0])
ax.set_xticklabels(tps)

ax.set_ylabel("Job Completion Time (s)")

plt.legend(fontsize='small', loc='upper center')
fig.tight_layout()
fig.savefig('jcts_ccc.pdf', dpi=fig.dpi, bbox_inches='tight')
