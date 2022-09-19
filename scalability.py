from matplotlib import pyplot as plt
import re
from datetime import datetime, timedelta

pattern = '\d{2}\d{2} \d{2}:\d{2}:\d{2}\.\d{6}'
compiled = re.compile(pattern)
sched_time = timedelta(microseconds=0)
all_sched_times = []
num_scheduled = 0
pods_added = {}
pods_deleted = {}
add_event_string = "Add event for unscheduled pod"
delete_event_string = "Delete event for unscheduled pod"
fr= datetime.min
l=datetime.min
f=""
#Compare scheduling times.
with open("results/syslog/syslog.d.10000J.1000X.50N.20S.YH",'r') as f:
    for line in f:
        if add_event_string not in line and delete_event_string not in line:
            continue
        if add_event_string in line:
            podname = line.split("Add event for unscheduled pod")[1].split()[1]
            pods_added[podname] = datetime.strptime(compiled.search(line).group(0),'%m%d %H:%M:%S.%f')
            if fr == datetime.min:
                fr= pods_added[podname]
            continue
        if delete_event_string in line:
            podname = line.split("Delete event for unscheduled pod")[1].split()[1]
            pods_deleted[podname] = datetime.strptime(compiled.search(line).group(0),'%m%d %H:%M:%S.%f')
            l = pods_deleted[podname]
for podname in pods_deleted.keys():
    if podname not in pods_added.keys():
        #raise AssertionError("Podname " + podname + " doesn't have queue add only queue delete")
        continue
    if pods_added[podname] == datetime.min or pods_added[podname] > pods_deleted[podname]:
            raise AssertionError("Podname " + podname + " Got queue add time greater than queue eject time -- " + str(queue_add_time) + " " + str(queue_eject_time) + "-- " + line)
    t = pods_deleted[podname] - pods_added[podname]
    all_sched_times.append(t.total_seconds())
    if int(t.total_seconds()) > 39:
        print(podname, "Got pod scheduling time in sec - ", t.total_seconds())
        #raise AssertionError("Debug pod " + podname)
    sched_time += t
    num_scheduled += 1
plt.plot(all_sched_times)
plt.show()
print("File", f)
print("First", fr, "last", l)
t = sched_time.total_seconds()
tasks_per_sec = num_scheduled / t
print("Total Tasks Scheduled is ", num_scheduled, "in time", sched_time)
print("Tasks per sec" , tasks_per_sec)
