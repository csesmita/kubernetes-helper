To restart master and workers -

yes | sudo kubeadm reset && sudo iptables -F && sudo iptables -t nat -F && sudo iptables -t mangle -F && sudo iptables -X && sudo rm -rf /etc/cni/net.d && sudo rm -rf $HOME/.kube/config && sudo ip link set cni0 down && sudo ip link set flannel.1 down && sudo ip link delete cni0 && sudo ip link delete flannel.1 && sudo systemctl restart containerd && sudo systemctl restart kubelet

Master -
sudo kubeadm init --pod-network-cidr=10.244.0.0/16

mkdir -p $HOME/.kube && sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config && sudo chown $(id -u):$(id -g) $HOME/.kube/config && kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml


kubectl create secret docker-registry regcred --docker-server=https://index.docker.io/v1/ --docker-username=sv440 --docker-password="\\$w1tch#123" --docker-email="sv440@cam.ac.uk" && kubectl get secret regcred --output="jsonpath={.data.\\.dockerconfigjson}" | base64 --decode

kubectl apply -f  my-scheduler.yaml 

Similarly, create the regcred secret for my-scheduler service account -
kubectl create secret docker-registry regcred -n kube-system --docker-server=https://index.docker.io/v1/ --docker-username=sv440 --docker-password="\\$w1tch#123" --docker-email="sv440@cam.ac.uk" && kubectl get secret regcred -n kube-system --output="jsonpath={.data.\\.dockerconfigjson}" | base64 --decode


kubectl patch serviceaccount my-scheduler -n kube-system  -p '{"imagePullSecrets": [{"name": "regcred"}]}'

For custom scheduler instances - First create the service account (my-scheduler) then apply the scheduler configs.

After applying scheduler1, etc confirm regcred has been added. 
kubectl get pod scheduler1-xxx -n kube-system -o=jsonpath='{.spec.imagePullSecrets[0].name}{"\n"}'



kubectl apply -f redis-pod.yaml && kubectl apply -f redis-service.yaml


//Change Redis IP in files - create script and in job.yaml. No docker image rebuilding required. 

// Change logging levels of kube-scheduler by copying from /tmp, and --terminated-pod-gc-threshold by copying kube-controller-manager from /tmp. //Copy kube-scheduler scheduler.conf into schedulerconf/ if using the multi profile with schedulerconf/	

// Copy config dir from 104 to 306.
//scp -r /home/sv440/.kube/  caelum-306:

// Set taint on 306. Kubectl taint nodes caelum-306 key1=value1:NoSchedule. 

// Verify - kubectl get nodes -o custom-columns=NAME:.metadata.name,TAINTS:.spec.taints --no-headers 


Nodes-

sudo kubeadm join 128.232.80.13:6443 --token 0qshgj.2y0cyd7xvp1r5i1v \
        --discovery-token-ca-cert-hash sha256:abe80e46c3015541832ed616d43a6542023065b9588c7bc4c1fd15d22bc0ac70
        
        
        

Additional Notes - 
1. Syslog is used for logs' shipping. /etc/rsyslog.conf has to be modified for server (to allow logs on udp on port 514) and on the client (to export all syslog.* to caelum-xxx:514). Docker logging config (in /etc/docker/daemon.json) should point to log-driver as syslog. Restart systemctl after changes to rsyslog or docker services. Fluentd, etc not needed.
