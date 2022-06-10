#!/usr/bin/env python
import re
from datetime import timedelta, datetime
from numpy import percentile
import collections
import sys
import subprocess
from multiprocessing import Pool
from time import time

job_to_numtasks = {}
#Stats printed out.
pods_discarded = 0
qtimes = []
algotimes = []
kubeletqtimes = []
node_to_pod_count = collections.defaultdict(int)
default_time = timedelta(microseconds=0)

def extractDateTime(timestr):
    return datetime.strptime(timestr,'%H:%M:%S.%f')

# Returns difference in two timedeltas in seconds
def timeDiff(e1, s1):
    return (e1 - s1).total_seconds()

# Start the worker processes to catch job completion events.
def stats():
    process()
    post_process()

def process_pod_scheduling_params(compiled, jobname):
    QUEUE_ADD_LOG    = "Add event for unscheduled pod"
    QUEUE_DELETE_LOG = "Delete event for unscheduled pod"
    START_SCH_LOG    = "About to try and schedule pod"
    UNABLE_SCH_LOG   = "Unable to schedule pod"
    BIND_LOG         = "Attempting to bind pod to node"
    KUBELET_Q_ADD    = "Added pod to worker queue"
    KUBELET_Q_DELETE = "Ejecting pod from worker queue"

    #Fetch the logs for pods of this job. Result is in jobname.txt
    out = subprocess.check_output(['./pods.sh', jobname, str(job_to_numtasks[jobname])])
    filename=''.join([jobname,'.txt'])

    with open(filename, 'r') as f:
        # Fetch all pod related stats for each pod.
        return_results = []
        podname=""
        for log in f:
            if "Logs for" in log:
                if len(podname) > 0:
                    print("Pod", podname, "- Scheduler Queue Time", queue_time,"Scheduling Algorithm Time", scheduling_algorithm_time, "Kubelet Queue Time", kubelet_queue_time, "Node", nodename)
                    qtime = timeDiff(queue_time, default_time)
                    algotime = timeDiff(scheduling_algorithm_time, default_time)
                    kubeletqtime = timeDiff(kubelet_queue_time, default_time)
                    return_results.append((nodename, qtime, algotime, kubeletqtime))
                #Two (maybe three in decentralized case) outputs for this pod
                queue_time = timedelta(microseconds=0)
                kubelet_queue_time = timedelta(microseconds=0)
                scheduling_algorithm_time = timedelta(microseconds=0)
                #Interim points
                queue_add_time = datetime.min
                queue_eject_time = datetime.min
                start_sch_time = datetime.min
                unable_sch_time = datetime.min
                attempt_bind_time = datetime.min
                kubelet_queue_add_time = datetime.min
                kubelet_queue_eject_time = datetime.min
                nodename=''
                podname = log.split()[2]
                continue
            #This log happens exactly once
            if QUEUE_ADD_LOG in log:
                if queue_add_time > datetime.min:
                    raise AssertionError("--------Check calculcations for pod for queue add time"+ podname)
                queue_add_time = extractDateTime(compiled.search(log).group(0))
                continue
            #This log happens exactly once
            if QUEUE_DELETE_LOG in log:
                queue_eject_time = extractDateTime(compiled.search(log).group(0))
                #print("Node", nodename,"Pod", podname,"Started", queue_add_time, "ended at", queue_eject_time)
                queue_time = queue_eject_time - queue_add_time
                continue
            if START_SCH_LOG in log:
                if start_sch_time > datetime.min:
                    print("--------Check calculcations for pod for start sch time", podname)
                    #Skip this pod's scheduling queue and algorithm time calculations.
                    pods_discarded += 1
                    break
                start_sch_time = extractDateTime(compiled.search(log).group(0))
                continue
            if UNABLE_SCH_LOG in log:
                if start_sch_time == datetime.min:
                    # This happens if some logs failed to make it to the distributed logging service.
                    print("--------Check calculcations for pod for unschedulable pod time", podname)
                    #Skip this pod's scheduling queue and algorithm time calculations.
                    pods_discarded += 1
                    break
                unable_sch_time = extractDateTime(compiled.search(log).group(0))
                scheduling_algorithm_time = scheduling_algorithm_time + unable_sch_time - start_sch_time
                start_sch_time = datetime.min
                continue
            #This log happens exactly once
            if BIND_LOG in log:
                if start_sch_time == datetime.min:
                    # This happens if some logs failed to make it to the distributed logging service.
                    print("---------Check calculcations for pod for bind time", podname)
                    #Skip this pod's scheduling queue and algorithm time calculations.
                    pods_discarded += 1
                    break
                attempt_bind_time = extractDateTime(compiled.search(log).group(0))
                scheduling_algorithm_time = scheduling_algorithm_time + attempt_bind_time - start_sch_time
                start_sch_time = datetime.min
                nodename = log.split('node=')[1]
                continue
            if KUBELET_Q_ADD in log:
                if kubelet_queue_add_time > datetime.min:
                    print("--------Check calculcations for pod for kubelet queue add time", podname)
                    #Skip this pod's scheduling queue and algorithm time calculations.
                    pods_discarded += 1
                    break
                kubelet_queue_add_time = extractDateTime(compiled.search(log).group(0))
                continue
            if KUBELET_Q_DELETE in log:
                kubelet_queue_eject_time = extractDateTime(compiled.search(log).group(0))
                kubelet_queue_time = kubelet_queue_eject_time - kubelet_queue_add_time
                continue
    return return_results

def complete_processing(results):
    global node_to_pod_count, qtimes, algotimes, kubeletqtimes
    for r in results:
        # r = (nodename, qtime, algotime, kubeletqtime)
        node_to_pod_count[r[0]] += 1
        qtimes.append(r[1])
        algotimes.append(r[2])
        kubeletqtimes.append(r[3])

def process():
    #Look for 12:14:58.422793 pattern in logs
    pattern = '\d{2}:\d{2}:\d{2}\.\d{6}'
    compiled = re.compile(pattern)
    
    # Process workload file to get num tasks for each job
    jobid = 0
    f = open('temp.tr', 'r')
    for row in f:
        row = row.split()
        num_tasks = int(row[1])
        jobid += 1
        jobstr = "".join(["job",str(jobid)])
        job_to_numtasks[jobstr]=num_tasks
        #process_pod_scheduling_params(compiled, jobstr)

    with Pool() as p:
        results=[]
        for jobname in job_to_numtasks.keys():
            r = p.apply_async(process_pod_scheduling_params, (compiled, jobname), callback=complete_processing)
            results.append(r)
        for r in results:
            r.wait()


def post_process():
    node_to_pods = list(dict(sorted(node_to_pod_count.items(), key=lambda item: item[1])).values())
    print("Total number of pods evaluated", len(qtimes))
    print("Stats for Scheduler Queue Times -",percentile(qtimes, 50), percentile(qtimes, 90), percentile(qtimes, 99))
    print("Stats for Scheduler Algorithm Times -"",",percentile(algotimes, 50), percentile(algotimes, 90), percentile(algotimes, 99))
    print("Stats for Kubelet Queue Times -",percentile(kubeletqtimes, 50), percentile(kubeletqtimes, 90), percentile(kubeletqtimes, 99))
    print("Count of pods on nodes", percentile(node_to_pods, 50), percentile(node_to_pods, 90), percentile(node_to_pods, 99))
    percent_discarded = pods_discarded / (pods_discarded + len(qtimes)) * 100
    print("Pods discarded is", pods_discarded, "and that is", percent_discarded, "% of all pods")

#Process pod stats.    
start_time = time()
stats()
print("Script took a total of", time() - start_time,"s")
