#!/usr/bin/env python

import time
import rediswq
import os
import sys

host = os.getenv("REDIS_SERVICE_HOST")
jobid = os.getenv("JOBID")

q = rediswq.RedisWQ(name=jobid, host=host)
print("Worker with sessionID: " +  q.sessionID())
print("Initial queue state: empty=" + str(q.empty()))
done=False
while not q.empty():
  #Lease this item till the value indicated on the item.
  item = q.lease()
  if item is not None:
    itemstr = item.decode("utf-8")
    print("Working on " + itemstr)
    time.sleep(float(itemstr))
    count = q.complete(item)
    if count == 0:
      print("Work finished by some other pod!")
      sys.exit("Work finished by some other pod!")
    done=True
    break
  else:
    #See if any of the leases have expired, so they can be processed next.
    has_expired = q.get_expired()
    if has_expired == False:
      print("Nothing to work on, and no expired leases!")
      sys.exit("Nothing to work on, and no expired leases!")
if done:
    print("Work completed by this task")
else:
    print("Queue empty, so no work done by this task.")
    sys.exit("Queue empty, so no work done by this task.")
