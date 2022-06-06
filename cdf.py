import csv
import numpy as np
from matplotlib import pyplot as plt

#matplotlib.use("GTK3Agg")

c=[]
d=[]
jobids=[]
jobid = 0
with open("c.default", 'r') as f:
    rows = csv.reader(f)
    for r in rows:
        c.append(float(r[0]))
        jobid += 1
        jobids.append(jobid)
with open("d", 'r') as f:
    rows = csv.reader(f)
    for r in rows:
        d.append(float(r[0]))
np.sort(c)
np.sort(d)

assert(len(c) == len(d))

cp = 1. * np.arange(len(c)) / (len(c) - 1)
dp = 1. * np.arange(len(d)) / (len(d) - 1)

'''
plt.plot(jobids, c, 'b', label="Centralized")
plt.plot(jobids, d, 'r--', label="Decentralized")
plt.xlabel('Job Ids')
plt.ylabel('Job Response Times')
plt.legend()
plt.show()
'''

#Show CDF
plt.plot(c, cp, 'b', label="Centralized")
plt.plot(d, dp, 'r--', label="Decentralized")
plt.xlabel('Job Response Times')
plt.ylabel('CDF')
plt.legend()
plt.show()

#Show Histogram
q25, q75 = np.percentile(d, [25,75])
width = 2 * (q75 - q25) * len(d) ** (-1/3)
bins = round( (max(d) - min(d)) / width)
print(bins)
plt.hist(c, density=True, bins=bins, label="Centralized")
plt.hist(d, density=True, bins=bins, label="Decentralized")
plt.ylabel('Probability')
plt.xlabel('Job Response Time')
plt.legend()
plt.show()

#Show percentiles as bar
percentiles=['25','50','75','100']
plt.bar(percentiles, [np.percentile(c, 25), np.percentile(c, 50), np.percentile(c, 75), np.percentile(c, 100)], label="Centralized")
plt.bar(percentiles, [np.percentile(d, 25), np.percentile(d, 50), np.percentile(d, 75), np.percentile(d, 100)], label="Decentralized")
plt.ylabel("Percentile Job Response Times")
plt.legend()
plt.show()
