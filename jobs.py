#!/usr/bin/env python
import rediswq
import os
import subprocess
from time import sleep
from time import time

# Read in the job template file
with open('job.yaml', 'r') as file :
    job_tmpl = file.read()
host = "10.104.1.86"
jobid = 0
start_epoch = 0.0

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
    jobs = subprocess.check_output(["kubectl", "get", "job", "--server-print=false"])
    for job in jobs.split('\n'):
        #Skip the header
        if "NAME" in job and "AGE" in job:
            continue
        job = job.split()
        if job == []:
            break
        jobname = job[0]
        #Check if the job has completed
        has_completed = subprocess.check_output(["kubectl", "get", "jobs", jobname, "-o","jsonpath='{.status.completionTime}'"])
        if has_completed != '':
            is_deleted = subprocess.check_output(["kubectl", "delete", "jobs",jobname])
    #Start the job
    endTime = time()
    sleep_time = start_epoch + arrival_time - endTime
    sleep(sleep_time)
    print "Starting job at", time() - start_epoch
    subprocess.check_output(["kubectl","apply", "-f", filename])
    subprocess.check_output(["rm", "-rf", filename])
