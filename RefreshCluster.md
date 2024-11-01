### Starting a New Cluster

New Cluster Setup Steps -


0. Copy in id_ed* files into node0 so that it can ssh to other nodes. Also copy in .screenrc to node0. Also copy in kubelet and kubelet.c. 
1. git clone https://... /kubernetes-helper on the master node. (Node 0) - Generate personal access token and copy into node0 git clone command (password).
2. SSH and set the shell to bash. sudo chsh -s /bin/bash sv440.
3. Log off and log in again. Check shell is $SHELL.
4. cd kubernetes-helper
5. Run pre-master.sh

#### Create a New Token and Print Join Command for a Node
kubeadm token create --print-join-command

### Reset an existing cluster
First reset master and workers.

Then init and join them all together.
This is because doing a reset onn workes after mmaster has been setup destroys the CNI config.

To restart master and workers -

yes | sudo kubeadm reset && sudo iptables -F && sudo iptables -t nat -F && sudo iptables -t mangle -F && sudo iptables -X && sudo rm -rf /etc/cni/net.d && sudo rm -rf $HOME/.kube/config ; sudo ip link set cni0 down ; sudo ip link set flannel.1 down ; sudo ip link delete cni0 ; sudo ip link delete flannel.1 ; sudo systemctl restart containerd && sudo systemctl restart kubelet

Master -
sudo kubeadm init --pod-network-cidr=10.244.0.0/16

mkdir -p $HOME/.kube && sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config && sudo chown sv440:decentralizedsch $HOME/.kube/config && kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml


//If $ (id -u) : $(id -g) gives an illegal variable, then run id, and replace these with sv440 and group name, etc.



// At this point, create worker nodes so other kube-system pods can be hosted on them.

kubectl apply -f commponent.yaml

(For the following command try =\$w1tch\#123 with no " " if the command fails.)
kubectl create secret docker-registry regcred --docker-server=https://index.docker.io/v1/ --docker-username=sv440 --docker-password="\\$w1tch#123" --docker-email="sv440@cam.ac.uk" && kubectl get secret regcred --output="jsonpath={.data.\\.dockerconfigjson}" | base64 --decode


// Default scheduler - sudo mkdir -p /etc/kubernetes/schedulerconf folder && sudo cp kube-scheduler.conf /etc/kubernetes/schedulerconf

// Copy sudo cp /etc/kubernetes/scheduler.conf /etc/kubernetes/schedulerconf/

// Replace kube-scheduler.yaml with kube-scheduler.yaml.multiprofiles and restart default scheduler.


kubectl apply -f  my-scheduler.yaml 

Similarly, create the regcred secret for my-scheduler service account -
kubectl create secret docker-registry regcred -n kube-system --docker-server=https://index.docker.io/v1/ --docker-username=sv440 --docker-password="\\$w1tch#123" --docker-email="sv440@cam.ac.uk" && kubectl get secret regcred -n kube-system --output="jsonpath={.data.\\.dockerconfigjson}" | base64 --decode



kubectl patch serviceaccount my-scheduler -n kube-system  -p '{"imagePullSecrets": [{"name": "regcred"}]}'




For custom scheduler instances - First create the service account (my-scheduler) then apply the scheduler configs.

After applying scheduler1, etc confirm regcred has been added. 
kubectl get pod scheduler1-xxx -n kube-system -o=jsonpath='{.spec.imagePullSecrets[0].name}{"\n"}'



// Disable API Server Rate limiting
// Disable enable-priority-and-fairness flag in API server.
// Perhaps set events-ttl to 3h0m0s or whatever time the script runs for.



kubectl apply -f redis-pod.yaml && kubectl apply -f redis-service.yaml

// For debugging redis, use - 
kubectl run -i --tty redis-image --image redis --command "/bin/sh"	
kubectl attach redis-image -c redis-image -i -t


//Change Redis IP in files - create script and in job.yaml. No docker image rebuilding required. 

// Change logging levels of kube-scheduler by copying from /tmp.


// Copy config dir from Master (104) to Management(306).
//scp -r /home/sv440/.kube/  caelum-306:

// Set taint on 306. kubectl taint nodes caelum-306 key1=value1:NoSchedule 

// Verify - kubectl get nodes -o custom-columns=NAME:.metadata.name,TAINTS:.spec.taints --no-headers 


Nodes-

sudo kubeadm join 128.232.80.13:6443 --token 0qshgj.2y0cyd7xvp1r5i1v \
        --discovery-token-ca-cert-hash sha256:abe80e46c3015541832ed616d43a6542023065b9588c7bc4c1fd15d22bc0ac70
        
        
        

Additional Notes - 
1. Syslog is used for logs' shipping. /etc/rsyslog.conf has to be modified for server (to allow logs on udp on port 514) and on the client (to export all syslog.* to caelum-xxx:514). Docker logging config (in /etc/docker/daemon.json) should point to log-driver as syslog. Restart systemctl after changes to rsyslog or docker services. Fluentd, etc not needed.
2. When starting an experiment, ensure screen and then start the experiment on management node. Else, once network disconnects, the script will stop.


Changing binary of the scheduler - 
0. Ensure scheduler is built with changes from fit.go to remove 110 pod limit. Ensure that kubelet is not built with this diff since only a 110 pods should be running at anytime on the kubelet and the rest should be in worker queue.
1. Build new binary and copy into caelum-104.
sv440@caelum-104:~$ cat Dockerfile-scheduler
FROM gcr.io/distroless/base-debian10:latest
ADD ./kube-scheduler.peekmany /usr/local/bin/kube-scheduler
2. sudo docker build -t sv440/sv440:<tag> -f Dockerfile-scheduler .
3. sudo docker push sv440/sv440:<tag>
4. Change manifest of scheduler to have image as the new tag.
5. If capturing a new log message, add that to syslog configs.
6. If changing centralized scheduler, regcred don't work for static pods. So, host local docker repository and pull image from there. 
        docker run -d -p 5000:5000 --restart=always --name registry registry:2 (check that sudo docker image ls should shouw registry as a repository.)
        docker tag my-scheduler-image localhost:5000/my-scheduler-image
        docker push localhost:5000/my-scheduler-image
 
        
        
HA Setup - 
        
        1. sudo apt update && sudo apt install keepalived haproxy
        
        2. Identify common interface. ip addr and using ping <nodeid> -I <interface>
        
        3. Identify non-pinging IP address on this interface. This is the API server dest port. Usually .200 IP should work.
        
        4. Copy in check_apiserver.sh and keepalived.conf into /etc/keepalived and haproxy.conf into /etc/haproxy
        
    ${STATE} is MASTER for one and BACKUP for all other hosts, hence the virtual IP will initially be assigned to the MASTER.
    ${INTERFACE} is the network interface taking part in the negotiation of the virtual IP, e.g. eth0.
    ${ROUTER_ID} should be the same for all keepalived cluster hosts while unique amongst all clusters in the same subnet. Many distros pre-configure its value to 51.
    ${PRIORITY} should be higher on the control plane node than on the backups. Hence 101 and 100 respectively will suffice.
    ${AUTH_PASS} should be the same for all keepalived cluster hosts, e.g. 42
    ${APISERVER_VIP} is the virtual IP address negotiated between the keepalived cluster hosts.

        
        5. Change check_apiserver.sh
        
    ${APISERVER_VIP} is the virtual IP address negotiated between the keepalived cluster hosts.
    ${APISERVER_DEST_PORT} the port through which Kubernetes will talk to the API Server.

        6. Change haproxy.conf
        
        
    ${APISERVER_DEST_PORT} the port through which Kubernetes will talk to the API Server.
    ${APISERVER_SRC_PORT} the port used by the API Server instances
    ${HOST1_ID} a symbolic name for the first load-balanced API Server host
    ${HOST1_ADDRESS} a resolvable address (DNS name, IP address) for the first load-balanced API Server host
    additional server lines, one for each load-balanced API Server host

        7. Run on all control plane nodes -
        systemctl enable haproxy --now && systemctl enable keepalived --now
        
        8. kubeadm init --control-plane-endpoint vip.mycluster.local:8443 --pod-network-cidr=10.244.0.0/16 --upload-certs
        
        Continue from there on. 
        
