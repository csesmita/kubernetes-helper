To restart master and workers -
yes | sudo kubeadm reset && sudo iptables -F && sudo iptables -t nat -F && sudo iptables -t mangle -F && sudo iptables -X && sudo rm -rf /etc/cni/net.d && sudo rm -rf $HOME/.kube/config
sudo ip link set cni0 down && sudo ip link set flannel.1 down && sudo ip link delete cni0 && sudo ip link delete flannel.1 && systemctl restart containerd && systemctl restart kubelet

Master -
sudo kubeadm init --pod-network-cidr=10.244.0.0/16
  mkdir -p $HOME/.kube
  sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
  sudo chown $(id -u):$(id -g) $HOME/.kube/config
kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml

kubectl create secret docker-registry regcred --docker-server=https://index.docker.io/v1/ --docker-username=sv440 --docker-password="\$w1tch#123" --docker-email="sv440@cam.ac.uk"
kubectl get secret regcred --output="jsonpath={.data.\.dockerconfigjson}" | base64 --decode

kubectl run -i --tty redis-image --image redis --command "/bin/sh"	
kubectl attach redis-image -c redis-image -i -t

Nodes-
sudo kubeadm join 128.232.80.13:6443 --token 87ojgr.jwgf8ilz7uvnoz5r \
        --discovery-token-ca-cert-hash sha256:250c0679317c200c81a5b767522111e28a3c91509d0928f6b70603204f6ac873
