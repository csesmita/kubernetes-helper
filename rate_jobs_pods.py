import re
from datetime import datetime, timedelta

pattern = '\d{2}\d{2} \d{2}:\d{2}:\d{2}\.\d{6}'
compiled = re.compile(pattern)
jobs_added = {}
pods_added = {}
pods_unscheduled = {}
j_event_string = "Adding job default"
c_event_string = " created pod "
s_event_string = "Add event for unscheduled pod"
fr= datetime.min
l=datetime.min
'''
with open("/local/scratch/syslog.jobs",'r') as f:
    for line in f:
        jobname = line.split(j_event_string)[1].split()[0]
        jobs_added[jobname] = datetime.strptime(compiled.search(line).group(0),'%m%d %H:%M:%S.%f')
        if fr == datetime.min:
            fr = jobs_added[jobname]
        l = jobs_added[jobname]

num_pods = len(jobs_added.keys())
print("Number of jobs created at input of controller", num_pods)
print("Started creating at", fr, "and ended at", l)
print("Creation Time Per Job At Controller = ", ((l - fr).total_seconds()) / num_pods)
print("-----------------")

fr= datetime.min
l=datetime.min
with open("/local/scratch/syslog.controller",'r') as f:
    for line in f:
        podname = line.split(c_event_string)[1].split()[0]
        pods_added[podname] = datetime.strptime(compiled.search(line).group(0),'%m%d %H:%M:%S.%f')
        if fr == datetime.min:
            fr = pods_added[podname]
        l = pods_added[podname]

num_pods = len(pods_added.keys())
print("Number of pods created by controller", num_pods)
print("Started creating at", fr, "and ended at", l)
print("Creation Time Per Pod At Controller = ", ((l - fr).total_seconds()) / num_pods)
print("-----------------")

'''
fr= datetime.max
l=datetime.min
with open("/local/scratch/etcd_defaults.500Xpod.100N/50S.1cpupersched.NRL", 'r') as f:
    for line in f:
        if s_event_string in line:
            podname = line.split(s_event_string)[1].split()[1]
            pods_unscheduled[podname] = datetime.strptime(compiled.search(line).group(0),'%m%d %H:%M:%S.%f')
            if fr >pods_unscheduled[podname]:
                fr = pods_unscheduled[podname]
            if l < pods_unscheduled[podname]:
                l = pods_unscheduled[podname]

num_pods = len(pods_unscheduled.keys())
print("Number of unscheduled pods", num_pods)
print("Started scheduling at", fr, "and ended at", l)
print("Time Per Pod At Scheduler = ", ((l - fr).total_seconds()) / num_pods)
print("Pods Per Sec At Scheduler = ", num_pods / ((l - fr).total_seconds()))
print("-----------------")
