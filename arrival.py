import matplotlib.pyplot as plt
import sys
from math import ceil
import numpy as np

arrival = []
f = open(sys.argv[1], 'r')
start_time = 0
for row in f:
    row = row.split(' ')
    next_time = float(row[0])
    arrival.append(next_time - start_time)
    start_time = next_time
arrival.sort()
print("50th percentile: ",  np.percentile(arrival, 50))
print("90th percentile: ",  np.percentile(arrival, 90))
print("99th percentile: ",  np.percentile(arrival, 99))
