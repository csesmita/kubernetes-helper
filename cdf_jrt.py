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
def addlabels(ax, y, pos):
    for i in range(len(y)):
        plt.text(2 + 3*i*pos,y[i], "{:.2f}".format(y[i]), ha = 'right', fontsize='x-small', color='dimgray')

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
percentiles=['Murmuration', 'Kubernetes']
#tps=['400', '1200', '2000']
x=np.arange(len(percentiles))
width=0.35


fig, (ax, ax_b) = plt.subplots(2, 1, gridspec_kw=dict(height_ratios=[4,1]), sharex=True)
#fig, ax = plt.subplots()
y_50= [int(np.percentile(d[200], 50)), int(np.percentile(c[200], 50))]
y_90= [int(np.percentile(d[200], 90)), int(np.percentile(c[200], 90))]
y_99= [int(np.percentile(d[200], 99)), int(np.percentile(c[200], 99))]
y_d = [int(np.percentile(d[200], 50)), int(np.percentile(d[200], 90)), int(np.percentile(d[200], 99))]
y_c = [int(np.percentile(c[200], 50)), int(np.percentile(c[200], 90)), int(np.percentile(c[200], 99))]
y=[((j)/i) for i,j in zip(y_d, y_c)]
#addlabels(ax, y, width/3)
rects1= ax.bar(x-width/3 + x, y_50, width, label="50th %ile", color=colors[0])
rects2= ax.bar(x+2*width/3 + x, y_90, width, label="90th %ile", color=colors[1])
rects3= ax.bar(x+5*width/3 + x, y_99, width, label="99th %ile", color=colors[2])
rects1= ax_b.bar(x-width/3 + x, y_50, width, label="50th %ile", color=colors[0])
rects2= ax_b.bar(x+2*width/3 + x, y_90, width, label="90th %ile", color=colors[1])
rects3= ax_b.bar(x+5*width/3 + x, y_99, width, label="99th %ile", color=colors[2])
for i in range(len(y)):
    plt.text(2 + 3*i*width/3 - width/3,y[i], "{:.2f}".format(y[i]), fontsize='x-small', color='dimgray')

ax.set_ylabel("Job Completion Time (s)")
ax.set_ylim(25000, 45000)
ax_b.set_ylim(0,5000)
ax.spines['bottom'].set_visible(False)
ax_b.spines['top'].set_visible(False)
ax.xaxis.tick_top()
ax.tick_params(labeltop=False)
ax_b.xaxis.tick_bottom()
#ax.set_xlabel("Tasks Per Second")
ax_b.set_xticks([0+2*width/3,2+2*width/3])
ax_b.set_xticklabels(percentiles)

dw=0.005
kwargs = dict(transform=ax.transAxes, color='k', clip_on=False)
ax.plot((-dw, +dw), (-dw, +dw), **kwargs)
ax.plot((1 - dw, 1 + dw), (-dw, +dw), **kwargs) 

kwargs.update(transform=ax_b.transAxes) 
ax_b.plot((-dw, +dw), (1 - dw, 1 + dw), **kwargs)
ax_b.plot((1 - dw, 1 + dw), (1 - dw, 1 + dw), **kwargs)
ax_b.set_yticks([0,5000])
ax.set_yticks([25000, 30000, 35000, 40000, 45000])
plt.legend(fontsize='small', loc='upper center')
fig.tight_layout()
fig.savefig('jcts1.pdf', dpi=fig.dpi, bbox_inches='tight')

fig, (ax, ax_b) = plt.subplots(2, 1, gridspec_kw=dict(height_ratios=[4,1]), sharex=True)
#fig, ax = plt.subplots()
y_50= [int(np.percentile(d[600], 50)), int(np.percentile(c[600], 50))]
y_90= [int(np.percentile(d[600], 90)), int(np.percentile(c[600], 90))]
y_99= [int(np.percentile(d[600], 99)), int(np.percentile(c[600], 99))]
y_d = [int(np.percentile(d[600], 50)), int(np.percentile(d[600], 90)), int(np.percentile(d[600], 99))]
y_c = [int(np.percentile(c[600], 50)), int(np.percentile(c[600], 90)), int(np.percentile(c[600], 99))]
y=[((j)/i) for i,j in zip(y_d, y_c)]
#addlabels(ax, y, width/3)
rects1= ax.bar(x-width/3 + x, y_50, width, label="50th %ile", color=colors[0])
rects2= ax.bar(x+2*width/3 + x, y_90, width, label="90th %ile", color=colors[1])
rects3= ax.bar(x+5*width/3 + x, y_99, width, label="99th %ile", color=colors[2])
rects1= ax_b.bar(x-width/3 + x, y_50, width, label="50th %ile", color=colors[0])
rects2= ax_b.bar(x+2*width/3 + x, y_90, width, label="90th %ile", color=colors[1])
rects3= ax_b.bar(x+5*width/3 + x, y_99, width, label="99th %ile", color=colors[2])
for i in range(len(y)):
    plt.text(2 + 3*i*width/3 - width/3,y[i], "{:.2f}".format(y[i]), fontsize='x-small', color='dimgray')

ax.set_ylabel("Job Completion Time (s)")
ax.set_ylim(25000, 45000)
ax_b.set_ylim(0,5000)
ax.spines['bottom'].set_visible(False)
ax_b.spines['top'].set_visible(False)
ax.xaxis.tick_top()
ax.tick_params(labeltop=False)
ax_b.xaxis.tick_bottom()
#ax.set_xlabel("Tasks Per Second")
ax_b.set_xticks([0+2*width/3,2+2*width/3])
ax_b.set_xticklabels(percentiles)

dw=0.005
kwargs = dict(transform=ax.transAxes, color='k', clip_on=False)
ax.plot((-dw, +dw), (-dw, +dw), **kwargs)
ax.plot((1 - dw, 1 + dw), (-dw, +dw), **kwargs) 

kwargs.update(transform=ax_b.transAxes) 
ax_b.plot((-dw, +dw), (1 - dw, 1 + dw), **kwargs)
ax_b.plot((1 - dw, 1 + dw), (1 - dw, 1 + dw), **kwargs)
ax_b.set_yticks([0,5000])
ax.set_yticks([25000, 30000, 35000, 40000, 45000])
plt.legend(fontsize='small', loc='upper center')
fig.tight_layout()
fig.savefig('jcts2.pdf', dpi=fig.dpi, bbox_inches='tight')

fig, (ax, ax_b) = plt.subplots(2, 1, gridspec_kw=dict(height_ratios=[4,1]), sharex=True)
#fig, ax = plt.subplots()
y_50= [int(np.percentile(d[1000], 50)), int(np.percentile(c[1000], 50))]
y_90= [int(np.percentile(d[1000], 90)), int(np.percentile(c[1000], 90))]
y_99= [int(np.percentile(d[1000], 99)), int(np.percentile(c[1000], 99))]
y_d = [int(np.percentile(d[1000], 50)), int(np.percentile(d[1000], 90)), int(np.percentile(d[1000], 99))]
y_c = [int(np.percentile(c[1000], 50)), int(np.percentile(c[1000], 90)), int(np.percentile(c[1000], 99))]
y=[((j)/i) for i,j in zip(y_d, y_c)]
#addlabels(ax, y, width/3)
rects1= ax.bar(x-width/3 + x, y_50, width, label="50th %ile", color=colors[0])
rects2= ax.bar(x+2*width/3 + x, y_90, width, label="90th %ile", color=colors[1])
rects3= ax.bar(x+5*width/3 + x, y_99, width, label="99th %ile", color=colors[2])
rects1= ax_b.bar(x-width/3 + x, y_50, width, label="50th %ile", color=colors[0])
rects2= ax_b.bar(x+2*width/3 + x, y_90, width, label="90th %ile", color=colors[1])
rects3= ax_b.bar(x+5*width/3 + x, y_99, width, label="99th %ile", color=colors[2])
for i in range(len(y)):
    plt.text(2 + 3*i*width/3 - width/3,y[i], "{:.2f}".format(y[i]), fontsize='x-small', color='dimgray')

ax.set_ylabel("Job Completion Time (s)")
ax.set_ylim(25000, 45000)
ax_b.set_ylim(0,5000)
ax.spines['bottom'].set_visible(False)
ax_b.spines['top'].set_visible(False)
ax.xaxis.tick_top()
ax.tick_params(labeltop=False)
ax_b.xaxis.tick_bottom()
#ax.set_xlabel("Tasks Per Second")
ax_b.set_xticks([0+2*width/3,2+2*width/3])
ax_b.set_xticklabels(percentiles)

dw=0.005
kwargs = dict(transform=ax.transAxes, color='k', clip_on=False)
ax.plot((-dw, +dw), (-dw, +dw), **kwargs)
ax.plot((1 - dw, 1 + dw), (-dw, +dw), **kwargs) 

kwargs.update(transform=ax_b.transAxes) 
ax_b.plot((-dw, +dw), (1 - dw, 1 + dw), **kwargs)
ax_b.plot((1 - dw, 1 + dw), (1 - dw, 1 + dw), **kwargs)
ax_b.set_yticks([0,5000])
ax.set_yticks([25000, 30000, 35000, 40000, 45000])
plt.legend(fontsize='small', loc='upper center')
fig.tight_layout()
fig.savefig('jcts3.pdf', dpi=fig.dpi, bbox_inches='tight')
