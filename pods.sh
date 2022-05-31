#!/bin/bash

match="Work completed by this task"
if [ "$#" -eq 1 ]; then
    rm pods.txt || true
    #return podnames for all jobs
    for (( i=1; i<=$1; i++ )) 
    do
        jobs=()
        jobname="job$i"
        podprefix="${jobname}-"
        while read -r line; do
           if [[ $line == *${match}* ]]; then
               jobs+=( "$(cut -d' ' -f6 <<< ${line} | cut -d':' -f1)" )
           fi
        done < <(grep $podprefix /local/scratch/syslog)
        printf "${jobs[*]} \n" >> pods.txt
    done
elif [ "$#" -eq 2 ]; then
    #return timestamp sorted logs for this pod.
    podname=$2
    logs=$(grep $podname /local/scratch/syslog |sort -k7)
    echo "$logs"
else
    echo "Illegal number of arguments."
fi
