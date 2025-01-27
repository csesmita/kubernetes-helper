#!/usr/bin/env python
import rediswq
import os
import re
import subprocess
from datetime import timedelta, datetime
from time import sleep, time, mktime
from threading import Timer
from numpy import percentile
from random import randint, gauss, random
import collections
import sys
import signal
from kubernetes import client, config, utils
from kubernetes.client.rest import ApiException
from math import ceil

#TODO - Handle duplicate values when inserting into redis.
#A dict for pods' watch to keep track of.
job_to_podlist = collections.defaultdict(set)
SPEEDUP = 1000
#2 hours
RUNTIME = 7200.0
schedulertojob = collections.defaultdict(int)
job_to_scheduler = {}
job_to_numtasks = {}
job_start_time = {}
max_job_id = 0
start_epoch = 0.0
#Stats printed out.
job_to_jrt = {}
jrt = []
qtimes = []
algotimes = []
kubeletqtimes = []
node_to_pod_count = collections.defaultdict(int)
scheduler_to_algotimes = collections.defaultdict(int)
jobnames = []
jobs_pending = []
config.load_kube_config()
k8s_client = client.ApiClient()
job_client = client.BatchV1Api()

host = "10.104.173.26"

UTIL_LOG_INTERVAL = 120
UTIL_LOG_NAME = "node_utilization.txt"
def log_node_util():
    #print out to file
    with open(UTIL_LOG_NAME, "a+") as f:
        subprocess.run(["kubectl", "top", "nodes", "--sort-by", "cpu"], stdout=f)

class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)


def extractDateTime(timestr):
    return datetime.strptime(timestr,'%H:%M:%S.%f')

# Returns difference in two timedeltas in seconds
def timeDiff(e1, s1):
    return (e1 - s1).total_seconds()

def setup_job(row, jobid, is_central, num_sch, job_tmpl):
    setup_start_time = time()
    row = row.split()
    num_tasks = int(row[1])
    est_time = float(row[2])
    while True:
        #mis-est is a normal distribution of 15% on the mean and 50% on the 90th percentile (z-score=1.645) of the original estimate
        misest = est_time * gauss(15.0, 30.395) / 100.0
        #positive or negative misest?
        sign = randint(0, 1)
        if sign == 0:
            est_time -= misest
            if est_time > 0:
                break
        else:
            est_time += misest
            break
    actual_duration = []
    for index in range(num_tasks):
        actual_duration.append(float(row[3+index]))
    
    # Replace the template file with actual values
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
        job_to_scheduler[jobstr] = "kube-scheduler"
    filename = jobstr+".yaml"
    with open(filename, 'w') as file:
      file.write(filedata)
    q = rediswq.RedisWQ(name=jobstr, host=host)
    # Cleanup possible remnants of an older run
    q.delete(jobstr)
    q.rpush(actual_duration)
    q.disconnect()
    jobnames.append(jobstr)
    #print("Setup complete.Took", time() - setup_start_time)
    return filename

t = RepeatTimer(UTIL_LOG_INTERVAL, log_node_util)
def signal_handler(signal, frame):
    post_process()
    sys.exit(0)

def main():
    global max_job_id, start_epoch
    jobid=0
    threads = []

    #signal.signal(signal.SIGINT, signal_handler)
    if len(sys.argv) != 4:
        print("Incorrect number of parameters. Usage: python jobs.py d 10 -e")
        sys.exit(1)

    is_central = sys.argv[1] == 'c'
    # Read in the job template file
    job_file = "job_d.yaml"
    if is_central:
        job_file = "job_c.yaml"
        print("CENTRALIZED SCHEDULER")
    else:
        print("DECENTRALIZED SCHEDULER")

    with open(job_file, 'r') as file :
        job_tmpl = file.read()

    num_sch = int(sys.argv[2])
    #max_job_id = setup(is_central, num_sch, 0)
    # Process workload file
    f = open('temp.tr', 'r')
    arrival_time = 0.0
    startTime = time()
    #Start logging node utilization
    t.start()
    continue_param = None
    last_resource_version = 0
    while True:
        for row in f:
            jobid += 1
            filename = setup_job(row, jobid, is_central, num_sch, job_tmpl)
            if start_epoch == 0.0:
                start_epoch = startTime
            '''
            while True:
                speedup = gauss(SPEEDUP, SPEEDUP/2)
                if speedup > 0:
                    break
            #The median arrival of job in YH is 7.5 seconds.
            arrival_time += 7.5/speedup
            '''
            row = row.split()
            arrival_time = float(row[0]) / float(SPEEDUP)
            jobstr = "job"+str(jobid)
            #Sleep till it is time to start the job.
            endTime = time()
            sleep_time = start_epoch + arrival_time - endTime
            if sleep_time > 0:
                sleep(sleep_time)
            endTime = time()
            job_start_time[jobstr] = endTime
            utils.create_from_yaml(k8s_client, filename)
            print("Starting", jobstr, "at", job_start_time[jobstr] - start_epoch)
            jobs_pending.append(jobstr)
            continue_param, last_resource_version  = process_completed_jobs(20, True, continue_param, last_resource_version)
            if endTime - start_epoch >= RUNTIME:
                f.close()
                break
            max_job_id = jobid
        '''
        try:
            f.seek(0)
            print("------RESTARTING WORKLOAD--------")
        except:
            break
        '''
        break

    print("Started", max_job_id, "jobs")
    #Process scheduler stats. 
    stats(continue_param, last_resource_version)

# Start the worker processes to catch job completion events.
def stats(continue_param, last_resource_version):
    get_job_and_pod_events(20, False, continue_param, last_resource_version)
    post_process()

def get_job_and_pod_events(limit, once, continue_param, last_resource_version):
    # Watch for completed jobs.
    process_completed_jobs(limit, once, continue_param, last_resource_version)

# For running this along with the job creation threads, split creation and watch on
# two different machines.
def process_completed_jobs(limit, once, continue_param, last_resource_version):
    #Run the main job loop with the resource version.
    #Only watch for completed jobs. Caution : This watch runs forever. So, actively break.
    timeout_seconds = 1
    job_events = job_client.list_namespaced_job(namespace='default', limit=limit)
    while True:
        if job_events != None:
            continue_param = job_events.metadata._continue
            last_resource_version = job_events.metadata.resource_version
            #print("Jobs - Got", len(job_events.items),"events at version -",last_resource_version)
            for job_object in job_events.items:
                is_return = process_job_object(job_object, last_resource_version)
                if is_return:
                    return None, 0
            if once:
                return continue_param, last_resource_version
            if time() - start_epoch >= RUNTIME:
                return None, 0
        job_events, e = get_job_events(limit, continue_param, timeout_seconds, last_resource_version)
        if e != None:
            # TODO - What if there are missed events between now and new resource version?
            # Handle by actively querying for them.
            if e.status == 410:
                print("JOB - Caught resource version too old exception.")
                continue_param = None
                last_resource_version = 0
            #else:
            #raise e

def process_job_object(job_object, last_resource_version):
    jobname = job_object.metadata.name
    if jobname not in jobs_pending:
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
    jrt.append(job_completion)
    job_to_jrt[jobname] = job_completion
    print(time() - start_epoch,": Job", jobname, "has JRT", job_completion)
    jobs_pending.remove(jobname)
    job_client.delete_namespaced_job(name=jobname, namespace="default",
        body=client.V1DeleteOptions(
            grace_period_seconds=0,
            propagation_policy='Background'))
    if len(jobs_pending) == 0:
        return True
    return False

#Returns job_events and any exceptions raised
def get_job_events(limit, continue_param, timeout_seconds, last_resource_version):
    try:
        if continue_param != None:
            return job_client.list_namespaced_job(namespace='default', limit=limit, _continue=continue_param), None
        #If resource_version is set then send the events from exact version, else if 0, then send event from any version.
        return job_client.list_namespaced_job(namespace='default', limit=limit, resource_version = last_resource_version, resource_version_match='NotOlderThan'), None
    except ApiException as e:
        print("Exception", e)
        return None, e


def post_process():
    t.cancel()
    print("Total number of jobs completed is", len(jrt))
    if len(jrt) > 0:
        print("Stats for JRT -"",",percentile(jrt, 50), percentile(jrt, 90), percentile(jrt, 99))
    for jobname in jobnames:
        q = rediswq.RedisWQ(name=jobname, host=host)
        # Cleanup remnants of the run
        q.delete(jobname)
        q.disconnect()
   
    if len(jobs_pending) > 0:
        for jobname in jobs_pending:
            #print("Deleting", jobname)
            try:
                job_client.delete_namespaced_job(name=jobname, namespace="default",
                    body=client.V1DeleteOptions(
                    grace_period_seconds=0,
                    propagation_policy='Background'))
            except:
                continue
    print("Script took a total of", time() - start_epoch,"s")


if __name__ == '__main__':
    main()
