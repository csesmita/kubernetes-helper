import csv
import numpy as np
import collections
import random
from matplotlib import pyplot as plt, rcParams
from collections import defaultdict
from palettable.colorbrewer.qualitative import Pastel2_7
from matplotlib.ticker import FormatStrFormatter

import matplotlib
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42


colors = Pastel2_7.mpl_colors
# function to add value labels
def addlabels(ax, y, pos):
    for i in range(len(y)):
        ax.text(pos + i*0.35,y[i], "{:.2f}".format(y[i]), ha = 'right', fontsize='x-small', color='dimgray')

c200 = []
c600 = []
c800 = []
c1000 = []
d200 = []
d600 = []
d800 = []
d1000 = []
with open("results/jrt/c.10000J.200X.50N.YH", 'r') as f:
    for r in f:
        if "has JRT" not in r:
            continue
        r= r.split()
        jrt = float(r[4])
        c200.append(jrt)
with open("results/jrt/c.10000J.600X.50N.YH", 'r') as f:
    for r in f:
        if "has JRT" not in r:
            continue
        r= r.split()
        jrt = float(r[4])
        c600.append(jrt)
with open("results/jrt/c.10000J.800X.50N.YH", 'r') as f:
    for r in f:
        if "has JRT" not in r:
            continue
        r= r.split()
        jrt = float(r[4])
        c800.append(jrt)
with open("results/jrt/c.10000J.1000X.50N.YH", 'r') as f:
    for r in f:
        if "has JRT" not in r:
            continue
        r= r.split()
        jrt = float(r[4])
        c1000.append(jrt)

d=collections.defaultdict(list)
with open("results/jrt/d.10000J.200X.50N.10S.YH", 'r') as f:
    for r in f:
        if "has JRT" not in r:
            continue
        r= r.split()
        jrt = float(r[4])
        d200.append(jrt)
with open("results/jrt/d.10000J.800X.50N.10S.YH", 'r') as f:
    for r in f:
        if "has JRT" not in r:
            continue
        r= r.split()
        jrt = float(r[4])
        d800.append(jrt)
with open("results/jrt/d.10000J.600X.50N.10S.YH", 'r') as f:
    for r in f:
        if "has JRT" not in r:
            continue
        r= r.split()
        jrt = float(r[4])
        d600.append(jrt)
with open("results/jrt/d.10000J.1000X.50N.10S.YH", 'r') as f:
    for r in f:
        if "has JRT" not in r:
            continue
        r= r.split()
        jrt = float(r[4])
        d1000.append(jrt)
params = {
   'axes.labelsize': 14,
   'font.size': 12,
   'legend.fontsize': 12,
   'xtick.labelsize': 16,
   'ytick.labelsize': 16,
   'text.usetex': False,
   'figure.figsize': [4.2, 1.8]
   #'figure.figsize': [6,3.4]
}
rcParams.update(params)

fig, ax = plt.subplots()
c = np.sort(c200)
cp = 1. * np.arange(len(c)) / (len(c) - 1)
ax.plot(c, cp,'b', label="Kubernetes", linewidth=3, color=colors[1])
d = np.sort(d200)
dp = 1. * np.arange(len(d)) / (len(d) - 1)
ax.plot(d, dp, label="Murmuration", linewidth=3, color=colors[0], linestyle="dashed")
ax.set_ylabel('CDF')
ax.set_xlabel('Duration (seconds)')
ax.set_xticks([0, 25000, 50000, 75000])
ax.set_yticks([0.0, 0.5, 1.0])
legend = ax.legend()
frame = legend.get_frame()
frame.set_facecolor('1.0')
frame.set_edgecolor('1.0')
#fig.tight_layout()
fig.savefig('cd400.pdf', dpi=fig.dpi, bbox_inches='tight')


fig, ax = plt.subplots()
c = np.sort(c600)
cp = 1. * np.arange(len(c)) / (len(c) - 1)
ax.plot(c, cp,'b', label="Kubernetes", linewidth=3, color=colors[0])
d = np.sort(d600)
dp = 1. * np.arange(len(d)) / (len(d) - 1)
ax.plot(d, dp, label="Murmuration", linewidth=3, color=colors[1])
ax.set_ylabel('CDF')
ax.set_xlabel('Duration (seconds)')
legend = ax.legend()
frame = legend.get_frame()
frame.set_facecolor('1.0')
frame.set_edgecolor('1.0')
fig.tight_layout()
fig.savefig('cd1200.pdf', dpi=fig.dpi, bbox_inches='tight')

fig, ax = plt.subplots()
c = np.sort(c800)
cp = 1. * np.arange(len(c)) / (len(c) - 1)
ax.plot(c, cp,'b', label="Kubernetes", linewidth=3, color=colors[1])
d = np.sort(d800)
dp = 1. * np.arange(len(d)) / (len(d) - 1)
ax.plot(d, dp, label="Murmuration", linewidth=3, color=colors[0], linestyle="dashed")
print("Kubernetes", np.percentile(c800, 50), np.percentile(c800, 100))
print("Murmuration", np.percentile(d800, 50), np.percentile(d800, 100))
#ax.set_ylabel('CDF')
ax.set_xlabel('Duration (seconds)')
ax.set_xticks([0, 25000, 50000])
ax.set_yticks([0.0, 0.5, 1.0])
#ax.set_ylabel('CDF')
legend = ax.legend(loc="lower right")
frame = legend.get_frame()
frame.set_facecolor('1.0')
frame.set_edgecolor('1.0')
#fig.tight_layout()
fig.savefig('cd1600.pdf', dpi=fig.dpi, bbox_inches='tight')



fig, ax = plt.subplots()
c = np.sort(c1000)
print("2000X")
print("Kubernetes", np.percentile(c1000, 50), np.percentile(c1000, 100))
print("Murmuration", np.percentile(d1000, 50), np.percentile(d1000, 100))
cp = 1. * np.arange(len(c)) / (len(c) - 1)
ax.plot(c, cp,'b', label="Kubernetes", linewidth=3, color=colors[1])
d = np.sort(d1000)
dp = 1. * np.arange(len(d)) / (len(d) - 1)
ax.plot(d, dp, label="Murmuration", linewidth=3, color=colors[0], linestyle="dashed")
ax.set_xticks([0, 25000, 50000])
#ax.set_ylabel('CDF')
ax.set_xlabel('Duration (seconds)')
ax.set_yticks([0.0, 0.5, 1.0])
legend = ax.legend(loc="lower right")
frame = legend.get_frame()
frame.set_facecolor('1.0')
frame.set_edgecolor('1.0')
#fig.tight_layout()
fig.savefig('cd2000.pdf', dpi=fig.dpi, bbox_inches='tight')
