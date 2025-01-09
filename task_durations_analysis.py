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
for i in range(num_workloads):
    jobid = 0
    est_task_dur_list = []
    task_dev = []
    task_dev_abs = {}
    tasks_std = []
    f = open(sys.argv[1+i], 'r')
    while 1:
        line = f.readline()
        if line =='':
            break
        job_args = (line.split('\n'))[0].split()
        mean_task_duration = float(job_args[2])
        jobid += 1
        est_task_dur_list.append(mean_task_duration)
        num_tasks= int(job_args[1])
        task_dev_abs[jobid] = []
        for j in range(num_tasks):
            if mean_task_duration > 0:
                task_dev.append(abs(float(job_args[3+j]) - mean_task_duration) / mean_task_duration)
            task_dev_abs[jobid].append(float(job_args[3+j]))
        tasks_std.append(np.std(task_dev_abs[jobid]))
    f.close()
    d= np.sort(est_task_dur_list)
    dp = 1. * np.arange(len(d)) / (len(d) - 1)
    plt.plot(d, dp, label=sys.argv[1+i], color=colors[i])
    print("50th percentile: ",  np.percentile(est_task_dur_list, 50))
    print("95th percentile: ",  np.percentile(est_task_dur_list, 95))
    print("99th percentile: ",  np.percentile(est_task_dur_list, 99))
    print("Max: ",  d[len(est_task_dur_list)-1])
    print("50th percentile task estimate deviation from mean", np.percentile(task_dev, 50))
    print("90th percentile task estimate deviation from mean", np.percentile(task_dev, 90))
    print("99th percentile task estimate deviation from mean", np.percentile(task_dev, 99))
    print("50th percentile task estimate deviation", np.percentile(tasks_std, 50))
    print("90th percentile task estimate deviation", np.percentile(tasks_std, 90))
    print("99th percentile task estimate deviation", np.percentile(tasks_std, 99))

'''
plt.xlabel('Duration (s)')
plt.ylabel('CDF')
plt.xscale('log')
plt.minorticks_off()
plt.legend()
fig.tight_layout()
fig.savefig('task_duration.pdf', dpi=fig.dpi, bbox_inches='tight')
'''
