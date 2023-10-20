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

c100 = []
cs100 = []
with open("c.2h.1000X.49N.YH", 'r') as f:
    for r in f:
        if "has JRT" not in r:
            continue
        r= r.split()
        jrt = float(r[6])
        c100.append(jrt)
with open("c.2h.1000X.49N.YH.stragglers", 'r') as f:
    for r in f:
        if "has JRT" not in r:
            continue
        r= r.split()
        jrt = float(r[6])
        cs100.append(jrt)

params = {
   'axes.labelsize': 16,
   'font.size': 16,
   'legend.fontsize': 12,
   'xtick.labelsize': 16,
   'ytick.labelsize': 16,
   'text.usetex': False,
   'figure.figsize': [6,3.4]
}
rcParams.update(params)
print(np.percentile(c100, 50), np.percentile(c100, 99))
print(np.percentile(cs100, 50), np.percentile(cs100, 99))

fig, ax = plt.subplots()
c = np.sort(c100)
cp = 1. * np.arange(len(c)) / (len(c) - 1)
ax.plot(c, cp,'b', label="Kubernetes", linewidth=3, color=colors[0])
d = np.sort(cs100)
dp = 1. * np.arange(len(d)) / (len(d) - 1)
ax.plot(d, dp, label="Kubernetes with Stragglers", linewidth=3, color=colors[1], linestyle="dashdot")
ax.set_ylabel('JCT')
ax.set_xlabel('Duration (seconds)')
legend = ax.legend()
frame = legend.get_frame()
frame.set_facecolor('1.0')
frame.set_edgecolor('1.0')
fig.tight_layout()
fig.savefig('c_stragglers_1000.pdf', dpi=fig.dpi, bbox_inches='tight')

