echo "This file is executed at airwolf post a successful run at cloudlab cluster."
if [ "$#" -ne 1 ]; then
	echo "Provide the name of node1 for scp'ing the files."
	exit 1
fi
node=$1
cd ~/kubernetes-helper
scp $node:d.* results/jrt/
scp $node:c.* results/jrt/
scp $node:pods.d.* results/pods/
scp $node:pods.c.* results/pods/
scp $node:node_utilization.txt results/utilization/

scp $node:/local/scratch/syslog results/
scp results/syslog caelum-306:/local/scratch/syslog.xxxx
echo "Change the name of the syslog file on caelum-306."
echo "Press any key when done."
read  -n 1
