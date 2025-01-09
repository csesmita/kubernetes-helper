from matplotlib import pyplot as plt, rcParams
import numpy as np
from palettable.colorbrewer.qualitative import Set2_7

colors = Set2_7.mpl_colors
# function to add value labels
def addlabels(y, pos):
    for i in range(len(y)):
        #plt.text(i + pos,y[i], y[i], ha = 'center', #bbox = dict(facecolor = 'red', alpha =.8), fontsize='x-small')
        va = 'bottom'
        if y[i] < 0:
            va = 'top'
        plt.text(i + pos,y[i], y[i], ha = 'left', fontsize='x-small', va=va)

x=[]
sparrow=[]
sparrowpt=[]
clwl_1_1_100_100=[]
dlwl_1_1_100_100=[]
murmuration=[]

params = {
   'axes.labelsize': 10,
   'font.size': 10,
   'legend.fontsize': 10.5,
   'xtick.labelsize': 10,
   'ytick.labelsize': 10,
   'text.usetex': False,
   'figure.figsize': [6, 3.6]
}
rcParams.update(params)

#Cutoffs for small jobs are as defined in EPFL simulator. 1 for all other systems.
x.extend([5000, 10000, 15000, 20000])
x1=np.arange(len(x))
sparrow.extend([46912.87372943037, 21608.60747403196, 13547.049070962734, 9656.50809077262])
murmuration.extend([45783.605816879106, 20807.280634007275, 12934.642125257476, 9133.29874477102])
clwl_1_1_100_100.extend([47582.23005038472, 21921.161483767075, 13716.140556707272, 9745.127348575375])
dlwl_1_1_100_100.extend([242876.24703741248, 240381.0591729727, 251032.7426245071, 261482.82627773413])
sparrowpt.extend([46587.1265077002, 21418.030076650306, 13391.2619069199, 9496.417731654823])
fig = plt.figure()
width=0.2
sparrow= [int(100*(i-j)/j) for i,j in zip(sparrow,murmuration)]
plt.bar(x1+width/2,sparrow, width, label="Sparrow", color=colors[0])
addlabels(sparrow, 0)
sparrowpt= [int(100*(i-j)/j) for i,j in zip(sparrowpt,murmuration)]
plt.bar(x1+width/2 + width,sparrowpt, width, label="SparrowPT", color=colors[1])
addlabels(sparrowpt, width)
clwl_1_1_100_100= [int(100*(i-j)/j) for i,j in zip(clwl_1_1_100_100,murmuration)]
plt.bar(x1+width/2 + 2*width,clwl_1_1_100_100, width, label="YaqC", color=colors[2])
addlabels(clwl_1_1_100_100, 2*width)
dlwl_1_1_100_100= [int(100*(i-j)/j) for i,j in zip(dlwl_1_1_100_100,murmuration)]
plt.bar(x1+width/2 + 3*width,dlwl_1_1_100_100, width, label="YaqD", color=colors[3])
addlabels(dlwl_1_1_100_100, 3*width)
plt.xlabel("Number of Workers in Cluster")
plt.ylabel("Relative JCT")
x1 = [i + 5*width/2 for i in x1]
plt.xticks(ticks=x1, labels=[str(n) for n in x])
plt.title("JCT Comparison for Different Schedulers Relative to Murmuration")
plt.legend()
fig.tight_layout()
fig.savefig('simulation_scalability_goog.pdf', dpi=fig.dpi, bbox_inches='tight')

'''
#Plot only relative differences with Sparrow and SparrowPT
sparrow_diff = []
sparrowpt_diff = []
for i in list(range(8)):
    diff = (sparrowpt[i] - murmuration[i]) / murmuration[i]
    sparrowpt_diff.append(diff * 100)
    diff = (sparrow[i] - murmuration[i]) / murmuration[i]
    sparrow_diff.append(diff * 100)
fig = plt.figure()
width=0.1
plt.bar(x1-width/2,sparrow_diff, width, label="Sparrow")
plt.bar(x1+width/2,sparrowpt_diff, width, label="SparrowPT")
plt.xlabel("Number of Workers in Cluster")
plt.ylabel("Relative JCT")
plt.xticks(ticks=x1, labels=[str(n) for n in x])
plt.title("JCT Comparison with Murmuration for Sparrow with Batching and Sparrow Per Task")
plt.legend()
fig.tight_layout()
fig.savefig('simulation_sparrow.pdf', dpi=fig.dpi, bbox_inches='tight')
'''

'''
systems=["Hawk", "Eagle", "SparrowPT"]
normal=[]
normal.append(hawk[0])
normal.append(eagle[0])
normal.append(sparrowpt[0])
#jobcutoff=[90, 5, 300, 600, 900]
#jobcutoff_small=[224985.65562049852, 224855.47512149863]
jobcutoff_large=[319613.44829496334, 577239.334365965, 324619.5352899935]
jobcutoff_larger=[320598.15798149526, 1607702.9244568273, 324501.29215749394]
jobcutoff_largest=[321945.7456839945, 2751181.5871102354, 324638.3712859941]

#longjobreservation=[98, 80,90]
#longres_80=[38203.71233899819, 27550.218491000247]
#longres_90=[67508.21301448907, 55648.38497549626]

fig = plt.figure()
x1=np.arange(len(systems))
plt.xticks(ticks=x1, labels=[str(n) for n in systems])
width=0.1
plt.bar(x1-width/2, normal, width, label="Recommended Cutoff 90s")
#plt.bar(x1-width/2 + width,jobcutoff_small,width,  label="Cutoff Small")
plt.bar(x1-width/2 + width,jobcutoff_large,width,  label="Cutoff 300s")
plt.bar(x1-width/2 + 2*width,jobcutoff_larger,width,  label="Cutoff 600s")
plt.bar(x1-width/2 + 3*width,jobcutoff_largest,width,  label="Cutoff 900s")
#plt.bar(x1-width/2 + 3*width,longres_80,width,  label="80")
#plt.bar(x1-width/2 + 4*width,longres_90,width,  label="90")
plt.legend()
plt.xlabel("Short Job Cutoff")
plt.ylabel("JCT")
plt.title("JCT Comparison for Different Schedulers")
fig.tight_layout()
fig.savefig('simulation_misest.pdf', dpi=fig.dpi, bbox_inches='tight')
'''

#Trends in update delays
#25% schedulers 1ms / 10ms / 100ms delay
#50% scheduler 1ms / 10ms / 100ms delay
#75% scheduler 1ms / 10ms / 100ms delay
#100% scheduler 1ms / 10ms / 100ms delay
sched_ratio = [25, 50, 75, 100]
murmuration_0ms = [61632.88888549984, 61632.88888549984, 61632.88888549984, 61632.88888549984]
murmuration_1ms = [61631.87370049979, 61631.87370049979, 61631.87370049979, 61631.87370049979]
murmuration_10ms = [61682.27035899973, 61677.87640899991, 61680.7253299998, 61683.372558999894]
murmuration_100ms = [62788.18407699976, 62788.79351499988, 62799.432374999735, 62825.113482999805]
murmuration_1s = [68118.84050999983, 68417.66758999991, 68853.56527556547, 68536.22512451475]
fig = plt.figure()
x1=np.arange(len(sched_ratio))
width=0.2
murmuration_10ms = [int(100 * (j-i)/i) for i,j in zip(murmuration_1ms, murmuration_10ms)]
murmuration_100ms = [int(100 * (j-i)/i) for i,j in zip(murmuration_1ms, murmuration_100ms)]
murmuration_1s = [int(100 * (j-i)/i) for i,j in zip(murmuration_1ms, murmuration_1s)]
perf=list(zip(murmuration_10ms, murmuration_100ms, murmuration_1s))
perf_100schedulers = perf[3]
#plt.bar(x1+width/2, murmuration_10ms, width, label="10ms delay")
#addlabels(murmuration_10ms, width / 2)
#plt.bar(x1+width/2 + width, murmuration_100ms, width, label="100ms delay")
#addlabels(murmuration_100ms, 1*width)
#plt.bar(x1+width/2 + 2*width, murmuration_1s, width, label="1s delay")
#addlabels(murmuration_1s, 2*width)
plt.plot(perf_100schedulers, label="100 schedulers")
#plt.xticks(ticks=x1 + width, labels=[str(n) for n in sched_ratio])
plt.xticks([1, 10, 100])
plt.xscale("log")
plt.legend(loc='best',  fontsize='x-small')
plt.xlabel("Ratio of Schedulers to Workers")
plt.ylabel("Relative JCT")
plt.title("JCT Comparison for Different Update Delays")
fig.tight_layout()
fig.savefig('simulation_updatedelay_goog.pdf', dpi=fig.dpi, bbox_inches='tight')
