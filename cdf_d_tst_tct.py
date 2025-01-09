import csv
import numpy as np
import collections
import random
from matplotlib import pyplot as plt, rcParams
from collections import defaultdict
from palettable.colorbrewer.qualitative import Paired_12, Set2_7

import matplotlib
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42


colors = Paired_12.mpl_colors

###########################################################################
# The second part of the script analyzes the pod queue and scheduling times.
# Files have been generated from syslog files using the following command -
# python3 pods.py (taking syslog files as defined in pods.sh and temp.tr)
# Generates pod logs with the following format in d.3000 -
# Pod job89-p7xxb - SchedulerQueueTime 0.023927 SchedulingAlgorithmTime 0.000503 KubeletQueueTime 0.000363 Node "caelum-507" ExecutionTime 25.5900908177
###########################################################################
# Scheduler Algorithm and Queue times, and the execution times.
# Scheduler Algorithm and Queue times, Kubelet queue times, cumulative queue times, and the execution times.
d_sq_list=[]
d_sa_list=[]
d_kq_list=[]
d_q_list=[]
d_xt_list=[]

t_d_sq_list=[]
t_d_sa_list=[]
t_d_kq_list=[]
t_d_q_list=[]
t_d_xt_list=[]

d_job_sq_list=collections.defaultdict(float)
d_job_sa_list=collections.defaultdict(float)
d_job_kq_list=collections.defaultdict(float)
d_job_q_list=collections.defaultdict(float)
d_job_xt_list=collections.defaultdict(float)
d_job_completion_list=collections.defaultdict(float)

#Tail Tasks
t_d_job_sq_list=collections.defaultdict(float)
t_d_job_sa_list=collections.defaultdict(float)
t_d_job_kq_list=collections.defaultdict(float)
t_d_job_q_list=collections.defaultdict(float)
t_d_job_xt_list=collections.defaultdict(float)
t_d_job_completion_list=collections.defaultdict(float)

#Queue times across tasks of a job
d_job_sq_dev=collections.defaultdict(list)

discard_jobs_d = ['job4', 'job3', 'job2', 'job1', 'job5', 'job6', 'job7', 'job8', 'job9', 'job10', 'job11', 'job12', 'job13', 'job15', 'job14', 'job18', 'job16', 'job19', 'job17', 'job21', 'job20', 'job22', 'job23', 'job24', 'job25', 'job26', 'job27', 'job28', 'job29', 'job30', 'job31', 'job33', 'job32', 'job34', 'job35', 'job36', 'job37', 'job38', 'job39', 'job40', 'job42', 'job41', 'job43', 'job44', 'job45', 'job46', 'job47', 'job48', 'job49', 'job51', 'job50', 'job52', 'job53', 'job55', 'job54', 'job56', 'job57', 'job58', 'job59', 'job60', 'job61', 'job62', 'job64', 'job63', 'job65', 'job67', 'job66', 'job68', 'job69', 'job72', 'job70', 'job71', 'job73', 'job74', 'job76', 'job75', 'job77', 'job78', 'job79', 'job80', 'job81', 'job82', 'job84', 'job83', 'job85', 'job86', 'job88', 'job87', 'job89', 'job90', 'job92', 'job91', 'job95', 'job94', 'job93', 'job97', 'job96', 'job98', 'job99', 'job101', 'job100', 'job103', 'job102', 'job105', 'job104', 'job106', 'job107', 'job109', 'job108', 'job110', 'job111', 'job113', 'job114', 'job115', 'job116', 'job112', 'job117', 'job118', 'job119', 'job121', 'job122', 'job123', 'job125', 'job126', 'job124', 'job127', 'job128', 'job129', 'job130', 'job131', 'job132', 'job133', 'job134', 'job136', 'job137', 'job135', 'job138', 'job140', 'job139', 'job141', 'job142', 'job143', 'job144', 'job145', 'job146', 'job147', 'job148', 'job149', 'job150', 'job151', 'job153', 'job152', 'job154', 'job155', 'job156', 'job157', 'job159', 'job161', 'job160', 'job162', 'job163', 'job158', 'job164', 'job165', 'job166', 'job168', 'job167', 'job169', 'job171', 'job170', 'job172', 'job173', 'job175', 'job174', 'job177', 'job176', 'job179', 'job178', 'job181', 'job183', 'job180', 'job182', 'job184', 'job185', 'job187', 'job186', 'job189', 'job188', 'job190', 'job191', 'job192', 'job193', 'job194', 'job195', 'job196', 'job197', 'job199', 'job198', 'job200', 'job201', 'job203', 'job202', 'job204', 'job205', 'job207', 'job206', 'job208', 'job209', 'job211', 'job212', 'job210', 'job213', 'job215', 'job216', 'job214', 'job217', 'job220', 'job219', 'job218', 'job221', 'job222', 'job223', 'job224', 'job225', 'job226', 'job227', 'job229', 'job228', 'job230', 'job231', 'job232', 'job234', 'job233', 'job235', 'job236', 'job237', 'job240', 'job238', 'job241', 'job239', 'job242', 'job243', 'job244', 'job245', 'job246', 'job247', 'job248', 'job250', 'job249', 'job251', 'job253', 'job252', 'job254', 'job257', 'job256', 'job258', 'job260', 'job261', 'job262', 'job259', 'job255', 'job263', 'job264', 'job265', 'job266', 'job267', 'job269', 'job268', 'job270', 'job272', 'job273', 'job274', 'job275', 'job276', 'job277', 'job279', 'job271', 'job280', 'job278', 'job281', 'job283', 'job284', 'job282', 'job285', 'job286', 'job287', 'job289', 'job288', 'job291', 'job292', 'job290', 'job293', 'job294', 'job295', 'job296', 'job299', 'job298', 'job301', 'job302', 'job303', 'job304', 'job305', 'job306', 'job308', 'job307', 'job309', 'job310', 'job311', 'job312', 'job313', 'job314', 'job315', 'job317', 'job318', 'job316', 'job319', 'job321', 'job320', 'job322', 'job324', 'job323', 'job325', 'job326', 'job327', 'job328', 'job330', 'job329', 'job331', 'job332', 'job334', 'job333', 'job335', 'job336', 'job337', 'job338', 'job339', 'job340', 'job341', 'job342', 'job343', 'job344', 'job345', 'job346', 'job347', 'job348', 'job349', 'job300', 'job350', 'job351', 'job352', 'job353', 'job354', 'job356', 'job355', 'job357', 'job358', 'job359', 'job360', 'job361', 'job362', 'job364', 'job366', 'job365', 'job367', 'job363', 'job368', 'job369', 'job370', 'job371', 'job372', 'job373', 'job374', 'job375', 'job377', 'job378', 'job376', 'job379', 'job380', 'job382', 'job381', 'job383', 'job385', 'job387', 'job384', 'job386', 'job388', 'job390', 'job391', 'job389', 'job392', 'job394', 'job393', 'job395', 'job396', 'job397', 'job398', 'job399', 'job400', 'job401', 'job402', 'job403', 'job404', 'job405', 'job406', 'job407', 'job408', 'job409', 'job410', 'job411', 'job412', 'job415', 'job414', 'job413', 'job417', 'job416', 'job418', 'job419', 'job420', 'job421', 'job422', 'job424', 'job425', 'job426', 'job427', 'job428', 'job430', 'job429', 'job431', 'job432', 'job423', 'job433', 'job434', 'job435', 'job436', 'job437', 'job438', 'job439', 'job440', 'job441', 'job442', 'job443', 'job444', 'job446', 'job445', 'job447', 'job448', 'job450', 'job449', 'job451', 'job452', 'job454', 'job453', 'job455', 'job458', 'job456', 'job457', 'job459', 'job460', 'job462', 'job463', 'job464', 'job465', 'job466', 'job467', 'job468', 'job469', 'job471', 'job472', 'job474', 'job473', 'job475', 'job476', 'job477', 'job478', 'job479', 'job481', 'job482', 'job480', 'job483', 'job485', 'job484', 'job486', 'job488', 'job487', 'job490', 'job489', 'job491', 'job493', 'job492', 'job494', 'job495', 'job497', 'job496', 'job498', 'job501', 'job499', 'job502', 'job503', 'job504', 'job505', 'job506', 'job507', 'job509', 'job508', 'job510', 'job512', 'job511', 'job513', 'job500', 'job514', 'job515', 'job516', 'job518', 'job517', 'job519', 'job520', 'job521', 'job522', 'job523', 'job524', 'job526', 'job525', 'job527', 'job529', 'job528', 'job530', 'job531', 'job532', 'job534', 'job533', 'job535', 'job536', 'job537', 'job538', 'job540', 'job539', 'job541', 'job542', 'job543', 'job544', 'job546', 'job545', 'job547', 'job548', 'job549', 'job550', 'job551', 'job554', 'job552', 'job553', 'job555', 'job557', 'job556', 'job558', 'job560', 'job561', 'job559', 'job562', 'job565', 'job563', 'job564', 'job566', 'job568', 'job567', 'job569', 'job570', 'job571', 'job572', 'job573', 'job574', 'job575', 'job576', 'job577', 'job578', 'job579', 'job580', 'job581', 'job582', 'job584', 'job585', 'job583', 'job587', 'job586', 'job589', 'job588', 'job590', 'job592', 'job591', 'job593', 'job594', 'job595', 'job596', 'job597', 'job598', 'job599', 'job600', 'job602', 'job601', 'job603', 'job604', 'job605', 'job606', 'job607', 'job608', 'job609', 'job610', 'job611', 'job612', 'job613', 'job615', 'job617', 'job614', 'job616', 'job618', 'job619', 'job622', 'job623', 'job624', 'job625', 'job626', 'job627', 'job628', 'job620', 'job629', 'job630', 'job631', 'job633', 'job634', 'job632', 'job637', 'job635', 'job638', 'job636', 'job639', 'job640', 'job642', 'job643', 'job645', 'job644', 'job646', 'job647', 'job648', 'job649', 'job650', 'job651', 'job641', 'job653', 'job652', 'job654', 'job655', 'job656', 'job657', 'job659', 'job658', 'job661', 'job660', 'job663', 'job662', 'job665', 'job664', 'job666', 'job667', 'job668', 'job669', 'job670', 'job671', 'job673', 'job674', 'job675', 'job672', 'job676', 'job677', 'job678', 'job679', 'job680', 'job682', 'job681', 'job683', 'job684', 'job685', 'job687', 'job686', 'job688', 'job689', 'job690', 'job691', 'job693', 'job692', 'job694', 'job695', 'job696', 'job697', 'job698', 'job699', 'job700', 'job701', 'job702', 'job703', 'job705', 'job704', 'job706', 'job707', 'job708', 'job709', 'job710', 'job711', 'job713', 'job712', 'job714', 'job717', 'job715', 'job716', 'job718', 'job719', 'job721', 'job720', 'job722', 'job723', 'job724', 'job725', 'job726', 'job727', 'job728', 'job730', 'job729', 'job731', 'job733', 'job734', 'job732', 'job735', 'job736', 'job737', 'job739', 'job738', 'job740', 'job741', 'job743', 'job744', 'job742', 'job745', 'job748', 'job747', 'job746', 'job749', 'job752', 'job751', 'job753', 'job755', 'job754', 'job756', 'job757', 'job758', 'job759', 'job760', 'job761', 'job762', 'job763', 'job764', 'job766', 'job765', 'job767', 'job768', 'job769', 'job770', 'job771', 'job772', 'job773', 'job774', 'job775', 'job776', 'job777', 'job778', 'job780', 'job781', 'job779', 'job782', 'job783', 'job784', 'job786', 'job787', 'job788', 'job785', 'job789', 'job790', 'job750', 'job792', 'job791', 'job793', 'job794', 'job795', 'job796', 'job797', 'job799', 'job800', 'job798', 'job801', 'job802', 'job803', 'job804', 'job805', 'job806', 'job807', 'job808', 'job809', 'job812', 'job810', 'job811', 'job813', 'job814', 'job815', 'job817', 'job816', 'job818', 'job820', 'job819', 'job821', 'job822', 'job823', 'job824', 'job825', 'job826', 'job827', 'job828', 'job829', 'job830', 'job833', 'job832', 'job834', 'job836', 'job837', 'job835', 'job838', 'job839', 'job840', 'job842', 'job831', 'job841', 'job843', 'job844', 'job845', 'job846', 'job847', 'job849', 'job848', 'job850', 'job851', 'job852', 'job855', 'job854', 'job856', 'job853', 'job857', 'job858', 'job860', 'job862', 'job861', 'job859', 'job863', 'job864', 'job865', 'job868', 'job866', 'job867', 'job869', 'job871', 'job870', 'job872', 'job873', 'job875', 'job876', 'job874', 'job877', 'job881', 'job884', 'job885', 'job886', 'job887', 'job883', 'job889', 'job1232', 'job1192', 'job1364', 'job1451', 'job1568', 'job2556', 'job2591', 'job2621', 'job3123', 'job3467', 'job3559', 'job3736', 'job3761', 'job3894', 'job4301', 'job4619', 'job4660', 'job4907', 'job4977', 'job5414', 'job5548', 'job5558', 'job5979', 'job6054', 'job6108', 'job6232', 'job6206', 'job6273', 'job6356', 'job6367', 'job6376', 'job6401', 'job6420', 'job6590', 'job6733', 'job6954', 'job6953', 'job7096', 'job7645', 'job7760', 'job7767', 'job7860', 'job7850', 'job7985', 'job8294', 'job8440', 'job8472', 'job8606', 'job8674', 'job8693', 'job8741', 'job8798', 'job8821', 'job8854', 'job8912', 'job9198', 'job9453', 'job9480', 'job9509', 'job9731', 'job9803', 'job9906', 'job9843', 'job9960']
d_pod_qt={}
count_tasks = collections.defaultdict(int)
#Pod job18-bl57n - SchedulerQueueTime 0.00192 SchedulingAlgorithmTime 0.000493 KubeletQueueTime 0.000207 Node "node28.sv440-128365.decentralizedsch-pg0.utah.cloudlab.us" ExecutionTime 500.37717814 NumSchedulingCycles 1 StartedAfterSec 5.45567 TAIL TASK
with open("results/pods/pods.d.10000J.400X.50N.10S.YH", 'r') as f:
    for line in f:
        if "SchedulerQueueTime" not in line:
            continue
        r = line.split()
        jobname = r[1].split("-")[0]
        if jobname in discard_jobs_d:
            continue
        sq = float(r[4])
        sa = float(r[6])
        kq = float(r[8])
        xt = float(r[12])
        tc = float((line.split("TaskCompletionTime")[1]).split()[0])

        d_sq_list.append(sq)
        d_sa_list.append(sa)
        d_kq_list.append(kq)
        d_q_list.append(sq + kq)
        d_xt_list.append(xt)

        podname = r[1]
        d_pod_qt[podname] = sq + kq

        d_job_sq_list[jobname] += sq
        d_job_sa_list[jobname] += sa
        d_job_kq_list[jobname] += kq
        d_job_q_list[jobname]  += sq + kq
        d_job_xt_list[jobname] += xt
        d_job_sq_dev[jobname].append(sq + kq)
        d_job_completion_list[jobname] += tc
        count_tasks[jobname] += 1

        if "TAIL TASK" in line:
            t_d_sq_list.append(sq)
            t_d_sa_list.append(sa)
            t_d_kq_list.append(kq)
            t_d_q_list.append(sq + kq)
            t_d_xt_list.append(xt)
            t_d_job_sq_list[jobname] += sq
            t_d_job_sa_list[jobname] += sa
            t_d_job_kq_list[jobname] += kq
            t_d_job_q_list[jobname]  += sq + kq
            t_d_job_xt_list[jobname] += xt
            t_d_job_completion_list[jobname] = tc
            #t_d_secafterepoch[jobname] = float((line.split("SecAfterEpoch")[1]).split()[0])
params = {
   'axes.labelsize': 18,
   'font.size': 16,
   'legend.fontsize': 14,
   'xtick.labelsize': 18,
   'ytick.labelsize': 18,
   'text.usetex': False,
   'figure.figsize': [6,3.4]
}
rcParams.update(params)

#CDF of tail tasks.
for jobname, num_tasks in count_tasks.items():
    d_job_sq_list[jobname] /= num_tasks
    '''
    if d_job_sq_list[jobname] > 14:
            print(jobname, "has high TST", d_job_sq_list[jobname])
    '''
    d_job_xt_list[jobname] /= num_tasks
    d_job_completion_list[jobname] /= num_tasks

colors = Set2_7.mpl_colors
fig, ax_jct = plt.subplots()
ax_jct.minorticks_off()
d_xt_list = list(d_job_xt_list.values())
d = np.sort(d_xt_list)
dp = 1. * np.arange(len(d)) / (len(d) - 1)
ax_jct.plot(d, dp, label="Average $x_t$", linestyle=':', linewidth=3, color=colors[2])
d_sq_list = list(d_job_sq_list.values())
t_d_sq_list = list(t_d_job_sq_list.values())
print("Average TST min and max", min(d_sq_list), max(d_sq_list))
print("Tail TST min and max", min(t_d_sq_list), max(t_d_sq_list))
d = np.sort(d_sq_list)
dp = 1. * np.arange(len(d)) / (len(d) - 1)
#plt.plot(c, cp, label="Average TST per job", linestyle='-.', linewidth=2, color=colors[0])
ax_jct.plot(d, dp, label="Average $S_t$", linestyle='-.', alpha=0.5, color=colors[0], linewidth=3)
d = np.sort(t_d_sq_list)
dp = 1. * np.arange(len(d)) / (len(d) - 1)
ax_jct.plot(d, dp, label="Tail $S_t$", linestyle='--', color=colors[0], linewidth=3)
d_completion_list = list(d_job_completion_list.values())
t_d_completion_list = list(t_d_job_completion_list.values())
d = np.sort(d_completion_list)
dp = 1. * np.arange(len(d)) / (len(d) - 1)
ax_jct.plot(d, dp, label="Average $C_t$", color=colors[1], alpha=0.5, linewidth=3)
d = np.sort(t_d_completion_list)
dp = 1. * np.arange(len(d)) / (len(d) - 1)
ax_jct.plot(d, dp, label="Tail $C_t$", color=colors[1], linestyle='--', linewidth=3)
ax_jct.set_ylabel('CDF')
ax_jct.set_xlabel('Duration (seconds)')
ax_jct.set_xticks(ticks=[0,25000,50000])
#ax_jct.set_xticks(ticks=[0,10000, 20000, 30000,40000])
#ax_jct.margins(0)
legend = ax_jct.legend()
frame = legend.get_frame()
frame.set_facecolor('1.0')
frame.set_edgecolor('1.0')
ax_jct.set_ylim(0.0, 1.1)
fig.tight_layout()
fig.savefig('fig8b.pdf', dpi=fig.dpi, bbox_inches='tight')
print("Murmuration tail TCT", np.percentile(t_d_completion_list, 50), np.percentile(t_d_completion_list, 90), np.percentile(t_d_completion_list, 99))

'''
fig, ax_jct = plt.subplots()
ax_jct.minorticks_off()
d_xt_list = list(d_job_xt_list.values())
d = np.sort(d_xt_list)
dp = 1. * np.arange(len(d)) / (len(d) - 1)
ax_jct.plot(d, dp, label="Average x", linestyle=':', linewidth=2, color=colors[2])
d_completion_list = list(d_job_completion_list.values())
t_d_completion_list = list(t_d_job_completion_list.values())
print("Completion times", np.percentile(d_completion_list, 50), np.percentile(d_completion_list, 90), np.percentile(d_completion_list, 99))
print("Tail Completion times", np.percentile(t_d_completion_list, 50), np.percentile(t_d_completion_list, 90), np.percentile(t_d_completion_list, 99))
d = np.sort(d_completion_list)
dp = 1. * np.arange(len(d)) / (len(d) - 1)
#plt.plot(c, cp, label="Completion Time for Tasks across Jobs", linewidth=2, color='cyan', alpha=0.5)
ax_jct.plot(d, dp, label="Average TCT", color=colors[0], alpha=0.5, linewidth=2)
d = np.sort(t_d_completion_list)
dp = 1. * np.arange(len(d)) / (len(d) - 1)
#plt.plot(c, cp, label="Completion Time for Tail Tasks across Jobs", linewidth=2, color='orange', alpha=0.5)
ax_jct.plot(d, dp, label="Tail TCT", color=colors[1], alpha=0.5, linewidth=2)
ax_jct.set_ylabel('CDF')
#ax_jct.set_xscale('log')
ax_jct.set_xlabel('Duration (seconds)')
#ax_jct.text(-0.75,-0.25, "(a) Kubernetes", size=12, ha="center", transform=ax_jct.transAxes)
print(ax_jct.get_xticks())
#plt.title('x and average and tail TST and TCT in Murmuration')
legend = ax_jct.legend()
frame = legend.get_frame()
frame.set_facecolor('1.0')
frame.set_edgecolor('1.0')
ax_jct.set_ylim(0.0, 1.1)
#plt.xticks(np.arange(0, 60001, 30000))
fig.tight_layout()
#fig.savefig('task_completion_time.pdf', dpi=fig.dpi, bbox_inches='tight')
fig.savefig('d_tct.pdf', dpi=fig.dpi, bbox_inches='tight')

fig, ax_jct = plt.subplots()
ax_jct.minorticks_off()
d_xt_list = list(d_job_xt_list.values())
d = np.sort(d_xt_list)
dp = 1. * np.arange(len(d)) / (len(d) - 1)
ax_jct.plot(d, dp, label="Average x", linestyle=':', linewidth=2, color=colors[2])
d_sq_list = list(d_job_sq_list.values())
t_d_sq_list = list(t_d_job_sq_list.values())
d = np.sort(d_sq_list)
dp = 1. * np.arange(len(d)) / (len(d) - 1)
#plt.plot(c, cp, label="Average TST per job", linestyle='-.', linewidth=2, color=colors[0])
ax_jct.plot(d, dp, label="Average TST", linestyle='-.', color=colors[0], linewidth=2)
d = np.sort(t_d_sq_list)
dp = 1. * np.arange(len(d)) / (len(d) - 1)
ax_jct.plot(d, dp, label="Tail TST", linestyle='--', color=colors[1], linewidth=2)
ax_jct.set_ylabel('CDF')
#ax_jct.set_xscale('log')
ax_jct.set_xlabel('Duration (seconds)')
#ax_jct.text(-0.75,-0.25, "(a) Kubernetes", size=12, ha="center", transform=ax_jct.transAxes)
print(ax_jct.get_xticks())
#plt.title('x and average and tail TST and TCT in Murmuration')
legend = ax_jct.legend()
frame = legend.get_frame()
frame.set_facecolor('1.0')
frame.set_edgecolor('1.0')
ax_jct.set_ylim(0.0, 1.1)
#plt.xticks(np.arange(0, 60001, 30000))
fig.tight_layout()
#fig.savefig('task_completion_time.pdf', dpi=fig.dpi, bbox_inches='tight')
print(fig.get_size_inches())
fig.savefig('d_tst.pdf', dpi=fig.dpi, bbox_inches='tight')
'''
