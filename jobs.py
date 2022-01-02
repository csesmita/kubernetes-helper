#!/usr/bin/env python
import rediswq
import os
import subprocess
from threading import Thread
from datetime import timedelta, datetime
from time import sleep, time, mktime
from collections import defaultdict
from numpy import percentile

job_to_podlist = defaultdict(list)
SPEEDUP = 1
sch_queue_add = "Add event for unscheduled pod"
sch_queue_eject = "About to try and schedule pod"
sch_attempt_schedule = "Attempting to schedule pod"
sch_attempt_bind = "Attempting to bind pod to node"

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
        # Replace the template file with actual values
        jobid += 1
        jobstr = "job"+str(jobid)
        filename = jobstr+".yaml"
        #Cleanup all jobs that have completed till now.
        #Needn't be the most aged job. Any orderinng is fine.
        #Start the job
        endTime = time()
        sleep_time = start_epoch + arrival_time - endTime
        if sleep_time < 0:
            print "Script loop started at", startTime,"and ran for", endTime - startTime,"sec but sleep is -ve at", sleep_time
            print "Next job due at", start_epoch + arrival_time, "but time now is", endTime
            raise AssertionError('script overran job interval!')
        sleep(sleep_time)
        apply_job(filename, jobstr, start_epoch)
        #thr = Thread(target=apply_job, args=(filename, jobstr, start_epoch), kwargs={})
        #thr.start()
        #threads.append(thr)
        #thr.join()

    f.close()

    #Wait for all threads to start their respective jobs.
    #for thr in threads:
    #    thr.join()

    #Process scheduler stats.    
    stats()

def apply_job(filename, jobstr, start_epoch):
        #This command takes about 0.25s. So jobs can't arrive faster than this.
        subprocess.check_output(["kubectl","apply", "-f", filename])
        #subprocess.check_output(["rm", "-rf", filename])
        print "Starting", jobstr, "at", time() - start_epoch

def stats():
    pending_jobs = True
    #Change directory to scheduler logs
    os.chdir("/var/lib/docker/containers/75a6972b0af20eefd1e68ac2735bcfcc579982570682a267e648be6f5e9e9eda")
    while pending_jobs:
        pending_jobs = add_pod_info()
        print "Pending jobs?", pending_jobs
        process()
        sleep(2)
    print "Finished processing all jobs"


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
    return True

#TODO - Docker should give read access to all users. For now, run sudo chmod 755 on /var/lib/docker.
#TODO - Automate to pick up sym link from /var/log/pods/kube-system_kube-scheduler*/*/ directory. For now, hard code dir name.
#TODO - Configue logrotate from docker instead of kubernetes. https://www.reddit.com/r/kubernetes/comments/bcoiwr/clearing_logs_log_rotation/. For now, it runs every 15 mmins.
def process():
    for jobname,pods in job_to_podlist.items():
        # Fetch all pod related stats for each pod.
        for podname in pods:
            queue_time =  0.0
            scheduling_algorithm_time = timedelta(microseconds=0)
            queue_add_time = timedelta(microseconds=0)
            queue_eject_time = 0.0
            attempt_schedule_time = 0.0
            attempt_bind_time = 0.0
            logs =  subprocess.check_output(['grep','-ri',podname]).split('\n')
            #Grep'ed logs can be out of order in time.
            for log in logs:
                if sch_queue_add in log:
                    queue_add_time = log.split(' ')[1]
                    continue
                if sch_queue_eject in log:
                    #if queue_add_time == 0.0:
                    #    raise AssertionError('Got a queue eject time, but not a queue add time for pod ' + podname)
                    queue_eject_time = log.split(' ')[1]
                    queue_time = timeDiff(queue_eject_time, queue_add_time)
                    continue
                if sch_attempt_schedule in log:
                    #if queue_time == 0.0:
                    #    raise AssertionError('Got a attempt schedule time, but queue time has not yet been calculated for pod ' + podname)
                    attempt_schedule_time = log.split(' ')[1]
                    continue
                if sch_attempt_bind in log:
                    #if attempt_schedule_time == 0.0:
                    #    raise AssertionError('Got a attempt bind time, but not a attempt schedule time for pod ' + podname)
                    attempt_bind_time = log.split(' ')[1]
                    scheduling_algorithm_time = timeDiff(attempt_bind_time, attempt_schedule_time)
                    continue
                if scheduling_algorithm_time.total_seconds() > 0.0 and queue_time.total_seconds() > 0.0:
                    break
            if scheduling_algorithm_time.total_seconds() == 0.0 or queue_time.total_seconds() == 0.0:
                raise AssertionError('Scheduling algorithm time or queue time not calculated for pod ' + podname)
            print "Job", jobname,"Pod", podname,"Scheduler Queue Time", queue_time,"Scheduling Algorithm Time", scheduling_algorithm_time
        subprocess.check_output(["kubectl", "delete", "jobs",jobname])
    job_to_podlist.clear()

if __name__ == '__main__':
    main()
