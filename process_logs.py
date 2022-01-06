#!/usr/bin/env python
from datetime import datetime
from time import mktime
from numpy import percentile
import sys

# Returns differennce in microseconds
def timeDiff(end, start):
    try:
        e1 = datetime.strptime(end, '%H:%M:%S.%f')
    except Error as e:
        print end
    s1 = datetime.strptime(start, '%H:%M:%S.%f')
    ms_diff = (mktime(e1.utctimetuple()) - mktime(s1.utctimetuple())) * 1000000 + e1.microsecond - s1.microsecond
    return int(ms_diff)

default_time = "00:00:00.000000"
qtimes = []
algotimes = []
logname = sys.argv[1]
f = open(logname, 'r')
for line in f:
    if "Scheduler Queue Time" not in line:
        continue
    data = line.split('Scheduler Queue Time')[1]
    qdiff = timeDiff(data.split()[0], default_time)
    qtimes.append(qdiff)
    algotime_str = data.split('Scheduling Algorithm Time')[1]
    algodiff = timeDiff(algotime_str.split()[0], default_time)
    algotimes.append(algodiff)
qtimes.sort()
algotimes.sort()
print logname,": Total number of pods evaluated", len(qtimes)
print "Stats for Scheduler Queue Times -",percentile(qtimes, 50), percentile(qtimes, 90), percentile(qtimes, 99)
print "Stats for Scheduler Algorithm Times -"",",percentile(algotimes, 50), percentile(algotimes, 90), percentile(algotimes, 99)
