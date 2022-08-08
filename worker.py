#!/usr/bin/env python

#import time
import subprocess
import rediswq
import os

host = os.getenv("REDIS_SERVICE_HOST")
jobid = os.getenv("JOBID")
podname = os.getenv("PODNAME")
index = int(os.getenv("JOB_COMPLETION_INDEX"))

q = rediswq.RedisWQ(name=jobid, host=host)
print(podname + ": Worker with sessionID: " +  q.sessionID())
print(podname + ": Initial queue state: empty=" + str(q.empty()))
item = q.get(index)
itemstr = item.decode("utf-8")
print(podname + ": Working on " + itemstr)
#time.sleep(float(itemstr))
subprocess.run(["timeout", itemstr, "sha1sum", "/dev/zero"])
print(podname + ": Finished sleeping for " + itemstr)
print(podname + ": Work completed by this task")
