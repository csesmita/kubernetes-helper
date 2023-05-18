from matplotlib import pyplot as plt, rcParams
import numpy as np
from palettable.colorbrewer.qualitative import Set2_7

colors = Set2_7.mpl_colors
params = {
   'axes.labelsize': 12,
   'font.size': 12,
   'legend.fontsize': 12,
   'xtick.labelsize': 12,
   'ytick.labelsize': 12,
   'text.usetex': False,
   #'figure.figsize': [6, 3.6]
}
rcParams.update(params)

# function to add value labels
def addlabels(y, pos):
    for i in range(len(y)):
        plt.text(i + pos,y[i], "{:.2f}".format(y[i]), ha = 'center', bbox = dict(facecolor = 'red', alpha =.8))

'''
#From results/jrt/d.10000J.1000X.50N.10S.YH
original_jrt = [26544.585094809532,34522.52695565224,37118.944876954556]
#25% jobs have 25 positive misestimation - results/jrt/d.10000J.1000X.50N.10S.YH.0.25+MISEST
positive_25p = [26550.986672639847,34521.37364616394,37137.39110995293]
#25% jobs have 25 negative misestimation - results/jrt/d.10000J.1000X.50N.10S.YH.0.25-MISEST
negative_25p = [26548.931873083115,34520.29573545456,37142.22423663855]
#All jobs have 50% randomly distributed misestimate around the given value - results/jrt/d.10000J.1000X.50N.10S.YH.0.5MISEST
gauss_50p = [26544.23251056671,34515.50167002678,37129.57029220581]
#All jobs have 100% randomly distributed misestimate around the given value - results/jrt/d.10000J.1000X.50N.10S.YH.1.0MISEST
gauss_100p = [26549.894215464592,34521.4772247076,37135.684959728715]
'''
jrt_50 = [26544.585094809532, 26550.986672639847, 26548.931873083115, 26544.23251056671, 26549.894215464592]
jrt_90 = [34522.52695565224, 34521.37364616394, 34520.29573545456, 34515.50167002678, 34521.4772247076]
jrt_99 = [37118.944876954556, 37137.39110995293, 37142.22423663855, 37129.57029220581, 37135.684959728715]

#Show Percentiles
percentiles=['50', '90', '99']
systems=['Positive 25%', 'Negative 25%', 'Gaussian 50%', 'Gaussian 100%']
x=np.arange(len(systems))
#x=[0.5, 1.0, 1.5]
width = 0.35
#width=0.5
fig, ax = plt.subplots()

rel_50 = [(x-jrt_50[0])/jrt_50[0] * 100 for x in jrt_50[1:]]
ax.bar(x-width/3 + x, rel_50, width, label="50th %ile", color=colors[0])
#addlabels(rel_50, 0)

rel_90 = [(x-jrt_90[0])/jrt_90[0] * 100 for x in jrt_90[1:]]
ax.bar(x + 2*width/3 + x, rel_90, width, label="90th %ile",color=colors[1])
#addlabels(rel_90, 2)

rel_99 = [(x-jrt_99[0])/jrt_99[0] * 100 for x in jrt_99[1:]]
ax.bar(x + 5*width/3 + x, rel_99, width, label="99th %ile", color=colors[2])
#addlabels(rel_99,4)

ax.set_ylabel("100 X (JCT_Misest - JCT)/ JCT")
ax.set_xlabel("Types of Misestimations")
#plt.title("Relative JCT in Murmuration for Different Mis-estimations")
ax.set_xticks([0+2*width/3,2+2*width/3,4+2*width/3, 6+2*width/3])
ax.set_xticklabels(systems)
#ax.set_ylim([25000, 45000])
ax.legend()
fig.tight_layout()
#plt.show()
fig.savefig('misestimation.pdf')
