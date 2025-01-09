import matplotlib.pyplot as plt
import numpy as np
import sys
from palettable.colorbrewer.qualitative import Set2_7
from matplotlib import pyplot as plt, rcParams

colors = Set2_7.mpl_colors
params = {
   'axes.labelsize': 12,
   'font.size': 12,
   'legend.fontsize': 12,
   'xtick.labelsize': 12,
   'ytick.labelsize': 12,
   'text.usetex': False,
   #'figure.figsize': [10, 3]
}
rcParams.update(params)

num_workloads = len(sys.argv[1:])
fig=plt.figure()
for i in range(num_workloads):
    num_tasks = []
    f = open(sys.argv[1+i], 'r')
    start_time = 0
    count = 0
    for row in f:
        row = row.split(' ')
        num_tasks.append(int(row[1]))
        count += 1
    f.close()

    #CDF of tail tasks.
    d = np.sort(num_tasks)
    dp = 1. * np.arange(len(d)) / (len(d) - 1)
    #Show CDF
    plt.plot(d, dp, label=sys.argv[1+i], color=colors[i])
    print("50th percentile: ",  np.percentile(num_tasks, 50))
    print("90th percentile: ",  np.percentile(num_tasks, 90))
    print("99th percentile: ",  np.percentile(num_tasks, 99))
    '''
    num_tasks.sort()
    plt.plot(num_tasks, label=sys.argv[1+i], color=colors[i])
    '''

    
plt.xlabel('Number of Tasks')
plt.ylabel('CDF')
plt.xscale('log')
plt.minorticks_off()
plt.legend()
fig.tight_layout()
fig.savefig('num_tasks.pdf', dpi=fig.dpi, bbox_inches='tight')

print("Total tasks",sum(num_tasks))

'''
#num_tasks.sort()
plt.plot(job_id,num_tasks, color = 'g', label = 'Data')
plt.xlabel('Job Ids', fontsize = 12)
plt.ylabel('Num Tasks', fontsize = 12)
  
plt.title('Num Tasks of Jobs', fontsize = 20)
plt.legend()
plt.show()

'''
