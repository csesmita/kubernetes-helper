import matplotlib.pyplot as plt
import sys
import numpy as np

est_task_dur_list = []
f = open(sys.argv[1], 'r')
while 1:
    line = f.readline()
    if line =='':
        break
    job_args = (line.split('\n'))[0].split()
    mean_task_duration = float(job_args[2])
    est_task_dur_list.append(mean_task_duration)

print("50th percentile: ",  np.percentile(est_task_dur_list, 50))
print("90th percentile: ",  np.percentile(est_task_dur_list, 90))
print("99th percentile: ",  np.percentile(est_task_dur_list, 99))
