#!/usr/bin/env python
import rediswq
import os
import re
import subprocess
from threading import Thread
from datetime import timedelta, datetime
from time import sleep, time, mktime
from numpy import percentile


#Maintains job to pod list mapping for completed jobs.
job_to_podlist = {}
SPEEDUP = 1

#Stats printed out.
qtimes = []
algotimes = []
pod_start = {}
pod_end = {}
pod_node = {}
pod_durations = {}
pod_qdiff= {}

def extractDateTime(timestr):
    return datetime.strptime(timestr,'%H:%M:%S.%f')

# Returns difference in two timedeltas in seconds
def timeDiffMilliseconds(e1, s1):
    return (e1 - s1).total_seconds()

def setup():
    # Read in the job template file
    with open('job.yaml', 'r') as file :
        job_tmpl = file.read()
    host = "10.104.213.87"
    jobid = 0

    # Process workload file
    f = open('temp.tr', 'r')
    for row in f:
        row = row.split()
        num_tasks = int(row[1])
        est_time = float(row[2])
        actual_duration = []
        for index in range(num_tasks):
            actual_duration.append(float(row[3+index]))
        # Replace the template file with actual values
        jobid += 1
        jobstr = "job"+str(jobid)
        filedata = job_tmpl.replace('$JOBID',jobstr).replace("$NUM_TASKS",str(num_tasks))
        filename = jobstr+".yaml"
        with open(filename, 'w') as file:
          file.write(filedata)
        q = rediswq.RedisWQ(name=jobstr, host=host)
        q.rpush(actual_duration)
    f.close()


def main():
    jobid = 0
    start_epoch = 0.0
    threads = []

    setup()
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
    stats(jobid)
    print "Script took a total of", time() - start_epoch,"s"

def apply_job(filename, jobstr, start_epoch):
        #This command takes about 0.25s. So jobs can't arrive faster than this.
        subprocess.check_output(["kubectl","apply", "-f", filename])
        print "Starting", jobstr, "at", time() - start_epoch

def stats(num_jobs):
    pending_jobs = True
    #Change directory to scheduler logs
    os.chdir("/local/scratch/")
    #Look for 12:14:58.422793 pattern in logs
    pattern = '\d{2}:\d{2}:\d{2}\.\d{6}'
    compiled = re.compile(pattern)
    log_file_name = '_'.join(["logs", "X"+str(SPEEDUP), str(num_jobs)])
    while pending_jobs:
        pending_jobs = add_pod_info()
        process(compiled)
        sleep(5)
    post_process(log_file_name)

def add_pod_info():
    if len(job_to_podlist.keys()) == 0:
        return False
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
        pods_list = subprocess.check_output(['kubectl','get', 'pods', '--selector=job-name='+jobname, '--no-headers'])
        for pod in pods_list.splitlines():
            podstrs = pod.split()
            podname = podstrs[0]
            status = podstrs[2]
            if status == "OutOfpods" or status == "Evicted":
                #Known error. This happens when etcd is slower than events in the cluster.
                #However, the job has sucessfully completed. So, look for other pods.
                continue
            if status != "Completed":
                raise AssertionError("Pod" + podname + "is not in a completed state!")
            job_to_podlist[jobname].append(podname)
    return True

def process(compiled):
    QUEUE_ADD_LOG    = "Add event for unscheduled pod"
    QUEUE_DELETE_LOG = "Delete event for unscheduled pod"
    START_SCH_LOG    = "About to try and schedule pod"
    UNABLE_SCH_LOG   = "Unable to schedule pod"
    BIND_LOG         = "Attempting to bind pod to node"

    default_time = timedelta(microseconds=0)
    for jobname,pods in job_to_podlist.items():
        # Fetch all pod related stats for each pod.
        has_pods = False
        for podname in pods:
            has_pods = True
            #Two outputs for this pod
            queue_time = timedelta(microseconds=0)
            scheduling_algorithm_time = timedelta(microseconds=0)
            #Interim points
            queue_add_time = datetime.min
            queue_eject_time = datetime.min
            start_sch_time = datetime.min
            unable_sch_time = datetime.min
            attempt_bind_time = datetime.min
            nodename=''
            logs =  subprocess.check_output(['grep','-ri',podname, 'syslog']).split('\n')
            #Grep'ed logs can be out of order in time.
            #sch_queue_eject and unable_sch may happen multiple times.
            for log in logs:
                #This log happens exactly once
                if QUEUE_ADD_LOG in log:
                    if queue_add_time > datetime.min:
                        raise AssertionError("Check calculcations for pod for queue add time"+ podname)
                    queue_add_time = extractDateTime(compiled.search(log).group(0))
                    continue
                #This log happens exactly once
                if QUEUE_DELETE_LOG in log:
                    queue_eject_time = extractDateTime(compiled.search(log).group(0))
                    print "Job", jobname,"Pod", podname,"Started", queue_add_time, "ended at", queue_eject_time,
                    queue_time = queue_eject_time - queue_add_time
                    break
                if START_SCH_LOG in log:
                    if start_sch_time > datetime.min:
                        raise AssertionError("Check calculcations for pod for start sch time"+ podname)
                    start_sch_time = extractDateTime(compiled.search(log).group(0))
                    continue
                if UNABLE_SCH_LOG in log:
                    if start_sch_time == datetime.min:
                        raise AssertionError("Check calculcations for pod for unschedulable pod time"+ podname)
                    unable_sch_time = extractDateTime(compiled.search(log).group(0))
                    scheduling_algorithm_time = scheduling_algorithm_time + unable_sch_time - start_sch_time
                    start_sch_time = datetime.min
                    continue
                #This log happens exactly once
                if BIND_LOG in log:
                    if start_sch_time == datetime.min:
                        raise AssertionError("Check calculcations for pod for unschedulable pod time"+ podname)
                    attempt_bind_time = extractDateTime(compiled.search(log).group(0))
                    scheduling_algorithm_time = scheduling_algorithm_time + attempt_bind_time - start_sch_time
                    start_sch_time = datetime.min
                    nodename = log.split('node=')[1]
                    continue
            print "Scheduler Queue Time", queue_time,"Scheduling Algorithm Time", scheduling_algorithm_time, "Node", nodename
            qtimes.append(timeDiffMilliseconds(queue_time, default_time))
            algotimes.append(timeDiffMilliseconds(scheduling_algorithm_time, default_time))
        if has_pods:
            del job_to_podlist[jobname]

def post_process(log_file_name):
    log_file = open(log_file_name, 'w')
    qtimes.sort()
    algotimes.sort()
    print >> log_file, "Total number of pods evaluated", len(qtimes)
    print >> log_file, "Stats for Scheduler Queue Times -",percentile(qtimes, 50), percentile(qtimes, 90), percentile(qtimes, 99)
    print >> log_file, "Stats for Scheduler Algorithm Times -"",",percentile(algotimes, 50), percentile(algotimes, 90), percentile(algotimes, 99)
    log_file.close()

if __name__ == '__main__':
    main()
