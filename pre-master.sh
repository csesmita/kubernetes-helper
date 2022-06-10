#!/bin/bash

git clone https://github.com/csesmita/kubernetes-helper.git
git config --global credential.helper storage
bash remote-setup.sh
yes | sudo kubeadm reset && sudo iptables -F && sudo iptables -t nat -F && sudo iptables -t mangle -F && sudo iptables -X && sudo rm -rf /etc/cni/net.d && sudo rm -rf $HOME/.kube/config ; sudo ip link set cni0 down ; sudo ip link set flannel.1 down ; sudo ip link delete cni0 ; sudo ip link delete flannel.1 ; sudo systemctl restart containerd && sudo systemctl restart kubelet
sudo kubeadm init --pod-network-cidr=10.244.0.0/16
mkdir -p $HOME/.kube && sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config && sudo chown sv440:decentralizedsch $HOME/.kube/config && kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml
