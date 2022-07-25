#!/bin/bash
numnodes=$1

cd $HOME/kubernetes-helper
echo "Current working directory is"
pwd
read -n 1 -p "Ensure directory is set to kubernetes-helper, and that this is node0. Press to continue."

echo "Creating Secret Credentials and Verifying."
kubectl create secret docker-registry regcred --docker-server=https://index.docker.io/v1/ --docker-username=sv440 --docker-password=\$w1tch#123 --docker-email="sv440@cam.ac.uk" && kubectl get secret regcred --output="jsonpath={.data.\\.dockerconfigjson}" | base64 --decode
read -n 1 -p "Credentials look ok?"

sudo mkdir -p /etc/kubernetes/schedulerconf && sudo cp kube-scheduler.conf /etc/kubernetes/schedulerconf && sudo cp /etc/kubernetes/scheduler.conf /etc/kubernetes/schedulerconf/
sudo mv /etc/kubernetes/manifests/kube-scheduler.yaml /tmp && sudo mv /etc/kubernetes/manifests/kube-apiserver.yaml /tmp && sudo mv /etc/kubernetes/manifests/kube-controller-manager.yaml /tmp && sudo mv /etc/kubernetes/manifests/etcd.yaml /tmp

read -n 1 -p "Copy in API server, Kube Controller Manager, Kube Scheduler (from kube-scheduler.yaml.multiprofiles) and ETCD paramteres and restart. Also check image details are 1.23.6. Press any key when ready."
read -n 1 -p "Check API server, etc are up using kubectl get pods -n kube-system | grep apiserver"

kubectl apply -f cpu-defaults.yaml --namespace=default

kubectl apply -f  my-scheduler.yaml && kubectl create secret docker-registry regcred -n kube-system --docker-server=https://index.docker.io/v1/ --docker-username=sv440 --docker-password=\$w1tch#123 --docker-email="sv440@cam.ac.uk" && kubectl get secret regcred -n kube-system --output="jsonpath={.data.\.dockerconfigjson}" | base64 --decode
read -n 1 -p "Credentials look ok for my-scheduler?"

kubectl patch serviceaccount my-scheduler -n kube-system  -p '{"imagePullSecrets": [{"name": "regcred"}]}'

#Include the management node for now.
for (( i=1; i<=$numnodes; i++ ))
do
    node="node$i"
    ssh $node "/bin/sh -s" < worker-reset.sh &
done
wait

sleep 10
kubectl get nodes
read -n 1 -p "Check the status of nodes. Press when all are ready."

read -n 1 -p "Ensure desired number of schedulers are in the scheduler_config. Press when ready."
kubectl apply -f scheduler_configs

echo "Checking if credentials got applied correctly to custom schedulers."
schedname=$(kubectl get pods -n kube-system | grep scheduler3 | awk -F' ' '{print $1}')
kubectl get pod $schedname -n kube-system -o=jsonpath='{.spec.imagePullSecrets[0].name}{"\n"}'
read -n 1 -p "All ok?"

kubectl apply -f redis-pod.yaml && kubectl apply -f redis-service.yaml
kubectl get svc | grep redis
read -n 1 -p "Change Redis IP in files - jobs.py and in job_*.yaml. Press when ready."

echo "Making node1 the management node."
scp -r $HOME/.kube/  node1:
node1name=$(kubectl get nodes -n kube-system | grep node1.sv440 | awk -F' ' '{print $1}')
kubectl taint nodes $node1name key1=value1:NoSchedule
kubectl get nodes -o custom-columns=NAME:.metadata.name,TAINTS:.spec.taints --no-headers
read -n 1 -p "Verify that taint has been set on $node1name"

#Syslog config - Master
sudo cp syslog-configs/50-default.conf /etc/rsyslog.d/
sudo cp syslog-configs/master-node-rsyslog.conf /etc/rsyslog.conf
sudo systemctl restart rsyslog

#Syslog config - Management
scp syslog-configs/50-default.conf syslog-configs/management-node-rsyslog.conf YH.tr pods.py pods.sh rediswq.py delete_jobs.sh jobs.py job_c.yaml job_d.yaml ~/.screenrc node1:
ssh node1 "sudo cp 50-default.conf /etc/rsyslog.d/; sudo cp management-node-rsyslog.conf /etc/rsyslog.conf;sudo systemctl restart rsyslog"

#Syslog config - Workers. Starts with 2 since 1 is the management node.
for (( i=2; i<=$numnodes; i++ ))
do
    node="node$i"
    scp syslog-configs/50-default.conf syslog-configs/worker-node-rsyslog.conf $node: &
done
wait

for (( i=2; i<=$numnodes; i++ ))
do
    node="node$i"
    ssh $node "sudo cp 50-default.conf /etc/rsyslog.d/; sudo cp worker-node-rsyslog.conf /etc/rsyslog.conf; sudo systemctl restart rsyslog" &
done
wait

echo "If running C then delete all schedulers using kubectl delete -f scheduler_configs/"
echo "If running D then copy in kubelet and run switch_kubelet.sh. Let C scheduler remain as it schedules system pods."
echo "Ensure you start a screen on node1 before starting experiments. Also, press yes when asked about screen. CHeck if jobs are created after starting the script."
