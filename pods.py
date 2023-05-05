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
from concurrent import futures

job_to_numtasks = {}
#Stats printed out.
pods_discarded = 0
qtimes = []
algotimes = []
kubeletqtimes = []
node_to_pod_count = collections.defaultdict(int)
scheduling_cycles_per_pod=[]
default_time = timedelta(microseconds=0)
jrt = []

#For calculating time interval between pod deletion at node versus scheduling a new pod at the node.
all_intervals=[]

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
    POD_DONE_LOG     = "Delete event for scheduled pod"

    #Fetch the logs for pods of this job. Result is in jobname.txt
    out = subprocess.check_output(['bash', 'pods.sh', jobname, str(job_to_numtasks[jobname])])
    filename=''.join([jobname,'.txt'])

    return_results = []
    job_start_time = datetime.max
    job_end_time = datetime.min
    tail_task = ""
    with open(filename, 'r') as f:
        # Fetch all pod related stats for each pod.
        podname=""
        for log in f:
            if "Logs for" in log:
                if len(podname) > 0:
                    if not discarded:
                        #Some sanity checking here.
                        if queue_time.days > 0 or scheduling_algorithm_time.days > 0 or kubelet_queue_time.days > 0:
                            print("--------Check calculations for pod", podname)
                            discarded = True
                        qtime = timeDiff(queue_time, default_time)
                        algotime = timeDiff(scheduling_algorithm_time, default_time)
                        kubeletqtime = timeDiff(kubelet_queue_time, default_time)
                    return_results.append((podname, nodename, qtime, algotime, kubeletqtime, discarded, execution_time, scheduling_cycles, queue_add_time, pod_done_time))
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
                nodename="None"
                # Atleast 1 scheduling cycle per pod.
                scheduling_cycles = 1
                podname = log.split()[2]
                continue
            # Discard all lines till the next pod.
            if discarded:
                continue
            #This log happens exactly once
            if QUEUE_ADD_LOG in log:
                if queue_add_time > datetime.min:
                    # This happens if some logs failed to make it to the distributed logging service.
                    print("--------Check calculations for pod for queue add time", podname)
                    #Skip this pod's scheduling queue and algorithm time calculations.
                    discarded = True
                    continue
                queue_add_time = extractDateTime(compiled.search(log).group(0))
                if job_start_time > queue_add_time:
                    job_start_time = queue_add_time
                continue
            #This log happens exactly once
            if QUEUE_DELETE_LOG in log:
                if queue_add_time == datetime.min:
                    # This happens if some logs failed to make it to the distributed logging service.
                    print("--------Check calculations for pod for queue delete time", podname)
                    #Skip this pod's scheduling queue and algorithm time calculations.
                    discarded = True
                    continue
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
                scheduling_cycles += 1
                continue
            #This log happens exactly once
            if BIND_LOG in log:
                if start_sch_time == datetime.min:
                    # This happens if some logs failed to make it to the distributed logging service.
                    print("---------Check calculations for pod for bind time", podname)
                    #Skip this pod's scheduling queue and algorithm time calculations.
                    discarded = True
                    continue
                attempt_bind_time = extractDateTime(compiled.search(log).group(0))
                scheduling_algorithm_time = scheduling_algorithm_time + attempt_bind_time - start_sch_time
                start_sch_time = datetime.min
                #This log line has an extranous "\n" at the end, so remove that.
                nodename = log.split('node=')[1].split()[0]
                continue
            if KUBELET_Q_ADD in log:
                if kubelet_queue_add_time > datetime.min:
                    print("--------Check calculations for pod for kubelet queue add time", podname)
                    #Skip this pod's scheduling queue and algorithm time calculations.
                    discarded = True
                    continue
                kubelet_queue_add_time = extractDateTime(compiled.search(log).group(0))
                continue
            if KUBELET_Q_DELETE in log:
                if kubelet_queue_add_time == datetime.min:
                    # This happens if some logs failed to make it to the distributed logging service.
                    print("---------Check calculations for pod for kubelet delete time", podname)
                    #Skip this pod's scheduling queue and algorithm time calculations.
                    discarded = True
                    continue
                kubelet_queue_eject_time = extractDateTime(compiled.search(log).group(0))
                kubelet_queue_time = kubelet_queue_eject_time - kubelet_queue_add_time
                continue
            if EXECUTION_LOG in log:
                # Working on 19.458. Extract the last field in the line.
                execution_time = float(log.split()[-1])
                continue
            if POD_DONE_LOG in log:
                pod_done_time = extractDateTime(compiled.search(log).group(0))
                if job_end_time < pod_done_time:
                    job_end_time = pod_done_time
                    tail_task = podname
        #For the last pod in file.
        if len(podname) > 0:
            if not discarded:
                #Some sanity checking here.
                if queue_time.days > 0 or scheduling_algorithm_time.days > 0 or kubelet_queue_time.days > 0:
                    print("--------Check calculations for pod", podname)
                    discarded = True
                qtime = timeDiff(queue_time, default_time)
                algotime = timeDiff(scheduling_algorithm_time, default_time)
                kubeletqtime = timeDiff(kubelet_queue_time, default_time)
            return_results.append((podname, nodename, qtime, algotime, kubeletqtime, discarded, execution_time, scheduling_cycles, queue_add_time, pod_done_time))

    os.remove(filename)
    return_results.insert(0, (jobname, job_start_time, job_end_time, tail_task))
    return return_results

epoch_start = datetime.max
def complete_processing(results):
    global node_to_pod_count, qtimes, algotimes, kubeletqtimes, pods_discarded, scheduling_cycles_per_pod, jrt, epoch_start
    count = 0
    jobname = ""
    for r in results:
        if len(r) == 10:
            # r = (podname, nodename, qtime, algotime, kubeletqtime, discarded, execution_time, scheduling_cycles, queue_add_time, pod_done_time)
            discarded = r[5]
            if discarded == True:
                pods_discarded += 1
                continue
            count += 1
            podname = r[0]
            nodename = r[1]
            qtime = r[2]
            algotime = r[3]
            kubeletqtime = r[4]
            execution_time = r[6]
            scheduling_cycles = r[7]
            queue_add_time = r[8]
            pod_done_time = r[9]
            node_to_pod_count[nodename] += 1
            qtimes.append(qtime)
            algotimes.append(algotime)
            kubeletqtimes.append(kubeletqtime)
            scheduling_cycles_per_pod.append(scheduling_cycles)
            diff = timeDiff((queue_add_time- job_start_time), default_time)
            tc_time = timeDiff((pod_done_time - job_start_time), default_time)
            if epoch_start > queue_add_time:
                epoch_start = queue_add_time
            queue_add_time_abs = timeDiff(queue_add_time - epoch_start, default_time)
            if podname == tail_task:
                print("Pod", podname, "- SchedulerQueueTime", qtime,"SchedulingAlgorithmTime", algotime, "KubeletQueueTime", kubeletqtime, "Node", nodename, "ExecutionTime", execution_time, "NumSchedulingCycles", scheduling_cycles, "StartedSecAfter", diff, "QueueAddTime", queue_add_time_abs, "TaskCompletionTime", tc_time, "TAIL TASK")
            else:
                print("Pod", podname, "- SchedulerQueueTime", qtime,"SchedulingAlgorithmTime", algotime, "KubeletQueueTime", kubeletqtime, "Node", nodename, "ExecutionTime", execution_time, "NumSchedulingCycles", scheduling_cycles, "StartedSecAfter", diff, "QueueAddTime", queue_add_time_abs, "TaskCompletionTime", tc_time)
        elif len(r) == 4:
            jobname = r[0]
            job_start_time = r[1]
            job_end_time = r[2]
            tail_task = r[3]
            diff = timeDiff((job_end_time - job_start_time) , default_time)
            print("Job ",jobname,"has JRT", diff)
            jrt.append(diff)
    if count < job_to_numtasks[jobname]:
        print("Job", jobname, "only has", count,"pods while the file enumerates", job_to_numtasks[jobname])

pattern = '\d{2}\d{2} \d{2}:\d{2}:\d{2}\.\d{6}'
compiled = re.compile(pattern)
def process_interval(filepath):
    partial_intervals = []
    with open(filepath, 'r') as f:
        start = datetime.min
        for log in f:
            if "Attempting to bind pod to node" in log:
                start = extractDateTime(compiled.search(log).group(0))
                continue
            if "Delete event for scheduled pod" in log:
                if start == datetime.min:
                    continue
                partial_intervals.append(extractDateTime(compiled.search(log).group(0)) - start)
                start = datetime.min
                continue
    return partial_intervals


def process():
    global all_intervals
    #https://github.com/kubernetes/klog/blob/main/klog.go#642
    #Log lines have this form:
    #    Lmmdd hh:mm:ss.uuuuuu threadid file:line] msg...
    #where the fields are defined as follows:
    #    L                A single character, representing the log level (eg 'I' for INFO)
    #    mm               The month (zero padded; ie May is '05')
    #    dd               The day (zero padded)
    #    hh:mm:ss.uuuuuu  Time in hours, minutes and fractional seconds
    #Look for Lmmdd hh:mm:ss.uuuuuu pattern in logs
    # Process workload file to get num tasks for each job
    jobid = 0
    print("This file processes the number of jobs present in temp.tr. Ensure that is fine.")
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

    '''
    subprocess.check_output(['bash', 'time_poddelete_podschedule.sh'])
    filepaths = []
    count = 0
    for filename in os.listdir('/local/scratch/tempdir'):
        filepaths.append(os.path.join('/local/scratch/tempdir', filename))
    with futures.ProcessPoolExecutor() as pool:
        for partial_intervals in pool.map(process_interval, filepaths):
            all_intervals += partial_intervals
            count += 1
            print("Finished processing", count,"files for interval evaluation")
    '''


def post_process():
    node_to_pods = list(dict(sorted(node_to_pod_count.items(), key=lambda item: item[1])).values())
    print("Total number of pods evaluated", len(qtimes))
    print("Stats for Scheduler Queue Times -",percentile(qtimes, 50), percentile(qtimes, 90), percentile(qtimes, 99))
    print("Stats for Scheduler Algorithm Times -",percentile(algotimes, 50), percentile(algotimes, 90), percentile(algotimes, 99))
    print("Stats for Kubelet Queue Times -",percentile(kubeletqtimes, 50), percentile(kubeletqtimes, 90), percentile(kubeletqtimes, 99))
    print("Number of worker nodes", len(node_to_pod_count.keys()))
    print("Count of pods on nodes -", percentile(node_to_pods, 50), percentile(node_to_pods, 90), percentile(node_to_pods, 99))
    print("Stats for number of scheduling cycles per pod -", percentile(scheduling_cycles_per_pod, 50), percentile(scheduling_cycles_per_pod, 90), percentile(scheduling_cycles_per_pod, 99))
    print("Stats for JRT -",percentile(jrt, 50), percentile(jrt, 90), percentile(jrt, 99))
    print("Pods discarded is", pods_discarded)
    #print("Number of pods evaluated for intervals in pod deletion and schedule times", len(all_intervals))
    #print("Stats for Interval Times between pod being deleted and node being scheduled -",percentile(all_intervals, 50), percentile(all_intervals, 90), percentile(all_intervals, 99))

#Process pod stats.    
start_time = time()
stats()
print("Script took a total of", time() - start_time,"s")
