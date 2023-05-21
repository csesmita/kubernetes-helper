from matplotlib import pyplot as plt, rcParams
import numpy as np
from palettable.colorbrewer.qualitative import Set2_7

colors = Set2_7.mpl_colors
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
clwl_1_1_100_100=[]
dlwl_1_1_100_100=[]
murmuration=[]

params = {
   'axes.labelsize': 12,
   'font.size': 12,
   'legend.fontsize': 12,
   'xtick.labelsize': 12,
   'ytick.labelsize': 12,
   'text.usetex': False,
   #'figure.figsize': [12, 3]
}
rcParams.update(params)
#fig, (ax1, ax2) = plt.subplots(1,2)
fig, ax1 = plt.subplots()

#YH workload
x.extend([5000, 10000, 15000, 20000])
x1=np.arange(len(x))
sparrow.extend([62660.37020649956, 31024.873130000014, 20838.53644000001, 14714.710908000008])
murmuration.extend([61632.88888549984, 29269.478930000005, 18562.988509500006, 12776.685030000004])
clwl_1_1_100_100.extend([63607.694380999834, 30463.157585000008, 19453.445559000007, 13333.524955000004])
dlwl_1_1_100_100.extend([90034.83339549994, 51590.03351499943, 38859.38692599994, 28996.48845000012])
hawk.extend([56579.311824994074, 26157.57722000018, 16709.9283800001, 11946.25521000007])
eagle.extend([50302.90787999714, 23512.296885000207, 15216.196305000125, 10924.01540500008])
sparrowpt.extend([65370.78715999971, 35226.49731999994, 23351.94402900001, 20650.18398])


width=0.2
sparrow= [i/j for i,j in zip(sparrow,murmuration)]
ax1.bar(x1+width/2 + 2*width,sparrow, width, label="Sparrow", color=colors[0])
addlabels(ax1, sparrow, 2*width)
sparrowpt= [i/j for i,j in zip(sparrowpt,murmuration)]
ax1.bar(x1+width/2 + 3*width,sparrowpt, width, label="SparrowPT", color=colors[1])
addlabels(ax1, sparrowpt, 3*width)
clwl_1_1_100_100= [i/j for i,j in zip(clwl_1_1_100_100,murmuration)]
ax1.bar(x1+width/2 + width,clwl_1_1_100_100, width, label="YaqC", color=colors[2])
addlabels(ax1, clwl_1_1_100_100, width)
dlwl_1_1_100_100= [i/j for i,j in zip(dlwl_1_1_100_100,murmuration)]
ax1.bar(x1+width/2 + 4*width,dlwl_1_1_100_100, width, label="YaqD", color=colors[3])
addlabels(ax1, dlwl_1_1_100_100, 4*width)
ax1.set_xlabel("Number of Workers in Cluster")
ax1.set_ylabel("Relative JCT")
x1 = [i + 5*width/2 for i in x1]
ax1.set_xticks(x1)
ax1.set_xticklabels([str(n) for n in x])
#ax1.title.set_text("JCT Comparison (Yahoo Workload)")
ax1.legend()
fig.savefig('jcts_combined_a.pdf', dpi=fig.dpi, bbox_inches='tight')

#Google workload
x=[]
eagle=[]
hawk=[]
sparrow=[]
sparrowpt=[]
clwl_1_1_100_100=[]
dlwl_1_1_100_100=[]
murmuration=[]
x.extend([5000, 10000, 15000, 20000])
x1=np.arange(len(x))
sparrow.extend([46912.87372943037, 21608.60747403196, 13547.049070962734, 9656.50809077262])
murmuration.extend([45783.605816879106, 20807.280634007275, 12934.642125257476, 9133.29874477102])
clwl_1_1_100_100.extend([47582.23005038472, 21921.161483767075, 13716.140556707272, 9745.127348575375])
dlwl_1_1_100_100.extend([242876.24703741248, 240381.0591729727, 251032.7426245071, 261482.82627773413])
sparrowpt.extend([46587.1265077002, 21418.030076650306, 13391.2619069199, 9496.417731654823])

fig, ax2 = plt.subplots()
sparrow= [i/j for i,j in zip(sparrow,murmuration)]
ax2.bar(x1+width/2 + 2*width,sparrow, width, label="Sparrow", color=colors[0])
addlabels(ax2, sparrow, 2*width)
sparrowpt= [i/j for i,j in zip(sparrowpt,murmuration)]
ax2.bar(x1+width/2 + 3*width,sparrowpt, width, label="SparrowPT", color=colors[1])
addlabels(ax2, sparrowpt, 3*width)
clwl_1_1_100_100= [i/j for i,j in zip(clwl_1_1_100_100,murmuration)]
ax2.bar(x1+width/2 + width,clwl_1_1_100_100, width, label="YaqC", color=colors[2])
addlabels(ax2, clwl_1_1_100_100, width)
dlwl_1_1_100_100= [i/j for i,j in zip(dlwl_1_1_100_100,murmuration)]
ax2.bar(x1+width/2 + 4*width,dlwl_1_1_100_100, width, label="YaqD", color=colors[3])
addlabels(ax2, dlwl_1_1_100_100, 4*width)
ax2.set_xlabel("Number of Workers in Cluster")
ax2.set_ylabel("Relative JCT")
x1 = [i + 5*width/2 for i in x1]
ax2.set_xticks(x1)
ax2.set_xticklabels([str(n) for n in x])
#ax2.title.set_text("JCT Comparison (Google Workload)")
ax2.legend()
fig.tight_layout()
fig.savefig('jcts_combined_b.pdf', dpi=fig.dpi, bbox_inches='tight')
