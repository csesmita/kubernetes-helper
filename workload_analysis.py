import matplotlib.pyplot as plt
import numpy as np
from palettable.colorbrewer.qualitative import Set2_7

colors = Set2_7.mpl_colors

num_tasks_yh = []
f = open('YH.tr', 'r')
for row in f:
    row = row.split(' ')
    num_tasks_yh.append(int(row[1]))
f.close()

num_tasks_google = []
f = open('goog.tr', 'r')
for row in f:
    row = row.split(' ')
    num_tasks_google.append(int(row[1]))
f.close()

num_tasks_yh = np.sort(num_tasks_yh)
num_tasks_google = np.sort(num_tasks_google)
num_tasks_yh = 1. * np.arange(len(num_tasks_yh)) / (len(num_tasks_yh) - 1)
num_tasks_google = 1. * np.arange(len(num_tasks_google)) / (len(num_tasks_google) - 1)
plt.plot(num_tasks_yh, 'b', label="Yahoo")
plt.plot(num_tasks_google, 'r--', label="Google")
plt.xlabel('Num Tasks')
plt.title('CDF')
plt.ylabel('CDF')
plt.legend()
plt.savefig('cdf_numtasks.pdf')
