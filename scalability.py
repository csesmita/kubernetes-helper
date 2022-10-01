from matplotlib import pyplot as plt
import re
from datetime import datetime, timedelta

pattern = '\d{2}\d{2} \d{2}:\d{2}:\d{2}\.\d{6}'
compiled = re.compile(pattern)
sched_time = 0.0
all_sched_times = []
num_scheduled = 0
pods_added = {}
pods_deleted = {}
add_event_string = "Add event for unscheduled pod"
delete_event_string = "Attempting to bind pod to node"
fr= datetime.min
l=datetime.min
f=""

#Compare scheduling times.
with open("results/ha/syslog/syslog.d.1000J.1000X.50N.10S.YH.sched1cpu.1controlplaneonly",'r') as f:
    for line in f:
        if add_event_string not in line and delete_event_string not in line:
            continue
        if add_event_string in line:
            podname = line.split(add_event_string)[1].split()[1]
            pods_added[podname] = datetime.strptime(compiled.search(line).group(0),'%m%d %H:%M:%S.%f')
            if fr == datetime.min:
                fr= pods_added[podname]
            continue
        if delete_event_string in line:
            podname = line.split(delete_event_string)[1].split()[1]
            pods_deleted[podname] = datetime.strptime(compiled.search(line).group(0),'%m%d %H:%M:%S.%f')
            l = pods_deleted[podname]
print("Pods with add and no delete statement", list(set(pods_added.keys()) - set(pods_deleted.keys())))     
print("Pods with delete and no add statement", list(set(pods_deleted.keys()) - set(pods_added.keys())))     
for podname in pods_deleted.keys():
    if podname not in pods_added.keys():
        continue
    if pods_added[podname] == datetime.min or pods_added[podname] > pods_deleted[podname]:
            raise AssertionError("Podname " + podname + " Got queue add time greater than queue eject time -- " + str(queue_add_time) + " " + str(queue_eject_time) + "-- " + line)
    t = (pods_deleted[podname] - pods_added[podname]).total_seconds()
    #if t > 20:
    #    print("Check pod", podname,"with", t, "seconds of scheduling")
    all_sched_times.append(t)
    sched_time += t
    num_scheduled += 1
#plt.plot(all_sched_times)
#plt.show()
print("File", f)
print("First", fr, "last", l)
tasks_per_sec = num_scheduled / sched_time
print("Total Tasks Scheduled is ", num_scheduled, "in time", sched_time)
print("Tasks per sec" , tasks_per_sec)
