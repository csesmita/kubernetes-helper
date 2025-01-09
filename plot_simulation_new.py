from matplotlib import pyplot as plt, rcParams
import numpy as np
from palettable.colorbrewer.qualitative import Set2_7

colors = Set2_7.mpl_colors
params = {
   'axes.labelsize': 14,
   'font.size': 14,
   'legend.fontsize': 14,
   'xtick.labelsize': 14,
   'ytick.labelsize': 14,
   'text.usetex': False,
   #'figure.figsize': [4,2.0]
}
rcParams.update(params)

jct_m_8=[]
jct_m_10=[]
jct_m_12=[]
jct_m_14=[]
jct_m_16=[]
with open("/home/sv440/Android/eagle/simulation/results_new/jct/murmuration/YH/m.8000M",'r') as f:
    for line in f:
        if "total_job_running_time" not in line:
            continue
        jct_m_8.append(float((line.split("total_job_running_time:")[1]).split()[0]))
with open("/home/sv440/Android/eagle/simulation/results_new/jct/murmuration/YH/m.10000M",'r') as f:
    for line in f:
        if "total_job_running_time" not in line:
            continue
        jct_m_10.append(float((line.split("total_job_running_time:")[1]).split()[0]))
with open("/home/sv440/Android/eagle/simulation/results_new/jct/murmuration/YH/m.12000M",'r') as f:
    for line in f:
        if "total_job_running_time" not in line:
            continue
        jct_m_12.append(float((line.split("total_job_running_time:")[1]).split()[0]))
with open("/home/sv440/Android/eagle/simulation/results_new/jct/murmuration/YH/m.14000M",'r') as f:
    for line in f:
        if "total_job_running_time" not in line:
            continue
        jct_m_14.append(float((line.split("total_job_running_time:")[1]).split()[0]))
with open("/home/sv440/Android/eagle/simulation/results_new/jct/murmuration/YH/m.16000M",'r') as f:
    for line in f:
        if "total_job_running_time" not in line:
            continue
        jct_m_16.append(float((line.split("total_job_running_time:")[1]).split()[0]))

jct_s_8=[]
jct_s_10=[]
jct_s_12=[]
jct_s_14=[]
jct_s_16=[]
with open("/home/sv440/Android/eagle/simulation/results_new/jct/sparrow/YH/s.8000M",'r') as f:
    for line in f:
        if "total_job_running_time" not in line:
            continue
        jct_s_8.append(float((line.split("total_job_running_time:")[1]).split()[0]))
with open("/home/sv440/Android/eagle/simulation/results_new/jct/sparrow/YH/s.10000M",'r') as f:
    for line in f:
        if "total_job_running_time" not in line:
            continue
        jct_s_10.append(float((line.split("total_job_running_time:")[1]).split()[0]))
with open("/home/sv440/Android/eagle/simulation/results_new/jct/sparrow/YH/s.12000M",'r') as f:
    for line in f:
        if "total_job_running_time" not in line:
            continue
        jct_s_12.append(float((line.split("total_job_running_time:")[1]).split()[0]))
with open("/home/sv440/Android/eagle/simulation/results_new/jct/sparrow/YH/s.14000M",'r') as f:
    for line in f:
        if "total_job_running_time" not in line:
            continue
        jct_s_14.append(float((line.split("total_job_running_time:")[1]).split()[0]))
with open("/home/sv440/Android/eagle/simulation/results_new/jct/sparrow/YH/s.16000M",'r') as f:
    for line in f:
        if "total_job_running_time" not in line:
            continue
        jct_s_16.append(float((line.split("total_job_running_time:")[1]).split()[0]))

jct_yaqc_8=[]
jct_yaqc_10=[]
jct_yaqc_12=[]
jct_yaqc_14=[]
jct_yaqc_16=[]
with open("/home/sv440/Android/eagle/simulation/results_new/jct/yaqc/YH/yaqc.8000M",'r') as f:
    for line in f:
        if "total_job_running_time" not in line:
            continue
        jct_yaqc_8.append(float((line.split("total_job_running_time:")[1]).split()[0]))
with open("/home/sv440/Android/eagle/simulation/results_new/jct/yaqc/YH/yaqc.10000M",'r') as f:
    for line in f:
        if "total_job_running_time" not in line:
            continue
        jct_yaqc_10.append(float((line.split("total_job_running_time:")[1]).split()[0]))
with open("/home/sv440/Android/eagle/simulation/results_new/jct/yaqc/YH/yaqc.12000M",'r') as f:
    for line in f:
        if "total_job_running_time" not in line:
            continue
        jct_yaqc_12.append(float((line.split("total_job_running_time:")[1]).split()[0]))
with open("/home/sv440/Android/eagle/simulation/results_new/jct/yaqc/YH/yaqc.14000M",'r') as f:
    for line in f:
        if "total_job_running_time" not in line:
            continue
        jct_yaqc_14.append(float((line.split("total_job_running_time:")[1]).split()[0]))
with open("/home/sv440/Android/eagle/simulation/results_new/jct/yaqc/YH/yaqc.16000M",'r') as f:
    for line in f:
        if "total_job_running_time" not in line:
            continue
        jct_yaqc_16.append(float((line.split("total_job_running_time:")[1]).split()[0]))

jct_yaqd_8=[]
jct_yaqd_10=[]
jct_yaqd_12=[]
jct_yaqd_14=[]
jct_yaqd_16=[]
with open("/home/sv440/Android/eagle/simulation/results_new/jct/yaqd/YH/yaqd.8000M",'r') as f:
    for line in f:
        if "total_job_running_time" not in line:
            continue
        jct_yaqd_8.append(float((line.split("total_job_running_time:")[1]).split()[0]))
with open("/home/sv440/Android/eagle/simulation/results_new/jct/yaqd/YH/yaqd.10000M",'r') as f:
    for line in f:
        if "total_job_running_time" not in line:
            continue
        jct_yaqd_10.append(float((line.split("total_job_running_time:")[1]).split()[0]))
with open("/home/sv440/Android/eagle/simulation/results_new/jct/yaqd/YH/yaqd.12000M",'r') as f:
    for line in f:
        if "total_job_running_time" not in line:
            continue
        jct_yaqd_12.append(float((line.split("total_job_running_time:")[1]).split()[0]))
with open("/home/sv440/Android/eagle/simulation/results_new/jct/yaqd/YH/yaqd.14000M",'r') as f:
    for line in f:
        if "total_job_running_time" not in line:
            continue
        jct_yaqd_14.append(float((line.split("total_job_running_time:")[1]).split()[0]))
with open("/home/sv440/Android/eagle/simulation/results_new/jct/yaqd/YH/yaqd.16000M",'r') as f:
    for line in f:
        if "total_job_running_time" not in line:
            continue
        jct_yaqd_16.append(float((line.split("total_job_running_time:")[1]).split()[0]))

fig, ax1 = plt.subplots()
c=np.sort(jct_m_8)
cp = 1. * np.arange(len(c)) / (len(c) - 1)
ax1.plot(c, cp, label="Murmuration", color=colors[0], linewidth=3)
c=np.sort(jct_s_8)
cp = 1. * np.arange(len(c)) / (len(c) - 1)
ax1.plot(c, cp, label="Sparrow", color=colors[1], linewidth=3)
c=np.sort(jct_yaqc_8)
cp = 1. * np.arange(len(c)) / (len(c) - 1)
ax1.plot(c, cp, label="Yaq-C", color=colors[2], linewidth=3)
c=np.sort(jct_yaqd_8)
cp = 1. * np.arange(len(c)) / (len(c) - 1)
#ax1.plot(c, cp, label="Yaq-D", color=colors[3], linewidth=3)
ax1.set_ylabel('CDF')
ax1.set_xlabel('Job Completion Times (s)')
plt.title('Cluster Size = 8000')
legend = ax1.legend()
frame = legend.get_frame()
frame.set_facecolor('1.0')
frame.set_edgecolor('1.0')
ax1.set_ylim(0.0, 1.1)
fig.tight_layout()
fig.savefig('simulation_jct_yh_8.pdf', dpi=fig.dpi, bbox_inches='tight')
plt.close(fig)

fig, ax1 = plt.subplots()
c=np.sort(jct_m_12)
cp = 1. * np.arange(len(c)) / (len(c) - 1)
ax1.plot(c, cp, label="Murmuration", color=colors[0], linewidth=3)
c=np.sort(jct_s_12)
cp = 1. * np.arange(len(c)) / (len(c) - 1)
ax1.plot(c, cp, label="Sparrow", color=colors[1], linewidth=3)
c=np.sort(jct_yaqc_12)
cp = 1. * np.arange(len(c)) / (len(c) - 1)
ax1.plot(c, cp, label="Yaq-C", color=colors[2], linewidth=3)
c=np.sort(jct_yaqd_12)
cp = 1. * np.arange(len(c)) / (len(c) - 1)
#ax1.plot(c, cp, label="Yaq-D", color=colors[3], linewidth=3)
ax1.set_ylabel('CDF')
ax1.set_xlabel('Job Completion Times (s)')
plt.title('Cluster Size = 12000')
legend = ax1.legend()
frame = legend.get_frame()
frame.set_facecolor('1.0')
frame.set_edgecolor('1.0')
ax1.set_ylim(0.0, 1.1)
fig.tight_layout()
fig.savefig('simulation_jct_yh_12.pdf', dpi=fig.dpi, bbox_inches='tight')
plt.close(fig)

fig, ax1 = plt.subplots()
c=np.sort(jct_m_16)
cp = 1. * np.arange(len(c)) / (len(c) - 1)
ax1.plot(c, cp, label="Murmuration", color=colors[0], linewidth=3)
c=np.sort(jct_s_16)
cp = 1. * np.arange(len(c)) / (len(c) - 1)
ax1.plot(c, cp, label="Sparrow", color=colors[1], linewidth=3)
c=np.sort(jct_yaqc_16)
cp = 1. * np.arange(len(c)) / (len(c) - 1)
ax1.plot(c, cp, label="Yaq-C", color=colors[2], linewidth=3)
c=np.sort(jct_yaqd_16)
cp = 1. * np.arange(len(c)) / (len(c) - 1)
#ax1.plot(c, cp, label="Yaq-D", color=colors[3], linewidth=3)
ax1.set_ylabel('CDF')
ax1.set_xlabel('Job Completion Times (s)')
plt.title('Cluster Size = 16000')
legend = ax1.legend()
frame = legend.get_frame()
frame.set_facecolor('1.0')
frame.set_edgecolor('1.0')
ax1.set_ylim(0.0, 1.1)
fig.tight_layout()
fig.savefig('simulation_jct_yh_16.pdf', dpi=fig.dpi, bbox_inches='tight')
plt.close(fig)
