from matplotlib import pyplot as plt, rcParams
import numpy as np
from palettable.colorbrewer.qualitative import Pastel2_7
import matplotlib.ticker as mticker
import matplotlib
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42

colors = Pastel2_7.mpl_colors
# function to add value labels
def addlabels(y, pos):
    for i in range(len(y)):
        #plt.text(i + pos,y[i], y[i], ha = 'center', #bbox = dict(facecolor = 'red', alpha =.8), fontsize='x-small')
        va = 'bottom'
        if y[i] < 0:
            va = 'top'
        plt.text(i + pos,y[i], y[i], ha = 'left', fontsize='x-small', va=va)

def custom(x, pos):
    """The two arguments are the value and tick position."""
    return '{:f}'.format(x*10000)
x=[]
eagle=[]
hawk=[]
sparrow=[]
sparrowpt=[]
clwl_1_1_100_100=[]
dlwl_1_1_100_100=[]
murmuration=[]
'''
#Plot 50th percentile
#Cutoffs for small jobs are as defined in EPFL simulator. 1 for all other systems.
x=[1000, 2000, 3000, 4000]

#90,90 cutoff and 100,98 short and long job workers.
eagle=[262742.7852454686, 129945.58003750356, 85729.41649649928, 63409.95707099762]
#eagle_90_1=[272590.6089729327, 134658.37590000633, 89710.58161549998, 66718.62523699738]
#eagle_1_1=[327229.9244084968, 161236.86714749964, 106280.92820950001, 79571.18222649996]
hawk=[277365.55093693436, 140544.51252200763, 94691.00280199976, 71265.2447934934]
#hawk_90_1=[325254.47281449474, 164573.97055049962, 106156.31973399996, 79041.0681894999]
#hawk_1_1=[327229.9244084968, 161236.86714749964, 106280.92820950001, 79571.18222649996]

#1,90 cutoff and 100,98 short and long job workers, by default.
#dlwl=[275601.18673691794, 149036.42412099865, 97543.55121400263, 77591.66673699878]
#dlwl_1_1=[448443.0671204431, 250947.01395399612, 182757.75873598777, 133381.51494700252]
dlwl_1_1_100_100=[461454.81290748727, 240195.6150764919, 171271.69058999245, 127211.18714400189]
#clwl=[269597.8176269317, 133618.69647700313, 88568.59545949979, 66167.53709199495]
#clwl_1_1=[327229.9244084968, 161236.86714749964, 106280.92820950001, 79571.18222649996]
clwl_1_1_100_100=[320743.55286999635, 157952.7193149994, 104070.538355, 78073.77441299986]

#1, 90 cutoff and 100,100 short and long job workers, by default.
murmuration=[319011.7053509967, 156809.38950499953, 103167.482174, 77164.61286349992]
#murmuration_1_1=[319011.7053509967, 156809.38950499953, 103167.482174, 77164.61286349992]

#90, 90 cutoff and 100,100 short and long job workers, by default.
sparrow=[319765.7501429935, 162054.66123949934, 104984.6972894999, 78234.2627474999]
#sparrow_90_1=[319765.7501429935, 162054.66123949934, 104984.6972894999, 78234.2627474999]
#sparrow_1_1=[319652.86107549386, 162268.43524749955, 104813.9132149998, 78205.13856999973]
sparrowpt=[324629.0258469936, 163961.32083699916, 111238.37631350002, 81993.78772799968]

#Hawk, Eagle and SparrowPT with [300, 600, 900] job cutoffs for 1000 machines.
hawk_300=[319613.44829496334,0,0,0,0,0,0,0]
eagle_300=[577239.334365965,0, 0, 0,0,0,0,0]
sparrowpt_300=[324619.5352899935,0,0,0,0,0,0,0]

hawk_600=[320598.15798149526, 0,0,0,0,0,0,0]
eagle_600=[1607702.9244568273,0,0,0,0,0,0,0]
sparrowpt_600=[324501.29215749394,0,0,0,0,0,0,0]

hawk_900=[321945.7456839945,0,0,0,0,0,0,0]
eagle_900=[2751181.5871102354,0,0,0,0,0,0,0]
sparrowpt_900=[324638.3712859941,0,0,0,0,0,0,0]
'''

'''
jobcutoff_large=[319613.44829496334, 577239.334365965, 324619.5352899935]
jobcutoff_larger=[320598.15798149526, 1607702.9244568273, 324501.29215749394]
jobcutoff_largest=[321945.7456839945, 2751181.5871102354, 324638.3712859941]
'''

'''
fig = plt.figure()
plt.plot(x,eagle, label="Eagle")
#plt.plot(x,eagle_90_1, label="Eagle_90_-1")
#plt.plot(x,eagle_1_1, label="Eagle_-1_-1")

plt.plot(x,hawk, label="Hawk")
#plt.plot(x,hawk_90_1, label="Hawk_90_-1")
#plt.plot(x,hawk_1_1, label="Hawk_-1_-1")

#plt.plot(x,dlwl, label="DLWL")
#plt.plot(x,dlwl_1_1, label="DLWL_-1_-1")
plt.plot(x,dlwl_1_1_100_100, label="Yaq-D")

#plt.plot(x,clwl, label="CLWL")
#plt.plot(x,clwl_1_1, label="CLWL_-1_-1")
plt.plot(x,clwl_1_1_100_100, label="Yaq-C")

plt.plot(x,murmuration, label="Murmuration")

plt.plot(x,sparrow, label="Sparrow")
#plt.plot(x,sparrow_90_1, label="Sparrow_90_1")
#plt.plot(x,sparrow_1_1, label="Sparrow_-1_-1")
plt.plot(x,sparrowpt, label="SparrowPT")

plt.xlabel("Number of Workers in Cluster")
plt.ylabel("JCT")
plt.xticks(x)
plt.ylim(50000, )
ax = plt.gca()
ax.get_xaxis().get_major_formatter().set_useOffset(False)
ax.get_xaxis().get_major_formatter().set_scientific(False)
plt.legend()
fig.tight_layout()
fig.savefig('simulation_jrts.pdf', dpi=fig.dpi, bbox_inches='tight')

params = {
   'axes.labelsize': 16,
   'font.size': 16,
   'legend.fontsize': 16,
   'xtick.labelsize': 16,
   'ytick.labelsize': 16,
   'text.usetex': False,
   'figure.figsize': [6, 3.4]
}
'''
params = {
   'axes.labelsize': 18,
   'font.size': 18,
   'legend.fontsize': 13.5,
   'xtick.labelsize': 18,
   'ytick.labelsize': 18,
   'text.usetex': False,
   'figure.figsize': [8,3]
}
rcParams.update(params)


rcParams.update(params)

#Cutoffs for small jobs are as defined in EPFL simulator. 1 for all other systems.
x.extend([5000, 10000, 15000, 20000])
x1=np.arange(len(x))
sparrow.extend([62660.37020649956, 31024.873130000014, 20838.53644000001, 14714.710908000008])
murmuration.extend([61632.88888549984, 29269.478930000005, 18562.988509500006, 12776.685030000004])
clwl_1_1_100_100.extend([63607.694380999834, 30463.157585000008, 19453.445559000007, 13333.524955000004])
dlwl_1_1_100_100.extend([90034.83339549994, 51590.03351499943, 38859.38692599994, 28996.48845000012])
hawk.extend([56579.311824994074, 26157.57722000018, 16709.9283800001, 11946.25521000007])
eagle.extend([50302.90787999714, 23512.296885000207, 15216.196305000125, 10924.01540500008])
sparrowpt.extend([65370.78715999971, 35226.49731999994, 23351.94402900001, 20650.18398])
fig = plt.figure()
width=0.2
eagle = [int(100*(i-j)/j) for i,j in zip(eagle,murmuration)]
#plt.bar(x1+width/2,eagle, width, label="Eagle 90th %ile Cutoff")
#addlabels(eagle, 0)
hawk= [int(100*(i-j)/j) for i,j in zip(hawk,murmuration)]
#plt.bar(x1+width/2 + width,hawk,width,  label="Hawk")
#addlabels(hawk, width)
#plt.bar(x1-width/2 + 2*width,murmuration, width, label="Murmuration")
sparrow= [int(100*(i-j)/j) for i,j in zip(sparrow,murmuration)]
plt.bar(x1+width/2 + 2*width,sparrow, width, label="Sparrow", color=colors[0])
addlabels(sparrow, 2*width)
sparrowpt= [int(100*(i-j)/j) for i,j in zip(sparrowpt,murmuration)]
plt.bar(x1+width/2 + 3*width,sparrowpt, width, label="SparrowPT", color=colors[1])
addlabels(sparrowpt, 3*width)
clwl_1_1_100_100= [int(100*(i-j)/j) for i,j in zip(clwl_1_1_100_100,murmuration)]
plt.bar(x1+width/2 + width,clwl_1_1_100_100, width, label="YaqC", color=colors[2])
addlabels(clwl_1_1_100_100, width)
dlwl_1_1_100_100= [int(100*(i-j)/j) for i,j in zip(dlwl_1_1_100_100,murmuration)]
plt.bar(x1+width/2 + 4*width,dlwl_1_1_100_100, width, label="YaqD", color=colors[3])
addlabels(dlwl_1_1_100_100, 4*width)
hawk_611=[62413.42892349973, 30332.132180000015, 20233.42181500001, 14090.126965000009]
hawk_2360=[62723.85975349964, 31212.137902000017, 20829.78216000001, 14756.09983000001]
eagle_611=[315266.6321784836, 152255.65346500004, 89546.06370999989, 58905.280339999095]
eagle_2360=[1190457.2430690252, 460218.2707394904, 192134.3682044992, 27934.001305]
hawk_611 = [int(100*(i-j)/j) for i,j in zip(hawk_611, murmuration)]
#plt.bar(x1-width/2 + 6*width,hawk_611, width, label="Hawk 95th %ile Cutoff")
#addlabels(hawk_611, 6*width)
eagle_611 = [int(100*(i-j)/j) for i,j in zip(eagle_611, murmuration)]
#plt.bar(x1-width/2 + 5*width,eagle_611, width, label="Eagle 95th %ile Cutoff")
#addlabels(eagle_611, 5*width)
hawk_2360 = [int(100*(i-j)/j) for i,j in zip(hawk_2360, murmuration)]
#plt.bar(x1-width/2 + 8*width,hawk_2360, width, label="Hawk 99th %ile Cutoff")
#addlabels(hawk_2360, 8*width)
eagle_2360 = [int(100*(i-j)/j) for i,j in zip(eagle_2360, murmuration)]
#plt.bar(x1-width/2 + 6*width,eagle_2360, width, label="Eagle 99th %ile Cutoff")
#addlabels(eagle_2360, 6*width)
'''
plt.bar(x1-width/2 + 7*width,hawk_300, width, label="Hawk 300s Cutoff")
plt.bar(x1-width/2 + 8*width,eagle_300, width, label="Eagle 300s Cutoff")
plt.bar(x1-width/2 + 9*width,sparrowpt_300, width, label="SparrowPT 300s Cutoff")
plt.bar(x1-width/2 + 10*width,hawk_600, width, label="Hawk 600s Cutoff")
plt.bar(x1-width/2 + 11*width,eagle_600, width, label="Eagle 600s Cutoff")
plt.bar(x1-width/2 + 12*width,sparrowpt_600, width, label="SparrowPT 600s Cutoff")
plt.bar(x1-width/2 + 13*width,hawk_900, width, label="Hawk 900s Cutoff")
plt.bar(x1-width/2 + 14*width,eagle_900, width, label="Eagle 900s Cutoff")
plt.bar(x1-width/2 + 15*width,sparrowpt_900, width, label="SparrowPT 900s Cutoff")
'''

plt.xlabel("Number of Workers in Cluster")
plt.ylabel("Relative JCT")
x1 = [i + 5*width/2 for i in x1]
plt.xticks(ticks=x1, labels=[str(n) for n in x])
#plt.title("JCT Comparison for Different Schedulers Relative to Murmuration")
plt.legend()
fig.tight_layout()
fig.savefig('simulation_scalability.pdf', dpi=fig.dpi, bbox_inches='tight')

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

#Trends in update delays - 5000 machines
#25% schedulers 1ms / 10ms / 100ms / 1s / 10s / 100s delay
#50% scheduler 1ms / 10ms / 100ms / 1s / 10s / 100s delay
#75% scheduler 1ms / 10ms / 100ms / 1s / 10s / 100s delay
#100% scheduler 1ms / 10ms / 100ms / 1s / 10s / 100s delay
sched_ratio = [25, 50, 75, 100]
delays = ['100ms', '1s', '10s', '100s']
murmuration_0ms = [61632.88888549984, 61632.88888549984, 61632.88888549984, 61632.88888549984]
murmuration_1ms = [61631.87370049979, 61631.87370049979, 61631.87370049979, 61631.87370049979]
murmuration_10ms = [61682.27035899973, 61677.87640899991, 61680.7253299998, 61683.372558999894]
murmuration_100ms = [62788.18407699976, 62788.79351499988, 62799.432374999735, 62825.113482999805]
murmuration_1s = [68118.84050999983, 68417.66758999991, 68853.56527556547, 68536.22512451475]
murmuration_10s = [112349.11988057579, 114647.9171207549, 118916.20822904182, 120356.18326891531]
murmuration_100s = [130381.4712296931, 175905.5721315996, 199165.59239954042, 199049.26861579367]
fig = plt.figure()
x1=np.arange(len(sched_ratio))
width=0.2
murmuration_10ms = [j/i for i,j in zip(murmuration_1ms, murmuration_10ms)]
murmuration_100ms = [j/i for i,j in zip(murmuration_1ms, murmuration_100ms)]
murmuration_1s = [j/i for i,j in zip(murmuration_1ms, murmuration_1s)]
murmuration_10s = [j/i for i,j in zip(murmuration_1ms, murmuration_10s)]
murmuration_100s = [j/i for i,j in zip(murmuration_1ms, murmuration_100s)]
#perf=list(zip(murmuration_10ms, murmuration_100ms, murmuration_1s, murmuration_10s, murmuration_100s))
perf=list(zip(murmuration_100ms, murmuration_1s, murmuration_10s, murmuration_100s))
perf_25schedulers = perf[0]
perf_50schedulers = perf[1]
perf_75schedulers = perf[2]
perf_100schedulers = perf[3]
#plt.bar(x1+width/2, murmuration_10ms, width, label="10ms delay")
#addlabels(murmuration_10ms, 0)
#plt.bar(x1+width/2 + width, murmuration_100ms, width, label="100ms delay", color=colors[0])
#addlabels(murmuration_100ms, 1*width)
#plt.bar(x1+width/2 + 2*width, murmuration_1s, width, label="1s delay", color=colors[1])
#addlabels(murmuration_1s, 2*width)
#plt.bar(x1+width/2 + 3*width, murmuration_10s, width, label="10s delay", color=colors[2])
#addlabels(murmuration_10s, 3*width)
#plt.bar(x1+width/2 + 4*width, murmuration_100s, width, label="100s delay", color=colors[3])
#addlabels(murmuration_100s, 4*width)
plt.bar(x1+width/2 + width, perf_25schedulers, width, label="25% schedulers", color=colors[0], hatch='-', fill=False)
plt.bar(x1+width/2 + 2*width, perf_50schedulers, width, label="50% schedulers", color=colors[1], hatch='o', fill=False)
plt.bar(x1+width/2 + 3*width,perf_75schedulers, width, label="75% schedulers", color=colors[2], hatch="/", fill=False)
plt.bar(x1+width/2 + 4*width, perf_100schedulers,width, label="100% schedulers", color=colors[3], hatch=".", fill=False)
#plt.xticks(ticks=x1 + width, labels=[str(n) for n in sched_ratio])
#plt.xticks([10, 100, 1000, 10000, 100000], labels=["10", "100", "1000", "10000", "100000"])
plt.xticks([0.5, 1.5, 2.5, 3.5], labels=delays)
#plt.xticks([1, 2, 3, 4], labels=delays)
plt.yticks([0,1,2,3])
#plt.xscale("log")
#print("Ticks - locations and labels are", plt.gca().get_xticks())
#ax = plt.gca()
#ax.set_xscale('log')
#ax.xaxis.set_minor_formatter(mticker.ScalarFormatter())
#ax.xaxis.get_major_formatter().set_scientific(False)
#ax.xaxis.get_major_formatter().set_useOffset(False)
#ax.xaxis.set_major_formatter(custom)
#ax.ticklabel_format(useOffset=False)
#style='plain')
#print("Ticks - locations and labels are", ax.get_xticks())
legend = plt.legend(loc='best',  ncol=2, handlelength=3)
for patch in legend.get_patches():
	patch.set_height(15)
frame = legend.get_frame()
frame.set_facecolor('1.0')
frame.set_edgecolor('1.0')
plt.xlabel("Update Delays")
plt.ylabel("Relative JCT")
#plt.title("JCT Comparison for Different Update Delays")
fig.tight_layout()
fig.savefig('simulation_updatedelay.pdf', dpi=fig.dpi, bbox_inches='tight')
