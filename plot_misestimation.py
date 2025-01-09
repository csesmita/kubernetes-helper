from matplotlib import pyplot as plt, rcParams
import numpy as np
from palettable.colorbrewer.qualitative import Set2_7
import matplotlib
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42

colors = Set2_7.mpl_colors
params = {
   'axes.labelsize': 10,
   'font.size': 10,
   'legend.fontsize': 10,
   'xtick.labelsize': 10,
   'ytick.labelsize': 10,
   'text.usetex': False,
   'figure.figsize': [4,2.0]
}
rcParams.update(params)

jct=[]
jct_misest_50=[]
jct_misest_99=[]

with open("/home/sv440/Android/eagle/simulation/results_new/jct/murmuration/YH/m.8000M",'r') as f:
    for line in f:
        if "total_job_running_time" not in line:
            continue
        jct.append(float((line.split("total_job_running_time:")[1]).split()[0]))
with open("/home/sv440/Android/eagle/simulation/results_new/misest/YH/m.8000M.RANDOM_0.85-1.15",'r') as f:
    for line in f:
        if "total_job_running_time" not in line:
            continue
        jct_misest_50.append(float((line.split("total_job_running_time:")[1]).split()[0]))
with open("/home/sv440/Android/eagle/simulation/results_new/misest/YH/m.8000M.RANDOM_0.5-1.5",'r') as f:
    for line in f:
        if "total_job_running_time" not in line:
            continue
        jct_misest_99.append(float((line.split("total_job_running_time:")[1]).split()[0]))

jct = np.sort(jct)
jct_misest_50 = np.sort(jct_misest_50)
jct_misest_99 = np.sort(jct_misest_99)
cdf_jct = 1. * np.arange(len(jct)) / (len(jct) - 1)
cdf_jct_misest_50 = 1. * np.arange(len(jct_misest_50)) / (len(jct_misest_50) - 1)
cdf_jct_misest_99 = 1. * np.arange(len(jct_misest_99)) / (len(jct_misest_99) - 1)

fig, ax_jct = plt.subplots()
ax_jct.minorticks_off()
ax_jct.plot(jct, cdf_jct, label="No error", linestyle=':', linewidth=2, color=colors[0])
ax_jct.plot(jct_misest_50, cdf_jct_misest_50, label="15% error", linewidth=2, color=colors[1])
ax_jct.plot(jct_misest_99, cdf_jct_misest_99, label="50% error", linestyle='--', linewidth=2, color=colors[2])

print("Percentiles - No error", np.percentile(jct, 50), np.percentile(jct, 90), np.percentile(jct, 99))
print("Percentiles - Misest 15%", np.percentile(jct_misest_50, 50), np.percentile(jct_misest_50, 90), np.percentile(jct_misest_50, 99))
print("Percentiles - Misest 50%", np.percentile(jct_misest_99, 50), np.percentile(jct_misest_99, 90), np.percentile(jct_misest_99, 99))
ax_jct.set_ylabel('CDF')
ax_jct.set_xlabel('Duration (seconds)')
legend = ax_jct.legend()
frame = legend.get_frame()
frame.set_facecolor('1.0')
frame.set_edgecolor('1.0')
#ax_jct.set_ylim(0.0, 1.1)
#plt.xticks(np.arange(0, 60001, 30000))
fig.tight_layout()
fig.savefig('misest.pdf', dpi=fig.dpi, bbox_inches='tight')
