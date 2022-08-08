#!/usr/bin/env python

# Based on https://kubernetes.io/examples/application/job/redis/rediswq.py
# Adapted for storing actual running times of tasks from workload files.
# Allows multiple pods to be working on the same task. Leaves the management
# of such pods to the job controller.
# This code assumes distinct values in queue.
 
import redis
import uuid
import hashlib

class RedisWQ(object):
    """Simple Finite Work Queue with Redis Backend

    This work queue is finite: as long as no more work is added
    after workers start, the workers can detect when the queue
    is completely empty.

    The items in the work queue are assumed to have unique values.

    This object is not intended to be used by multiple threads
    concurrently.
    """
    def __init__(self, name, **redis_kwargs):
       """The default connection parameters are: host='localhost', port=6379, db=0

       The work queue is identified by "name".  The library may create other
       keys with "name" as a prefix. 
       """
       self._db = redis.StrictRedis(**redis_kwargs)
       # The session ID will uniquely identify this "worker".
       self._session = str(uuid.uuid4())
       # Work queue is implemented as two queues: main, and processing.
       # Work is initially in main, and moved to processing when a client picks it up.
       self._main_q_key = name
       self._processing_q_key = name + ":processing"
       self._lease_key_prefix = name + ":leased_by_session:"

    def sessionID(self):
        """Return the ID for this session."""
        return self._session

    def _main_qsize(self):
        """Return the size of the main queue."""
        return self._db.llen(self._main_q_key)

    def _processing_qsize(self):
        """Return the size of the processing queue."""
        return self._db.llen(self._processing_q_key)

    def empty(self):
        """Return True if the queue is empty, including work being done, False otherwise.

        False does not necessarily mean that there is work available to work on right now,
        """
        return self._main_qsize() == 0 and self._processing_qsize() == 0

# check_expired_leases(self):
#        """Return to the work queueReturn True if the queue is empty, False otherwise."""
# This function is not required since this is just a store to ensure all tasks are completed
# atleast once (not exaqctly once). The earliest finishing pod amongst these will be completed
# while the rest will fail with an os.EX_NOTFOUND. That should fail the container (and hence
# the pod).
    def _itemkey(self, item):
        """Returns a string that uniquely identifies an item (bytes)."""
        return hashlib.sha224(item).hexdigest()

    def _lease_exists(self, item):
        """True if a lease on 'item' exists."""
        return self._db.exists(self._lease_key_prefix + self._itemkey(item))

    def lease(self):
        """Begin working on an item the work queue. 

        Lease the item for the value specified in the item (if one is found).
        After that time, other workers may consider this client to have crashed or stalled
        and pick up the item instead. Read comment for check_expired_lease().
        """
        item = self._db.rpoplpush(self._main_q_key, self._processing_q_key)
        if item:
            # Record that we (this session id) are working on a key.  Expire that
            # note after the lease timeout.
            # Note: if we crash at this line of the program, then GC will see no lease
            # for this item a later return it to the main queue.
            itemkey = self._itemkey(item)
            itemstr = item.decode("utf-8")
            lease_secs = int(float(itemstr)) + 1
            self._db.setex(self._lease_key_prefix + itemkey, lease_secs, self._session)
        return item

    def get_expired(self):
        """Move one item with expired lease from processing to main queue."""
        for item in self._db.lrange(self._processing_q_key, 0, -1):
          if not self._lease_exists(item):
            # Not safe for distributed execution.
            # So, ensure the first of the pods completes execution
            # even if that means a second starts a redundant run.
            self._db.rpush(self._main_q_key, item)
            self._db.lrem(self._processing_q_key, 1, item)
            return True
        return False

    def complete(self, value):
        """Complete working on the item with 'value'.

        If the lease expired, the item may not have completed, and some
        other worker may have picked it up.  There is no indication
        of what happened.
        """
        count = self._db.lrem(self._processing_q_key, 1, value)
        # If we crash here, then the GC code will try to move the value, but it will
        # not be here, which is fine.  So this does not need to be a transaction.
        itemkey = self._itemkey(value)
        self._db.delete(self._lease_key_prefix + itemkey)
        return count

    def rpush(self, value):
        self._db.rpush(self._main_q_key, *value)

    # Clear the key if it exists
    def delete(self, name):
        self._db.delete(name)

    # Get value of element at index
    def get(self, index):
        value = self._db.lindex(self._main_q_key, index)
        return value

# TODO: add functions to clean up all keys associated with "name" when
# processing is complete.

# TODO: add a function to add an item to the queue.  Atomically
# check if the queue is empty and if so fail to add the item
# since other workers might think work is done and be in the process
# of exiting.

# TODO(etune): move to my own github for hosting, e.g. github.com/erictune/rediswq-py and
# make it so it can be pip installed by anyone (see
# http://stackoverflow.com/questions/8247605/configuring-so-that-pip-install-can-work-from-github)

# TODO(etune): finish code to GC expired leases, and call periodically
#  e.g. each time lease times out.

