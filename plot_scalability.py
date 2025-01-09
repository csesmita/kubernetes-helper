from matplotlib import pyplot as plt, rcParams
import numpy as np
from palettable.colorbrewer.qualitative import Set2_7

def millions(x, pos):
    """The two arguments are the value and tick position."""
    return '{:1.1f}M'.format(x*1e-6)

colors = Set2_7.mpl_colors
x=[10, 20, 30, 40, 50]
#1cpupersched
y1=[3986, 8055, 9661, 10126, 9379]
y1_avg=[2080, 1935, 1990, 2051, 2022]
#2cpupersched
y2=[8333,10092,10957,10937,10257]
y2_avg=[2430, 2824, 2666, 3072, 2925]
params = {
   'axes.labelsize': 12,
   'font.size': 12,
   'legend.fontsize': 12,
   'xtick.labelsize': 12,
   'ytick.labelsize': 12,
   'text.usetex': False,
   #'figure.figsize': [10, 3.5]
}
rcParams.update(params)

#fig = plt.figure()
#fig, (ax1, ax2) = plt.subplots(1,2)
fig, ax1 = plt.subplots()
ax1.plot(x,y1, color=colors[0], label="Maximum Throughput (1 cpu/sched)")
ax1.plot(x,y1_avg, color=colors[0], linestyle="--", label="Average Throughput (1 cpus/sched)")
'''
for xz,yz in zip(x,y1):
    label = "{:d}".format(yz)
    ax1.annotate(label, (xz,yz), textcoords="offset points", xytext=(0,3), ha='center')
for xz,yz in zip(x,y1_avg):
    label = "{:d}".format(yz)
    ax1.annotate(label, (xz,yz), textcoords="offset points", xytext=(0,-10), ha='center')
'''
ax1.plot(x,y2, color=colors[1], label="Maximum Throughput (2 cpu/sched)")
ax1.plot(x,y2_avg, color=colors[1], linestyle="--", label="Average Throughput (2 cpus/sched)")
'''
for xz,yz in zip(x,y2):
    label = "{:d}".format(yz)
    ax1.annotate(label, (xz,yz), textcoords="offset points", xytext=(0,5), ha='center')
for xz,yz in zip(x,y2_avg):
    label = "{:d}".format(yz)
    ax1.annotate(label, (xz,yz), textcoords="offset points", xytext=(0,5), ha='center')
'''
ax1.set_xlabel("Number of Schedulers")
ax1.set_xticks(x)
ax1.set_ylabel("Scheduling Throughput (Pods/sec)")
ax1.set_ylim(0,12000)
ax1.legend(prop={'size': 8})
#ax1.text(0.4,-0.4, "(a)", size=12, ha="center", transform=ax1.transAxes)
fig.tight_layout()
fig.savefig('scalability_a.pdf', dpi=fig.dpi, bbox_inches='tight')
#plt.show()

x=[100, 150, 200, 250, 300]
#1cpupersched
y=[8509, 7377, 10449, 6924, 7902]
y_avg=[1887, 1857, 1814, 1633, 1658] 
fig,ax2 = plt.subplots()
ax2.plot(x,y, color=colors[0], label="Maximum Throughput (1 cpu/sched)")
ax2.plot(x,y_avg, color=colors[0], linestyle="--", label="Average Throughput (1 cpu/sched)")
'''
for xz,yz in zip(x,y):
    label = "{:d}".format(yz)
    ax2.annotate(label, (xz,yz), textcoords="offset points", xytext=(0,10), ha='center')
for xz,yz in zip(x,y_avg):
    label = "{:d}".format(yz)
    ax2.annotate(label, (xz,yz), textcoords="offset points", xytext=(0,10), ha='center')
'''
ax2.set_xlabel("Number of Schedulers")
ax2.set_xticks(x)
ax2.set_ylabel("Scheduling Throughput (Pods/sec)")
ax2.set_ylim(0,12000)
ax2.legend(loc="center left", prop={'size': 8})
#ax2.text(0.5,-0.4, "(b)", size=12, ha="center", transform=ax2.transAxes)
fig.tight_layout()
fig.savefig('scalability_b.pdf', dpi=fig.dpi, bbox_inches='tight')

# Varying pod generation rate
x=[100, 200, 300, 400, 500]
#Peak scheduling rate
y1=[9379, 10429, 11837, 10141, 8153]
#Average scheduling rate
y1_avg=[2022, 1931, 1879, 1690, 1881]
#Total number of pods scheduled
y2=[1612162, 3208362, 4804493, 6400762, 7996319]
fig, ax1 = plt.subplots()
ax2 = ax1.twinx()
'''
params = {
   'legend.fontsize': 8,
}
rcParams.update(params)
'''

ax1.plot(x,y1, color=colors[0], label="Maximum Throughput")
'''
for xz,yz in zip(x,y1):
    label = "{:d}".format(yz)
    ax1.annotate(label, (xz,yz), textcoords="offset points", xytext=(0,-13), ha='center')
ax1.plot(x,y1_avg, color=colors[0], linestyle="--", label="Average Throughput")
for xz,yz in zip(x,y1_avg):
    label = "{:d}".format(yz)
    ax1.annotate(label, (xz,yz), textcoords="offset points", xytext=(0,10), ha='center')
'''
ax2.plot(x,y2, color=colors[1], marker='o') #label="Total number of scheduled pods")
'''
for xz,yz in zip(x,y2):
    label = "{:d}".format(yz)
    ax2.annotate(label, (xz,yz), textcoords="offset points", xytext=(0,10), ha='center')
'''
ax1.set_xlabel("Fake pod generation multiplier")
plt.xticks(x)
ax1.set_ylabel("Scheduling Throughput (Pods/sec)", color=colors[0])
ax1.set_ylim(0,12000)
ax2.set_ylabel("Total Number of Scheduled Pods", color=colors[1])
#ax2.yaxis.set_ticks([2000000,3000000,4000000,5000000,6000000,7000000,8000000])
#ax2.yaxis.set_ticklabels([2,3,4,5,6,7,8])
#ax2.ticklabel_format(style='plain')
#ax2.tick_params(axis='y', colors=colors[1])
ax2.yaxis.set_major_formatter(millions)
#ax2.set_ylim(0,8000000)
ax1.legend(loc='center left')
#ax2.legend(loc='best')
fig.tight_layout()
fig.savefig('scalability_c.pdf', dpi=fig.dpi, bbox_inches='tight')
