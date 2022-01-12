#!/usr/bin/env python

import time
import rediswq
import os

host = os.getenv("REDIS_SERVICE_HOST")
jobid = os.getenv("JOBID")

q = rediswq.RedisWQ(name=jobid, host=host)
print("Worker with sessionID: " +  q.sessionID())
print("Initial queue state: empty=" + str(q.empty()))
done=False
while not q.empty():
  item = q.lease(lease_secs=10, block=True, timeout=2) 
  if item is not None:
    itemstr = item.decode("utf-8")
    print("Working on " + itemstr)
    time.sleep(float(itemstr))
    q.complete(item)
    done=True
    break
if done:
    print("Work completed by this task")
else:
    print("Queue empty, so no work done by this task.")
