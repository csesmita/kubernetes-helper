#!/usr/bin/env python
from datetime import datetime
from time import mktime
from numpy import percentile
import sys 
import subprocess
import operator

def extractDateTime(timestr):
    return datetime.strptime(timestr,'%H:%M:%S.%f')

# Returns differennce in milliseconds
def timeDiffMilliseconds(end, start):
    e1 = extractDateTime(end)
    s1 = extractDateTime(start)
    ms_diff = (mktime(e1.utctimetuple()) - mktime(s1.utctimetuple())) * 1000000 + e1.microsecond - s1.microsecond
    return ms_diff * 1.0 / 1000

default_time = "00:00:00.000000"
qtimes = []
pod_start = {}
pod_end = {}
pod_node = {}
pod_durations = {}
pod_qdiff= {}
algotimes = []
logname = sys.argv[1]
f = open(logname, 'r')
for line in f:
    if "Scheduler Queue Time" not in line:
        continue
    podname = line.split('Pod ')[1].split()[0]
    nodename = line.split('Node ')[1].replace('"', "")
    nodename= nodename.split('\n')[0]
    pod_node[podname] = nodename
    started = extractDateTime(line.split('Started ')[1].split()[1])
    ended = extractDateTime(line.split('ended at ')[1].split()[1])
    pod_end[podname] = ended
    pod_start[podname] = started
    try:
        logs = subprocess.check_output(['kubectl','logs',podname]).split('\n')
    except subprocess.CalledProcessError  as e:
        status = subprocess.check_output(['kubectl','get','pods', podname, '--no-headers'])
        status = status.split()[2]
        print "Status of pod",podname,"is",status
        if status == "OutOfpods" or status == "Evicted":
            #Known error. This happens when etcd is slower than events in the cluster.
            #However, the job has sucessfully completed. So, look for other pods.
            del pod_node[podname]
            del pod_end[podname]
            del pod_start[podname]
            continue
    for log in logs:
        if "Working on " not in log:
            continue
        duration = float(log.split('Working on ')[1])
        pod_durations[podname] = duration
        break
    #TODO:
    #The following assertion might break when the pod container has been cleaned up by Docker.
    #This can be prevented using docker system prune -f -a --filter "until=168h" && 
    #docker volume prune -f. However, that might have an unintended consequence of delaying
    #other pods due to start. Do this better.
    #if podname not in pod_durations.keys():
    #    raise AssertionError('Check pod', podname,"logs. It has not worked on anything?")
    data = line.split('Scheduler Queue Time')[1]
    qdiff = timeDiffMilliseconds(data.split()[0], default_time)
    pod_qdiff[podname]=qdiff
    qtimes.append(qdiff)
    algotime_str = data.split('Scheduling Algorithm Time')[1]
    algodiff = timeDiffMilliseconds(algotime_str.split()[0], default_time)
    algotimes.append(algodiff)
qtimes.sort()
algotimes.sort()
print logname,": Total number of pods evaluated", len(qtimes)
print "Stats for Scheduler Queue Times -",percentile(qtimes, 50), percentile(qtimes, 90), percentile(qtimes, 99)
print logname,": Total number of pods evaluated", len(algotimes)
print "Stats for Scheduler Algorithm Times -"",",percentile(algotimes, 50), percentile(algotimes, 90), percentile(algotimes, 99)
'''
pods_ordered = (sorted(pod_start.items(), key=operator.itemgetter(1)))
for podname, start in pods_ordered:
    if podname in pod_qdiff.keys():
        print "Pod", podname,"started at", start, "in queue till", pod_end[podname],"assigned node", pod_node[podname], "duration", pod_durations[podname], "queue time", pod_qdiff[podname]
'''
