#!/usr/bin/env python

import subprocess
import rediswq
import os

host = os.getenv("REDIS_SERVICE_HOST")
jobid = os.getenv("JOBID")
podname = os.getenv("PODNAME")

q = rediswq.RedisWQ(name=jobid, host=host)
print(podname + ": Worker with sessionID: " +  q.sessionID())
print(podname + ": Initial queue state: empty=" + str(q.empty()))
done=False
while not q.empty():
  #Lease this item till the value indicated on the item.
  item = q.lease()
  if item is not None:
    itemstr = item.decode("utf-8")
    print(podname + ": Working on " + itemstr)
    subprocess.run(["timeout", itemstr, "sha1sum", "/dev/zero"])
    print(podname + ": Finished sleeping for " + itemstr)
    count = q.complete(item)
    if count == 0:
      print(podname + ": Work finished by some other pod!")
      #sys.exit(podname + ": Work finished by some other pod!")
    else:
      done=True
    break
  else:
    print(podname + ": Inside else. Queue state: empty=" + str(q.empty()))
    #See if any of the leases have expired, so they can be processed next.
    has_expired = q.get_expired()
    if has_expired == False:
      print(podname + ": Nothing to work on, and no expired leases!")
      #sys.exit("Nothing to work on, and no expired leases!")
      break
if done:
    print(podname + ": Work completed by this task")
else:
    print(podname + ": Queue empty, so no work done by this task.")
    #sys.exit(podname + ": Queue empty, so no work done by this task.")
