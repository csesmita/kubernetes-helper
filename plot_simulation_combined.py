from matplotlib import pyplot as plt, rcParams
import numpy as np
from palettable.colorbrewer.qualitative import Pastel2_7

colors = Pastel2_7.mpl_colors
# function to add value labels
def addlabels(ax, y, pos):
    for i in range(len(y)):
        #plt.text(i + pos,y[i], y[i], ha = 'center', #bbox = dict(facecolor = 'red', alpha =.8), fontsize='x-small')
        va = 'bottom'
        if y[i] < 0:
            va = 'top'
        ax.text(i + pos,y[i], "{:.2f}".format(y[i]), ha = 'left', fontsize='x-small', va=va)

x=[]
eagle=[]
hawk=[]
sparrow=[]
sparrowpt=[]
clwl=[]
dlwl=[]
murmuration=[]

params = {
   'axes.labelsize': 10,
   'font.size': 10,
   'legend.fontsize': 10,
   'xtick.labelsize': 10,
   'ytick.labelsize': 10,
   'text.usetex': False,
   'figure.figsize': [6, 2.3]
}
rcParams.update(params)

#YH workload - 99th percentile
x.extend([10000, 12000, 14000, 16000, 18000])
x1=np.arange(len(x))
sparrow.extend([#33057.75901797965, 
25953.072403712325, 21896.561114087828, 20336.154400800686,  16259.518353383197, 14318.255330369571])
murmuration.extend([#31440.09135707481, 
24408.664118216846, 20316.64533335374, 16587.30150557762, 13906.271477039389, 12101.808009983144])
clwl.extend([#34890.08216548455, 
27345.291287056352, 22703.65712470585, 19019.91153336021, 16013.825819320995, 13772.193668241149])
dlwl.extend([#199456.04509696507, 
143470.57837517394, 139583.119542626, 122934.57995148408, 107779.45641544762,  109683.01640012539])

fig, (ax_t, ax1) = plt.subplots(2, 1, sharex=True)
labels=[]
width=0.24
ax1.bar(x1+width/2 + width,murmuration, width, label="Murmuration", color=colors[1])
ax_t.bar(x1+width/2 + width,murmuration, width, label="Murmuration", color=colors[1])
ax1.bar(x1+width/2 + 2*width,sparrow, width, label="Sparrow", color=colors[0])
ax_t.bar(x1+width/2 + 2*width,sparrow, width, label="Sparrow", color=colors[0])
sparrow= [i/j for i,j in zip(sparrow,murmuration)]
labels.extend(sparrow)
ax1.bar(x1+width/2 + 3*width,clwl, width, label="Yaq-c", color=colors[2])
ax_t.bar(x1+width/2 + 3*width,clwl, width, label="Yaq-c", color=colors[2])
clwl= [i/j for i,j in zip(clwl,murmuration)]
labels.extend(clwl)
ax1.bar(x1+width/2 + 4*width,dlwl, width, label="Yaq-d", color=colors[3])
ax_t.bar(x1+width/2 + 4*width,dlwl, width, label="Yaq-d", color=colors[3])
ax1.set_ylim(10000, 30000)
ax1.set_yticks([10000, 20000, 30000])
ax_t.set_ylim(100000, 150000)
ax_t.set_yticks([100000, 120000, 140000])

ax_t.spines['bottom'].set_visible(False)
ax1.spines['top'].set_visible(False)
ax_t.xaxis.tick_top()
ax_t.tick_params(labeltop='off')  # don't put tick labels at the top
ax1.xaxis.tick_bottom()

d= 0.010
kwargs = dict(transform=ax_t.transAxes, color='k', clip_on=False)
ax_t.plot((-d, +d), (-d, +d), **kwargs)        # top-left diagonal
ax_t.plot((1 - d, 1 + d), (-d, +d), **kwargs)  # top-right diagonal

kwargs.update(transform=ax1.transAxes)  # switch to the bottom axes
ax1.plot((-d, +d), (1 - d, 1 + d), **kwargs)  # bottom-left diagonal
ax1.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)  # bottom-right diagonal

dlwl= [i/j for i,j in zip(dlwl,murmuration)]
for rect in ax1.patches:
    print(rect.get_x())
rects = ax1.patches[5:15]
for rect,label in zip(rects, labels):
    height = rect.get_height()
    ax1.text(rect.get_x() + rect.get_width() / 2, height + 2, "{:.2f}".format(label), ha="center", va="bottom", fontsize='x-small')
rects = ax1.patches[15:20]
labels = dlwl
for rect,label in zip(rects, labels):
    height = rect.get_height()
    ax_t.text(rect.get_x() + rect.get_width() / 2, height + 2, "{:.2f}".format(label), ha="center", va="bottom", fontsize='x-small')
ax1.set_xlabel("Cluster Size")
ax1.set_ylabel("Job Completion Time (s)")
x1 = [i + 5*width/2 for i in x1]
ax1.set_xticks(x1)
ax1.set_xticklabels([str(n) for n in x])
ax_t.legend(ncol=2, framealpha=0.1)
fig.savefig('jcts_yh_99.pdf', dpi=fig.dpi, bbox_inches='tight')

#CCc workload
sparrow=[]
clwl=[]
dlwl=[]
murmuration=[]

sparrow.extend([
167529.5188908236, 139506.9227318193, 119618.89851357606, 104660.55803209267, 92957.77443669726
])
murmuration.extend([
166777.01057396538, 138772.6069735263, 118689.78992883176, 103435.14147304447, 91637.49359163603
])
clwl.extend([
184817.25786375013, 153979.94847953145, 131951.590284276, 115150.77895931182,  101879.37363905388
])
dlwl.extend([
436811.6611898725, 525130.6509278043, 346336.8161739292, 292773.17085147323,  365259.5349738252
])

fig, (ax_t, ax1) = plt.subplots(2, 1, sharex=True)
labels=[]
width=0.24
x1=np.arange(len(x))
print(x1, width, murmuration)
ax1.bar(x1+width/2 + width,murmuration, width, label="Murmuration", color=colors[1])
ax_t.bar(x1+width/2 + width,murmuration, width, label="Murmuration", color=colors[1])
ax1.bar(x1+width/2 + 2*width,sparrow, width, label="Sparrow", color=colors[0])
ax_t.bar(x1+width/2 + 2*width,sparrow, width, label="Sparrow", color=colors[0])
sparrow= [i/j for i,j in zip(sparrow,murmuration)]
labels.extend(sparrow)
ax1.bar(x1+width/2 + 3*width,clwl, width, label="Yaq-c", color=colors[2])
ax_t.bar(x1+width/2 + 3*width,clwl, width, label="Yaq-c", color=colors[2])
clwl= [i/j for i,j in zip(clwl,murmuration)]
labels.extend(clwl)
ax1.bar(x1+width/2 + 4*width,dlwl, width, label="Yaq-d", color=colors[3])
ax_t.bar(x1+width/2 + 4*width,dlwl, width, label="Yaq-d", color=colors[3])
ax1.set_ylim(90000, 200000)
ax1.set_yticks([90000, 130000, 170000])
ax_t.set_ylim(290000, 550000)
ax_t.set_yticks([300000, 400000, 500000])

ax_t.spines['bottom'].set_visible(False)
ax1.spines['top'].set_visible(False)
ax_t.xaxis.tick_top()
ax_t.tick_params(labeltop='off')  # don't put tick labels at the top
ax1.xaxis.tick_bottom()

d= 0.010
kwargs = dict(transform=ax_t.transAxes, color='k', clip_on=False)
ax_t.plot((-d, +d), (-d, +d), **kwargs)        # top-left diagonal
ax_t.plot((1 - d, 1 + d), (-d, +d), **kwargs)  # top-right diagonal

kwargs.update(transform=ax1.transAxes)  # switch to the bottom axes
ax1.plot((-d, +d), (1 - d, 1 + d), **kwargs)  # bottom-left diagonal
ax1.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)  # bottom-right diagonal

dlwl= [i/j for i,j in zip(dlwl,murmuration)]
for rect in ax1.patches:
    print(rect.get_x())
rects = ax1.patches[5:15]
for rect,label in zip(rects, labels):
    height = rect.get_height()
    ax1.text(rect.get_x() + rect.get_width() / 2, height + 2, "{:.2f}".format(label), ha="center", va="bottom", fontsize='x-small')
rects = ax1.patches[15:20]
labels = dlwl
for rect,label in zip(rects, labels):
    height = rect.get_height()
    ax_t.text(rect.get_x() + rect.get_width() / 2, height + 2, "{:.2f}".format(label), ha="center", va="bottom", fontsize='x-small')
ax1.set_xlabel("Cluster Size")
ax1.set_ylabel("Job Completion Time (s)")
x1 = [i + 5*width/2 for i in x1]
ax1.set_xticks(x1)
ax1.set_xticklabels([str(n) for n in x])
ax_t.legend(ncol=2, framealpha=0.1)
fig.savefig('jcts_ccc_99.pdf', dpi=fig.dpi, bbox_inches='tight')

#CCc workload - 50th
sparrow=[]
clwl=[]
dlwl=[]
murmuration=[]

sparrow.extend([
103614.34613091926, 87982.96958096902, 76584.83392133054, 67594.18433095142, 53535.93086600685
])
murmuration.extend([
96479.65623244911, 78349.10115775488, 66927.96097458113, 58431.8303566542, 51863.32534634833
])
clwl.extend([
113338.20663409424, 87792.56343076366, 74382.6398646654, 65035.41860255272, 57777.873853679426
])
dlwl.extend([
168669.8408471723, 145738.3435018331, 119348.36154484571, 107920.16743023411, 93410.05471595799
])

fig, ax1 = plt.subplots()
labels=[]
width=0.24
x1=np.arange(len(x))
ax1.bar(x1+width/2 + width,murmuration, width, label="Murmuration", color=colors[1])
ax1.bar(x1+width/2 + 2*width,sparrow, width, label="Sparrow", color=colors[0])
sparrow= [i/j for i,j in zip(sparrow,murmuration)]
labels.extend(sparrow)
ax1.bar(x1+width/2 + 3*width,clwl, width, label="Yaq-c", color=colors[2])
clwl= [i/j for i,j in zip(clwl,murmuration)]
labels.extend(clwl)
ax1.bar(x1+width/2 + 4*width,dlwl, width, label="Yaq-d", color=colors[3])
#ax1.set_ylim(50000, 125000)
#ax1.set_yticks([50000, 75000, 100000, 125000])
dlwl= [i/j for i,j in zip(dlwl,murmuration)]
labels.extend(dlwl)
rects = ax1.patches[5:]
for rect,label in zip(rects, labels):
    height = rect.get_height()
    ax1.text(rect.get_x() + rect.get_width() / 2, height + 2, "{:.2f}".format(label), ha="center", va="bottom", fontsize='x-small')
ax1.set_xlabel("Cluster Size")
ax1.set_ylabel("Job Completion Time (s)")
x1 = [i + 5*width/2 for i in x1]
ax1.set_xticks(x1)
ax1.set_xticklabels([str(n) for n in x])
ax1.legend(ncol=2, framealpha=0.1)
fig.savefig('jcts_ccc_50.pdf', dpi=fig.dpi, bbox_inches='tight')


#YH workload - 50th
sparrow=[]
clwl=[]
dlwl=[]
murmuration=[]

sparrow.extend([
14727.584458492349, 11501.993378968222, 8892.63090469727, 7319.020406346475, 6141.674512481493
])
murmuration.extend([
11812.024637845068, 8899.006588903412, 7016.838180586128, 5766.398159778757, 4875.061755802422
])
clwl.extend([
13800.61705006642, 10406.96658338636, 8259.310702854867, 6735.303695029141, 5684.497077060243 
])
dlwl.extend([
19035.42146405007, 20731.582712914067, 14446.904864422577, 11133.492831413285, 6718.579905116319
])

fig, ax1 = plt.subplots()
labels=[]
width=0.24
x1=np.arange(len(x))
ax1.bar(x1+width + width,murmuration, width, label="Murmuration", color=colors[1])
ax1.bar(x1+width + 2*width,sparrow, width, label="Sparrow", color=colors[0])
sparrow= [i/j for i,j in zip(sparrow,murmuration)]
labels.extend(sparrow)
ax1.bar(x1+width + 3*width,clwl, width, label="Yaq-c", color=colors[2])
clwl= [i/j for i,j in zip(clwl,murmuration)]
labels.extend(clwl)
ax1.bar(x1+width + 4*width,dlwl, width, label="Yaq-d", color=colors[3])
#ax1.set_ylim(4000, 21000)
ax1.set_yticks([5000, 10000, 15000, 20000])
dlwl= [i/j for i,j in zip(dlwl,murmuration)]
labels.extend(dlwl)
rects = ax1.patches[5:20]
for rect,label in zip(rects, labels):
    height = rect.get_height()
    ax1.text(rect.get_x() + rect.get_width() / 2, height + 2, "{:.2f}".format(label), ha="center", va="bottom", fontsize='x-small')
ax1.set_xlabel("Cluster Size")
ax1.set_ylabel("Job Completion Time (s)")
x1 = [i + 7*width/2 for i in x1]
ax1.set_xticks(x1)
ax1.set_xticklabels([str(n) for n in x])
ax1.legend(ncol=2, framealpha=0.1)
fig.savefig('jcts_yh_50.pdf', dpi=fig.dpi, bbox_inches='tight')
