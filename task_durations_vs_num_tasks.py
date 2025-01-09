import matplotlib.pyplot as plt
import sys
import numpy as np
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
est_task_dur_list = []
num_tasks_list = []
f = open(sys.argv[1], 'r')
while 1:
    line = f.readline()
    if line =='':
        break
    job_args = (line.split('\n'))[0].split()
    mean_task_duration = float(job_args[2])
    est_task_dur_list.append(mean_task_duration)
    num_tasks= int(job_args[1])
    num_tasks_list.append(num_tasks)
f.close()
plt.plot(est_task_dur_list, label="Estimated Running Time", color=colors[0], linestyle='-')
plt.plot(num_tasks_list, label="Number of Tasks", color=colors[1], linestyle='-')
print(np.corrcoef(est_task_dur_list, num_tasks_list))
plt.xlabel('Job ID')
plt.ylabel('Estimated Duration / NumTasks')
plt.legend()
fig.tight_layout()
fig.savefig('task_durationvs_numtasks.pdf', dpi=fig.dpi, bbox_inches='tight')
