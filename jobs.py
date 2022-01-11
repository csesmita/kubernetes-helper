#!/usr/bin/env python
import rediswq
import os
import re
import subprocess
from threading import Thread
from datetime import timedelta, datetime
from time import sleep, time, mktime
from collections import defaultdict
from numpy import percentile

#Maintains job to pod list mapping for completed jobs.
job_to_podlist = {}
SPEEDUP = 1

#end and start are of the form HH:MM:SS.SSSSSS
def timeDiff(end, start):
    end_time = datetime.strptime(end, '%H:%M:%S.%f')
    start_time = datetime.strptime(start, '%H:%M:%S.%f')
    return end_time - start_time

def main():
    jobid = 0
    start_epoch = 0.0
    threads = []

    # Process workload file
    f = open('temp.tr', 'r')
    for row in f:
        row = row.split()
        startTime = time()
        if start_epoch == 0.0:
            start_epoch = startTime
        arrival_time = float(row[0])/float(SPEEDUP)
        jobid += 1
        jobstr = "job"+str(jobid)
        job_to_podlist[jobstr]=[]
        # Pick the correct job file.
        filename = jobstr+".yaml"
        #Sleep till it is time to start the job.
        endTime = time()
        sleep_time = start_epoch + arrival_time - endTime
        if sleep_time < 0:
            print "Script loop started at", startTime,"and ran for", endTime - startTime,"sec but sleep is -ve at", sleep_time
            print "Next job due at", start_epoch + arrival_time, "but time now is", endTime
            raise AssertionError('script overran job interval!')
        sleep(sleep_time)
        #"kubectl apply" is an expensive operation.
        #Spawn a background thread that will actually start the job.
        #apply_job(filename, jobstr, start_epoch)
        thr = Thread(target=apply_job, args=(filename, jobstr, start_epoch), kwargs={})
        thr.start()
        threads.append(thr)

    f.close()

    #Wait for all threads to start their respective jobs.
    for thr in threads:
        thr.join()

    #Process scheduler stats.    
    stats()
    print "Script took a total of", time() - start_epoch,"s"

def apply_job(filename, jobstr, start_epoch):
        #This command takes about 0.25s. So jobs can't arrive faster than this.
        subprocess.check_output(["kubectl","apply", "-f", filename])
        print "Starting", jobstr, "at", time() - start_epoch

def stats():
    pending_jobs = True
    #Change directory to scheduler logs
    os.chdir("/local/scratch/")
    #Look for 12:14:58.422793 pattern in logs
    pattern = '\d{2}:\d{2}:\d{2}\.\d{6}'
    compiled = re.compile(pattern)
    while pending_jobs:
        pending_jobs = add_pod_info()
        print "Pending jobs?", pending_jobs
        process(compiled)
        sleep(5)
    print "Finished processing all jobs"


def add_pod_info():
    if len(job_to_podlist.keys()) == 0:
        return False
    count = 0
    for jobname in job_to_podlist.keys():
        has_completed = subprocess.check_output(["kubectl", "get", "jobs", jobname, "-o","jsonpath='{.status.completionTime}'"])
        try:
            datetime.strptime(has_completed, '\'%Y-%m-%dT%H:%M:%SZ\'')
            #Check if the job has completed
            is_complete = subprocess.check_output(["kubectl", "get", "jobs", jobname, "-o", "jsonpath='{.status.conditions}'"])
            if "\"type\":\"Complete\"" not in is_complete:
                #Job might have failed.
                raise AssertionError("Job" + jobname + "has failed!")
        except ValueError as e:
            # This job has not yet completed.
            #print jobname,"has not completed yet. Got error", e
            continue
        # This job has completed.
        count += 1
        pods_list = subprocess.check_output(['kubectl','get', 'pods', '--selector=job-name='+jobname, '--server-print=false', '--no-headers'])
        for pod in pods_list.splitlines():
            podname = pod.split()[0]
            job_to_podlist[jobname].append(podname)
        #Utmost 5 completed jobs in each iteration.
        if count == 5:
            break
    return True

QUEUE_ADD_LOG    = "Add event for unscheduled pod"
QUEUE_DELETE_LOG = "Delete event for unscheduled pod"
START_SCH_LOG    = "About to try and schedule pod"
UNABLE_SCH_LOG   = "Unable to schedule pod"
BIND_LOG         = "Attempting to bind pod to node"
def process(compiled):
    for jobname,pods in job_to_podlist.items():
        # Fetch all pod related stats for each pod.
        has_pods = False
        for podname in pods:
            has_pods = True
            #Two outputs for this pod
            queue_time = timedelta(microseconds=0)
            scheduling_algorithm_time = timedelta(microseconds=0)
            #Intermittent points
            queue_add_time = datetime.min
            queue_eject_time = datetime.min
            start_sch_time = datetime.min
            unable_sch_time = datetime.min
            attempt_bind_time = datetime.min
            nodename=''
            logs =  subprocess.check_output(['grep','-ri',podname, 'syslog']).split('\n')
            #Grep'ed logs can be out of order in time.
            #sch_queue_eject and unable_sch may happen multiple times.
            #TODO- Assumes sch_queue_eject log happens before unable_sch log, and they always happen one after the other. 
            #TODO- That might not always be true.
            for log in logs:
                #This log happens exactly once
                if QUEUE_ADD_LOG in log:
                    if queue_add_time > datetime.min:
                        print "Check calculcations for pod for queue add time", podname,
                        queue_time = timedelta(microsecond=0)
                        scheduling_algorithm_time = timedelta(microsecond=0)
                        break
                    queue_add_time = datetime.strptime(compiled.search(log).group(0), '%H:%M:%S.%f')
                    continue
                #This log happens exactly once
                if QUEUE_DELETE_LOG in log:
                    queue_eject_time = datetime.strptime(compiled.search(log).group(0), '%H:%M:%S.%f')
                    print "Job", jobname,"Pod", podname,"Started", queue_add_time, "ended at", queue_eject_time,
                    queue_time = queue_eject_time - queue_add_time
                    break
                if START_SCH_LOG in log:
                    if start_sch_time > datetime.min:
                        print "Check calculcations for pod for start sch time", podname,
                        queue_time = timedelta(microsecond=0)
                        scheduling_algorithm_time = timedelta(microsecond=0)
                        break
                    start_sch_time = datetime.strptime(compiled.search(log).group(0), '%H:%M:%S.%f')
                    continue
                if UNABLE_SCH_LOG in log:
                    if start_sch_time == datetime.min:
                        print "Check calculcations for pod for unschedulable pod time", podname,
                        queue_time = timedelta(microsecond=0)
                        scheduling_algorithm_time = timedelta(microsecond=0)
                        break
                    unable_sch_time = datetime.strptime(compiled.search(log).group(0), '%H:%M:%S.%f')
                    scheduling_algorithm_time = scheduling_algorithm_time + unable_sch_time - start_sch_time
                    start_sch_time = datetime.min
                    continue
                #This log happens exactly once
                if BIND_LOG in log:
                    if start_sch_time == datetime.min:
                        print "Check calculcations for pod for unschedulable pod time", podname,
                        queue_time = timedelta(microsecond=0)
                        scheduling_algorithm_time = timedelta(microsecond=0)
                        break
                    attempt_bind_time = datetime.strptime(compiled.search(log).group(0), '%H:%M:%S.%f')
                    scheduling_algorithm_time = scheduling_algorithm_time + attempt_bind_time - start_sch_time
                    start_sch_time = datetime.min
                    nodename = log.split('node=')[1]
                    continue
            print "Scheduler Queue Time", queue_time,"Scheduling Algorithm Time", scheduling_algorithm_time, "Node", nodename
        if has_pods:
            del job_to_podlist[jobname]

if __name__ == '__main__':
    main()
