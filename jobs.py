#!/usr/bin/env python
import rediswq
import os
import re
import subprocess
from threading import Thread
from datetime import timedelta, datetime
from time import sleep, time, mktime
from numpy import percentile
from random import randint
import collections
import sys
from kubernetes import client, config, watch

#TODO - Handle dup;licate values when inserting into redis.
#Maintains job to pod list mapping for completed jobs.
job_to_podlist = {}
SPEEDUP = 20
schedulertojob = collections.defaultdict(int)
job_to_scheduler = {}
job_to_numtasks = {}
job_start_time = {}
job_response_time = {}
#Stats printed out.
jrt = []
qtimes = []
algotimes = []
pod_start = {}
pod_end = {}
pod_node = {}
pod_durations = {}
pod_qdiff= {}
node_to_pod_count = collections.defaultdict(int)
scheduler_to_algotimes = collections.defaultdict(int)

def extractDateTime(timestr):
    return datetime.strptime(timestr,'%H:%M:%S.%f')

# Returns difference in two timedeltas in seconds
def timeDiff(e1, s1):
    return (e1 - s1).total_seconds()

def setup(is_central, num_sch):
    # Read in the job template file
    job_file = "job_d.yaml"
    if is_central:
        job_file = "job_c.yaml"
        print "CENTRALIZED SCHEDULER"
    else:
        print "DECENTRALIZED SCHEDULER"
     
    with open(job_file, 'r') as file :
        job_tmpl = file.read()
    host = "10.110.132.160"
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
        jobstr = "".join(["job",str(jobid)])
        job_to_numtasks[jobstr]=num_tasks
        filedata = ""
        if not is_central:
            # Pick a number from 1 - num_sch. This job will be scheduled by that scheduler.
            schedulername = "".join(["scheduler",str(randint(1,num_sch))])
            schedulertojob[schedulername] += num_tasks
            job_to_scheduler[jobstr] = schedulername
            filedata = job_tmpl.replace('$JOBID',jobstr).replace("$NUM_TASKS",str(num_tasks)).replace("$SCHEDULER_NAME", schedulername).replace("$ESTRUNTIME", str(est_time))
        else:
            filedata = job_tmpl.replace('$JOBID',jobstr).replace("$NUM_TASKS",str(num_tasks)).replace("$ESTRUNTIME", str(est_time))
            job_to_scheduler[jobstr] = "schedulera"
        filename = jobstr+".yaml"
        with open(filename, 'w') as file:
          file.write(filedata)
        q = rediswq.RedisWQ(name=jobstr, host=host)
        # Cleanup possible remnants of an older run
        q.delete(jobstr)
        q.rpush(actual_duration)
    f.close()


def main():
    jobid = 0
    start_epoch = 0.0
    threads = []

    if len(sys.argv) != 3:
        print "Incorrect number of parameters"
        sys.exit(1)

    is_central = sys.argv[1] == 'c'
    num_sch = int(sys.argv[2])
    setup(is_central, num_sch)
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
            #raise AssertionError('script overran job interval!')
        else:    
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
        start_time = time()
        print "Starting", jobstr, "at", start_time - start_epoch
        job_response_time[jobstr] = 0
        job_start_time[jobstr] = start_time

def stats(num_jobs):
    pending_jobs = True
    #Change directory to scheduler logs
    os.chdir("/local/scratch/")
    #Look for 12:14:58.422793 pattern in logs
    pattern = '\d{2}:\d{2}:\d{2}\.\d{6}'
    compiled = re.compile(pattern)

    # Watch for completed jobs.
    config.load_kube_config()
    job_client = client.BatchV1Api()
    pod_client = client.CoreV1Api()
    w = watch.Watch()

    while pending_jobs:
        pending_jobs = get_completed_jobs(w, job_client, pod_client)
        process(compiled)
        sleep(1)
    post_process()

# For running this along with the job creation threads, split creation and watch on
# two different machines.
def get_completed_jobs(w, job_client, pod_client):
    if len(job_to_numtasks.keys()) == 0:
        w.stop()
        print "No more jobs left to process"
        return False
    #Only watch for completed jobs. Caution : This watch runs forever. So, actively break.
    for job_event in w.stream(func=job_client.list_namespaced_job, namespace='default'):
        job_object = job_event['object']
        jobname = job_object.metadata.name
        if jobname not in job_to_numtasks.keys():
            #This job has finished processing.
            continue
        status = job_object.status
        if status.completion_time != None:
            #Completion Time can be not None when Complete or Failed.
            if status.conditions[0].type != "Complete":
                #Job might have failed.
                raise AssertionError("Job" + jobname + "has failed!")
            # Process the completion time of the job to calculate its JRT.
            print jobname,"has completed at time", status.completion_time
            completed_sec_from_epoch = (status.completion_time.replace(tzinfo=None) - datetime(1970,1,1)).total_seconds()
            job_completion = completed_sec_from_epoch - job_start_time[jobname]
            if job_completion > job_response_time[jobname]:
                job_response_time[jobname] = job_completion
            # Get all pods of the job.
            pods = pod_client.list_namespaced_pod(namespace='default', label_selector='job-name={}'.format(jobname))
            for pod in pods.items:
                pod_status =  pod.status.phase
                if pod_status != "Succeeded":
                    #We are not interested in a pod that Failed.
                    #There are definitely others since the job has completed.
                    print pod.metadata.name,"has failed with status", pod_status,". Ignoring."
                    continue
                job_to_podlist[jobname].append(pod.metadata.name)
            if len(job_to_podlist[jobname]) != job_to_numtasks[jobname]:
                raise AssertionError("For " + jobname + "number of tasks is " + str(job_to_numtasks[jobname]) + "but its list has the following pods" + pods)
            del job_to_numtasks[jobname]
            break

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
        pods_evaluated = False
        schedulername = job_to_scheduler[jobname]
        for podname in pods:
            pods_evaluated = True
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
                    #print "Node", nodename,"Pod", podname,"Started", queue_add_time, "ended at", queue_eject_time
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
            #print "Pod", podname, "- Scheduler Queue Time", queue_time,"Scheduling Algorithm Time", scheduling_algorithm_time, "Node", nodename
            node_to_pod_count[nodename] += 1
            qtimes.append(timeDiff(queue_time, default_time))
            algotime = timeDiff(scheduling_algorithm_time, default_time)
            algotimes.append(algotime)
            scheduler_to_algotimes[schedulername] += algotime
        if pods_evaluated == True:
            print "Job", jobname, "has JRT", job_response_time[jobname]
            jrt.append(job_response_time[jobname])
            del job_to_podlist[jobname]
            # Delete job since all checks have passed.
            subprocess.call(["kubectl", "delete", "jobs", jobname])

def post_process():
    qtimes.sort()
    algotimes.sort()
    jrt.sort()
    node_to_pods = dict(sorted(node_to_pod_count.items(), key=lambda v:(v[1]))).values()
    scheduler_algotimes = dict(sorted(scheduler_to_algotimes.items(), key=lambda v:(v[1]))).values()
    print "Total number of pods evaluated", len(qtimes)
    print "Stats for Scheduler Queue Times -",percentile(qtimes, 50), percentile(qtimes, 90), percentile(qtimes, 99)
    print "Stats for Scheduler Algorithm Times -"",",percentile(algotimes, 50), percentile(algotimes, 90), percentile(algotimes, 99)
    print "Stats for JRT -"",",percentile(jrt, 50), percentile(jrt, 90), percentile(jrt, 99)
    print "Schedulers and number of tasks they assigned", schedulertojob
    print "Count of pods on nodes", percentile(node_to_pods, 50), percentile(node_to_pods, 90), percentile(node_to_pods, 99)
    print "Scheduler algorithm time per scheduler", percentile(scheduler_algotimes, 50), percentile(scheduler_algotimes, 90), percentile(scheduler_algotimes, 99)

if __name__ == '__main__':
    main()
