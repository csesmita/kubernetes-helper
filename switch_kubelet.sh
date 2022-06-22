#!/bin/bash
echo "Enter id of last worker node"
read numnodes
#Don't include node0 since it is already setup as master node.
for (( i=2; i<=$numnodes; i++ ))
do
    node="node$i"
    scp kubelet kubelet.c $node: &&   ssh $node "sudo systemctl stop kubelet && sudo cp kubelet /usr/bin/kubelet && sudo systemctl start kubelet" &
done
wait
