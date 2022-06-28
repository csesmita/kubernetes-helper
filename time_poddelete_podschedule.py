#!/usr/bin/env python
import os
import re
from datetime import timedelta, datetime
from concurrent import futures
from numpy import percentile

all_intervals=[]
def extractDateTime(timestr):
    return datetime.strptime(timestr,'%m%d %H:%M:%S.%f')

# Returns difference in two timedeltas in seconds
def timeDiff(e1, s1):
    return (e1 - s1).total_seconds()

pattern = '\d{2}\d{2} \d{2}:\d{2}:\d{2}\.\d{6}'
compiled = re.compile(pattern)

def process(filepath):
    partial_intervals = []
    with open(filepath, 'r') as f:
        start = datetime.min
        for log in f:
            if "Attempting to bind pod to node" in log:
                start = extractDateTime(compiled.search(log).group(0))
                continue
            if "Delete event for scheduled pod" in log:
                if start == datetime.min:
                    continue
                partial_intervals.append(extractDateTime(compiled.search(log).group(0)) - start)
                start = datetime.min
                continue
    return partial_intervals


subprocess.check_output(['bash', 'time_poddelete_podschedule.sh'])
filepaths = []
for filename in os.listdir('/local/scratch/tempdir'):
    filepaths.append(os.path.join('/local/scratch/tempdir', filename))

count = 0
with futures.ProcessPoolExecutor() as pool:
    for partial_intervals in pool.map(process, filepaths):
        all_intervals += partial_intervals
        count += 1
        print("Finished processing", count,"files")

print("Number of pods evaluated", len(all_intervals))
print("Stats for Interval Times between pod being deleted and node being scheduled -",percentile(all_intervals, 50), percentile(all_intervals, 90), percentile(all_intervals, 99))
