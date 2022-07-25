### Starting a New Cluster

New Cluster Setup Steps -


0. Copy in id_ed* files into node0 so that it can ssh to other nodes. Also copy in .screenrc to node0. Also copy in kubelet and kubelet.c. 
1. git clone https://... /kubernetes-helper on the master node. (Node 0) - Generate personal access token and copy into node0 git clone command (password).
2. cd kubernetes-helper
3. Run pre-master.sh


### Reset an existing cluster

To restart master and workers -

yes | sudo kubeadm reset && sudo iptables -F && sudo iptables -t nat -F && sudo iptables -t mangle -F && sudo iptables -X && sudo rm -rf /etc/cni/net.d && sudo rm -rf $HOME/.kube/config ; sudo ip link set cni0 down ; sudo ip link set flannel.1 down ; sudo ip link delete cni0 ; sudo ip link delete flannel.1 ; sudo systemctl restart containerd && sudo systemctl restart kubelet

Master -
sudo kubeadm init --pod-network-cidr=10.244.0.0/16

mkdir -p $HOME/.kube && sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config && sudo chown sv440:decentralizedsch $HOME/.kube/config && kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml


//If $ (id -u) : $(id -g) gives an illegal variable, then run id, and replace these with sv440 and group name, etc.


(For the following command try =\$w1tch\#123 with no " " if the command fails.)
kubectl create secret docker-registry regcred --docker-server=https://index.docker.io/v1/ --docker-username=sv440 --docker-password="\\$w1tch#123" --docker-email="sv440@cam.ac.uk" && kubectl get secret regcred --output="jsonpath={.data.\\.dockerconfigjson}" | base64 --decode
edit/main/RefreshCluster.md

// Default scheduler - sudo mkdir -p /etc/kubernetes/schedulerconf folder && sudo cp kube-scheduler.conf /etc/kubernetes/schedulerconf

// Copy sudo cp /etc/kubernetes/scheduler.conf /etc/kubernetes/schedulerconf/

// Replace kube-scheduler.yaml with kube-scheduler.yaml.multiprofiles and restart default scheduler.


kubectl apply -f  my-scheduler.yaml 

Similarly, create the regcred secret for my-scheduler service account -
kubectl create secret docker-registry regcred -n kube-system --docker-server=https://index.docker.io/v1/ --docker-username=sv440 --docker-password="\\$w1tch#123" --docker-email="sv440@cam.ac.uk" && kubectl get secret regcred -n kube-system --output="jsonpath={.data.\\.dockerconfigjson}" | base64 --decode



kubectl patch serviceaccount my-scheduler -n kube-system  -p '{"imagePullSecrets": [{"name": "regcred"}]}'


// At this point, create worker nodes so other kube-system pods can be hosted on them.

//If nodes say NotReady with CNI network not ready error, then run worker-reset on all noes again, without cni0 and flannel.1 interface actions. Then the kubeadm init should bring nodes back.


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
1. Build new binary and copy into caelum-104.
sv440@caelum-104:~$ cat Dockerfile-scheduler
FROM gcr.io/distroless/base-debian10:latest
ADD ./kube-scheduler.peekmany /usr/local/bin/kube-scheduler
2. sudo docker -t sv440/sv440:<tag> -f Dockerfile-scheduler .
3. sudo docker push sv440/sv440:<tag>
4. Change manifest of scheduler to have image as the new tag.
5. If capturing a new log message, add that to syslog configs.
6. If changing centralized scheduler, regcred don't work for static pods. So, host local docker repository and pull image from there. 
        docker run -d -p 5000:5000 --restart=always --name registry registry:2 (check that sudo docker image ls should shouw registry as a repository.)
        docker tag my-scheduler-image localhost:5000/my-scheduler-image
        docker push localhost:5000/my-scheduler-image
        
