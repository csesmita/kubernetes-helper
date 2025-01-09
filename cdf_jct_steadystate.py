import csv
import numpy as np
import collections
import random
from matplotlib import pyplot as plt, rcParams
from collections import defaultdict
from palettable.colorbrewer.qualitative import Set2_7
from bisect import bisect
from datetime import datetime
import re

colors = Set2_7.mpl_colors

WIDTH = 120
VARIANCE_TOLERANCE = 4
WINDOW_SAMPLES = 10
DELTA_SAMPLE_START_TIME =  WINDOW_SAMPLES * WIDTH
# NAME                                                        CPU(cores)   CPU%        MEMORY(bytes)   MEMORY%     
# node1.sv440-128429.decentralizedsch-pg0.utah.cloudlab.us    35844m       56%         2656Mi          2%
c_cpu = []
c_cpup = []
d_cpu = []
dc_cpu = {}
dd_cpu = {}
variance_cpup = []
new_cpup = []
suffix = "d.10000J.400X.50N.10S.YH"
with open("results/utilization/utilization." + suffix, 'r') as f:
    c_per_node_cpu = []
    c_per_node_cpup = []
    start_time = 0
    steady_state_start = 0
    steady_state_end = 0
    for r in f:
        if "NAME" in r:
            if len(c_per_node_cpu) > 0:
                # Take the average of this iteration over all nodes.
                cpu_avg = sum(c_per_node_cpu) / len(c_per_node_cpu)
                cpup_avg = sum(c_per_node_cpup) / len(c_per_node_cpup)
                c_cpu.append(cpu_avg)
                c_cpup.append(cpup_avg)
                c_per_node_cpu.clear()
                c_per_node_cpup.clear()
                dc_cpu[start_time] = cpup_avg 
                previous_start_time = start_time - DELTA_SAMPLE_START_TIME
                if previous_start_time > 0:
                    variance = abs(cpup_avg - dc_cpu[previous_start_time])
                    variance_cpup.append(variance)
                    if variance < VARIANCE_TOLERANCE: 
                        if steady_state_start == 0:
                            steady_state_start = previous_start_time
                        steady_state_end = start_time
                    else:
                        if steady_state_start > 0 and steady_state_end > 0:
                             break
                start_time += WIDTH
            continue
        if "node0" in r or "node1" in r:
            continue
        r = r.split()
        cpu = int((r[1].split("m"))[0])
        cpup = int((r[2].split("%"))[0])
        c_per_node_cpu.append(cpu)
        c_per_node_cpup.append(cpup)

new_cpup_time = []
for this_time in sorted(dc_cpu.keys()):
    if this_time >= steady_state_start and this_time <= steady_state_end:
        new_cpup.append(dc_cpu[this_time])
        new_cpup_time.append(this_time)

print("CPU% Utilization in C", np.percentile(c_cpup, 50), np.percentile(c_cpup, 90), np.percentile(c_cpup, 99))
#print("Variance", np.percentile(variance_cpup, 50), np.percentile(variance_cpup, 90), np.percentile(variance_cpup, 99))
print("Steady state identified as", steady_state_start, steady_state_end)
fig, ax1 = plt.subplots()
ax1.plot(variance_cpup, 'b', label="Variance")
#ax1.plot(dc_cpu.keys(), dc_cpu.values(), 'b', label="Utilization")
#ax1.plot(new_cpup_time, new_cpup, 'b', label="Steady State Utilization")
#ax1.set_ylim(0,40)
ax1.set_xlabel("Time")
ax1.set_ylabel("Variance in CPU Utilization")
ax1.legend()
fig.tight_layout()
fig.savefig('variance.pdf', dpi=fig.dpi, bbox_inches='tight')

def extractDateTime(timestr):
    return datetime.strptime(timestr,'%Y-%m-%d %H:%M:%S')

# Returns difference in two timedeltas in seconds
def timeDiff(e1, s1):
    return (e1 - s1).total_seconds()

pattern = '\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
compiled = re.compile(pattern)

#Pod job4-0-fp42b - SchedulerQueueTime 0.0 SchedulingAlgorithmTime 0.0 KubeletQueueTime 0.0 Node "node35.sv440-131085.decentralizedsch-pg0.utah.cloudlab.us" ExecutionTime 0.598316462111 NumSchedulingCycles 1 StartedSecAfter 0.0 QueueAddTime 1900-08-08 05:33:25 TaskCompletionTime 16.0 TaskExecutionStartTime 1900-08-08 05:33:38
final_jobs = []
discard_job = []
execstart = {}
epoch_start = datetime.max
with open("results/pods/pods." + suffix+".final",'r') as f:
    for line in f:
        if "Epoch start is" in line:
            epoch_start = extractDateTime(compiled.search(line).group(0))
            print("Epoch start", epoch_start)
            break
with open("results/pods/pods." + suffix+".final",'r') as f:
    for line in f:
        if "SchedulerQueueTime" not in line:
            continue
        r = line.split()
        podname = r[1]
        jobname = r[1].split("-")[0]
        if "TAIL TASK" in line:
            #print(line)
            log = line.split("TaskExecutionStartTime")[1]
            execstart[jobname] = extractDateTime(compiled.search(log).group(0))
            execstartdelta = timeDiff(execstart[jobname], epoch_start)
            if execstartdelta >= steady_state_start and execstartdelta <= steady_state_end:
                final_jobs.append(jobname)
            else:
                discard_job.append(jobname)
print("Number of jobs included", len(final_jobs))
print("Jobs included", discard_job)
c=[]
with open("results/jrt/" + suffix, 'r') as f:
    for r in f:
        if "has JRT" not in r:
            continue
        r= r.split()
        jobid = r[1]
        if jobid in final_jobs:
            jrt = float(r[4])
            c.append(jrt)

print("Stats for JRT in steady state", np.percentile(c,50), np.percentile(c,90), np.percentile(c,99))

