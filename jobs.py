#!/usr/bin/env python
import rediswq
import os
import re
import subprocess
import asyncio
from datetime import timedelta, datetime
from time import sleep, time, mktime
from numpy import percentile
from random import randint
import collections
import signal
import sys
from kubernetes import client, config, utils
from kubernetes.client.rest import ApiException
from multiprocessing import Pool, Queue
from math import ceil

#TODO - Handle duplicate values when inserting into redis.
#A dict for pods' watch to keep track of.
job_to_podlist = collections.defaultdict(set)
SPEEDUP = 200
schedulertojob = collections.defaultdict(int)
job_to_scheduler = {}
job_to_numtasks = {}
chunks = Queue()
job_start_time = {}
#Stats printed out.
pods_discarded = 0
jrt = []
qtimes = []
algotimes = []
node_to_pod_count = collections.defaultdict(int)
scheduler_to_algotimes = collections.defaultdict(int)

config.load_kube_config()
k8s_client = client.ApiClient()

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
    f.close()
    return jobid

def main():
    jobid=0
    start_epoch = 0.0
    threads = []

    if len(sys.argv) != 4:
        print("Incorrect number of parameters. Usage: python jobs.py d 10 -e")
        sys.exit(1)

    is_central = sys.argv[1] == 'c'
    num_sch = int(sys.argv[2])
    max_job_id = setup(is_central, num_sch)
    num_processes = setup_chunks(max_job_id)
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
        if sleep_time > 0:
            sleep(sleep_time)
        job_start_time[jobstr] = time()
        utils.create_from_yaml(k8s_client, filename)
        print("Starting", jobstr, "at", job_start_time[jobstr] - start_epoch)

    f.close()

    #Process scheduler stats.    
    stats(num_processes)
    print("Script took a total of", time() - start_epoch,"s")

def setup_chunks(num_jobs):
    num_cpu = os.cpu_count() - 1
    #Calculate max chunk size that each cpu should handle.
    chunk_size = int(ceil(float(num_jobs) / float(num_cpu)))
    #jobs start at id 1.
    start_index = 1
    done = False
    count = 0
    #Create start and ends of chunks
    for i in range(num_cpu):
        # Max job id should be 1 more than the desired end index.
        max_job_id = start_index + chunk_size
        if max_job_id > num_jobs:
            max_job_id = num_jobs + 1
            done = True
        chunks.put((start_index, max_job_id))
        count += 1
        if done:
            # Don't need to spin up num_cpu processes.
            break
        start_index += chunk_size
    return count if count < num_cpu else num_cpu

def init_process(q):
    start, end =  q.get()
    global all_jobs_jobwatch, all_jobs_podwatch, job_to_podlist, jrt
    # Global values to be used within the process.
    all_jobs_jobwatch = [''.join(["job",str(n)]) for n in range(start, end)]
    all_jobs_podwatch = all_jobs_jobwatch[:]
    # Global values to be returned by processes.
    job_to_podlist = collections.defaultdict(set)
    jrt = []

def stats(num_processes):
    with Pool(processes=num_processes, initializer=init_process, initargs=(chunks,)) as p:
        results=[]
        #Create processes
        for i in range(num_processes):
            #Spin up the process
            r = p.apply_async(get_job_and_pod_events, (), callback=stitch_partial_results)
            #Remember to wait for results
            results.append(r)
        for r in results:
            r.wait()

    #Change directory to scheduler logs
    os.chdir("/local/scratch/")
    #Look for 12:14:58.422793 pattern in logs
    pattern = '\d{2}:\d{2}:\d{2}\.\d{6}'
    compiled = re.compile(pattern)

    process(compiled)
    post_process()

def stitch_partial_results(partial_results):
    global job_to_podlist, jrt
    #partial_results is of the form (job_to_podlist, jrt)
    partial_job_to_podlist = partial_results[0]
    partial_jrt = partial_results[1]
    job_to_podlist.update(partial_job_to_podlist)
    jrt = jrt + partial_jrt

def get_job_and_pod_events():
    # Watch for completed jobs.
    job_client = client.BatchV1Api()
    pod_client = client.CoreV1Api()

    ioloop = asyncio.get_event_loop()
    return ioloop.run_until_complete(gather_stats(pod_client, job_client))

async def gather_stats(pod_client, job_client):
    coroutines = [process_completed_pods(pod_client, job_client), process_completed_jobs(job_client)]
    return await asyncio.gather(*coroutines, return_exceptions=True)

def process_job_object(job_object, job_client, last_resource_version):
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
    print("Job", jobname, "has JRT", job_completion, "v=",last_resource_version)
    jrt.append(job_completion)
    all_jobs_jobwatch.remove(jobname)
    if jobname not in all_jobs_podwatch:
        #Pods watch has also finished processing this job.
        # Delete job since all checks have passed.
        job_client.delete_namespaced_job(name=jobname, namespace="default",
            body=client.V1DeleteOptions(
                grace_period_seconds=0,
                propagation_policy='Background'))
    if len(all_jobs_jobwatch) == 0:
        return True
    return False

#Returns job_events and any exceptions raised
async def get_job_events(job_client, limit, continue_param, timeout_seconds, last_resource_version):
    try:
        if continue_param != None:
            return job_client.list_namespaced_job(namespace='default', limit=limit, _continue=continue_param, timeout_seconds=timeout_seconds), None
        #If resource_version is set then send the events from exact version, else if 0, then send event from any version.
        return job_client.list_namespaced_job(namespace='default', limit=limit, resource_version = last_resource_version, resource_version_match='NotOlderThan', timeout_seconds=timeout_seconds), None
    except ApiException as e:
        print("Exception", e)
        return None, e

# For running this along with the job creation threads, split creation and watch on
# two different machines.
async def process_completed_jobs(job_client):
    print("Starting job processing loop")
    #Run the main job loop with the resource version.
    #Only watch for completed jobs. Caution : This watch runs forever. So, actively break.
    limit = 20
    timeout_seconds = 5
    job_events = job_client.list_namespaced_job(namespace='default', limit=limit)
    jobs_events_none_counter = 0
    while True:
        if job_events != None:
            continue_param = job_events.metadata._continue
            last_resource_version = job_events.metadata.resource_version
            #print("Jobs - Got", len(job_events.items),"events at version -",last_resource_version)
            for job_object in job_events.items:
                is_return = process_job_object(job_object, job_client, last_resource_version)
                if is_return:
                    print("No more jobs left to process")
                    return jrt
        #print("Jobs watch yields")
        await asyncio.sleep(0)
        job_events, e = await get_job_events(job_client,limit, continue_param, timeout_seconds, last_resource_version)
        if e != None:
            # TODO - What if there are missed events between now and new resource version?
            # Handle by actively querying for them.
            if e.status == 410:
                print("JOB - Caught resource version too old exception.")
                last_resource_version = 0
                continue_param = None
            else:
                raise e

#Returns pod_events and any exceptions raised
async def get_pod_events(pod_client, limit, continue_param, timeout_seconds, last_resource_version):
    try:
        if continue_param != None:
            return pod_client.list_namespaced_pod(namespace='default', limit=limit, _continue=continue_param, field_selector='status.phase=Succeeded', timeout_seconds=timeout_seconds), None
        #If resource_version is set then send the events from exact version, else if 0, then send event from any version.
        return pod_client.list_namespaced_pod(namespace='default', limit=limit, resource_version = last_resource_version, resource_version_match='NotOlderThan',field_selector='status.phase=Succeeded', timeout_seconds=timeout_seconds), None
    except ApiException as e:
        print("Exception", e)
        return None, e


#TODO - Reduce processing done in this func.
async def process_completed_pods(pod_client, job_client):
    print("Starting pod events' loop")
    #We are not interested in a pod that Failed.
    #There are definitely others since the job will (has) complete(d).
    limit= 200
    timeout_seconds = 5
    pod_events = pod_client.list_namespaced_pod(namespace='default', limit=limit, field_selector='status.phase=Succeeded')
    pods_events_none_counter = 0
    while True:
        if pod_events != None:
            continue_param = pod_events.metadata._continue
            last_resource_version = pod_events.metadata.resource_version
            #print("Pods - Got", len(pod_events.items),"events at version",last_resource_version)
            for pod in pod_events.items:
                is_return = process_pod_object(pod, job_client, last_resource_version)
                if is_return:
                    print("No more pods left to process")
                    return job_to_podlist
        #print("Pods watch yields")
        await asyncio.sleep(0)
        pod_events, e = await get_pod_events(pod_client,limit, continue_param, timeout_seconds, last_resource_version)
        if e != None:
            # TODO - What if there are missed events between now and new resource version?
            # Handle by actively querying for them.
            if e.status == 410: # Resource too old
                print("POD - Caught resource version too old exception.")
                continue_param = None
                last_resource_version = 0
            else:
                raise e

def process_pod_object(pod, job_client, last_resource_version):
    if 'job-name' not in pod.metadata.labels:
        return False
    jobname = pod.metadata.labels['job-name']
    if jobname not in all_jobs_podwatch:
        return False
    job_to_podlist[jobname].add(pod.metadata.name)
    is_return = cleanup(job_client, jobname, last_resource_version)
    return is_return


def cleanup(job_client, jobname, last_resource_version):
    #Decide to cleanup the job.
    if jobname in all_jobs_podwatch:
        if len(job_to_podlist[jobname]) >= job_to_numtasks[jobname]:
            all_jobs_podwatch.remove(jobname)
            print("Pod list for", jobname, "is", job_to_podlist[jobname], "v=", last_resource_version)
            if jobname not in all_jobs_jobwatch:
                #Jobs watch has also finished processing this job.
                # Delete job since all checks have passed.
                job_client.delete_namespaced_job(name=jobname, namespace="default",
                    body=client.V1DeleteOptions(
                        grace_period_seconds=0,
                        propagation_policy='Background'))
    if len(all_jobs_podwatch) == 0:
        return True
    return False


def process_pod_scheduling_params(compiled, jobname):
    QUEUE_ADD_LOG    = "Add event for unscheduled pod"
    QUEUE_DELETE_LOG = "Delete event for unscheduled pod"
    START_SCH_LOG    = "About to try and schedule pod"
    UNABLE_SCH_LOG   = "Unable to schedule pod"
    BIND_LOG         = "Attempting to bind pod to node"

    default_time = timedelta(microseconds=0)
    # job_to_podlist only contains completed jobs.
    if len(job_to_podlist[jobname]) > job_to_numtasks[jobname]:
        pod_str = temp = ''.join([str(item) for item in job_to_podlist[jobname]])
        raise AssertionError("For " + jobname + "number of tasks is " + str(job_to_numtasks[jobname]) + "but its list has the following pods" + pod_str)
    # Fetch all pod related stats for each pod.
    pods = job_to_podlist[jobname]
    schedulername = job_to_scheduler[jobname]
    return_results = []
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
                    print("---------Check calculcations for pod for unschedulable pod time", podname)
                    #Skip this pod's scheduling queue and algorithm time calculations.
                    pods_discarded += 1
                    break
                attempt_bind_time = extractDateTime(compiled.search(log).group(0))
                scheduling_algorithm_time = scheduling_algorithm_time + attempt_bind_time - start_sch_time
                start_sch_time = datetime.min
                nodename = log.split('node=')[1]
                continue
        #print("Pod", podname, "- Scheduler Queue Time", queue_time,"Scheduling Algorithm Time", scheduling_algorithm_time, "Node", nodename)
        qtime = timeDiff(queue_time, default_time)
        algotime = timeDiff(scheduling_algorithm_time, default_time)
        return_results.append((nodename, schedulername, qtime, algotime))
    return return_results

def complete_processing(results):
    for r in results:
        # r = (nodename, schedulername, qtime, algotime)
        node_to_pod_count[r[0]] += 1
        scheduler_to_algotimes[r[1]] += r[3]
        qtimes.append(r[2])
        algotimes.append(r[3])

def process(compiled):
    num_cpu = os.cpu_count() - 1
    with Pool(num_cpu) as p:
        results=[]
        for jobname in job_to_podlist.keys():
            r = p.apply_async(process_pod_scheduling_params, (compiled, jobname), callback=complete_processing)
            results.append(r)
        for r in results:
            r.wait()

def post_process():
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

def signal_handler(sig, frame):
    print("-----Dumping job_to_podlist for all current jobs in podwatch--------")
    for jobname in all_jobs_podwatch:
        print(jobname,"-",job_to_podlist[jobname])
    print("-----DONE Dumping job_to_podlist for all current jobs in podwatch--------")

if __name__ == '__main__':
    signal.signal(signal.SIGUSR1, signal_handler)
    main()
