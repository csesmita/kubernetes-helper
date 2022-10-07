from matplotlib import pyplot as plt
import numpy as np

# function to add value labels
def addlabels(y, pos):
    for i in range(len(y)):
        plt.text(i + pos,y[i], y[i], ha = 'center', bbox = dict(facecolor = 'red', alpha =.8))

#From results/jrt/d.10000J.1000X.50N.10S.YH
original_jrt = [26544.585094809532,34522.52695565224,37118.944876954556]
#25% jobs have 25 positive misestimation - results/jrt/d.10000J.1000X.50N.10S.YH.0.25+MISEST
positive_25p = [26550.986672639847,34521.37364616394,37137.39110995293]
#25% jobs have 25 negative misestimation - results/jrt/d.10000J.1000X.50N.10S.YH.0.25-MISEST
negative_25p = [26548.931873083115,34520.29573545456,37142.22423663855]
#All jobs have 50% randomly distributed misestimate around the given value - results/jrt/d.10000J.1000X.50N.10S.YH.0.5MISEST
gauss_50p = [26544.23251056671,34515.50167002678,37129.57029220581]
#All jobs have 100% randomly distributed misestimate around the given value - results/jrt/d.10000J.1000X.50N.10S.YH.1.0MISEST
gauss_100p = [26549.894215464592,34521.4772247076,37135.684959728715]

#Show Percentiles
percentiles=['50', '90', '99']
#x=np.arange(len(percentiles))
x=[0.5, 1.0, 1.5]
width = 0.5
#width=0.5
fig, ax = plt.subplots()

positive_25p[:] = [(x - y)/y * 100 for x,y in zip(positive_25p, original_jrt)]
ax.bar(x, positive_25p, width, label="Positive 25%",)
#addlabels(positive_25p, 0)

negative_25p[:] = [(x - y)/y * 100 for x,y in zip(negative_25p, original_jrt)]
x[:] = [a + 2 for a in x]
ax.bar(x, negative_25p,  width, label="Negative 25%")
#addlabels(negative_25p, 0)

gauss_50p[:] = [(x - y)/y * 100 for x,y in zip(gauss_50p, original_jrt)]
x[:] = [a + 2 for a in x]
rects1= ax.bar(x, gauss_50p, width, label="Gaussian 50%",)
#addlabels(gauss_50p,4)

gauss_100p[:] = [(x - y)/y * 100 for x,y in zip(gauss_100p, original_jrt)]
x[:] = [a + 2 for a in x]
rects1= ax.bar(x, gauss_100p, width, label="Gaussian 100%",)
#addlabels(gauss_100p,4)

ax.set_ylabel("Percentage Deviation in JCT")
ax.set_xticks([1,3,5,7])
ax.set_xticklabels(['Positive 25p', 'Negative 25p', 'Gaussian 50%', 'Gaussian 100%'])
#ax.set_ylim([25000, 45000])
ax.legend()
fig.tight_layout()
#plt.show()
fig.savefig('misestimation.pdf')
