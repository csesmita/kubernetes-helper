from matplotlib import pyplot as plt
import numpy as np

x=[10, 15, 20, 25, 30, 40, 50, 75, 100, 150]
xl=['10S', '15S', '20S', '25S', '30S', '40S', '50S', '75S', '100S', '150S']
y=[3986, 5591, 7857, 8162, 9602, 10126, 9379, 10207, 8509, 7377]

fig = plt.figure()
plt.plot(x,y)
plt.xticks(x, xl)
for xz,yz in zip(x,y):
    label = "{:d}".format(yz)
    plt.annotate(label, (xz,yz), textcoords="offset points", xytext=(0,10), ha='center')
plt.xlabel("Number of Schedulers")
plt.ylabel("Total Number of Pods Scheduled Per Second")
plt.ylim(0,12000)
#fig.tight_layout()
#fig.savefig('scalability.pdf', dpi=fig.dpi, bbox_inches='tight')
plt.show()
