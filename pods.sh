#!/bin/bash
#This script first finds the accountable pods of the given job.
#It then looks for logs of each of the pods, sorts them by
#the log creation timestamp, and writes them into a file.
match="Work completed by this task"
if [ "$#" -eq 1 ]; then
    pods=()
    jobname=$1
    #numpods=$2
    podprefix="${jobname}-"
    filename="${jobname}.txt"
    tempfile="/local/scratch/temp-${jobname}"
    rm -f $filename || true
    count=0
    # Find all logs of this job. Expensive. So we write this into a file.
    LC_ALL=C fgrep $podprefix results/jrt/unsaturated/syslog.c.5000J.50X.47N.YH > $tempfile
    # Find all accountable pods of this job.
    while read line; do
       if [[ $line == *${match}* ]]; then
           podname=$(echo "${line}"| sed 's/^.*\('"$podprefix"'.*\):.*$/\1/')
           pods+=($podname)
           ((count++))
           #if [ $count -eq $numpods ]; then
           #    break
           #fi
       fi
    done <$tempfile
    #For each pod, time sort its logs and write into final file.
    for podname in "${pods[@]}"; do
        #Grep for all logs with podname and sort them.
        #First sort on date and then time.
        #Kubelet sometimes throws extra logs. If so, prune them out first.
        logs=$(LC_ALL=C fgrep $podname $tempfile | sed 's/{"cniVersion".*}//' | sort -k6,7)
        echo "Logs for $podname" >> $filename
        echo "$logs" >> $filename
    done
    rm $tempfile
else
    echo "Illegal number of arguments."
fi
