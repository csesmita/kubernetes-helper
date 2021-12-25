#!/usr/bin/env python
import rediswq
import os
import subprocess
from threading import Thread
from datetime import datetime
from time import sleep, time, mktime
from collections import defaultdict
from numpy import percentile

job_to_podlist = defaultdict(list)
SPEEDUP = 10

#end and start are of the form HH:MM:SS.SSSSSS
def timeDiff(end, start):
    end_time = datetime.strptime(end, '%H:%M:%S.%f')
    start_time = datetime.strptime(start, '%H:%M:%S.%f')
    return end_time - start_time

# Returns difference in microseconds
def timeDiffMicro(end, start):
    e1 = datetime.strptime(end, '%H:%M:%S.%f')
    s1 = datetime.strptime(start, '%H:%M:%S.%f')
    ms_diff = (mktime(e1.utctimetuple()) - mktime(s1.utctimetuple())) * 1000000 + e1.microsecond - s1.microsecond
    return int(ms_diff)

def main():
    jobid = 0 
    start_epoch = 0.0 

    # Process workload file
    f = open('temp.tr', 'r')
    for row in f:
        row = row.split()
        startTime = time()
        if start_epoch == 0.0:
            start_epoch = startTime
        arrival_time = float(row[0])/float(SPEEDUP)
        # Replace the template file with actual values
        jobid += 1
        jobstr = "job"+str(jobid)
        filename = jobstr+".yaml"
        #Cleanup all jobs that have completed till now.
        #Needn't be the most aged job. Any orderinng is fine.
        #add_pod_info()
        #Start the job
        endTime = time()
        sleep_time = start_epoch + arrival_time - endTime
        if sleep_time < 0:
            print "Script loop started at", startTime,"and ran for", endTime - startTime,"sec but sleep is -ve at", sleep_time
            print "Next job due at", start_epoch + arrival_time, "but time now is", endTime
            raise AssertionError('script overran job interval!')
        sleep(sleep_time)
        thr = Thread(target=apply_job, args=(filename, start_epoch), kwargs={})
        thr.start()

    f.close()
    #Process scheduler stats.    
    stats()

def apply_job(filename, start_epoch):
        #This command takes about 0.25s. So jobs can't arrive faster than this.
        subprocess.check_output(["kubectl","apply", "-f", filename])
        subprocess.check_output(["rm", "-rf", filename])

def stats():
    pending_jobs = True
    while pending_jobs:
        process()
        sleep(5)
        pending_jobs = add_pod_info()
        print "Pending jobs?", pending_jobs


def add_pod_info():
    jobs = subprocess.check_output(["kubectl", "get", "job", "--server-print=false", "--no-headers"])
    if jobs == '':
        return False
    for job in jobs.split('\n'):
        job = job.split()
        if job == []:
           break
        jobname = job[0]
        #Check if the job has completed
        has_completed = subprocess.check_output(["kubectl", "get", "jobs", jobname, "-o","jsonpath='{.status.completionTime}'"])
        try:
            datetime.strptime(has_completed, '\'%Y-%m-%dT%H:%M:%SZ\'')
        except ValueError as e:
            print "Job", jobname,"has not yet completed"
            continue
        # This job has completed.
        pods_list = subprocess.check_output(['kubectl','get', 'pods', '--selector=job-name='+jobname, '--server-print=false', '--no-headers'])
        for pod in pods_list.splitlines():
            podname = pod.split()[0]
            job_to_podlist[jobname].append(podname)
        subprocess.check_output(["kubectl", "delete", "jobs",jobname])
    return True

def process():
    #Get the name of the scheduler.
    scheduler_details = subprocess.check_output(["kubectl", "get", "pods", "-n", "kube-system", "-l", "component=kube-scheduler", "--no-headers"])
    scheduler_name = scheduler_details.split()[0]
    sch_queue_add = "Add event for unscheduled pod"
    sch_queue_eject = "About to try and schedule pod"
    sch_attempt_schedule = "Attempting to schedule pod"
    sch_attempt_bind = "Attempting to bind pod to node"
    logs =  subprocess.check_output(['kubectl','logs', '-n', 'kube-system', scheduler_name]).split('\n')
    for jobname,pods in job_to_podlist.items():
        # Fetch all pod related stats for each pod.
        for podname in pods:
            queue_time =  0.0
            scheduling_algorithm_time = 0.0
            queue_add_time = 0.0
            queue_eject_time = 0.0
            attempt_schedule_time = 0.0
            attempt_bind_time = 0.0
            for log in logs:
                pod_string = "pod=default/" + podname
                if podname not in log:
                    continue
                if sch_queue_add in log:
                    queue_add_time = log.split(' ')[1]
                    continue
                if sch_queue_eject in log:
                    if queue_add_time == 0.0:
                        raise AssertionError('Got a queue eject time, but not a queue add time')
                                            queue_eject_time = log.split(' ')[1]
                    queue_time = timeDiff(queue_eject_time, queue_add_time)
                    continue
                if sch_attempt_schedule in log:
                    if queue_time == 0.0:
                        raise AssertionError('Got a attempt schedule time, but queue time has not yet been calculated')
                    attempt_schedule_time = log.split(' ')[1]
                    continue
                if sch_attempt_bind in log:
                    if attempt_schedule_time == 0.0:
                        raise AssertionError('Got a attempt bind time, but not a attempt schedule time')
                    attempt_bind_time = log.split(' ')[1]
                    scheduling_algorithm_time = timeDiff(attempt_bind_time, attempt_schedule_time)
                    break
            if scheduling_algorithm_time == 0.0 or queue_time == 0.0:
                raise AssertionError('Scheduling algorithm time or queue time not calculated for pod ' + podname)
            print "Job", jobname,"Pod", podname,"Scheduler Queue Time", queue_time,"Scheduling Algorithm Time", scheduling_algorithm_time
    job_to_podlist.clear()

if __name__ == '__main__':
    main()
