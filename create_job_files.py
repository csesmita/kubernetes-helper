#!/usr/bin/env python
import rediswq

def main():
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

if __name__ == '__main__':
    main()
