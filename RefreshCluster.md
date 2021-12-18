To restart master and workers -
yes | sudo kubeadm reset && sudo iptables -F && sudo iptables -t nat -F && sudo iptables -t mangle -F && sudo iptables -X && sudo rm -rf /etc/cni/net.d && sudo rm -rf $HOME/.kube/config
sudo ip link set cni0 down && sudo ip link set flannel.1 down && sudo ip link delete cni0 && sudo ip link delete flannel.1 && systemctl restart containerd && systemctl restart kubelet

Master -
sudo kubeadm init --pod-network-cidr=10.244.0.0/16
mkdir -p $HOME/.kube &&  sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config &&   sudo chown $(id -u):$(id -g) $HOME/.kube/config
kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml

kubectl create secret docker-registry regcred --docker-server=https://index.docker.io/v1/ --docker-username=sv440 --docker-password="\$w1tch#123" --docker-email="sv440@cam.ac.uk"
kubectl get secret regcred --output="jsonpath={.data.\.dockerconfigjson}" | base64 --decode

kubectl apply -f redis-pod.yaml
kubectl apply -f redis-service.yaml
kubectl run -i --tty redis-image --image redis --command "/bin/sh"	
kubectl attach redis-image -c redis-image -i -t

Nodes-
sudo kubeadm join 128.232.80.13:6443 --token 0qshgj.2y0cyd7xvp1r5i1v \
        --discovery-token-ca-cert-hash sha256:abe80e46c3015541832ed616d43a6542023065b9588c7bc4c1fd15d22bc0ac70
