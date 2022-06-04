#!/bin/bash
#This script first finds the pods of the given job.
#It then looks for logs of each of the pods, sorts them by
#the log creation timestamp, and writes them into a file.
match="Work completed by this task"
if [ "$#" -eq 1 ]; then
    pods=()
    jobname=$1
    podprefix="${jobname}-"
    filename="${jobname}.txt"
    rm $filename || true
    while read -r line; do
       if [[ $line == *${match}* ]]; then
           podname=( "$(cut -d' ' -f7 <<< ${line} | cut -d':' -f1)" )
           pods+=("$podname")
           #return timestamp sorted logs for these pods.
           logs=$(LC_ALL=C fgrep $podname /local/scratch/syslog |sort -k7)
           echo "$logs" >> $filename
       fi
    done < <(grep $podprefix /local/scratch/syslog)
    echo "${#pods[@]}" >> $filename
    printf "${pods[*]} \n" >> $filename
else
    echo "Illegal number of arguments."
fi
