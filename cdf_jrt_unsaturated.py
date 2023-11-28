import csv
import numpy as np
import collections
import random
from matplotlib import pyplot as plt, rcParams
from collections import defaultdict
from palettable.colorbrewer.qualitative import Pastel2_7
from bisect import bisect

colors = Pastel2_7.mpl_colors

c50X_1 = [4494.134234666824,5877.78723359108,6339.980955386162]
c50X_2 = [4490.077031850815,5877.137363958359,6328.41065021038]
c50X_3 = [4495.058128356934,5878.299771928787,6339.958196897506]
c50X_4 = [4495.040051102638,5883.591784524918,6397.8622691941255]

c75X_1 = [4868.437785148621,6272.597789382935,6758.835675048831]
c75X_2 = [4867.7106412649155,6267.3406461715695,6704.731649067402]
c75X_3 = [4872.340055823326,6272.850074052811,6854.532067348957]
c75X_4 = [4867.683212995529,6266.743212676049,6704.054211900234]
c75X_5 = [4866.545258522034,6267.2183430194855,6710.605228400232]

c100X_1 = [5030.948400735855,6643.83340086937,7007.7673993396]
c100X_2 = [5143.024971365929,6676.06745095253,6997.1178347778305]
c100X_3 = [5201.402516365051,6728.310005569458,7046.412279422283]
c100X_4 = [5190.7008538246155,6731.215851593018,7045.746851916313]
c100X_5 = [5208.825495958328,6730.900497674942,7045.200493812561]

d50X_1 = [4494.31175327301,5873.729312944412,6189.076276469231]
d50X_2 = [4495.197189331055,5875.395967125893,6191.418493757248]
d50X_3 = [4495.350554943085,5877.61892004013,6191.0240444755555]
d50X_4 = [4494.329416275024,5874.912657165527,6191.3474055671695]

d75X_1 = [4867.681547045708,6280.89155049324,6717.907542309761]
d75X_2 = [4867.701786160469,6280.861784887314,6718.222793059349]
d75X_3 = [4867.357369422913,6273.517362809182,6716.949370853901]
d75X_4 = [4868.073789834976,6275.01379146576,6717.561769452095]
d75X_5 = [4871.71914100647,6280.389142084122,6717.8111409163475]

d100X_1 = [5263.102067947388,6671.799569392204,7016.4538173794745]
d100X_2 = [5312.3913667202,6642.221367645265,7040.632867031098]
d100X_3 = [5311.485458016396,6633.235478281975,6952.014206397534]
d100X_4 = [5309.329370737076,6635.849368190766,6958.891365842819]
d100X_5 = [5309.973803520203,6634.573805046081,6954.512809267045]

c_50X = list(zip(c50X_1, c50X_2, c50X_3, c50X_4))
d_50X = list(zip(d50X_1, d50X_2, d50X_3, d50X_4))

c_75X = list(zip(c75X_1, c75X_2, c75X_3, c75X_4, c75X_5))
d_75X = list(zip(d75X_1, d75X_2, d75X_3, d75X_4, d75X_5))

c_100X = list(zip(c100X_1, c100X_2, c100X_3, c100X_4, c100X_5))
d_100X = list(zip(d100X_1, d100X_2, d100X_3, d100X_4, d100X_5))

params = { 
   'axes.labelsize': 14, 
   'font.size': 14, 
   'legend.fontsize': 14, 
   'xtick.labelsize': 14, 
   'ytick.labelsize': 14, 
   'text.usetex': False,
}
rcParams.update(params)


tps=['100 (60%)', '150 (80%)', '200 (100%)']
x=np.arange(len(tps))
width=0.35
fig, ax = plt.subplots()

y_c50X_mean=np.mean(c_50X[0])
y_d50X_mean=np.mean(d_50X[0])
y_c50X_std=np.std(c_50X[0])
y_d50X_std=np.std(d_50X[0])

y_c75X_mean=np.mean(c_75X[0])
y_d75X_mean=np.mean(d_75X[0])
y_c75X_std=np.std(c_75X[0])
y_d75X_std=np.std(d_75X[0])

y_c100X_mean=np.mean(c_100X[0])
y_d100X_mean=np.mean(d_100X[0])
y_c100X_std=np.std(c_100X[0])
y_d100X_std=np.std(d_100X[0])

y_c_mean = [y_c50X_mean, y_c75X_mean, y_c100X_mean]
y_d_mean = [y_d50X_mean, y_d75X_mean, y_d100X_mean]
y_c_std = [y_c50X_std, y_c75X_std, y_c100X_std]
y_d_std = [y_d50X_std, y_d75X_std, y_d100X_std]

ax.bar(x+width/2, y_c_mean, yerr=y_c_std,width=width, label="Kubernetes", color=colors[0], capsize=10)
ax.bar(x-width/2, y_d_mean, yerr=y_d_std, width=width, label="Murmuration", color=colors[1], capsize=10)
labels = [((j)/i) for i,j in zip(y_d_mean, y_c_mean)]
ax.set_xlabel("Tasks Per Second (Pod Utilization)")
ax.set_xticks([0,1,2])
ax.set_ylim(4000,6000)
ax.set_yticks([4000,5000, 6000])
rects = ax.patches[0:3]
#ax.set_yticklabels([0,2500,5000,7500])
for rect,label in zip(rects, labels):
    height = rect.get_height()
    ax.text(rect.get_x() + rect.get_width() / 2, height + 50, "{:.2f}".format(label), ha="center", va="bottom")
ax.set_xticklabels(tps)
ax.set_ylabel("$50^{th}$ Job Completion Time (s)")
ax.legend(loc='upper center', fontsize='small')
fig.tight_layout()
fig.savefig('jcts_undersaturated_50.pdf', dpi=fig.dpi, bbox_inches='tight')
