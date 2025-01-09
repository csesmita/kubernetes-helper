import numpy as np
from matplotlib import pyplot as plt
from matplotlib.ticker import ScalarFormatter
from palettable.colorbrewer.qualitative import Set2_7
from matplotlib import pyplot as plt, rcParams
import random
import matplotlib

matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42

#RANDOM_SAMPLE = 1000
colors = Set2_7.mpl_colors
params = {
   'axes.labelsize': 16,
   'font.size': 16,
   'legend.fontsize': 14,
   'xtick.labelsize': 16,
   'ytick.labelsize': 16,
   'text.usetex': False,
   'figure.figsize': [7.4, 6.0]
}
rcParams.update(params)

discard_jobs = ['job4', 'job3', 'job2', 'job1', 'job5', 'job6', 'job7', 'job8', 'job9', 'job10', 'job11', 'job12', 'job13', 'job15', 'job14', 'job16', 'job18', 'job19', 'job17', 'job20', 'job21', 'job22', 'job23', 'job24', 'job25', 'job26', 'job27', 'job28', 'job29', 'job30', 'job31', 'job32', 'job33', 'job34', 'job35', 'job36', 'job37', 'job38', 'job39', 'job40', 'job41', 'job42', 'job43', 'job44', 'job45', 'job46', 'job47', 'job48', 'job49', 'job50', 'job51', 'job52', 'job53', 'job54', 'job55', 'job56', 'job57', 'job58', 'job59', 'job60', 'job61', 'job62', 'job63', 'job64', 'job65', 'job66', 'job67', 'job68', 'job69', 'job71', 'job70', 'job72', 'job73', 'job75', 'job76', 'job74', 'job77', 'job80', 'job78', 'job79', 'job81', 'job82', 'job83', 'job84', 'job85', 'job86', 'job87', 'job88', 'job89', 'job92','job91', 'job90', 'job93', 'job94', 'job95', 'job96', 'job97', 'job99', 'job98', 'job100', 'job101', 'job103', 'job102', 'job104', 'job105', 'job106', 'job107', 'job108', 'job109', 'job110', 'job111', 'job112', 'job113', 'job114', 'job115', 'job116', 'job117', 'job118', 'job119', 'job121', 'job122', 'job123', 'job125', 'job124', 'job126', 'job127', 'job128', 'job129', 'job130', 'job131', 'job132', 'job133', 'job134', 'job135', 'job136', 'job137', 'job138', 'job139', 'job140', 'job141', 'job142', 'job143', 'job144', 'job145', 'job146', 'job147', 'job148', 'job149', 'job150', 'job151', 'job153', 'job152', 'job154', 'job155', 'job156', 'job157', 'job158', 'job159', 'job161', 'job160', 'job162', 'job163', 'job165', 'job164', 'job166', 'job167', 'job168', 'job169', 'job170', 'job171', 'job172', 'job173', 'job174', 'job175', 'job177', 'job176', 'job178', 'job179', 'job181', 'job180', 'job182', 'job183', 'job184', 'job185', 'job186', 'job187', 'job188', 'job189', 'job190', 'job191', 'job192', 'job193', 'job194', 'job195', 'job196', 'job197', 'job198', 'job199', 'job200', 'job201', 'job202', 'job203', 'job204', 'job205', 'job206', 'job207', 'job208', 'job209', 'job210', 'job211', 'job212', 'job213', 'job214', 'job215', 'job216', 'job217', 'job218', 'job219', 'job220', 'job221', 'job222', 'job223', 'job224', 'job225', 'job226', 'job227', 'job228', 'job229', 'job230', 'job231', 'job232', 'job233', 'job234', 'job235', 'job236', 'job237', 'job238', 'job240', 'job239', 'job241', 'job242', 'job243', 'job244', 'job245', 'job246', 'job247', 'job248', 'job249', 'job250', 'job251', 'job252', 'job253', 'job254', 'job256', 'job257', 'job255', 'job258', 'job260', 'job259', 'job261', 'job262', 'job263', 'job264', 'job265', 'job266', 'job267', 'job268', 'job269', 'job270', 'job272', 'job273', 'job271', 'job274', 'job275', 'job276', 'job277', 'job278', 'job279', 'job280', 'job281', 'job282', 'job283', 'job284', 'job285', 'job286', 'job287', 'job288', 'job289', 'job290', 'job291', 'job292', 'job293', 'job294', 'job295', 'job296', 'job298', 'job299', 'job301', 'job302', 'job304', 'job303', 'job305', 'job306', 'job308', 'job307', 'job309', 'job310', 'job311', 'job312', 'job313', 'job314', 'job315', 'job316', 'job317', 'job318', 'job319', 'job320', 'job321', 'job322', 'job323', 'job324', 'job325', 'job326', 'job327', 'job328', 'job329', 'job330', 'job331', 'job332', 'job333', 'job334', 'job335', 'job336', 'job337', 'job338', 'job339', 'job340', 'job341', 'job342', 'job343', 'job344', 'job345', 'job346', 'job347', 'job300', 'job348', 'job349', 'job350', 'job352', 'job351', 'job353', 'job354', 'job355', 'job356', 'job357', 'job358', 'job359', 'job360', 'job361', 'job362', 'job364', 'job363', 'job365', 'job366', 'job367', 'job368', 'job369', 'job370', 'job371', 'job372', 'job373', 'job374', 'job375', 'job376', 'job377', 'job378', 'job379', 'job380', 'job381', 'job382', 'job383', 'job385', 'job384', 'job386', 'job387', 'job388', 'job389', 'job390', 'job391', 'job392', 'job393', 'job394', 'job395', 'job396', 'job397', 'job398', 'job399', 'job400', 'job401', 'job402', 'job403', 'job404', 'job405', 'job406', 'job407', 'job408', 'job409', 'job410', 'job411', 'job412', 'job414', 'job413', 'job415', 'job417', 'job416', 'job418', 'job419', 'job421', 'job420', 'job422', 'job424', 'job425', 'job426', 'job423', 'job427', 'job428', 'job430', 'job429', 'job431', 'job432', 'job433', 'job434', 'job435', 'job436', 'job437', 'job438', 'job439', 'job440', 'job441', 'job442', 'job443', 'job444', 'job445', 'job446', 'job447', 'job448', 'job449', 'job450', 'job451', 'job452', 'job453', 'job454', 'job455', 'job456', 'job458', 'job457', 'job459', 'job460', 'job462', 'job463', 'job464', 'job465', 'job466', 'job467', 'job468', 'job469', 'job471', 'job472', 'job473', 'job474', 'job475', 'job476', 'job477', 'job478', 'job479', 'job480', 'job481', 'job482', 'job483', 'job485', 'job484', 'job486', 'job487', 'job488', 'job489', 'job490', 'job491', 'job492', 'job493', 'job494', 'job495', 'job496', 'job497', 'job498', 'job499', 'job501', 'job502', 'job503', 'job504', 'job500', 'job505', 'job506', 'job507', 'job508', 'job509', 'job510', 'job511', 'job512', 'job513', 'job514', 'job515', 'job516', 'job517', 'job518', 'job519', 'job520', 'job521', 'job522', 'job523', 'job524', 'job525', 'job526', 'job527', 'job528', 'job529', 'job530', 'job531', 'job532', 'job533', 'job534', 'job535', 'job536', 'job537', 'job538', 'job539', 'job540', 'job541', 'job542', 'job543', 'job544', 'job545', 'job546', 'job547', 'job548', 'job549', 'job550', 'job551', 'job552', 'job554', 'job553', 'job555', 'job556', 'job557', 'job558', 'job560', 'job559', 'job561', 'job562', 'job563', 'job564', 'job565', 'job566', 'job568', 'job567', 'job569', 'job570', 'job571', 'job573', 'job572', 'job574', 'job575', 'job576', 'job577', 'job578', 'job579', 'job581', 'job580', 'job582', 'job585', 'job584', 'job583', 'job586', 'job587', 'job589', 'job588', 'job590', 'job592', 'job591', 'job593', 'job594', 'job595', 'job596', 'job597', 'job598', 'job599', 'job600', 'job601', 'job602', 'job603', 'job604', 'job605', 'job606', 'job607', 'job608', 'job609', 'job610', 'job611', 'job612', 'job613', 'job614', 'job615', 'job616', 'job617', 'job618', 'job619', 'job621', 'job622', 'job620', 'job623', 'job624', 'job625', 'job626', 'job627', 'job628', 'job629', 'job630', 'job631', 'job632', 'job633', 'job634', 'job635', 'job636', 'job637', 'job638', 'job639', 'job640', 'job642', 'job643', 'job641', 'job644', 'job645', 'job646', 'job647', 'job648', 'job649', 'job650', 'job651', 'job652', 'job653', 'job654', 'job655', 'job656', 'job657', 'job658', 'job659', 'job660', 'job661', 'job662', 'job663', 'job664', 'job665', 'job666', 'job667', 'job668', 'job669', 'job670', 'job671', 'job672', 'job673', 'job674', 'job675', 'job676', 'job677', 'job678', 'job679', 'job680', 'job681', 'job682', 'job683', 'job684', 'job685', 'job686', 'job687', 'job688', 'job689', 'job690', 'job691', 'job692', 'job693', 'job694', 'job695', 'job696', 'job697', 'job698', 'job699', 'job700', 'job701', 'job702', 'job703', 'job704', 'job705', 'job706', 'job707', 'job708', 'job709', 'job710', 'job711', 'job713', 'job712', 'job714', 'job715', 'job716', 'job717', 'job718', 'job719', 'job721', 'job720', 'job722', 'job723', 'job724', 'job725', 'job726', 'job727', 'job728', 'job729', 'job730', 'job731', 'job733', 'job732', 'job734', 'job735', 'job736', 'job737', 'job738', 'job739', 'job740', 'job741', 'job742', 'job743', 'job744', 'job745', 'job746', 'job747', 'job748', 'job749', 'job751', 'job752', 'job753', 'job754', 'job755', 'job756', 'job757', 'job758', 'job759', 'job760', 'job761', 'job762', 'job763', 'job764', 'job765', 'job766', 'job767', 'job768', 'job769', 'job770', 'job771', 'job772', 'job773', 'job774', 'job775', 'job776', 'job777', 'job778', 'job780', 'job779', 'job781', 'job782', 'job783', 'job784', 'job785', 'job786', 'job787', 'job788', 'job789', 'job790', 'job791', 'job792', 'job793', 'job794', 'job795', 'job796', 'job797', 'job798', 'job799', 'job800', 'job801', 'job802', 'job803', 'job804', 'job805', 'job806', 'job807', 'job808', 'job809', 'job810', 'job811', 'job812', 'job813', 'job814', 'job815', 'job816', 'job817', 'job818', 'job819', 'job820', 'job821', 'job822', 'job823', 'job824', 'job825', 'job1192', 'job1364', 'job2556', 'job2591', 'job2621', 'job3123', 'job3559', 'job3875', 'job4301', 'job4619', 'job4660', 'job4907', 'job4977', 'job5414', 'job5548', 'job5558', 'job5967', 'job5979', 'job6054', 'job6206', 'job6108', 'job6420', 'job6733', 'job6954', 'job7096', 'job7218', 'job6953', 'job7767', 'job7850', 'job8294', 'job8124', 'job8693', 'job8741', 'job8912', 'job9032', 'job9034', 'job9509', 'job9731', 'job9960', 'job9843']
queue_add_time = {}
execution_start_time = {}
pod_done_time = {}
execution_time = {}
queue_delete_time = {}
with open('point5_all_2.logs', 'r') as f:
    for log in f:
        if "QueueAddTime" not in log:
            continue
        log = log.split()
        jobname = int(log[1].split("job")[1])
        jobnamestr = "job"+ str(jobname)
        if jobnamestr in discard_jobs:
            continue
        if jobname not in queue_add_time.keys():
            queue_add_time[jobname] = []
            queue_delete_time[jobname] = []
            execution_start_time[jobname] = []
            pod_done_time[jobname] = []
            execution_time[jobname] = []
        queue_add_time[jobname].append(float(log[5]))
        queue_delete_time[jobname].append(float(log[7]))
        execution_start_time[jobname].append(float(log[9]))
        pod_done_time[jobname].append(float(log[11]))
        execution_time[jobname].append(float(log[11]) - float(log[9]))

std_queue_add_time = []
std_queue_delete_time = []
std_execution_start_time = []
std_pod_done_time = []
std_execution_time = []
jobnames = []
#Pick randomly sampled jobs
#final_jobs = random.choices(list(queue_add_time.keys()), k=RANDOM_SAMPLE)
#for jobname in sorted(final_jobs):
for jobname in queue_add_time.keys():
    std_queue_add_time.append(np.std(queue_add_time[jobname]))
    std_queue_delete_time.append(np.std(queue_delete_time[jobname]))
    std_execution_start_time.append(np.std(execution_start_time[jobname]))
    std_pod_done_time.append(np.std(pod_done_time[jobname]))
    std_execution_time.append(np.std(execution_time[jobname]))
    jobnames.append(jobname)
    #print(jobname, np.std(queue_add_time[jobname]), np.std(queue_delete_time[jobname]), np.std(execution_start_time[jobname]), np.std((pod_done_time[jobname])))
#print(RANDOM_SAMPLE,"samples")
#print(np.percentile(std_queue_add_time, 50), np.percentile(std_queue_add_time, 99))
#print(np.percentile(std_queue_delete_time, 50), np.percentile(std_queue_delete_time, 99))
#print(np.percentile(std_execution_start_time, 50), np.percentile(std_execution_start_time, 99))
#print(np.percentile(std_pod_done_time, 50), np.percentile(std_pod_done_time, 99))


fig = plt.figure()
gs = fig.add_gridspec(4, hspace=0.2)
ax = gs.subplots(sharex=True, sharey=True)
#ax.tick_params(axis='y', which='major', labelsize=10)
#plt.setp(ax, ylim=[0,18000], yticks=[0,8000,16000])
plt.setp(ax, ylim=[0,1], yticks=[0,1], xlim=[0,15000])
#print("Plotting", std_queue_add_time)
x = np.sort(std_queue_add_time)
y = np.arange(len(x))/float(len(x))
print("Plotting", min(x), max(x), min(y), max(y))
ax[0].plot(x,y, label="Added to scheduler's queue", marker="o", markersize=2, markeredgecolor=colors[0], markerfacecolor=colors[0], color=colors[0])
#legend = ax[0].legend(loc='upper center')
legend = ax[0].legend(loc='center right')
#print("Plotting", std_queue_delete_time)
x = np.sort(std_queue_delete_time)
y = np.arange(len(x))/float(len(x))
std_queue_delete_time.sort()
#print("!!Plotting", std_queue_delete_time)
print("Plotting", min(x), max(x), min(y), max(y))
ax[1].plot(x,y, label="Scheduled", marker="o", markersize=2, markeredgecolor=colors[1], markerfacecolor=colors[1], color=colors[1])
legend = ax[1].legend(loc='center right')
#print("Plotting", std_execution_start_time)
x = np.sort(std_execution_start_time)
y = np.arange(len(x))/float(len(x))
print("Plotting", min(x), max(x), min(y), max(y))
ax[2].plot(x,y, label="Execution started", marker="o", markersize=2, markeredgecolor=colors[2], markerfacecolor=colors[2], color=colors[2])
legend = ax[2].legend(loc='center right')
#print("Plotting", std_pod_done_time)
x = np.sort(std_pod_done_time)
y = np.arange(len(x))/float(len(x))
print("Plotting", min(x), max(x), min(y), max(y))
ax[3].plot(x,y, label="Execution ended", marker="o", markersize=2, markeredgecolor=colors[3], markerfacecolor=colors[3], color=colors[3])
legend = ax[3].legend(loc='center right')
fig.text(0.5, 0.00, 'Standard Deviation (seconds)', ha='center')
fig.text(0.055, 0.5, 'Jobs', va='center', rotation='vertical')
#xticks = np.arange(0, 10003, 2000)
#delta = max(RANDOM_SAMPLE/5, 1)
xticks = np.arange(0, 14001, 3500)
ax[3].set_xticks(xticks)
fig.savefig('point5_all_ecdf.pdf', dpi=fig.dpi, bbox_inches='tight')
