import csv
import numpy as np
import collections
import random
from matplotlib import pyplot as plt, rcParams
from collections import defaultdict
from palettable.colorbrewer.qualitative import Set2_7
from bisect import bisect
from matplotlib.ticker import ScalarFormatter
import matplotlib
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42

colors = Set2_7.mpl_colors

###########################################################################
# The second part of the script analyzes the pod queue and scheduling times.
# Files have been generated from syslog files using the following command -
# python3 pods.py (taking syslog files as defined in pods.sh and temp.tr)
# Generates pod logs with the following format in d.3000 -
# Pod job89-p7xxb - SchedulerQueueTime 0.023927 SchedulingAlgorithmTime 0.000503 KubeletQueueTime 0.000363 Node "caelum-507" ExecutionTime 25.5900908177
###########################################################################
# Scheduler Algorithm and Queue times, and the execution times.
discard_jobs = ['job4', 'job3', 'job2', 'job1', 'job5', 'job6', 'job7', 'job8', 'job9', 'job10', 'job11', 'job12', 'job13', 'job15', 'job14', 'job16', 'job18', 'job19', 'job17', 'job20', 'job21', 'job22', 'job23', 'job24', 'job25', 'job26', 'job27', 'job28', 'job29', 'job30', 'job31', 'job32', 'job33', 'job34', 'job35', 'job36', 'job37', 'job38', 'job39', 'job40', 'job41', 'job42', 'job43', 'job44', 'job45', 'job46', 'job47', 'job48', 'job49', 'job50', 'job51', 'job52', 'job53', 'job54', 'job55', 'job56', 'job57', 'job58', 'job59', 'job60', 'job61', 'job62', 'job63', 'job64', 'job65', 'job66', 'job67', 'job68', 'job69', 'job71', 'job70', 'job72', 'job73', 'job75', 'job76', 'job74', 'job77', 'job80', 'job78', 'job79', 'job81', 'job82', 'job83', 'job84', 'job85', 'job86', 'job87', 'job88', 'job89', 'job92','job91', 'job90', 'job93', 'job94', 'job95', 'job96', 'job97', 'job99', 'job98', 'job100', 'job101', 'job103', 'job102', 'job104', 'job105', 'job106', 'job107', 'job108', 'job109', 'job110', 'job111', 'job112', 'job113', 'job114', 'job115', 'job116', 'job117', 'job118', 'job119', 'job121', 'job122', 'job123', 'job125', 'job124', 'job126', 'job127', 'job128', 'job129', 'job130', 'job131', 'job132', 'job133', 'job134', 'job135', 'job136', 'job137', 'job138', 'job139', 'job140', 'job141', 'job142', 'job143', 'job144', 'job145', 'job146', 'job147', 'job148', 'job149', 'job150', 'job151', 'job153', 'job152', 'job154', 'job155', 'job156', 'job157', 'job158', 'job159', 'job161', 'job160', 'job162', 'job163', 'job165', 'job164', 'job166', 'job167', 'job168', 'job169', 'job170', 'job171', 'job172', 'job173', 'job174', 'job175', 'job177', 'job176', 'job178', 'job179', 'job181', 'job180', 'job182', 'job183', 'job184', 'job185', 'job186', 'job187', 'job188', 'job189', 'job190', 'job191', 'job192', 'job193', 'job194', 'job195', 'job196', 'job197', 'job198', 'job199', 'job200', 'job201', 'job202', 'job203', 'job204', 'job205', 'job206', 'job207', 'job208', 'job209', 'job210', 'job211', 'job212', 'job213', 'job214', 'job215', 'job216', 'job217', 'job218', 'job219', 'job220', 'job221', 'job222', 'job223', 'job224', 'job225', 'job226', 'job227', 'job228', 'job229', 'job230', 'job231', 'job232', 'job233', 'job234', 'job235', 'job236', 'job237', 'job238', 'job240', 'job239', 'job241', 'job242', 'job243', 'job244', 'job245', 'job246', 'job247', 'job248', 'job249', 'job250', 'job251', 'job252', 'job253', 'job254', 'job256', 'job257', 'job255', 'job258', 'job260', 'job259', 'job261', 'job262', 'job263', 'job264', 'job265', 'job266', 'job267', 'job268', 'job269', 'job270', 'job272', 'job273', 'job271', 'job274', 'job275', 'job276', 'job277', 'job278', 'job279', 'job280', 'job281', 'job282', 'job283', 'job284', 'job285', 'job286', 'job287', 'job288', 'job289', 'job290', 'job291', 'job292', 'job293', 'job294', 'job295', 'job296', 'job298', 'job299', 'job301', 'job302', 'job304', 'job303', 'job305', 'job306', 'job308', 'job307', 'job309', 'job310', 'job311', 'job312', 'job313', 'job314', 'job315', 'job316', 'job317', 'job318', 'job319', 'job320', 'job321', 'job322', 'job323', 'job324', 'job325', 'job326', 'job327', 'job328', 'job329', 'job330', 'job331', 'job332', 'job333', 'job334', 'job335', 'job336', 'job337', 'job338', 'job339', 'job340', 'job341', 'job342', 'job343', 'job344', 'job345', 'job346', 'job347', 'job300', 'job348', 'job349', 'job350', 'job352', 'job351', 'job353', 'job354', 'job355', 'job356', 'job357', 'job358', 'job359', 'job360', 'job361', 'job362', 'job364', 'job363', 'job365', 'job366', 'job367', 'job368', 'job369', 'job370', 'job371', 'job372', 'job373', 'job374', 'job375', 'job376', 'job377', 'job378', 'job379', 'job380', 'job381', 'job382', 'job383', 'job385', 'job384', 'job386', 'job387', 'job388', 'job389', 'job390', 'job391', 'job392', 'job393', 'job394', 'job395', 'job396', 'job397', 'job398', 'job399', 'job400', 'job401', 'job402', 'job403', 'job404', 'job405', 'job406', 'job407', 'job408', 'job409', 'job410', 'job411', 'job412', 'job414', 'job413', 'job415', 'job417', 'job416', 'job418', 'job419', 'job421', 'job420', 'job422', 'job424', 'job425', 'job426', 'job423', 'job427', 'job428', 'job430', 'job429', 'job431', 'job432', 'job433', 'job434', 'job435', 'job436', 'job437', 'job438', 'job439', 'job440', 'job441', 'job442', 'job443', 'job444', 'job445', 'job446', 'job447', 'job448', 'job449', 'job450', 'job451', 'job452', 'job453', 'job454', 'job455', 'job456', 'job458', 'job457', 'job459', 'job460', 'job462', 'job463', 'job464', 'job465', 'job466', 'job467', 'job468', 'job469', 'job471', 'job472', 'job473', 'job474', 'job475', 'job476', 'job477', 'job478', 'job479', 'job480', 'job481', 'job482', 'job483', 'job485', 'job484', 'job486', 'job487', 'job488', 'job489', 'job490', 'job491', 'job492', 'job493', 'job494', 'job495', 'job496', 'job497', 'job498', 'job499', 'job501', 'job502', 'job503', 'job504', 'job500', 'job505', 'job506', 'job507', 'job508', 'job509', 'job510', 'job511', 'job512', 'job513', 'job514', 'job515', 'job516', 'job517', 'job518', 'job519', 'job520', 'job521', 'job522', 'job523', 'job524', 'job525', 'job526', 'job527', 'job528', 'job529', 'job530', 'job531', 'job532', 'job533', 'job534', 'job535', 'job536', 'job537', 'job538', 'job539', 'job540', 'job541', 'job542', 'job543', 'job544', 'job545', 'job546', 'job547', 'job548', 'job549', 'job550', 'job551', 'job552', 'job554', 'job553', 'job555', 'job556', 'job557', 'job558', 'job560', 'job559', 'job561', 'job562', 'job563', 'job564', 'job565', 'job566', 'job568', 'job567', 'job569', 'job570', 'job571', 'job573', 'job572', 'job574', 'job575', 'job576', 'job577', 'job578', 'job579', 'job581', 'job580', 'job582', 'job585', 'job584', 'job583', 'job586', 'job587', 'job589', 'job588', 'job590', 'job592', 'job591', 'job593', 'job594', 'job595', 'job596', 'job597', 'job598', 'job599', 'job600', 'job601', 'job602', 'job603', 'job604', 'job605', 'job606', 'job607', 'job608', 'job609', 'job610', 'job611', 'job612', 'job613', 'job614', 'job615', 'job616', 'job617', 'job618', 'job619', 'job621', 'job622', 'job620', 'job623', 'job624', 'job625', 'job626', 'job627', 'job628', 'job629', 'job630', 'job631', 'job632', 'job633', 'job634', 'job635', 'job636', 'job637', 'job638', 'job639', 'job640', 'job642', 'job643', 'job641', 'job644', 'job645', 'job646', 'job647', 'job648', 'job649', 'job650', 'job651', 'job652', 'job653', 'job654', 'job655', 'job656', 'job657', 'job658', 'job659', 'job660', 'job661', 'job662', 'job663', 'job664', 'job665', 'job666', 'job667', 'job668', 'job669', 'job670', 'job671', 'job672', 'job673', 'job674', 'job675', 'job676', 'job677', 'job678', 'job679', 'job680', 'job681', 'job682', 'job683', 'job684', 'job685', 'job686', 'job687', 'job688', 'job689', 'job690', 'job691', 'job692', 'job693', 'job694', 'job695', 'job696', 'job697', 'job698', 'job699', 'job700', 'job701', 'job702', 'job703', 'job704', 'job705', 'job706', 'job707', 'job708', 'job709', 'job710', 'job711', 'job713', 'job712', 'job714', 'job715', 'job716', 'job717', 'job718', 'job719', 'job721', 'job720', 'job722', 'job723', 'job724', 'job725', 'job726', 'job727', 'job728', 'job729', 'job730', 'job731', 'job733', 'job732', 'job734', 'job735', 'job736', 'job737', 'job738', 'job739', 'job740', 'job741', 'job742', 'job743', 'job744', 'job745', 'job746', 'job747', 'job748', 'job749', 'job751', 'job752', 'job753', 'job754', 'job755', 'job756', 'job757', 'job758', 'job759', 'job760', 'job761', 'job762', 'job763', 'job764', 'job765', 'job766', 'job767', 'job768', 'job769', 'job770', 'job771', 'job772', 'job773', 'job774', 'job775', 'job776', 'job777', 'job778', 'job780', 'job779', 'job781', 'job782', 'job783', 'job784', 'job785', 'job786', 'job787', 'job788', 'job789', 'job790', 'job791', 'job792', 'job793', 'job794', 'job795', 'job796', 'job797', 'job798', 'job799', 'job800', 'job801', 'job802', 'job803', 'job804', 'job805', 'job806', 'job807', 'job808', 'job809', 'job810', 'job811', 'job812', 'job813', 'job814', 'job815', 'job816', 'job817', 'job818', 'job819', 'job820', 'job821', 'job822', 'job823', 'job824', 'job825', 'job1192', 'job1364', 'job2556', 'job2591', 'job2621', 'job3123', 'job3559', 'job3875', 'job4301', 'job4619', 'job4660', 'job4907', 'job4977', 'job5414', 'job5548', 'job5558', 'job5967', 'job5979', 'job6054', 'job6206', 'job6108', 'job6420', 'job6733', 'job6954', 'job7096', 'job7218', 'job6953', 'job7767', 'job7850', 'job8294', 'job8693', 'job8741', 'job8912', 'job9509', 'job9731', 'job9960', 'job9843']
c_sq_list=[]
c_sa_list=[]
c_xt_list=[]

t_c_sq_list=[]
t_c_sa_list=[]
t_c_xt_list=[]

c_job_sq_list=collections.defaultdict(float)
c_job_sa_list=collections.defaultdict(float)
c_job_xt_list=collections.defaultdict(float)
c_job_completion_list=collections.defaultdict(float)

#Tail Tasks
t_c_job_sq_list=collections.defaultdict(float)
t_c_job_sa_list=collections.defaultdict(float)
t_c_job_xt_list=collections.defaultdict(float)
t_c_job_completion_list=collections.defaultdict(float)

t_c_queueaddtime = {}

c_pod_qt={}
count_tasks = collections.defaultdict(int)
#Pod job18-bl57n - SchedulerQueueTime 0.00192 SchedulingAlgorithmTime 0.000493 KubeletQueueTime 0.000207 Node "node28.sv440-128365.decentralizedsch-pg0.utah.cloudlab.us" ExecutionTime 500.37717814 NumSchedulingCycles 1 StartedAfterSec 5.45567 TAIL TASK
with open("results/pods/pods.c.10000J.400X.50N.YH.2",'r') as f:
    for line in f:
        if "SchedulerQueueTime" not in line:
            continue
        r = line.split()
        sq = float(r[4])
        sa = float(r[6])
        xt = float(r[12])
        tc = float((line.split("TaskCompletionTime")[1]).split()[0])

        podname = r[1]
        c_pod_qt[podname] = sq

        c_sq_list.append(sq)
        c_sa_list.append(sa)
        c_xt_list.append(xt)

        jobname = r[1].split("-")[0]
        if jobname in discard_jobs:
            continue
        c_job_sq_list[jobname] += sq
        c_job_sa_list[jobname] += sa
        c_job_xt_list[jobname] += xt
        c_job_completion_list[jobname] += tc
        count_tasks[jobname] += 1
        if "TAIL TASK" in line:
            t_c_sq_list.append(sq)
            t_c_sa_list.append(sa)
            t_c_xt_list.append(xt)
            t_c_job_sq_list[jobname] += sq
            t_c_job_sa_list[jobname] += sa
            t_c_job_xt_list[jobname] += xt
            t_c_queueaddtime[jobname] = float((line.split("QueueAddTime")[1]).split()[0])
            t_c_job_completion_list[jobname] = tc
'''
#CDF of tail tasks.
c = np.sort(t_c_sq_list)
cp = 1. * np.arange(len(c)) / (len(c) - 1)
#Show CDF
fig = plt.plot(c, cp, label="Queue Time for Tail Tasks")
c = np.sort(c_sq_list)
cp = 1. * np.arange(len(c)) / (len(c) - 1)
plt.plot(c, cp, label="Queue Time for All Tasks")
plt.xlabel('Queue Times')
plt.title('Scheduler Queue Times across Tasks')
plt.ylabel('CDF')
plt.legend()
#plt.show()
'''
print("Scheduler Queue time across all tasks", np.percentile(c_sq_list,50), np.percentile(c_sq_list,90), np.percentile(c_sq_list,99))
print("Scheduler Queue time across tail tasks", np.percentile(t_c_sq_list,50), np.percentile(t_c_sq_list,90), np.percentile(t_c_sq_list,99))
print("################")

params = {
   'axes.labelsize': 16,
   'font.size': 16,
   'legend.fontsize': 11,
   'xtick.labelsize': 16,
   'ytick.labelsize': 16,
   'text.usetex': False,
   #'figure.figsize': [7.2, 3.4]
   'figure.figsize': [5.7, 3.4]
}
rcParams.update(params)
#CDF of tail tasks.
for jobname, num_tasks in count_tasks.items():
    c_job_sq_list[jobname] /= num_tasks
    c_job_xt_list[jobname] /= num_tasks
    c_job_completion_list[jobname] /= num_tasks
#fig, (ax_jct, ax_tail)= plt.subplots(1,2)
fig, ax_jct = plt.subplots()
ax_jct.minorticks_off()
#print("Fig size", fig.get_size_inches())
c_xt_list = list(c_job_xt_list.values())
c = np.sort(c_xt_list)
cp = 1. * np.arange(len(c)) / (len(c) - 1)
ax_jct.plot(c, cp, label="Average $x$", linestyle=':', linewidth=2, color=colors[2])
#Take the list of average task completions per job. Sort them. Plot as CDF.
c_sq_list = list(c_job_sq_list.values())
t_c_sq_list = list(t_c_job_sq_list.values())
c = np.sort(c_sq_list)
cp = 1. * np.arange(len(c)) / (len(c) - 1)
#plt.plot(c, cp, label="Average $S_t$ per job", linestyle='-.', linewidth=2, color=colors[0])
ax_jct.plot(c, cp, label="Average $TST$", linestyle='-.', color=colors[0])
c_completion_list = list(c_job_completion_list.values())
t_c_completion_list = list(t_c_job_completion_list.values())
print("Median Kubernetes Average $TCT$", np.percentile(c_completion_list, 50))
c = np.sort(c_completion_list)
cp = 1. * np.arange(len(c)) / (len(c) - 1)
#plt.plot(c, cp, label="Completion Time for Tasks across Jobs", linewidth=5, color='cyan', alpha=0.5)
ax_jct.plot(c, cp, label="Average $TCT$", color=colors[0], alpha=0.5)
c = np.sort(t_c_sq_list)
cp = 1. * np.arange(len(c)) / (len(c) - 1)
ax_jct.plot(c, cp, label="Tail $TST$", linestyle='--', color=colors[1])
c = np.sort(t_c_completion_list)
cp = 1. * np.arange(len(c)) / (len(c) - 1)
#plt.plot(c, cp, label="Completion Time for Tail Tasks across Jobs", linewidth=5, color='orange', alpha=0.5)
ax_jct.plot(c, cp, label="Tail $TCT$", color=colors[1], alpha=0.5)
ax_jct.set_ylabel('CDF')
#ax_jct.set_xscale('log')
ax_jct.set_xlabel('Duration (seconds)')
#ax_jct.text(-0.75,-0.25, "(a) Kubernetes", size=12, ha="center", transform=ax_jct.transAxes)
print(ax_jct.get_xticks())
#plt.title('Scheduler Queue Wait Times and Task Completion Times Aggregated Over Jobs')
legend = ax_jct.legend()
frame = legend.get_frame()
frame.set_facecolor('1.0')
frame.set_edgecolor('1.0')
ax_jct.set_ylim(0.0, 1.1)
#plt.xticks(np.arange(0, 60001, 30000))
#plt.show()
fig.tight_layout()
#fig.savefig('task_completion_time.pdf', dpi=fig.dpi, bbox_inches='tight')
print(fig.dpi)
fig.savefig('c_d_tail_tc_a.pdf', dpi=fig.dpi, bbox_inches='tight')
print("Scheduler Queue time across all tasks of jobs", np.percentile(c_sq_list,50), np.percentile(c_sq_list,90), np.percentile(c_sq_list,99))
print("Scheduler Queue time across tail tasks of jobs", np.percentile(t_c_sq_list,50), np.percentile(t_c_sq_list,90), np.percentile(t_c_sq_list,99))
print("Completion time across all tasks", np.percentile(c_completion_list,50), np.percentile(c_completion_list,90), np.percentile(c_completion_list,99))
print("Completion time across tail tasks", np.percentile(t_c_completion_list,50), np.percentile(t_c_completion_list,90), np.percentile(t_c_completion_list,99))
print("Execution time of tasks", np.percentile(c_xt_list,50), np.percentile(c_xt_list,90), np.percentile(c_xt_list,99))
print("################")

# NAME                                                        CPU(cores)   CPU%        MEMORY(bytes)   MEMORY%     
# node1.sv440-128429.decentralizedsch-pg0.utah.cloudlab.us    35844m       56%         2656Mi          2%
c_cpu = []
d_cpu = []
dc_cpu = {}
dd_cpu = {}
c_per_node_cpup = []
rampup_discard = 10 #before
ramdown_discard = 377 #after
discard_count = 0
with open("results/utilization/utilization.c.10000J.400X.50N.YH", 'r') as f:
    c_per_node_cpu = []
    start_time = 0
    for r in f:
        if "NAME" in r:
            discard_count += 1
            if len(c_per_node_cpu) > 0:
                # Take the average of this iteration over all nodes.
                cpu_avg = sum(c_per_node_cpu) / len(c_per_node_cpu)
                c_cpu.append(cpu_avg)
                c_per_node_cpu.clear()
                dc_cpu[start_time] = cpu_avg 
                start_time += 120
            continue
        if discard_count > ramdown_discard:
            break
        if discard_count < rampup_discard:
            continue
        if "node0" in r or "node1" in r:
            continue
        r = r.split()
        cpu = int((r[1].split("m"))[0])
        cpup = int((r[2].split("%"))[0])
        c_per_node_cpu.append(cpu)
        c_per_node_cpup.append(cpup)

print("CPU Utilization in C", np.percentile(c_cpu, 50), np.percentile(c_cpu, 90), np.percentile(c_cpu, 99))
print("CPU% Utilization in C", np.percentile(c_per_node_cpup, 50), np.percentile(c_per_node_cpup, 90), np.percentile(c_per_node_cpup, 99))

# Arrange tasks according to when they entered the scheduler queue.
sorted_t_c_queueaddtime = sorted(t_c_queueaddtime.items(), key=lambda item: item[1])
dtail_c_time_sorted = {}
jobnames, tail_queueaddtime = zip(*sorted_t_c_queueaddtime) # unpack a list of pairs into two tuples
#Bucketize dtail_c_time_sorted to get 50th/99th tail latency per interval period.
BUCKET_SIZE=10
start_time=0
end_time=60000
max_buckets = int(end_time / BUCKET_SIZE) + 1
#grid shows the start time of the bucket at that index.
grid=[start_time + n*BUCKET_SIZE for n in range(max_buckets)]
#bins stores sq times of tail tasks that got added to sq at that bucket index.
bins=collections.defaultdict(list)
#Tails of these jobs arrived in ascending order.
s = {}
for jobname in jobnames:
    tailtaskqueueaddtime = t_c_queueaddtime[jobname]
    idx = bisect(grid, tailtaskqueueaddtime)
    #dtail_c_time_sorted[tailtaskqueueaddtime] = t_c_job_sq_list[jobname]
    bins[idx].append(t_c_job_sq_list[jobname])
for idx in list(range(max_buckets)):
    if len(bins[idx]) == 0:
        continue
    dtail_c_time_sorted[grid[idx]] =  np.percentile(bins[idx], 99)
    s[grid[idx]] = len(bins[idx])

fig, ax_tail = plt.subplots()
ax_tail2 = ax_tail.twinx()
dc_cpu = sorted(dc_cpu.items())
dtail_c_time_sorted = sorted(dtail_c_time_sorted.items())
x,y = zip(*dc_cpu)
print("Max cpu utilization", max(y))
l1, = ax_tail.plot(x, y, label="CPU Utilization on Workers", linewidth=2, color=colors[0])
#ax_tail.set_xticks(np.arange(0, 60001, 30000))
ax_tail.set_xlabel('Duration in logarithmic scale (seconds)')
ax_tail.set_xscale('log')
ax_tail.set_ylim(0, 13000)
ax_tail.set_yticks([0,6000, 12000])
ax_tail.set_ylabel('CPU (millicores)', color=colors[0])
#time, tail latency
x,y=zip(*dtail_c_time_sorted)
s1 = [2*s[n] for n in x]
l2 = ax_tail2.scatter(x,y, marker = 'o', label="Tail Latencies", s=s1, color=colors[1])
z = np.polyfit(x, y, 2)
p = np.poly1d(z)
#l3= ax_tail2.plot(x, p(x), color=colors[2], linestyle="--")
ax_tail2.set_ylabel('Tail TST (seconds)', color=colors[1])
ax_tail2.set_ylim(0, 40000)
ax_tail2.set_yticks(np.arange(0, 50000 , 10000))    
ax_tail2.set_xscale('log')
#ax_tail.text(0.5,-0.4, "(b)", size=12, ha="center", transform=ax_tail.transAxes)
#legend = plt.legend([l1, l2, l3], ["Average CPU Utilization on Workers", "99th %ile Tail Task Scheduler Times", "Trend Line for Tail Task Scheduler Times"])
legend = plt.legend([l1, l2], ["Average CPU Utilization on Nodes", "99th %ile Tail TST"], framealpha=0.5)
frame = legend.get_frame()
frame.set_facecolor('1.0')
frame.set_edgecolor('1.0')
fig.tight_layout()
fig.savefig('fig2a.pdf', dpi=fig.dpi, bbox_inches='tight')
#plt.title('Comparison of CPU Utilization and Tail Latencies over time')
#plt.show()

###Distributed Scheduler
# Scheduler Algorithm and Queue times, and the execution times.
tct = []
w2x = []
tail_tct = []
jct_sparrow = []
#29.0950625  estimated_task_duration:  19  by_def:  0  total_job_running_time:  29.0015 job_start: 0.09356249999999999 job_end: 29.0950625 average TCT 19.0950625 tail TCT 29.0950625
#with open("/home/sv440/Android/eagle/simulation/results/sparrow_tail/s.14.10X.tail_analysis",'r') as f:
with open("/home/sv440/Android/eagle/simulation/results_new/jct/sparrow/YH/s.10000M",'r') as f:
    for line in f:
        if "Total time elapsed in the DC" in line:
            continue
        tct.append(float((line.split("average TCT")[1]).split()[0]))
        tail_tct.append(float((line.split("tail TCT")[1]).split()[0]))
        w2x.append(float((line.split("average w2x")[1]).split()[0]))
        jct_sparrow.append(float((line.split("total_job_running_time:")[1]).split()[0]))

count_tasks = collections.defaultdict(int)
c_job_xt_list=collections.defaultdict(float)
with open("results/pods/pods.c.10000J.400X.50N.YH.2",'r') as f:
    for line in f:
        if "SchedulerQueueTime" not in line:
            continue
        r = line.split()
        xt = float(r[12])
        jobname = r[1].split("-")[0]
        c_job_xt_list[jobname] += xt
        count_tasks[jobname] += 1

for jobname, num_tasks in count_tasks.items():
    c_job_xt_list[jobname] /= num_tasks

params = {
   'axes.labelsize': 16,
   'font.size': 16,
   'legend.fontsize': 14,
   'xtick.labelsize': 16,
   'ytick.labelsize': 16,
   'text.usetex': False,
   'figure.figsize': [5.7, 3.4]
}
rcParams.update(params)

#Take the list of average task completions per job. Sort them. Plot as CDF.
fig, ax_tail = plt.subplots()
ax_tail.minorticks_off()
print("Median Sparrow Average $TCT$", np.percentile(tct, 50))
c_xt_list = list(c_job_xt_list.values())
c = np.sort(c_xt_list)
cp = 1. * np.arange(len(c)) / (len(c) - 1)
ax_tail.plot(c, cp, label="Average $x$", linestyle=':', linewidth=2, color=colors[2])
c = np.sort(w2x)
cp = 1. * np.arange(len(c)) / (len(c) - 1)
ax_tail.plot(c, cp, label="Average $w2x$", linewidth=3, color=colors[3], alpha=0.75)
c = np.sort(tct)
cp = 1. * np.arange(len(c)) / (len(c) - 1)
ax_tail.plot(c, cp, label="Average $TCT$", linewidth=3, color=colors[0], alpha=0.75, linestyle='--')
c = np.sort(tail_tct)
cp = 1. * np.arange(len(c)) / (len(c) - 1)
ax_tail.plot(c, cp, label="Tail $TCT$", linewidth=3, color=colors[1])
c = np.sort(jct_sparrow)
cp = 1. * np.arange(len(c)) / (len(c) - 1)
ax_tail.plot(c, cp, label="$JCT$", linewidth=3, color=colors[4], alpha=0.75, linestyle='dashdot')
ax_tail.set_xlabel('Duration (seconds)')
#ax_tail.text(0.5,-0.25, "(b) Sparrow", size=12, ha="center", transform=ax_tail.transAxes)
#ax_tail.set_xscale('log')
#ax_tail.set_xticks([1.e-02, 1.e+00, 1.e+02, 1.e+04])
#ax_tail.set_xlim(-1000, 60001)
#ax_tail.set_xticks([0, 20000, 40000, 60000])
ax_tail.minorticks_off()
legend = ax_tail.legend()
frame = legend.get_frame()
frame.set_facecolor('1.0')
frame.set_edgecolor('1.0')
ax_tail.set_ylim(0.0, 1.1)
ax_tail.set_ylabel('CDF')
#x_formatter = ScalarFormatter(useOffset=True)
#ax_tail.xaxis.set_major_formatter(x_formatter)

fig.tight_layout()
#fig.savefig('c_tail_tc_util.pdf', dpi=fig.dpi, bbox_inches='tight')
fig.savefig('fig2c.pdf', dpi=fig.dpi, bbox_inches='tight')
