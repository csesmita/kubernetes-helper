yes | sudo kubeadm reset && sudo iptables -F && sudo iptables -t nat -F && sudo iptables -t mangle -F && sudo iptables -X && sudo rm -rf /etc/cni/net.d && sudo rm -rf $HOME/.kube/config && sudo ip link set cni0 down && sudo ip link set flannel.1 down && sudo ip link delete cni0 && sudo ip link delete flannel.1 && sudo systemctl restart containerd && sudo systemctl restart kubelet
sudo kubeadm join 128.232.80.13:6443 --token lpmoz4.6jgthuhbo2uj1h4z \
        --discovery-token-ca-cert-hash sha256:e013a562227dd69742a62eed94b239f26638b999c7159db0a8e40fe4014fcea5
