#!/bin/bash
#This script copies in logs from all schedulers.
fetch () {
    line=$1
    schedulerName=$(echo "$line" | awk -F ' ' {'print $1'})
    nodeLine=$(kubectl describe pods -n kube-system $schedulerName | grep Node:)
    nodeName=$(echo "$nodeLine" | awk -F' ' {'print $2'} | awk -F'.' {'print $1'})
    scp $nodeName:/local/scratch/syslog /local/scratch/$schedulerName
}

kubectl get pods -n kube-system | grep scheduler | grep -v kube-scheduler-node0 | grep  -e scheduler[1-9]- -e scheduler1[0-9]- -e scheduler2[0-5]- | while read line ; do
    fetch "$line" &
done
wait
