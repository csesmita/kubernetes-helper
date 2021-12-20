#!/usr/bin/env python
import rediswq
import os
import subprocess
from datetime import datetime
from time import sleep
from time import time

#end and start are of the form HH:MM:SS.SSSSSS
def timeDiff(end, start):
    end_time = datetime.strptime(end, '%H:%M:%S.%f')
    start_time = datetime.strptime(start, '%H:%M:%S.%f')
    return end_time - start_time

def main():
    # Read in the job template file
    with open('job.yaml', 'r') as file :
        job_tmpl = file.read()
    host = "10.106.246.16"
    jobid = 0
    start_epoch = 0.0

    #Get the name of the scheduler.
    scheduler_details = subprocess.check_output(["kubectl", "get", "pods", "-n", "kube-system", "-l", "component=kube-scheduler", "--no-headers"])
    scheduler_name = scheduler_details.split()[0]

    sch_queue_add = "Add event for unscheduled pod"
    sch_queue_eject = "About to try and schedule pod"
    sch_attempt_schedule = "Attempting to schedule pod"
    sch_attempt_bind = "Attempting to bind pod to node"

    # Process workload file
    f = open('temp.tr', 'r')
    for row in f:
        row = row.split()
        startTime = time()
        if start_epoch == 0.0:
            start_epoch = startTime
        arrival_time = float(row[0])
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
        #Cleanup all jobs that have completed till now.
        #Needn't be the most aged job. Any orderinng is fine.
        jobs = subprocess.check_output(["kubectl", "get", "job", "--server-print=false", "--no-headers"])
        for job in jobs.split('\n'):
            job = job.split()
            if job == []:
                break
            jobname = job[0]
            #Check if the job has completed
            has_completed = subprocess.check_output(["kubectl", "get", "jobs", jobname, "-o","jsonpath='{.status.completionTime}'"])
            if has_completed != '':
                # This job has completed.
                # Fetch all pod related stats for each pod.
                pods_list = subprocess.check_output(['kubectl','get', 'pods', '--selector=job-name='+jobname, '--server-print=false', '--no-headers'])
                logs =  subprocess.check_output(['kubectl','logs', '-n', 'kube-system', scheduler_name]).split('\n')
                for pod in pods_list.splitlines():
                    podname = pod.split()[0]
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
                        raise AssertionError('Scheduling algorithm time or queue time not calculated.')
                    print "Scheduler Queue Time", queue_time
                    print "Scheduling Algorithm Time", scheduling_algorithm_time
                is_deleted = subprocess.check_output(["kubectl", "delete", "jobs",jobname])
        #Start the job
        endTime = time()
        sleep_time = start_epoch + arrival_time - endTime
        print sleep_time
        if sleep_time > 0:
            sleep(sleep_time)
        print "Starting job at", time() - start_epoch
        subprocess.check_output(["kubectl","apply", "-f", filename])
        subprocess.check_output(["rm", "-rf", filename])

if __name__ == '__main__':
    main()
