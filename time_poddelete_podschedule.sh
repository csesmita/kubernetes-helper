#!/bin/bash
# This script finds all nodes in the first 500 lines of 
# the given syslog and then for each of these nodes, 
# looks for schedule and delete events of pods. It 
# then writes these logs alone into a temp node file.
match_delete="Delete event for scheduled pod"
match_schedule="Attempting to bind pod to node"
# First fish out all nodenames.
rm -rf /local/scratch/tempdir/
mkdir -p /local/scratch/tempdir/
nodes=($(fgrep -m 500 "$match_schedule" /local/scratch/syslog | awk -F 'node=' {'print $2'} | awk -F ' ' {'print $1'} | tr -d '"' | sort -u))
for nodename in "${nodes[@]}"; do
    tempfile="/local/scratch/tempdir/temp-${nodename}"
    LC_ALL=C fgrep -e "$match_delete" -e "$match_schedule" /local/scratch/syslog > $tempfile
done
