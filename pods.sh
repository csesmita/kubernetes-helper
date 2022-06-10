#!/bin/bash
#This script first finds the accountable pods of the given job.
#It then looks for logs of each of the pods, sorts them by
#the log creation timestamp, and writes them into a file.
match="Work completed by this task"
start_scheduling="Add event for unscheduled pod"
end_scheduling="Delete event for scheduled pod"
if [ "$#" -eq 2 ]; then
    jobname=$1
    numpods=$2
    podprefix="${jobname}-"
    filename="${jobname}.txt"
    rm -f $filename || true
    count=0
    #These are the log lines per pod we are interested in -
    #1(Add event for unscheduled pod)
    #*(About to try and schedule pod)
    #*(Unable to schedule pod)
    #1(Attempting to bind pod)
    #1(Delete event for unscheduled pod)
    #1(Added pod to worker queue)
    #1(Ejecting pod from worker queue)
    while read -r line; do
       if [[ $line == *${match}* ]]; then
           podname=( "$(cut -d' ' -f6 <<< ${line} | cut -d':' -f1)" )
           #We need timestamp sorted logs for these pods.
           #But we cannot use a simple maxnum param in grep for this.
           #like so - logs=$(LC_ALL=C fgrep -m $maxnum $podname /local/scratch/syslog |sort -k7)
           #because there are some logs that can occur multiple times like
           #about to try and schedule pod and unable to schedule pod.
           #So, look for line numbers of start and end of scheduling for this pod
           #(add event for unscheduled and delete event for unscheduled). 
           # Only grep for scheduler logs in between these lines.
           startline=$(grep -n -m 1 "$start_scheduling.*$podname"  /local/scratch/syslog|awk -F":" {'print $1'})
           endline=$(grep -n -m 1 "$end_scheduling.*$podname"  /local/scratch/syslog |awk -F":" {'print $1'})
           #Keep some buffer on the starting edge as well.
           start=$startline
           if (($startline > 100)); then
               start=$(($startline - 100))
           fi
           logs=$(tail -n +$start /local/scratch/syslog |head -n $(($endline - $start)) | LC_ALL=C fgrep $podname | sort -k6)
           echo "Logs for $podname" >> $filename
           echo "$logs" >> $filename
           ((count++))
           if [ $count -eq $numpods ]; then
               break
           fi
       fi
    done < <(LC_ALL=C fgrep $podprefix /local/scratch/syslog)
else
    echo "Illegal number of arguments."
fi
