#!/usr/bin/env python
import re
from datetime import timedelta, datetime
from numpy import percentile
import collections
import sys
import subprocess
from multiprocessing import Pool
from time import time
import os

job_to_numtasks = {}
#Stats printed out.
pods_discarded = 0
qtimes = []
algotimes = []
kubeletqtimes = []
node_to_pod_count = collections.defaultdict(int)
default_time = timedelta(microseconds=0)

def extractDateTime(timestr):
    return datetime.strptime(timestr,'%m%d %H:%M:%S.%f')

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
    # This log comes from the pod image.
    EXECUTION_LOG    = "Working on"

    #Fetch the logs for pods of this job. Result is in jobname.txt
    out = subprocess.check_output(['bash', 'pods.sh', jobname, str(job_to_numtasks[jobname])])
    filename=''.join([jobname,'.txt'])

    return_results = []
    with open(filename, 'r') as f:
        # Fetch all pod related stats for each pod.
        podname=""
        for log in f:
            if "Logs for" in log:
                if len(podname) > 0:
                    #Some sanity checking here.
                    if queue_time.days > 0 or scheduling_algorithm_time.days > 0 or kubelet_queue_time.days > 0:
                        print("--------Check calculcations for pod", podname)
                        discarded = True
                    qtime = timeDiff(queue_time, default_time)
                    algotime = timeDiff(scheduling_algorithm_time, default_time)
                    kubeletqtime = timeDiff(kubelet_queue_time, default_time)
                    return_results.append((podname, nodename, qtime, algotime, kubeletqtime, discarded, execution_time))
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
                execution_time = 0.0
                discarded = False
                nodename=''
                podname = log.split()[2]
                continue
            #This log happens exactly once
            if QUEUE_ADD_LOG in log:
                if queue_add_time > datetime.min:
                    # This happens if some logs failed to make it to the distributed logging service.
                    print("--------Check calculcations for pod for queue add time", podname)
                    #Skip this pod's scheduling queue and algorithm time calculations.
                    discarded = True
                    break
                queue_add_time = extractDateTime(compiled.search(log).group(0))
                continue
            #This log happens exactly once
            if QUEUE_DELETE_LOG in log:
                if queue_add_time == datetime.min:
                    # This happens if some logs failed to make it to the distributed logging service.
                    print("--------Check calculcations for pod for queue delete time", podname)
                    #Skip this pod's scheduling queue and algorithm time calculations.
                    discarded = True
                    break
                queue_eject_time = extractDateTime(compiled.search(log).group(0))
                #print("Node", nodename,"Pod", podname,"Started", queue_add_time, "ended at", queue_eject_time)
                queue_time = queue_eject_time - queue_add_time
                continue
            if START_SCH_LOG in log:
                # if start_sch_time > datetime.min:
                # This happens if some logs failed to make it to the distributed logging service.
                # Since this log may occur multiple times, overwrite with this value.
                # Skip the previous log time and overwrite with this one.
                start_sch_time = extractDateTime(compiled.search(log).group(0))
                continue
            if UNABLE_SCH_LOG in log:
                if start_sch_time == datetime.min:
                    # This happens if some logs failed to make it to the distributed logging service.
                    # Since this log may occur multiple times, skip this new value.
                    # Skip this datapoint in pod's scheduling time calculation.
                    continue
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
                    discarded = True
                    break
                attempt_bind_time = extractDateTime(compiled.search(log).group(0))
                scheduling_algorithm_time = scheduling_algorithm_time + attempt_bind_time - start_sch_time
                start_sch_time = datetime.min
                #This log line has an extranous "\n" at the end, so remove that.
                nodename = log.split('node=')[1].split()[0]
                continue
            if KUBELET_Q_ADD in log:
                if kubelet_queue_add_time > datetime.min:
                    print("--------Check calculcations for pod for kubelet queue add time", podname)
                    #Skip this pod's scheduling queue and algorithm time calculations.
                    discarded = True
                    break
                kubelet_queue_add_time = extractDateTime(compiled.search(log).group(0))
                continue
            if KUBELET_Q_DELETE in log:
                if kubelet_queue_add_time == datetime.min:
                    # This happens if some logs failed to make it to the distributed logging service.
                    print("---------Check calculcations for pod for kubelet delete time", podname)
                    #Skip this pod's scheduling queue and algorithm time calculations.
                    discarded = True
                    break
                kubelet_queue_eject_time = extractDateTime(compiled.search(log).group(0))
                kubelet_queue_time = kubelet_queue_eject_time - kubelet_queue_add_time
                continue
            if EXECUTION_LOG in log:
                # Working on 19.458. Extract the last field in the line.
                execution_time = float(log.split()[-1])
                continue
        #For the last pod in file.
        if len(podname) > 0:
            #Some sanity checking here.
            if queue_time.days > 0 or scheduling_algorithm_time.days > 0 or kubelet_queue_time.days > 0:
                print("--------Check calculcations for pod", podname)
                discarded = True
            qtime = timeDiff(queue_time, default_time)
            algotime = timeDiff(scheduling_algorithm_time, default_time)
            kubeletqtime = timeDiff(kubelet_queue_time, default_time)
            return_results.append((podname, nodename, qtime, algotime, kubeletqtime, discarded, execution_time))

    os.remove(filename)
    return return_results

def complete_processing(results):
    global node_to_pod_count, qtimes, algotimes, kubeletqtimes
    for r in results:
        # r = (podname, nodename, qtime, algotime, kubeletqtime, discarded, execution_time)
        podname = r[0]
        nodename = r[1]
        qtime = r[2]
        algotime = r[3]
        kubeletqtime = r[4]
        discarded = r[5]
        execution_time = r[6]
        if discarded == True:
            pods_discarded += 1
            continue
        node_to_pod_count[nodename] += 1
        qtimes.append(qtime)
        algotimes.append(algotime)
        kubeletqtimes.append(kubeletqtime)
        print("Pod", podname, "- SchedulerQueueTime", qtime,"SchedulingAlgorithmTime", algotime, "KubeletQueueTime", kubeletqtime, "Node", nodename, "ExecutionTime", execution_time)

def process():
    #https://github.com/kubernetes/klog/blob/main/klog.go#642
    #Log lines have this form:
    #    Lmmdd hh:mm:ss.uuuuuu threadid file:line] msg...
    #where the fields are defined as follows:
    #    L                A single character, representing the log level (eg 'I' for INFO)
    #    mm               The month (zero padded; ie May is '05')
    #    dd               The day (zero padded)
    #    hh:mm:ss.uuuuuu  Time in hours, minutes and fractional seconds
    #Look for Lmmdd hh:mm:ss.uuuuuu pattern in logs
    pattern = '\d{2}\d{2} \d{2}:\d{2}:\d{2}\.\d{6}'
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
