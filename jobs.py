#!/usr/bin/env python
import rediswq
import os
import re
import subprocess
import sys
import subprocess
import operator
import json
from threading import Thread
from datetime import timedelta, datetime
from time import sleep, time, mktime
from collections import defaultdict
from kubernetes import client, config, watch

#Maintains job to pod list mapping for completed jobs.
job_to_podlist = defaultdict(list)
all_jobs = set()
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

# Returns difference in milliseconds
def timeDiffMilliseconds(e1, s1):
    #e1 = extractDateTime(end)
    #s1 = extractDateTime(start)
    ms_diff = (mktime(e1.utctimetuple()) - mktime(s1.utctimetuple())) * 1000000 + e1.microsecond - s1.microsecond
    return ms_diff * 1.0 / 1000

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
        if start_epoch == 0.0:
            start_epoch = time()
        arrival_time = float(row[0])/float(SPEEDUP)
        jobid += 1
        jobstr = "".join(["job",str(jobid)])
        all_jobs.add(jobstr)
        # Pick the correct job file.
        filename = jobstr+".yaml"
        #Sleep till it is time to start the job.
        endTime = time()
        sleep_time = start_epoch + arrival_time - endTime
        if sleep_time < 0:
            #print "Script loop started at", startTime,"and ran for", endTime - startTime,"sec but sleep is -ve at", sleep_time
            #print "Next job due at", start_epoch + arrival_time, "but time now is", endTime
            raise AssertionError('script overran job interval!')
        sleep(sleep_time)
        #"kubectl apply" is an expensive operation.
        apply_job(filename, jobstr, start_epoch)
        #Spawn a background thread that will actually start the job.
        #thr = Thread(target=apply_job, args=(filename, jobstr, start_epoch), kwargs={})
        #thr.start()
        #threads.append(thr)

    f.close()

    #Wait for all threads to start their respective jobs.
    #for thr in threads:
    #    thr.join()

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
    #Look for 12:14:58.422793 pattern in logs
    os.chdir("/local/scratch/")
    pattern = '\d{2}:\d{2}:\d{2}\.\d{6}'
    compiled = re.compile(pattern)
    log_file_name = '_'.join(["logs", "X"+str(SPEEDUP), str(num_jobs)]) 
    #Configue the Kubernetes client for watching jobs.
    config.load_kube_config()
    job_client = client.BatchV1Api()
    pod_client = client.CoreV1Api()
    metrics_client = client.CustomObjectsApi()
    w = watch.Watch()
    #Only watch for completed jobs.
    for job_event in w.stream(func=job_client.list_namespaced_job, namespace='default'):
        job_object = job_event['object']
        jobname = job_object.metadata.name
        if jobname not in all_jobs:
            #This job has finished processing.
            continue 
        status = job_object.status
        if status.completion_time != None:
            #Completion Time can be not None when Complete or Failed.
            if status.conditions[0].type != "Complete":
                #Job might have failed.
                raise AssertionError("Job" + jobname + "has failed!")
            print jobname,"has completed at time", status.completion_time
            pods = pod_client.list_namespaced_pod(namespace='default', label_selector='job-name={}'.format(jobname))
            for pod in pods.items:
                pod_status =  pod.status.phase
                if pod_status != "Succeeded":
                    #We are not interested in a pod that Failed.
                    #There are definitely others since the job has completed.
                    continue
                job_to_podlist[jobname].append(pod.metadata.name)
            all_jobs.remove(jobname)
            if len(all_jobs) == 0:
                w.stop()
                with open('dict.pkl', 'wb') as f:
                        pickle.dump(job_to_podlist, f)
                print "Wrote everything to file", job_to_podlist
                break

if __name__ == '__main__':
    main()
