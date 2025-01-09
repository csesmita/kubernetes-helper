import matplotlib.pyplot as plt
import numpy as np
import sys
from datetime import datetime
from dateutil.parser import parse

workload_file = open('trinity.tr', 'w')
start_trace="2016-02-02 06:53:00-07:00"
start_trace_time = parse(start_trace)
f = open(sys.argv[1], 'r')
start = True
for row in f:
    if start == True:
        start = False
        continue
    if "JOBEND" not in row:
        continue
    row = row.split(',')
    num_tasks = int(row[10])
    arrival_time = (parse(row[2]) - start_trace_time).total_seconds()
    est_duration = (parse(row[6]) - parse(row[3])).total_seconds()
    task_durations = []
    for i in range(num_tasks):
        task_durations.append(est_duration)
    workload_file.write('%f %d %f %s\n' %(arrival_time, num_tasks, est_duration, ' '.join(map(str, task_durations))))
f.close()
workload_file.close()
