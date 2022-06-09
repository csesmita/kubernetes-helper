#!/bin/bash
numnodes=$1

cd $HOME/kubernetes-helper
echo "Current working directory is"
echo pwd
read -n 1 -p "Ensure directory is set to kubernetes-helper, and that this is node0. Press to continue."

echo "Creating Secret Credentials and Verifying."
kubectl create secret docker-registry regcred --docker-server=https://index.docker.io/v1/ --docker-username=sv440 --docker-password=\$w1tch#123 --docker-email="sv440@cam.ac.uk" && kubectl get secret regcred --output="jsonpath={.data.\\.dockerconfigjson}" | base64 --decode
read -n 1 -p "Credentials look ok?"

sudo mkdir -p /etc/kubernetes/schedulerconf && sudo cp kube-scheduler.conf /etc/kubernetes/schedulerconf && sudo cp /etc/kubernetes/scheduler.conf /etc/kubernetes/schedulerconf/
sudo mv /etc/kubernetes/manifests/kube-scheduler.yaml /tmp && sudo cp kube-scheduler.yaml.multiprofiles /etc/kubernetes/manifests/kube-scheduler.yaml

read -n 1 -p "Copy in API server paramteres and restart. Press any key when ready"
read -n 1 -p "Check API server is up using kubectl get pods -n kube-system | grep apiserver"

kubectl apply -f  my-scheduler.yaml && kubectl create secret docker-registry regcred -n kube-system --docker-server=https://index.docker.io/v1/ --docker-username=sv440 --docker-password=\$w1tch#123 --docker-email="sv440@cam.ac.uk" && kubectl get secret regcred -n kube-system --output="jsonpath={.data.\.dockerconfigjson}" | base64 --decode
read -n 1 -p "Credentials look ok for my-scheduler?"

kubectl patch serviceaccount my-scheduler -n kube-system  -p '{"imagePullSecrets": [{"name": "regcred"}]}'

for (( i=1; i<=$numnodes; i++ ))
do
    node="node$i"
    ssh $node "/bin/sh -s" < worker-reset.sh &
done
wait

sleep 10
kubectl get nodes
read -n 1 -p "Check the status of nodes. Press when all are ready."

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
node1name=$(kubectl get nodes -n kube-system | grep node1 | awk -F' ' '{print $1}')
kubectl taint nodes $node1name key1=value1:NoSchedule
kubectl get nodes -o custom-columns=NAME:.metadata.name,TAINTS:.spec.taints --no-headers
read -n 1 -p "Verify that no taint has been set on $node1name"