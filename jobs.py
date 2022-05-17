#!/usr/bin/env python
import rediswq
import os
import re
import subprocess
import asyncio
from threading import Thread
from datetime import timedelta, datetime
from time import sleep, time, mktime
from numpy import percentile
from random import randint
import collections
import sys
from kubernetes import client, config, watch
from kubernetes.client.rest import ApiException

#TODO - Handle duplicate values when inserting into redis.
#A list for both pods and jobs watch to keep track of.
#A dict for pods' watch to keep track of.
job_to_podlist = collections.defaultdict(set)
SPEEDUP = 200
schedulertojob = collections.defaultdict(int)
job_to_scheduler = {}
job_to_numtasks = {}
#A list for jobs' watch to keep track of.
all_jobs_jobwatch = set()
#A list for pods' watch to keep track of.
all_jobs_podwatch = set()
job_start_time = {}
#Stats printed out.
pods_discarded = 0
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
        print("CENTRALIZED SCHEDULER")
    else:
        print("DECENTRALIZED SCHEDULER")
     
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
        all_jobs_jobwatch.add(jobstr)
        all_jobs_podwatch.add(jobstr)
    f.close()


def main():
    jobid = 0
    start_epoch = 0.0
    threads = []

    if len(sys.argv) != 4:
        print("Incorrect number of parameters. Usage: python jobs.py d 10 -e")
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
        # Pick the correct job file.
        filename = jobstr+".yaml"
        #Sleep till it is time to start the job.
        endTime = time()
        sleep_time = start_epoch + arrival_time - endTime
        if sleep_time < 0:
            print("Script loop started at", startTime,"and ran for", endTime - startTime,"sec but sleep is -ve at", sleep_time)
            print("Next job due at", start_epoch + arrival_time, "but time now is", endTime)
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
    print("Script took a total of", time() - start_epoch,"s")

def apply_job(filename, jobstr, start_epoch):
        #This command takes about 0.25s. So jobs can't arrive faster than this.
        subprocess.check_output(["kubectl","apply", "-f", filename])
        start_time = time()
        print("Starting", jobstr, "at", start_time - start_epoch)
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

    ioloop = asyncio.get_event_loop()
    ioloop.run_until_complete(gather_stats(pod_client, job_client))

    process(compiled)
    post_process()

async def gather_stats(pod_client, job_client):
    coroutines = [process_completed_pods(pod_client, job_client), process_completed_jobs(job_client)]
    await asyncio.gather(*coroutines, return_exceptions=True)

def process_job_object(job_object, job_client):
    jobname = job_object.metadata.name
    if jobname not in all_jobs_jobwatch:
        #We have finished processing this job.
        return False
    status = job_object.status
    if status.completion_time == None:
        return False
    #Completion Time is set, so job is Complete or Failed.
    if status.conditions[0].type != "Complete":
        #Job might have failed.
        raise AssertionError("Job" + jobname + "has failed!")
    # Process the completion time of the job to calculate its JRT.
    completed_sec_from_epoch = (status.completion_time.replace(tzinfo=None) - datetime(1970,1,1)).total_seconds()
    job_completion = completed_sec_from_epoch - job_start_time[jobname]
    print("Job", jobname, "has JRT", job_completion)
    jrt.append(job_completion)
    all_jobs_jobwatch.remove(jobname)
    if jobname not in all_jobs_podwatch:
        #Pods watch has also finished processing this job.
        # Delete job since all checks have passed.
        job_client.delete_namespaced_job(name=jobname, namespace="default",
            body=client.V1DeleteOptions(
                grace_period_seconds=0,
                propagation_policy='Background'))
        #subprocess.call(["kubectl", "delete", "jobs", jobname])
    if len(all_jobs_jobwatch) == 0:
        return True
    return False

# For running this along with the job creation threads, split creation and watch on
# two different machines.
async def process_completed_jobs(job_client):
    print("Starting job processing loop")
    #Run the main job loop with the resource version.
    #Only watch for completed jobs. Caution : This watch runs forever. So, actively break.
    limit = 5
    job_events = job_client.list_namespaced_job(namespace='default', limit=limit)
    while True:
        try:
            continue_param = job_events.metadata._continue
            last_resource_version = job_events.metadata.resource_version
            for job_object in job_events.items:
                is_return = process_job_object(job_object, job_client)
                if is_return:
                    w.stop()
                    print("No more jobs left to process")
                    return
            #print("Jobs watch yields")
            await asyncio.sleep(0)
            if continue_param != None:
                job_events = job_client.list_namespaced_job(namespace='default', limit=limit, _continue=continue_param)
            else:
                job_events = job_client.list_namespaced_job(namespace='default', limit=limit, resource_version = last_resource_version, resource_version_match='NotOlderThan')
        except ApiException as e:
            print("Exception", e)
            # TODO - What if there are missed events between now and new resource version?
            # Handle by actively querying for them.
            if e.status == 410: # Resource too old
                print("JOB WATCH - Caught resource version exception and passing.")
                return process_completed_jobs(job_client)
            else:
                raise

def process_pod_object(pod, job_client):
    if 'job-name' not in pod.metadata.labels:
        return False
    jobname = pod.metadata.labels['job-name']
    if jobname not in all_jobs_podwatch:
        return False
    pod_status =  pod.status.phase
    job_to_podlist[jobname].add(pod.metadata.name)
    is_return = cleanup(job_client)
    return is_return

#TODO - Reduce processing done in this func.
async def process_completed_pods(pod_client, job_client):
    print("Starting pod events' loop")
    #We are not interested in a pod that Failed.
    #There are definitely others since the job will (has) complete(d).
    limit=50
    pod_events = pod_client.list_namespaced_pod(namespace='default', limit=limit, field_selector='status.phase=Succeeded')
    while True:
        try:
            continue_param = pod_events.metadata._continue
            last_resource_version = pod_events.metadata.resource_version
            #print("Got continue param", continue_param, "and last_resource_version", last_resource_version)
            for pod in pod_events.items:
                is_return = process_pod_object(pod, job_client)
                if is_return:
                    w.stop()
                    print("Pods watch returning")
                    return
            #print("Pods watch yields")
            await asyncio.sleep(0)
            if continue_param != None:
                pod_events = pod_client.list_namespaced_pod(namespace='default', limit=limit, _continue=continue_param, field_selector='status.phase=Succeeded')
            else:
                pod_events = pod_client.list_namespaced_pod(namespace='default', limit=limit, resource_version = last_resource_version, resource_version_match='NotOlderThan',field_selector='status.phase=Succeeded')
            #pod_events = pod_client.list_namespaced_pod(namespace='default', limit=limit, _continue=continue_param, field_selector='status.phase=Succeeded')
            #print("Got new set of events", len(pod_events.items))
        except ApiException as e:
            # TODO - What if there are missed events between now and new resource version?
            # Handle by actively querying for them.
            print("Exception",e)
            if e.status == 410: # Resource too old
                print("POD WATCH - Caught resource version exception and passing.")
                return process_completed_pods(pod_client, job_client)
            else:
                raise

def cleanup(job_client):
    jobs = []
    for jobname in job_to_podlist.keys():
        if jobname not in all_jobs_podwatch:
            continue
        if len(job_to_podlist[jobname]) < job_to_numtasks[jobname]:
            continue
        if len(job_to_podlist[jobname]) > job_to_numtasks[jobname]:
            pod_str = temp = ''.join([str(item) for item in job_to_podlist[jobname]])
            raise AssertionError("For " + jobname + "number of tasks is " + str(job_to_numtasks[jobname]) + "but its list has the following pods" + pod_str)
        #len(job_to_podlist[jobname]) == job_to_numtasks[jobname]:
        #print("Trying pods of", jobname, " - ",len(job_to_podlist[jobname]),":",job_to_numtasks[jobname])
        jobs.append(jobname)
    for jobname in jobs:
        all_jobs_podwatch.remove(jobname)
        if jobname not in all_jobs_jobwatch:
            #Jobs watch has also finished processing this job.
            # Delete job since all checks have passed.
            job_client.delete_namespaced_job(name=jobname, namespace="default",
                body=client.V1DeleteOptions(
                    grace_period_seconds=0,
                    propagation_policy='Background'))
            #subprocess.call(["kubectl", "delete", "jobs", jobname])
    if len(all_jobs_podwatch) == 0:
        print("Request to terminate pod loop")
        return True
    return False

def process(compiled):
    QUEUE_ADD_LOG    = "Add event for unscheduled pod"
    QUEUE_DELETE_LOG = "Delete event for unscheduled pod"
    START_SCH_LOG    = "About to try and schedule pod"
    UNABLE_SCH_LOG   = "Unable to schedule pod"
    BIND_LOG         = "Attempting to bind pod to node"

    default_time = timedelta(microseconds=0)
    # job_to_podlist only contains completed jobs.
    for jobname, pods in job_to_podlist.items():
        # Fetch all pod related stats for each pod.
        schedulername = job_to_scheduler[jobname]
        for podname in pods:
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
            logs =  subprocess.check_output(['grep','-ri',podname, 'syslog'], encoding='utf-8', text=True).split('\n')
            # TODO - Grep'ed logs can be out of order in time.
            # sch_queue_eject and unable_sch may happen multiple times.
            # However, this function assumes in order for caculation of scheduling and queue times.
            for log in logs:
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
                    break
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
                        print("Check calculcations for pod for unschedulable pod time", podname)
                        #Skip this pod's scheduling queue and algorithm time calculations.
                        pods_discarded += 1
                        break
                    attempt_bind_time = extractDateTime(compiled.search(log).group(0))
                    scheduling_algorithm_time = scheduling_algorithm_time + attempt_bind_time - start_sch_time
                    start_sch_time = datetime.min
                    nodename = log.split('node=')[1]
                    continue
            #print("Pod", podname, "- Scheduler Queue Time", queue_time,"Scheduling Algorithm Time", scheduling_algorithm_time, "Node", nodename)
            node_to_pod_count[nodename] += 1
            qtimes.append(timeDiff(queue_time, default_time))
            algotime = timeDiff(scheduling_algorithm_time, default_time)
            algotimes.append(algotime)
            scheduler_to_algotimes[schedulername] += algotime

def post_process():
    qtimes.sort()
    algotimes.sort()
    jrt.sort()
    node_to_pods = list(dict(sorted(node_to_pod_count.items(), key=lambda item: item[1])).values())
    scheduler_algotimes = list(dict(sorted(scheduler_to_algotimes.items(), key=lambda v:(v[1]))).values())
    print("Total number of pods evaluated", len(qtimes))
    print("Stats for Scheduler Queue Times -",percentile(qtimes, 50), percentile(qtimes, 90), percentile(qtimes, 99))
    print("Stats for Scheduler Algorithm Times -"",",percentile(algotimes, 50), percentile(algotimes, 90), percentile(algotimes, 99))
    print("Stats for JRT -"",",percentile(jrt, 50), percentile(jrt, 90), percentile(jrt, 99))
    print("Schedulers and number of tasks they assigned", schedulertojob)
    print("Count of pods on nodes", percentile(node_to_pods, 50), percentile(node_to_pods, 90), percentile(node_to_pods, 99))
    print("Scheduler algorithm time per scheduler", percentile(scheduler_algotimes, 50), percentile(scheduler_algotimes, 90), percentile(scheduler_algotimes, 99))
    percent_discarded = pods_discarded / (pods_discarded + len(scheduler_algotimes)) * 100
    print("Pods discarded is", pods_discarded, "and that is", percent_discarded, "% of all pods")

if __name__ == '__main__':
    main()
