from matplotlib import pyplot as plt, rcParams
import numpy as np
from palettable.colorbrewer.qualitative import Pastel2_7
import os

colors = Pastel2_7.mpl_colors
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

jct_systems_50 = {}
jct_systems_99 = {}
jct = []
system = ""
dirname='results_new/rebuttal/1000X_CCc/'
#Each contains 5 runs.
for run_dir in os.listdir(dirname):
        for filename in os.listdir(os.path.join(dirname, run_dir)):
            if "1000N." in filename:
               continue
            if "h.10000J." in filename:
                system = "Sparrow"
            if "m.10000J." in filename:
                system = "Murmuration"
            if "yaqc.10000J." in filename:
                system="Yaq-c"
            if "yaqd.10000J." in filename:
                system="Yaq-d"
            if system not in jct_systems_50.keys():
                jct_systems_50[system] = {}
                jct_systems_99[system] = {}
            if run_dir not in jct_systems_50[system].keys():
                jct_systems_50[system][run_dir] = []
                jct_systems_99[system][run_dir] = []
            with open(os.path.join(dirname, run_dir, filename), 'r') as infile:
                jct=[]
                for line in infile:
                    if "estimated_task_duration:" not in line:
                        continue
                    line = line.split()
                    completion_time = float(line[6])
                    jct.append(completion_time)
                print("JCT Percentiles for ",filename,"is",np.percentile(jct,50), np.percentile(jct,90), np.percentile(jct,99))
            jct_systems_50[system][run_dir].append(np.percentile(jct, 50))
            jct_systems_99[system][run_dir].append(np.percentile(jct, 99))

size = [5000,10000, 15000]
xsize=np.arange(len(size))
fig, ax1 = plt.subplots()
labels=[]
width=0.15
distance = 0.75
count = 0
systems = ["Murmuration", "Sparrow", "Yaq-c", "Yaq-d"]
for system in systems:
    jct_dcsize = {}
    for run in jct_systems_99[system].keys():
        for dcsize in range(len(jct_systems_99[system][run])):
            if dcsize not in jct_dcsize.keys():
                jct_dcsize[dcsize] = []
            jct_dcsize[dcsize].append(jct_systems_99[system][run][dcsize])
    count += 1
    mean = []
    std = []
    #Sor on dc sizes. By default, the order is 10k, 15k and 5k. Make it 5k, 10k and 15k.
    for dcsize in [2,0,1]:
        mean.append(np.mean(jct_dcsize[dcsize]))
        std.append(np.std(jct_dcsize[dcsize]))
    print("System", system,mean, std)
    ax1.bar(xsize*distance+width/2 + count*width, mean, yerr=std,width=width, label=system, color=colors[count], capsize=2)
    if system == "Murmuration":
        murmuration = mean
    else:
        system_labels = [i/j for i,j in zip(mean,murmuration)]
        labels.extend(system_labels)
ax1.set_xlabel("Cluster Size")
ax1.set_ylabel("Job Completion Time (s)")
xsize = [i*distance + 6*width/2 for i in xsize]
ax1.set_xticks(xsize)
ax1.legend()
ax1.set_xticklabels([str(n) for n in size])
#Labels on other bars
rects = ax1.patches[3:12]
for rect,label in zip(rects, labels):
    height = rect.get_height()
    ax1.text(rect.get_x() + rect.get_width() / 2, height + 4, "{:.2f}".format(label), ha="center", va="bottom", fontsize='x-small')
fig.savefig('simulation_jcts_cc_99.pdf', dpi=fig.dpi, bbox_inches='tight')
