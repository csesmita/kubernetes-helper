#!/bin/bash
target_dir="/var/log/pods/kube-system_kube-scheduler*/*/"
cd $target_dir
links=$(find . -type l -ls | awk '{print $13}')
linksarray=($links)
for link in "${linksarray[@]}"
do
    cd "$(dirname "${link}")"    
    echo $w1tch#123 | sudo /usr/sbin/logrotate /etc/logrotate.d/schedulerlogs
done
